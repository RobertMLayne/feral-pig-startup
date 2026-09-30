from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from urllib.parse import urlparse


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_id(provider: str, value: str) -> str:
    return provider + ":" + re.sub(r"\s+", "", value).lower()


@dataclass(frozen=True)
class Job:
    provider: str
    operation: str
    value: str
    dataset: str = "references"
    max_results: int = 25
    citation_depth: int = 0
    download_files: bool = False
    allow_hosts: tuple[str, ...] = ()
    max_depth: int = 1
    schema_version: int = 1
    render_js: bool = False
    render_pdf: bool = False
    content_selector: str = ""

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("unsupported job schema version")
        if self.provider not in {"openalex", "uspto", "web", "local"}:
            raise ValueError("provider must be openalex, uspto, web, or local")
        if not self.value.strip() or len(self.value) > 4096:
            raise ValueError("value must be nonempty and at most 4096 characters")
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", self.dataset):
            raise ValueError("dataset must be a short safe name")
        result_limit = 10000 if self.provider == "local" else 100
        if not 1 <= self.max_results <= result_limit:
            raise ValueError(f"max_results must be 1..{result_limit}")
        if not 0 <= self.citation_depth <= 1:
            raise ValueError("citation_depth must be 0 or 1")
        if self.citation_depth and (self.provider != "openalex" or self.operation != "lookup"):
            raise ValueError("citation expansion is supported for OpenAlex lookup jobs only")
        if self.provider == "web" and not self.allow_hosts:
            raise ValueError("web acquisitions require explicit allow_hosts")
        if self.provider == "web" and self.operation not in {"capture", "mirror"}:
            raise ValueError("web operation must be capture or mirror")
        if self.render_js and (self.provider != "web" or self.operation != "capture"):
            raise ValueError("JavaScript rendering is available for single web captures only")
        if self.render_pdf and not self.render_js:
            raise ValueError("rendered PDF requires JavaScript rendering")
        if self.content_selector and not self.render_js:
            raise ValueError("content selector requires JavaScript rendering")
        if len(self.content_selector) > 256 or any(ord(char) < 32 for char in self.content_selector):
            raise ValueError("content selector must be at most 256 printable characters")
        if not 0 <= self.max_depth <= 3:
            raise ValueError("max_depth must be 0..3")
        if self.provider == "openalex" and self.operation not in {"lookup", "search"}:
            raise ValueError("openalex operation must be lookup or search")
        if self.provider == "local" and self.operation not in {"ingest", "ingest_tree", "import_ris"}:
            raise ValueError("local operation must be ingest, ingest_tree, or import_ris")
        if self.provider == "local" and (self.download_files or self.citation_depth):
            raise ValueError("local ingest cannot download files or expand citations")
        if self.provider == "uspto" and self.operation not in {"application", "documents", "search", "petition", "bulk", "ptab_trials", "ptab_documents", "ptab_decisions", "ptab_appeals", "ptab_interferences", "get"}:
            raise ValueError("unsupported uspto operation")
        for host in self.allow_hosts:
            if not re.fullmatch(r"[a-zA-Z0-9.-]+", host):
                raise ValueError("allow_hosts must contain hostnames, not URLs")

    def asdict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RequestPlan:
    method: str
    url: str
    purpose: str
    allowed_host: str
    body: dict | None = None
    auth_env: str | None = None

    def __post_init__(self) -> None:
        if self.method not in {"GET", "POST"}:
            raise ValueError("unsupported HTTP method")
        parsed = urlparse(self.url)
        if parsed.scheme != "https" or parsed.hostname != self.allowed_host:
            raise ValueError("request must use HTTPS and the approved exact host")

    def asdict(self) -> dict:
        return asdict(self)


@dataclass
class Reference:
    provider: str
    kind: str
    stable_id: str
    title: str
    source_url: str
    retrieved_at: str
    raw_sha256: str
    raw_path: str
    creators: list[str] = field(default_factory=list)
    identifiers: dict[str, str] = field(default_factory=dict)
    dates: dict[str, str] = field(default_factory=dict)
    abstract: str = ""
    extras: dict = field(default_factory=dict)
    source_paths: dict = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)
    access_status: str = "metadata_only"
    schema_version: int = 1
    retrieval_url: str = ""
    rights: dict = field(default_factory=dict)
    citation: dict[str, str] = field(default_factory=dict)

    def asdict(self) -> dict:
        return asdict(self)


def json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
