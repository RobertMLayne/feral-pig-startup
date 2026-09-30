"""Offline URL intake, artifact regeneration, and export validation."""
from __future__ import annotations

import csv
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import uuid

from .engine import _Text
from .model import digest, json_bytes, now


URL_PATTERN = re.compile(r"https?://[^\s<>\"'`]+", re.I)
TEXT_SUFFIXES = {".txt", ".md", ".html", ".htm", ".json", ".jsonl", ".xml", ".csv", ".yaml", ".yml", ".ris", ".bib"}
MAX_LOCAL_TEXT_BYTES = 25 * 1024 * 1024


def extract_urls(paths: list[Path]) -> list[str]:
    """Extract and deduplicate URLs from explicitly selected local text files."""
    found: set[str] = set()
    for source in paths:
        files = sorted(p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES) if source.is_dir() else [source]
        for path in files:
            if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > MAX_LOCAL_TEXT_BYTES:
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            for match in URL_PATTERN.finditer(content):
                candidate = match.group(0).rstrip(".,;:!?)]}")
                parsed = urlparse(candidate)
                if parsed.scheme in {"http", "https"} and parsed.hostname:
                    found.add(candidate)
    return sorted(found)


def _pdf_text(data: bytes, *, ocr: bool, max_pages: int) -> tuple[str, str]:
    if ocr:
        try:
            import fitz  # type: ignore
            from PIL import Image  # type: ignore
            import pytesseract  # type: ignore
        except ImportError as exc:
            raise RuntimeError("OCR requires PyMuPDF, Pillow, pytesseract, and the Tesseract executable") from exc
        document = fitz.open(stream=data, filetype="pdf")
        pages = []
        for index in range(min(len(document), max_pages)):
            pixmap = document[index].get_pixmap(dpi=150)
            picture = Image.open(BytesIO(pixmap.tobytes("png")))
            pages.append(f"## Page {index + 1}\n\n" + pytesseract.image_to_string(picture).strip())
        return "\n\n".join(pages).strip() + "\n", "ocr:tesseract"
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return "PDF captured. Text extraction requires the optional pypdf package.\n", "pdf:unavailable"
    reader = PdfReader(BytesIO(data))
    pages = []
    for index, page in enumerate(reader.pages[:max_pages]):
        pages.append(f"## Page {index + 1}\n\n" + (page.extract_text() or "").strip())
    return "\n\n".join(pages).strip() + "\n", "pdf:pypdf"


