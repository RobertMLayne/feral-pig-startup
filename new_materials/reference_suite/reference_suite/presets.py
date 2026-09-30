"""Local, revisioned acquisition configurations; validation never acquires data.

SHA-256 and the revision chain detect inconsistent stored data, not authorship.
Jobs are checked again through the current offline provider planner when loaded.
"""
from __future__ import annotations

from dataclasses import fields
import json
from pathlib import Path
import re
import sqlite3

from .model import Job, digest, json_bytes, now
from .providers import plan


SCHEMA = "reference-suite.preset.v1"
MAX_REVISION_BYTES = 64 * 1024
_TEXT_FIELDS = {"provider", "operation", "value", "dataset", "content_selector"}
_INTEGER_FIELDS = {"max_results", "citation_depth", "max_depth", "schema_version"}
_BOOLEAN_FIELDS = {"download_files", "render_js", "render_pdf"}
_RECORD_FIELDS = {"schema", "name", "revision", "created_at", "description", "reason",
                  "provenance", "job", "job_sha256"}


def job_from_dict(data: dict) -> Job:
    """Validate JSON primitives, Job constraints, and the offline request scope."""
    if not isinstance(data, dict) or set(data) - {field.name for field in fields(Job)}:
        raise ValueError("job must be an object containing only supported Job fields")
    for key, value in data.items():
        if key in _TEXT_FIELDS and not isinstance(value, str):
            raise ValueError(key + " must be text")
        if key in _INTEGER_FIELDS and type(value) is not int:
            raise ValueError(key + " must be an integer")
        if key in _BOOLEAN_FIELDS and type(value) is not bool:
            raise ValueError(key + " must be a boolean")
    hosts = data.get("allow_hosts", ())
    if not isinstance(hosts, (list, tuple)) or any(not isinstance(host, str) for host in hosts):
        raise ValueError("allow_hosts must be an array of hostnames")
    try:
        job = Job(**{**data, "allow_hosts": tuple(hosts)})
        plan(job)
        if len(json_bytes(job.asdict())) > MAX_REVISION_BYTES // 2:
            raise ValueError("job exceeds the preset size limit")
        return job
    except (TypeError, AttributeError) as error:
        raise ValueError("invalid or missing job fields") from error


def _name(name: str) -> str:
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", name):
        raise ValueError("preset name must be 1..64 lowercase letters, digits, underscores, or hyphens")
    return name


def _text(value: str, label: str, limit: int, required=False) -> str:
    if not isinstance(value, str) or len(value) > limit or (required and not value.strip()):
        raise ValueError(f"{label} must be {'nonempty ' if required else ''}text of at most {limit} characters")
    return value.strip()


def _connect(root: Path, *, create=False) -> sqlite3.Connection | None:
    root = Path(root).resolve()
    if create:
        root.mkdir(parents=True, exist_ok=True)
    path = root / "presets.sqlite3"
    # SQLite can create journal files beside its database; all stay under this root.
    for candidate in (path, *(path.with_name(path.name + suffix) for suffix in ("-journal", "-wal", "-shm"))):
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            raise ValueError("preset storage cannot use symbolic links or junctions")
        if not candidate.resolve().is_relative_to(root):
            raise ValueError("preset storage escaped the selected data root")
    if not create and not path.exists():
        return None
    connection = sqlite3.connect(path if create else path.as_uri() + "?mode=ro", uri=not create, timeout=10)
    if create:
        connection.execute("""CREATE TABLE IF NOT EXISTS preset_revisions (
            name TEXT NOT NULL, revision INTEGER NOT NULL,
            record_json TEXT NOT NULL, revision_sha256 TEXT NOT NULL,
            PRIMARY KEY(name, revision)
        )""")
    return connection


