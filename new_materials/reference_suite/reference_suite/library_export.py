"""Combined local citation export from the latest successful record versions."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import uuid
from datetime import datetime, timezone

from .citation import bibtex, ris
from .model import Reference, digest, json_bytes, now
from .offline import inspect_export
from .storage import Library


MAX_BUNDLE_BYTES = 2 * 1024 * 1024 * 1024


def _hash_file(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def export_library(root: Path, *, provider: str | None = None, dataset: str | None = None, include_attachments: bool = False) -> dict:
    library = Library(root)
    try:
        selected = library.latest_records(provider, dataset)
        for item in selected:
            item["fulfillments"] = library.linked_fulfillments(item["record"]["stable_id"])
    finally:
        library.close()
    if not selected:
        raise ValueError("no complete records match the library export filter")
    checked_runs: dict[str, str] = {}
    source_run_dirs: dict[str, Path] = {}

    def verify_run(run_id: str, manifest_value: str) -> None:
        if run_id in checked_runs:
            return
        manifest_path = Path(manifest_value)
        if not manifest_path.is_file() or not inspect_export(manifest_path.parent)["valid"]:
            raise ValueError("source run integrity check failed: " + run_id)
        checked_runs[run_id] = _hash_file(manifest_path)
        source_run_dirs[run_id] = manifest_path.resolve().parent

    for item in selected:
        verify_run(item["run_id"], item["manifest_path"])
        for evidence in item["fulfillments"]:
            verify_run(evidence["source_run_id"], evidence["manifest_path"])
    export_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8]
    folder = root / "out" / "library_exports" / export_id
    folder.mkdir(parents=True, exist_ok=False)
    copied: dict[str, str] = {}
    copied_bytes = 0

    def copy_verified(source_value: str, expected_sha: str, source_run_dir: Path) -> str:
        nonlocal copied_bytes
        source = Path(source_value).resolve()
        if not source.is_relative_to(source_run_dir):
            raise ValueError("source attachment is outside its verified run: " + source_value)
        if not source.is_file() or _hash_file(source) != expected_sha:
            raise ValueError("source attachment is missing or changed: " + source_value)
        if str(source) in copied:
            return copied[str(source)]
        copied_bytes += source.stat().st_size
        if copied_bytes > MAX_BUNDLE_BYTES:
            raise ValueError("attachment bundle exceeds 2 GiB limit")
        target = folder / "attachments" / (expected_sha + source.suffix.lower())
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(source, target)
        if _hash_file(target) != expected_sha:
            raise ValueError("copied attachment hash mismatch")
        copied[str(source)] = str(target.resolve())
        return copied[str(source)]

    records: list[Reference] = []
    provenance: list[dict] = []
    for item in selected:
        rec = Reference(**item["record"])
        source_run_dir = source_run_dirs[item["run_id"]]
        fulfillments = item["fulfillments"]
        if fulfillments:
            rec.attachments.extend(fulfillments)
            rec.access_status = "acquired"
        provenance.append({"stable_id": rec.stable_id, "source_run_id": item["run_id"], "source_manifest_sha256": checked_runs[item["run_id"]], "source_raw_path": rec.raw_path, "source_raw_sha256": rec.raw_sha256,
                           "procurement_evidence": [dict(evidence, source_manifest_sha256=checked_runs[evidence["source_run_id"]]) for evidence in fulfillments],
                           "metadata_review": rec.extras.get("reviewed_metadata", {}),
                           "correction_history": item["correction_history"]})
        if include_attachments:
            rec.raw_path = copy_verified(rec.raw_path, rec.raw_sha256, source_run_dir)
            for attachment in rec.attachments:
                if attachment.get("path"):
                    if not attachment.get("sha256"):
                        raise ValueError("source attachment has no SHA-256")
                    previous = attachment["path"]
                    attachment_run = source_run_dirs[attachment["source_run_id"]] if attachment.get("role") == "procurement_source" else source_run_dir
                    attachment["path"] = copy_verified(previous, attachment["sha256"], attachment_run)
                    attachment["source_path"] = previous
            derived = rec.extras.get("derived_markdown")
            if derived:
                derived_path = Path(derived).resolve()
                if not derived_path.is_relative_to(source_run_dir):
                    raise ValueError("derived text is outside its verified run")
                rec.extras["derived_markdown"] = copy_verified(str(derived_path), _hash_file(derived_path), source_run_dir)
        if item["correction_history"]:
            review_path = folder / "reviews" / (digest(rec.stable_id.encode("utf-8")) + ".json")
            review_path.parent.mkdir(parents=True, exist_ok=True)
            review_payload = json_bytes({"schema": "reference-suite.metadata-review.v1", "stable_id": rec.stable_id,
                                         "source_run_id": item["run_id"], "source_raw_sha256": rec.raw_sha256,
                                         "effective_record": rec.asdict(), "events": item["correction_history"]})
            review_path.write_bytes(review_payload)
            rec.attachments.append({"path": str(review_path.resolve()), "sha256": digest(review_payload), "role": "metadata_review"})
        records.append(rec)
    (folder / "references.ris").write_text(ris(records), encoding="utf-8")
    (folder / "references.bib").write_text(bibtex(records), encoding="utf-8")
    (folder / "records.jsonl").write_text("".join(json.dumps(rec.asdict(), ensure_ascii=False, sort_keys=True) + "\n" for rec in records), encoding="utf-8")
    (folder / "provenance.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in provenance), encoding="utf-8")
    artifacts = []
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            artifacts.append({"path": path.relative_to(folder).as_posix(), "sha256": _hash_file(path), "bytes": path.stat().st_size})
    manifest = {"schema": "reference-suite.library-export.v1", "export_id": export_id, "created_at": now(), "provider": provider, "dataset": dataset, "record_count": len(records), "source_run_count": len(checked_runs), "include_attachments": include_attachments, "artifacts": artifacts}
    (folder / "manifest.json").write_bytes(json_bytes(manifest))
    return {"export_dir": str(folder.resolve()), "records": len(records), "source_runs": len(checked_runs), "attachments_copied": len(copied), "manifest": str((folder / "manifest.json").resolve())}