def derive_bytes(data: bytes, suffix: str, *, ocr: bool = False, max_pdf_pages: int = 25) -> tuple[str, str]:
    suffix = suffix.lower()
    if data.startswith(b"%PDF-") or suffix == ".pdf":
        return _pdf_text(data, ocr=ocr, max_pages=max_pdf_pages)
    if suffix in {".html", ".htm"} or b"<html" in data[:2048].lower():
        parser = _Text()
        parser.feed(data.decode("utf-8", errors="replace"))
        return parser.markdown(), "html:static"
    if suffix in {".json", ".jsonl"}:
        try:
            value = json.loads(data.decode("utf-8"))
            return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```\n", "json:pretty"
        except json.JSONDecodeError:
            return "```jsonl\n" + data.decode("utf-8", errors="replace") + "\n```\n", "jsonl:raw"
    if suffix == ".xml":
        try:
            root = ET.fromstring(data)
            ET.indent(root)
            return "```xml\n" + ET.tostring(root, encoding="unicode") + "\n```\n", "xml:pretty"
        except ET.ParseError:
            return data.decode("utf-8", errors="replace"), "xml:unparsed"
    if suffix in {".csv", ".txt", ".md", ".yaml", ".yml", ".ris", ".bib"}:
        return data.decode("utf-8", errors="replace"), "text:decoded"
    return "Binary capture retained; no text derivation is available for this type.\n", "binary:unavailable"


def _load_manifest(run_dir: Path) -> dict:
    path = run_dir / "manifest.json"
    if not path.is_file():
        raise ValueError("run directory has no manifest.json")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "reference-suite.run.v1":
        raise ValueError("unsupported run manifest schema")
    return manifest


def _verify_raw_artifacts(run_dir: Path, manifest: dict) -> None:
    for artifact in manifest["artifacts"]:
        relative = Path(artifact["path"])
        if not relative.parts or relative.parts[0] != "raw":
            continue
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("raw artifact has an unsafe path")
        path = run_dir / relative
        if not path.is_file() or path.stat().st_size != artifact["bytes"] or digest(path.read_bytes()) != artifact["sha256"]:
            raise ValueError("raw artifact is missing or changed: " + artifact["path"])


def normalize_export(run_dir: Path, *, ocr: bool = False, max_pdf_pages: int = 25, split_chars: int = 0) -> dict:
    if not 1 <= max_pdf_pages <= 100:
        raise ValueError("max_pdf_pages must be 1..100")
    if split_chars and not 1000 <= split_chars <= 1000000:
        raise ValueError("split_chars must be 0 or 1000..1000000")
    manifest = _load_manifest(run_dir)
    _verify_raw_artifacts(run_dir, manifest)
    derived = []
    chunk_count = 0
    for source in sorted((run_dir / "raw").rglob("*")):
        if not source.is_file() or source.suffix == ".part":
            continue
        raw_bytes = source.read_bytes()
        text, method = derive_bytes(raw_bytes, source.suffix, ocr=ocr, max_pdf_pages=max_pdf_pages)
        stem = digest(str(source.relative_to(run_dir)).encode())[:12]
        output = run_dir / "derived" / (stem + ".md")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        sidecar = output.with_suffix(".meta.json")
        sidecar.write_bytes(json_bytes({"source": str(source.relative_to(run_dir)).replace("\\", "/"), "source_sha256": digest(raw_bytes), "method": method, "generated_at": now()}))
        derived += [output, sidecar]
        if split_chars and len(text) > split_chars:
            chunk_folder = run_dir / "derived" / "splits" / (stem + "_" + str(split_chars) + "_" + digest(text.encode("utf-8"))[:12])
            chunk_folder.mkdir(parents=True, exist_ok=True)
            chunks = []
            for index, start in enumerate(range(0, len(text), split_chars), 1):
                end = min(start + split_chars, len(text))
                chunk_path = chunk_folder / f"part_{index:05d}.txt"
                chunk_path.write_text(text[start:end], encoding="utf-8")
                chunks.append({"path": chunk_path.relative_to(run_dir).as_posix(), "start": start, "end": end, "sha256": digest(chunk_path.read_bytes())})
                derived.append(chunk_path)
                chunk_count += 1
            index_path = chunk_folder / "index.json"
            index_path.write_bytes(json_bytes({"source": source.relative_to(run_dir).as_posix(), "full_derived": output.relative_to(run_dir).as_posix(), "split_chars": split_chars, "chunks": chunks}))
            derived.append(index_path)
    indexed = {entry["path"]: entry for entry in manifest["artifacts"]}
    for path in derived:
        relative = str(path.relative_to(run_dir)).replace("\\", "/")
        indexed[relative] = {"path": relative, "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size}
    manifest["artifacts"] = [indexed[key] for key in sorted(indexed)]
    temp = run_dir / "manifest.tmp"
    temp.write_bytes(json_bytes(manifest))
    temp.replace(run_dir / "manifest.json")
    return {"derived_files": len(derived), "chunks": chunk_count, "run_dir": str(run_dir.resolve())}


def inspect_export(run_dir: Path) -> dict:
    manifest = _load_manifest(run_dir)
    missing: list[str] = []
    changed: list[str] = []
    missing_references: list[str] = []
    for artifact in manifest["artifacts"]:
        relative = Path(artifact["path"])
        if relative.is_absolute() or ".." in relative.parts:
            changed.append(artifact["path"])
            continue
        path = run_dir / relative
        if not path.is_file():
            missing.append(artifact["path"])
        elif digest(path.read_bytes()) != artifact["sha256"] or path.stat().st_size != artifact["bytes"]:
            changed.append(artifact["path"])
    records_path = run_dir / "normalized_canonical.jsonl"
    if records_path.is_file():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            references = [record.get("raw_path"), (record.get("extras") or {}).get("derived_markdown")]
            references.extend(item.get("path") for item in record.get("attachments") or [] if isinstance(item, dict))
            for reference in references:
                if reference and not Path(reference).is_file():
                    missing_references.append(str(reference))
    return {"run_id": manifest["run_id"], "status": manifest["status"], "expected_artifacts": len(manifest["artifacts"]), "missing": missing, "changed": changed, "missing_references": sorted(set(missing_references)), "valid": not missing and not changed and not missing_references}


def write_web_reports(run_dir: Path) -> dict:
    manifest = _load_manifest(run_dir)
    _verify_raw_artifacts(run_dir, manifest)
    if manifest["job"]["provider"] != "web":
        raise ValueError("web reports require a web run")
    records_path = run_dir / "normalized_canonical.jsonl"
    rows = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    urls = sorted({row["source_url"] for row in rows if row.get("source_url")})
    reports = run_dir / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "urls.txt").write_text("\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")
    (reports / "urls.json").write_bytes(json_bytes(urls))
    xml = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        ET.SubElement(ET.SubElement(xml, "url"), "loc").text = url
    ET.ElementTree(xml).write(reports / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    with (reports / "crawl_details.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["stable_id", "title", "source_url", "retrieved_at", "raw_sha256", "raw_path"])
        for row in rows:
            writer.writerow([row.get(field, "") for field in ("stable_id", "title", "source_url", "retrieved_at", "raw_sha256", "raw_path")])
    indexed = {entry["path"]: entry for entry in manifest["artifacts"]}
    for path in reports.iterdir():
        relative = str(path.relative_to(run_dir)).replace("\\", "/")
        indexed[relative] = {"path": relative, "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size}
    manifest["artifacts"] = [indexed[key] for key in sorted(indexed)]
    temporary = run_dir / "manifest.tmp"
    temporary.write_bytes(json_bytes(manifest))
    temporary.replace(run_dir / "manifest.json")
    return {"urls": len(urls), "report_dir": str(reports.resolve())}


def batch_urls(source: Path, root: Path, allow_hosts: tuple[str, ...], *, max_urls: int = 100, execute_jobs: bool = False, dataset: str = "references", transport_factory=None) -> dict:
    """Prevalidate every URL before any batch network action, then group child runs."""
    from .engine import execute
    from .model import Job
    from .providers import plan

    if not 1 <= max_urls <= 1000:
        raise ValueError("max_urls must be 1..1000")
    urls = extract_urls([source])
    if len(urls) > max_urls:
        raise ValueError(f"URL batch contains {len(urls)} items, above the {max_urls} limit")
    jobs = [Job("web", "capture", url, dataset=dataset, allow_hosts=allow_hosts) for url in urls]
    plans = [{"job": job.asdict(), "requests": [request.asdict() for request in plan(job)]} for job in jobs]
    if not execute_jobs:
        return {"count": len(plans), "plans": plans, "network_access": False}
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    folder = root / "out" / "batches" / batch_id
    folder.mkdir(parents=True, exist_ok=False)
    results = []
    for job in jobs:
        transport = transport_factory() if transport_factory else None
        results.append(execute(job, root, transport))
    report = {"schema": "reference-suite.batch.v1", "batch_id": batch_id, "source": str(source.resolve()), "created_at": now(), "status": "complete" if all(x["status"] == "complete" for x in results) else "partial", "results": results}
    (folder / "manifest.json").write_bytes(json_bytes(report))
    return {"batch_dir": str(folder.resolve()), "count": len(results), "status": report["status"]}