def _history(connection: sqlite3.Connection, name: str) -> list[dict]:
    history = []
    rows = connection.execute("SELECT revision, record_json, revision_sha256 FROM preset_revisions WHERE name=? ORDER BY revision", (name,))
    for expected_revision, (revision, raw, sha256) in enumerate(rows, 1):
        if revision != expected_revision or not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_REVISION_BYTES:
            raise ValueError("preset revision history is incomplete or invalid")
        try:
            record = json.loads(raw)
            if (not isinstance(record, dict) or set(record) != _RECORD_FIELDS
                    or record["schema"] != SCHEMA or record["name"] != name
                    or type(record["revision"]) is not int or record["revision"] != revision
                    or digest(json_bytes(record)) != sha256):
                raise ValueError("preset revision integrity check failed")
            job = job_from_dict(record["job"])
            if digest(json_bytes(job.asdict())) != record["job_sha256"]:
                raise ValueError("stored preset job hash does not match")
            previous = history[-1] if history else None
            provenance = record["provenance"]
            if (not isinstance(provenance, dict)
                    or set(provenance) != {"source", "reviewer", "previous_revision", "previous_sha256"}
                    or provenance["previous_revision"] != (previous["revision"] if previous else None)
                    or provenance["previous_sha256"] != (previous["revision_sha256"] if previous else None)):
                raise ValueError("preset revision chain does not match")
            _text(record["created_at"], "created_at", 100, True)
            _text(record["description"], "description", 4000)
            _text(record["reason"], "reason", 1000, True)
            _text(provenance["source"], "source", 2048, True)
            _text(provenance["reviewer"], "reviewer", 200)
        except (KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
            raise ValueError("stored preset revision is malformed") from error
        history.append({**record, "revision_sha256": sha256})
    return history


def save_preset(root: Path, name: str, job: Job | dict, *, reason: str,
                description="", source="local preset save", reviewer="") -> dict:
    """Append one immutable revision, retaining and verifying earlier revisions."""
    name = _name(name)
    job = job_from_dict(job.asdict() if isinstance(job, Job) else job)
    reason = _text(reason, "reason", 1000, True)
    description = _text(description, "description", 4000)
    source = _text(source, "source", 2048, True)
    reviewer = _text(reviewer, "reviewer", 200)
    connection = _connect(root, create=True)
    try:
        # Serialize numbering and commit the entire new revision atomically.
        with connection:
            connection.execute("BEGIN IMMEDIATE")
            history = _history(connection, name)
            previous = history[-1] if history else None
            record = {"schema": SCHEMA, "name": name, "revision": len(history) + 1,
                      "created_at": now(), "description": description, "reason": reason,
                      "provenance": {"source": source, "reviewer": reviewer,
                                     "previous_revision": previous["revision"] if previous else None,
                                     "previous_sha256": previous["revision_sha256"] if previous else None},
                      "job": json.loads(json_bytes(job.asdict())), "job_sha256": digest(json_bytes(job.asdict()))}
            payload = json_bytes(record)
            if len(payload) > MAX_REVISION_BYTES:
                raise ValueError("preset revision exceeds 64 KiB")
            sha256 = digest(payload)
            connection.execute("INSERT INTO preset_revisions VALUES (?,?,?,?)",
                               (name, record["revision"], payload.decode("utf-8"), sha256))
        return {**record, "revision_sha256": sha256}
    finally:
        connection.close()


def list_revisions(root: Path, name: str) -> list[dict]:
    """Return validated revisions in creation order; a missing name yields []."""
    name = _name(name)
    connection = _connect(root)
    if connection is None:
        return []
    try:
        return _history(connection, name)
    finally:
        connection.close()


def load_preset(root: Path, name: str, revision: int | None = None) -> dict:
    """Load a validated revision envelope; omitted revision selects the latest."""
    if revision is not None and (type(revision) is not int or revision < 1):
        raise ValueError("preset revision must be a positive integer")
    history = list_revisions(root, name)
    if not history or revision is not None and revision > len(history):
        raise ValueError("preset or requested revision was not found")
    return history[-1] if revision is None else history[revision - 1]


def preset_job(root: Path, name: str, revision: int | None = None) -> Job:
    """Return the validated Job for explicit preview or execution by the caller."""
    return job_from_dict(load_preset(root, name, revision)["job"])


def list_presets(root: Path) -> list[dict]:
    """List latest revision summaries, verifying each complete revision history."""
    connection = _connect(root)
    if connection is None:
        return []
    try:
        summaries = []
        for (name,) in connection.execute("SELECT DISTINCT name FROM preset_revisions ORDER BY name").fetchall():
            latest = _history(connection, _name(name))[-1]
            summaries.append({key: latest[key] for key in ("name", "revision", "created_at", "description", "reason", "job_sha256", "revision_sha256")} |
                             {key: latest["job"][key] for key in ("provider", "operation", "dataset")})
        return summaries
    finally:
        connection.close()
