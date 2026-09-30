from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
from urllib import robotparser
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urldefrag, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid

from .citation import export, validate_sidecars
from .model import Job, Reference, RequestPlan, digest, json_bytes, now, stable_id
from .providers import exact_openalex_match, extract_records, normalize_openalex, normalize_uspto, plan
from .storage import Library


MAX_RESPONSE_BYTES = 25 * 1024 * 1024
MAX_FILE_BYTES = 1024 * 1024 * 1024
LOCAL_CAPTURE_SUFFIXES = {".pdf", ".html", ".htm", ".txt", ".md", ".json", ".jsonl", ".xml", ".csv", ".yaml", ".yml", ".ris", ".bib"}


@dataclass
class Response:
    body: bytes
    url: str
    status: int
    content_type: str


class _BoundRedirect(HTTPRedirectHandler):
    def __init__(self, hosts: set[str]):
        self.hosts = hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname not in self.hosts:
            raise ValueError("redirect crossed the approved HTTPS host boundary")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Transport:
    def __init__(self, *, timeout: float = 30, retries: int = 2, min_interval: float = 0.25):
        self.timeout = timeout
        self.retries = retries
        self.min_interval = min_interval
        self._last_request = 0.0
        self._robots_cache: dict[str, robotparser.RobotFileParser | bool] = {}

    def fetch(self, request: RequestPlan, allowed_hosts: set[str]) -> Response:
        parsed = urlparse(request.url)
        if parsed.scheme != "https" or parsed.hostname not in allowed_hosts or parsed.hostname != request.allowed_host:
            raise ValueError("request URL is not on an allowed HTTPS host")
        headers = {"User-Agent": "ReferenceSuite/0.1", "Accept": "application/json, text/html, application/pdf, */*"}
        if parsed.hostname == "api.openalex.org" and os.environ.get("OPENALEX_EMAIL"):
            email = os.environ["OPENALEX_EMAIL"].strip()
            if "\r" in email or "\n" in email:
                raise ValueError("invalid OPENALEX_EMAIL")
            headers["User-Agent"] += f" (mailto:{email})"
            headers["From"] = email
        if request.auth_env:
            key = os.environ.get(request.auth_env)
            if not key:
                raise ValueError(f"missing API key environment variable: {request.auth_env}")
            headers["X-API-KEY"] = key
        body = json_bytes(request.body) if request.body is not None else None
        if body is not None:
            headers["Content-Type"] = "application/json"
        opener = build_opener(_BoundRedirect(allowed_hosts))
        for attempt in range(self.retries + 1):
            interval = self.min_interval - (time.monotonic() - self._last_request)
            if interval > 0:
                time.sleep(interval)
            self._last_request = time.monotonic()
            try:
                req = Request(request.url, data=body, headers=headers, method=request.method)
                with opener.open(req, timeout=self.timeout) as response:
                    content_len = response.headers.get("Content-Length")
                    if content_len and int(content_len) > MAX_RESPONSE_BYTES:
                        raise ValueError("response exceeds size cap")
                    data = response.read(MAX_RESPONSE_BYTES + 1)
                    if len(data) > MAX_RESPONSE_BYTES:
                        raise ValueError("response exceeds size cap")
                    return Response(data, response.url, response.status, response.headers.get("Content-Type", ""))
            except HTTPError as error:
                if attempt >= self.retries or error.code not in (429, 500, 502, 503, 504):
                    raise
                retry_after = error.headers.get("Retry-After") if error.headers else None
                time.sleep(min(float(retry_after), 10) if retry_after and retry_after.isdigit() else 2**attempt)
            except URLError:
                if attempt >= self.retries:
                    raise
                time.sleep(2**attempt)
        raise RuntimeError("unreachable")

    def robots_allowed(self, url: str, allowed_hosts: set[str]) -> bool:
        parsed = urlparse(url)
        cached = self._robots_cache.get(parsed.hostname)
        if cached is not None:
            return cached.can_fetch("ReferenceSuite/0.1", url) if isinstance(cached, robotparser.RobotFileParser) else cached
        robots_url = f"https://{parsed.hostname}/robots.txt"
        try:
            response = self.fetch(RequestPlan("GET", robots_url, "robots policy", parsed.hostname), allowed_hosts)
            policy = robotparser.RobotFileParser()
            policy.parse(response.body.decode("utf-8", errors="replace").splitlines())
            self._robots_cache[parsed.hostname] = policy
            delay = policy.crawl_delay("ReferenceSuite/0.1")
            if isinstance(delay, (int, float)):
                self.min_interval = max(self.min_interval, min(float(delay), 60.0))
            return policy.can_fetch("ReferenceSuite/0.1", url)
        except HTTPError as error:
            if error.code == 404:
                self._robots_cache[parsed.hostname] = True
                return True
            self._robots_cache[parsed.hostname] = False
            return False
        except (URLError, ValueError):
            self._robots_cache[parsed.hostname] = False
            return False

    def download(self, request: RequestPlan, allowed_hosts: set[str], destination: Path) -> Response:
        parsed = urlparse(request.url)
        if parsed.scheme != "https" or parsed.hostname not in allowed_hosts or parsed.hostname != request.allowed_host:
            raise ValueError("download URL is not on an allowed HTTPS host")
        destination.parent.mkdir(parents=True, exist_ok=True)
        part = destination.with_name(destination.name + ".part")
        offset = part.stat().st_size if part.exists() else 0
        if offset > MAX_FILE_BYTES:
            raise ValueError("partial download exceeds file size cap")
        headers = {"User-Agent": "ReferenceSuite/0.1", "Accept": "*/*"}
        if request.auth_env:
            key = os.environ.get(request.auth_env)
            if not key:
                raise ValueError(f"missing API key environment variable: {request.auth_env}")
            headers["X-API-KEY"] = key
        if offset:
            headers["Range"] = f"bytes={offset}-"
        opener = build_opener(_BoundRedirect(allowed_hosts))
        req = Request(request.url, headers=headers, method="GET")
        with opener.open(req, timeout=self.timeout) as response:
            if offset and response.status != 206:
                offset = 0
            if offset and response.status == 206:
                content_range = response.headers.get("Content-Range", "")
                if not content_range.startswith(f"bytes {offset}-"):
                    raise ValueError("resumed download has unexpected Content-Range")
            mode = "ab" if offset else "wb"
            total = offset
            with part.open(mode) as stream:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_FILE_BYTES:
                        raise ValueError("download exceeds file size cap")
                    stream.write(chunk)
            part.replace(destination)
            return Response(b"", response.url, response.status, response.headers.get("Content-Type", ""))


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts: list[str] = []
        self.title = ""
        self.in_title = False
        self.page_links: list[str] = []
        self.asset_links: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.page_links.append(attributes["href"])
        if tag in {"img", "script", "source", "link"} and (attributes.get("src") or attributes.get("href")):
            self.asset_links.append(attributes.get("src") or attributes.get("href"))
        if tag in {"script", "style", "noscript"}:
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag in {"p", "h1", "h2", "h3", "li", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.skip:
            return
        value = data.strip()
        if value:
            if self.in_title:
                self.title += value + " "
            self.parts.append(value + " ")

    def markdown(self) -> str:
        return re.sub(r"\n{3,}", "\n\n", "".join(self.parts)).strip() + "\n"


def _write_jsonl(path: Path, values: list[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", value)[:80]


def _candidate_file_urls(job: Job, raw: dict) -> list[str]:
    if not job.download_files:
        return []
    urls: list[str] = []
    if job.provider == "openalex":
        loc = raw.get("best_oa_location") or {}
        if loc.get("pdf_url"):
            urls.append(loc["pdf_url"])
    elif job.provider == "uspto":
        for key in ("downloadUrl", "documentURI"):
            if raw.get(key):
                urls.append(raw[key])
        for opt in raw.get("downloadOptionBag") or []:
            if isinstance(opt, dict):
                urls.extend(x for x in (opt.get("downloadUrl"), opt.get("downloadURI")) if x)
        if job.operation == "bulk":
            product = raw.get("productIdentifier") or job.value
            bag = (raw.get("productFileBag") or {}).get("fileDataBag") or []
            for item in bag[:job.max_results]:
                if isinstance(item, dict) and item.get("fileName"):
                    urls.append("https://api.uspto.gov/api/v1/datasets/products/files/" + quote(str(product), safe="") + "/" + quote(str(item["fileName"]), safe=""))
    return urls[:job.max_results]


def _openalex_work_id(value: str) -> str | None:
    match = re.search(r"(?:^|/)W(\d+)$", value, re.I)
    return "W" + match.group(1) if match else None


def _write_capture(run_dir: Path, response: Response, name: str, suffix_override: str = "") -> tuple[str, str]:
    sha = digest(response.body)
    suffix = suffix_override if suffix_override in LOCAL_CAPTURE_SUFFIXES else (".json" if "json" in response.content_type else (".html" if "html" in response.content_type else (".pdf" if "pdf" in response.content_type else ".bin")))
    path = run_dir / "raw" / (_safe_name(name) + "_" + sha[:12] + suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.body)
    return str(path.resolve()), sha


def execute(job: Job, root: Path, transport: Transport | None = None, resume_run_id: str | None = None, renderer=None) -> dict:
    """Execute a prevalidated job. Network access occurs only here, never in plan()."""
    requests = plan(job)
    transport = transport or Transport()
    allowed = {r.allowed_host for r in requests} | {h.lower() for h in job.allow_hosts}
    run_id = resume_run_id or (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8])
    if not re.fullmatch(r"[A-Za-z0-9_]+", run_id):
        raise ValueError("invalid run ID")
    run_dir = root / "out" / job.provider / job.dataset / run_id
    library = Library(root)
    if resume_run_id:
        existing = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
        if existing["job"] != json.loads(json.dumps(job.asdict())) or existing["status"] == "complete":
            library.close()
            raise ValueError("resume job differs or run is already complete")
        library.resume(run_id)
    else:
        run_dir.mkdir(parents=True, exist_ok=False)
        library.start(run_id, job.provider, job.dataset, now())
    records: list[Reference] = []
    raw_by_id: dict[str, dict] = {}
    events: list[dict] = []
    links: list[dict] = []
    web_seen = {requests[0].url} if job.provider == "web" else set()
    web_depth = {requests[0].url: 0} if job.provider == "web" else {}
    asset_seen: set[str] = set()
    status = "failed"
    error = ""
    try:
        if job.provider == "local" and job.operation == "ingest_tree":
            from .local_intake import ingest_tree

            tree_records, tree_raw, tree_events = ingest_tree(Path(job.value), root, run_dir, job.max_results)
            records.extend(tree_records)
            raw_by_id.update(tree_raw)
            events.extend(tree_events)
        elif job.provider == "local":
            source = Path(job.value).expanduser().resolve()
            if not source.is_file():
                raise ValueError("local input is not a file")
            if source.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("local input exceeds file size cap")
            if job.operation == "import_ris" and source.stat().st_size > MAX_RESPONSE_BYTES:
                raise ValueError("RIS input exceeds 25 MiB text size cap")
            data = source.read_bytes()
            if job.operation == "import_ris":
                from .ris_import import normalize_ris, parse_ris

                entries = parse_ris(data, job.max_results)
                source_sha = digest(data)
                source_copy = run_dir / "raw" / "imports" / (source_sha + ".ris")
                source_copy.parent.mkdir(parents=True, exist_ok=True)
                source_copy.write_bytes(data)
                events.append({"event": "ris_import_source", "path": str(source), "sha256": source_sha, "raw_path": str(source_copy.resolve()), "records": len(entries), "retrieved_at": now()})
                used_ids: set[str] = set()
                for index, entry in enumerate(entries):
                    entry_sha = digest(entry.raw)
                    entry_path = run_dir / "raw" / "items" / (f"{index:05d}_" + entry_sha[:16] + ".ris")
                    entry_path.parent.mkdir(parents=True, exist_ok=True)
                    entry_path.write_bytes(entry.raw)
                    rec = normalize_ris(entry, entry_sha, str(entry_path.resolve()), now(), used_ids, str(source_copy.resolve()))
                    records.append(rec)
                    raw_by_id[rec.stable_id] = entry.fields
            else:
                from .offline import derive_bytes

                mime = "application/pdf" if data.startswith(b"%PDF-") else ("text/html" if source.suffix.lower() in {".html", ".htm"} else ("application/json" if source.suffix.lower() == ".json" else "application/octet-stream"))
                raw_path, sha = _write_capture(run_dir, Response(data, "", 0, mime), "local_" + source.name, source.suffix.lower())
                text_value, method = derive_bytes(data, source.suffix)
                derived_path = run_dir / "derived" / (sha[:16] + ".md")
                derived_path.parent.mkdir(parents=True, exist_ok=True)
                derived_path.write_text(text_value, encoding="utf-8")
                kind = "dataset" if source.suffix.lower() in {".json", ".jsonl", ".csv"} else ("web_page" if source.suffix.lower() in {".html", ".htm"} else "document")
                rec = Reference("local", kind, stable_id("local", sha), source.stem, "", now(), sha, raw_path, identifiers={"sha256": sha}, extras={"original_local_path": str(source), "derived_markdown": str(derived_path.resolve()), "derivation_method": method}, attachments=[{"path": raw_path, "sha256": sha, "role": "original"}], access_status="acquired")
                records.append(rec)
                raw_by_id[rec.stable_id] = {"original_local_path": str(source), "raw_path": raw_path, "sha256": sha}
                events.append({"event": "local_ingest", "path": str(source), "sha256": sha, "raw_path": raw_path, "retrieved_at": now()})
        for index, request in enumerate(requests):
            if job.provider == "web" and hasattr(transport, "robots_allowed") and not transport.robots_allowed(request.url, allowed):
                raise ValueError("web capture blocked by robots policy or robots policy unavailable")
            screenshot = None
            rendered_pdf = None
            selected_html = b""
            selected_selector = ""
            if job.provider == "web" and job.render_js:
                if renderer is None:
                    from .rendered import PlaywrightRenderer
                    renderer = PlaywrightRenderer()
                rendered = renderer.capture(request.url, allowed, render_pdf=job.render_pdf, content_selector=job.content_selector)
                rendered_target = urlparse(rendered.url)
                if rendered_target.scheme != "https" or rendered_target.hostname not in allowed:
                    raise ValueError("rendered page returned a URL outside approved HTTPS hosts")
                if any(len(data) > MAX_RESPONSE_BYTES for data in (rendered.html, rendered.screenshot, rendered.pdf, rendered.selected_html)):
                    raise ValueError("rendered output exceeds response size cap")
                response = Response(rendered.html, rendered.url, 200, "text/html")
                screenshot = rendered.screenshot
                rendered_pdf = rendered.pdf
                selected_html = rendered.selected_html
                selected_selector = rendered.selector
            else:
                response = transport.fetch(request, allowed)
            raw_path, sha = _write_capture(run_dir, response, f"response_{index}")
            events.append({"event": "response", "purpose": request.purpose, "url": response.url, "status": response.status, "sha256": sha, "path": raw_path, "retrieved_at": now()})
            if job.provider == "web":
                kind = "web_page"
                if "html" in response.content_type:
                    parser = _Text()
                    parser.feed(response.body.decode("utf-8", errors="replace"))
                    content_parser = _Text()
                    content_parser.feed((selected_html or response.body).decode("utf-8", errors="replace"))
                    text_path = run_dir / "derived" / (sha[:16] + ".md")
                    text_path.parent.mkdir(parents=True, exist_ok=True)
                    text_path.write_text(content_parser.markdown(), encoding="utf-8")
                    title = parser.title.strip() or response.url
                    extra = {"derived_markdown": str(text_path.resolve())}
                    if selected_selector:
                        extra["content_selector"] = selected_selector
                    if job.operation == "mirror":
                        depth = web_depth.get(request.url, 0)
                        for raw_link in parser.page_links:
                            link = urldefrag(urljoin(response.url, raw_link))[0]
                            parsed_link = urlparse(link)
                            if parsed_link.scheme != "https" or parsed_link.hostname not in allowed:
                                events.append({"event": "discovered_offhost", "url": link, "from": response.url})
                                continue
                            if link in web_seen or depth >= job.max_depth or len(web_seen) >= job.max_results:
                                continue
                            web_seen.add(link)
                            web_depth[link] = depth + 1
                            requests.append(RequestPlan("GET", link, "mirrored web page", parsed_link.hostname))
                        if job.download_files:
                            for raw_link in parser.asset_links:
                                link = urldefrag(urljoin(response.url, raw_link))[0]
                                parsed_link = urlparse(link)
                                if link in asset_seen or len(asset_seen) >= job.max_results:
                                    continue
                                asset_seen.add(link)
                                if parsed_link.scheme != "https" or parsed_link.hostname not in allowed:
                                    events.append({"event": "discovered_offhost_asset", "url": link, "from": response.url})
                                    continue
                                try:
                                    file_req = RequestPlan("GET", link, "mirrored asset", parsed_link.hostname)
                                    if hasattr(transport, "download"):
                                        target = run_dir / "raw" / "assets" / (digest(link.encode()) + ".bin")
                                        file_response = transport.download(file_req, allowed, target)
                                        asset_path, asset_sha = str(target.resolve()), digest(target.read_bytes())
                                    else:
                                        file_response = transport.fetch(file_req, allowed)
                                        asset_path, asset_sha = _write_capture(run_dir, file_response, "asset_" + link)
                                    events.append({"event": "mirrored_asset", "url": link, "path": asset_path, "sha256": asset_sha, "retrieved_at": now()})
                                except Exception as exc:
                                    events.append({"event": "asset_error", "url": link, "message": str(exc)})
                elif "pdf" in response.content_type or response.body.startswith(b"%PDF-"):
                    from .offline import derive_bytes

                    kind = "document"
                    title = Path(urlparse(response.url).path).name or response.url
                    text_value, method = derive_bytes(response.body, ".pdf")
                    text_path = run_dir / "derived" / (sha[:16] + ".md")
                    text_path.parent.mkdir(parents=True, exist_ok=True)
                    text_path.write_text(text_value, encoding="utf-8")
                    extra = {"derived_markdown": str(text_path.resolve()), "derivation_method": method}
                else:
                    title, extra = response.url, {}
                ref = Reference("web", kind, stable_id("web", response.url), title, response.url, now(), sha, raw_path, identifiers={"url": response.url}, extras=extra, attachments=[{"path": raw_path, "sha256": sha, "role": "original"}], access_status="acquired", retrieval_url=response.url)
                if screenshot:
                    image_path = run_dir / "raw" / "screenshots" / (digest(screenshot) + ".png")
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    image_path.write_bytes(screenshot)
                    ref.attachments.append({"path": str(image_path.resolve()), "sha256": digest(screenshot), "role": "screenshot"})
                    events.append({"event": "screenshot", "url": response.url, "path": str(image_path.resolve()), "sha256": digest(screenshot), "retrieved_at": now()})
                if rendered_pdf:
                    pdf_path = run_dir / "raw" / "rendered_pdf" / (digest(rendered_pdf) + ".pdf")
                    pdf_path.parent.mkdir(parents=True, exist_ok=True)
                    pdf_path.write_bytes(rendered_pdf)
                    ref.attachments.append({"path": str(pdf_path.resolve()), "sha256": digest(rendered_pdf), "role": "rendered_pdf"})
                    events.append({"event": "rendered_pdf", "url": response.url, "path": str(pdf_path.resolve()), "sha256": digest(rendered_pdf), "retrieved_at": now()})
                records.append(ref)
                raw_by_id[ref.stable_id] = {"content_type": response.content_type, "raw_path": raw_path, "sha256": sha}
                continue
            payload = json.loads(response.body.decode("utf-8"))
            items = extract_records(job, payload)
            if job.provider == "openalex" and job.operation == "lookup" and "results" in payload:
                items = [item for item in items if exact_openalex_match(job.value, item)]
            for item in items:
                item_data = json_bytes(item)
                item_sha = digest(item_data)
                item_path = run_dir / "raw" / "items" / (item_sha + ".json")
                item_path.parent.mkdir(parents=True, exist_ok=True)
                item_path.write_bytes(item_data)
                kind = "decision" if job.operation in {"petition", "ptab_decisions", "ptab_appeals", "ptab_interferences"} else ("case" if job.operation == "ptab_trials" else ("dataset" if job.operation in {"bulk", "get"} else ("document" if job.operation in {"documents", "ptab_documents"} else "patent")))
                rec = normalize_openalex(item, response.url, now(), item_sha, str(item_path.resolve())) if job.provider == "openalex" else normalize_uspto(item, response.url, now(), item_sha, str(item_path.resolve()), kind)
                file_urls = _candidate_file_urls(job, item)
                if job.download_files and not file_urls:
                    library.procurement(run_id, rec.stable_id, "", "lead", "provider metadata has no downloadable file URL", now())
                for file_url in file_urls:
                    fulfillment = library.acquired_fulfillment(run_id, rec.stable_id, file_url)
                    if fulfillment:
                        rec.access_status = "acquired"
                        rec.extras.setdefault("procurement_request_ids", []).append(fulfillment["id"])
                        events.append({"event": "retained_procurement_fulfillment", "request_id": fulfillment["id"], "at": now()})
                        continue
                    host = urlparse(file_url).hostname
                    if urlparse(file_url).scheme != "https" or host not in allowed:
                        rec.diagnostics.append("file URL requires explicit allowed host: " + file_url)
                        library.procurement(run_id, rec.stable_id, file_url, "needs_host_approval", "URL is outside this job's allowed HTTPS hosts", now())
                        continue
                    try:
                        file_request = RequestPlan("GET", file_url, "source file", host, auth_env="USPTO_ODP_API_KEY" if host == "api.uspto.gov" else None)
                        if hasattr(transport, "download"):
                            target = run_dir / "raw" / "attachments" / (digest(file_url.encode()) + ".bin")
                            file_response = transport.download(file_request, allowed, target)
                            path, file_sha = str(target.resolve()), digest(target.read_bytes())
                        else:
                            file_response = transport.fetch(file_request, allowed)
                            path, file_sha = _write_capture(run_dir, file_response, "attachment_" + rec.stable_id)
                        rec.attachments.append({"path": path, "sha256": file_sha, "source_url": file_response.url, "request_url": file_url, "role": "source"})
                        rec.access_status = "acquired"
                        library.procurement(run_id, rec.stable_id, file_url, "acquired", "source file captured and SHA-256 recorded", now())
                        events.append({"event": "attachment", "stable_id": rec.stable_id, "url": file_response.url, "sha256": file_sha, "path": path, "retrieved_at": now()})
                    except Exception as exc:
                        rec.diagnostics.append("file acquisition failed: " + str(exc))
                        library.procurement(run_id, rec.stable_id, file_url, "failed", str(exc), now())
                previous = next((old for old in records if old.stable_id == rec.stable_id), None)
                if previous:
                    if previous.raw_sha256 != rec.raw_sha256:
                        previous.diagnostics.append("duplicate stable ID with different raw content in same run: " + rec.raw_sha256)
                    continue
                records.append(rec)
                raw_by_id[rec.stable_id] = item
                if job.provider == "openalex" and job.citation_depth:
                    refs = item.get("referenced_works") or []
                    for cited in refs[:job.max_results]:
                        if isinstance(cited, str):
                            links.append({"from_id": rec.stable_id, "to_id": stable_id("openalex", cited), "relation": "references", "source_url": response.url})
        if job.provider == "openalex" and job.citation_depth and records:
            root_record = records[0]
            primary = raw_by_id[root_record.stable_id]
            for index, cited in enumerate((primary.get("referenced_works") or [])[:job.max_results]):
                work_id = _openalex_work_id(cited) if isinstance(cited, str) else None
                if not work_id:
                    root_record.diagnostics.append("unrecognized referenced work ID: " + str(cited))
                    continue
                url = "https://api.openalex.org/works/" + work_id
                try:
                    response = transport.fetch(RequestPlan("GET", url, "referenced work metadata", "api.openalex.org"), allowed)
                    raw = json.loads(response.body.decode("utf-8"))
                    if not isinstance(raw, dict):
                        raise ValueError("referenced work is not a JSON object")
                    path, sha = _write_capture(run_dir, response, f"reference_{index}")
                    ref = normalize_openalex(raw, response.url, now(), sha, path)
                    if not any(old.stable_id == ref.stable_id for old in records):
                        records.append(ref)
                        raw_by_id[ref.stable_id] = raw
                    events.append({"event": "network_reference", "url": url, "sha256": sha, "path": path, "retrieved_at": now()})
                except Exception as exc:
                    root_record.diagnostics.append("referenced work fetch failed: " + str(exc))
            root_work_id = _openalex_work_id(str(primary.get("id") or ""))
            if root_work_id:
                url = "https://api.openalex.org/works?" + urlencode({"filter": "cites:" + root_work_id, "per-page": job.max_results})
                try:
                    response = transport.fetch(RequestPlan("GET", url, "citing works metadata", "api.openalex.org"), allowed)
                    path, sha = _write_capture(run_dir, response, "citing_works")
                    payload = json.loads(response.body.decode("utf-8"))
                    for raw in extract_records(Job("openalex", "search", "citations", max_results=job.max_results), payload):
                        item_sha = digest(json_bytes(raw))
                        item_path = run_dir / "raw" / "items" / (item_sha + ".json")
                        item_path.parent.mkdir(parents=True, exist_ok=True)
                        item_path.write_bytes(json_bytes(raw))
                        ref = normalize_openalex(raw, response.url, now(), item_sha, str(item_path.resolve()))
                        links.append({"from_id": ref.stable_id, "to_id": root_record.stable_id, "relation": "cites", "source_url": response.url})
                        if not any(old.stable_id == ref.stable_id for old in records):
                            records.append(ref)
                            raw_by_id[ref.stable_id] = raw
                    events.append({"event": "network_citations", "url": url, "sha256": sha, "path": path, "retrieved_at": now()})
                except Exception as exc:
                    root_record.diagnostics.append("citing works fetch failed: " + str(exc))
        export(run_dir, records, raw_by_id)
        validate_sidecars(records)
        for rec in records:
            library.record(run_id, rec)
        for link in links:
            library.relationship(run_id, **link)
        _write_jsonl(run_dir / "raw_provider.jsonl", [{"stable_id": rec.stable_id, "payload_kind": "capture_pointer" if rec.provider in {"web", "local"} else "provider_record", "raw_sha256": rec.raw_sha256, "raw_path": rec.raw_path, "payload": raw_by_id.get(rec.stable_id)} for rec in records])
        _write_jsonl(run_dir / "normalized_canonical.jsonl", [rec.asdict() for rec in records])
        _write_jsonl(run_dir / "mapping_diagnostics.jsonl", [{"stable_id": rec.stable_id, "diagnostics": rec.diagnostics} for rec in records])
        _write_jsonl(run_dir / "relationships.jsonl", links)
        status = "partial" if any(rec.diagnostics for rec in records) or any(e["event"] == "asset_error" for e in events) else "complete"
    except Exception as exc:
        error = str(exc)
        if isinstance(exc, HTTPError):
            try:
                body = exc.read(min(MAX_RESPONSE_BYTES, 1024 * 1024))
                if body:
                    path, sha = _write_capture(run_dir, Response(body, exc.url, exc.code, exc.headers.get("Content-Type", "") if exc.headers else ""), "http_error")
                    events.append({"event": "http_error_response", "url": exc.url, "status": exc.code, "sha256": sha, "path": path, "retrieved_at": now()})
            except Exception:
                pass
        events.append({"event": "error", "message": error, "at": now()})
    finally:
        _write_jsonl(run_dir / "acquisition.jsonl", events)
        artifacts = []
        for path in sorted(run_dir.rglob("*")):
            if path.is_file() and path.name != "manifest.json":
                artifacts.append({"path": str(path.relative_to(run_dir)).replace("\\", "/"), "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size})
        manifest = {"schema": "reference-suite.run.v1", "run_id": run_id, "job": job.asdict(), "planned_requests": [r.asdict() for r in requests], "status": status, "error": error, "finished_at": now(), "record_count": len(records), "relationship_count": len(links), "artifacts": artifacts}
        manifest_path = run_dir / "manifest.json"
        manifest_path.write_bytes(json_bytes(manifest))
        library.finish(run_id, status, now(), str(manifest_path.resolve()))
        if status == "complete":
            latest = root / "out" / job.provider / job.dataset / "latest.txt"
            temporary = latest.with_name("latest.tmp")
            temporary.write_text(run_id + "\n", encoding="utf-8")
            temporary.replace(latest)
        library.close()
    return {"status": status, "run_dir": str(run_dir.resolve()), "run_id": run_id, "records": len(records), "error": error}
