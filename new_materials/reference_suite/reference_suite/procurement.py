"""Manual source-file fulfillment with a separate immutable local capture run."""
from __future__ import annotations

import json
from pathlib import Path

from .engine import execute
from .model import Job, now
from .storage import Library


def fulfill_request(root: Path, request_id: int, source_file: Path, reviewer_note: str) -> dict:
    source_file = source_file.expanduser().resolve()
    if not source_file.is_file():
        raise ValueError("fulfillment source must be an existing local file")
    if not reviewer_note.strip() or len(reviewer_note) > 1000:
        raise ValueError("fulfillment requires a reviewer note of at most 1000 characters")
    library = Library(root)
    try:
        request = library.get_procurement(request_id)
        if request["status"] == "acquired":
            raise ValueError("procurement request is already acquired")
    finally:
        library.close()
    result = execute(Job("local", "ingest", str(source_file), dataset="procurement"), root)
    if result["status"] != "complete":
        return {"status": "failed", "request_id": request_id, "evidence_run": result}
    records_path = Path(result["run_dir"]) / "normalized_canonical.jsonl"
    evidence = json.loads(records_path.read_text(encoding="utf-8").splitlines()[0])
    library = Library(root)
    try:
        request = library.fulfill_procurement(request_id, result["run_id"], evidence["stable_id"], now(), reviewer_note)
    finally:
        library.close()
    return {"status": "acquired", "request": request, "evidence_run": result}
