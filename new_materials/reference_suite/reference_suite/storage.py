from __future__ import annotations

import json
import hashlib
from pathlib import Path
import sqlite3

from .model import Reference, now


def _file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _verify_captured_file(path: Path, sha256: str, manifest_path: Path, run_id: str) -> dict:
    """Check the retained bytes against the named acquisition manifest."""
    exists = path.is_file()
    hash_matches = exists and _file_sha256(path) == sha256
    manifest_matches = False
    try:
        relative = path.resolve().relative_to(manifest_path.resolve().parent).as_posix()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_matches = (
            manifest.get("schema") == "reference-suite.run.v1"
            and manifest.get("run_id") == run_id
            and any(item.get("path") == relative and item.get("sha256") == sha256
                    and exists and item.get("bytes") == path.stat().st_size
                    for item in manifest.get("artifacts", []))
        )
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return {"file_exists": exists, "sha256_matches": hash_matches, "manifest_matches": manifest_matches,
            "valid": hash_matches and manifest_matches}


class Library:
    def __init__(self, root: Path):
        root.mkdir(parents=True, exist_ok=True)
        self.path = root / "library.sqlite3"
        self.db = sqlite3.connect(self.path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, provider TEXT NOT NULL, dataset TEXT NOT NULL,
                status TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT, manifest_path TEXT
            );
            CREATE TABLE IF NOT EXISTS records (
                run_id TEXT NOT NULL REFERENCES runs(id), stable_id TEXT NOT NULL,
                provider TEXT NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL,
                raw_sha256 TEXT NOT NULL, data_json TEXT NOT NULL,
                PRIMARY KEY (run_id, stable_id)
            );
            CREATE INDEX IF NOT EXISTS ix_records_stable_id ON records(stable_id);
            CREATE INDEX IF NOT EXISTS ix_records_title ON records(title);
            CREATE TABLE IF NOT EXISTS relationships (
                run_id TEXT NOT NULL REFERENCES runs(id), from_id TEXT NOT NULL,
                to_id TEXT NOT NULL, relation TEXT NOT NULL, source_url TEXT NOT NULL,
                PRIMARY KEY (run_id, from_id, to_id, relation)
            );
            CREATE TABLE IF NOT EXISTS procurement_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL REFERENCES runs(id), stable_id TEXT NOT NULL,
                source_url TEXT NOT NULL, status TEXT NOT NULL, reason TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE (run_id, stable_id, source_url)
            );
            CREATE TABLE IF NOT EXISTS procurement_evidence (
                request_id INTEGER PRIMARY KEY REFERENCES procurement_requests(id) ON DELETE CASCADE,
                evidence_run_id TEXT NOT NULL REFERENCES runs(id),
                evidence_stable_id TEXT NOT NULL,
                evidence_path TEXT NOT NULL,
                evidence_sha256 TEXT NOT NULL,
                linked_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS procurement_evidence_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL REFERENCES procurement_requests(id),
                evidence_run_id TEXT NOT NULL REFERENCES runs(id),
                evidence_stable_id TEXT NOT NULL, evidence_path TEXT NOT NULL,
                evidence_sha256 TEXT NOT NULL, linked_at TEXT NOT NULL,
                reviewer_reason TEXT NOT NULL, superseded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS metadata_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT, stable_id TEXT NOT NULL,
                action TEXT NOT NULL CHECK(action IN ('correct', 'revert')),
                patch_json TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL,
                base_run_id TEXT NOT NULL REFERENCES runs(id), base_raw_sha256 TEXT NOT NULL,
                previous_values_json TEXT NOT NULL,
                reverts_id INTEGER UNIQUE REFERENCES metadata_corrections(id)
            );
            CREATE INDEX IF NOT EXISTS ix_metadata_corrections_stable_id ON metadata_corrections(stable_id);
            CREATE TRIGGER IF NOT EXISTS metadata_corrections_no_update
                BEFORE UPDATE ON metadata_corrections BEGIN
                SELECT RAISE(ABORT, 'metadata correction history is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS metadata_corrections_no_delete
                BEFORE DELETE ON metadata_corrections BEGIN
                SELECT RAISE(ABORT, 'metadata correction history is append-only'); END;
        """)
        self.db.commit()

    def start(self, run_id: str, provider: str, dataset: str, started_at: str) -> None:
        self.db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?)", (run_id, provider, dataset, "running", started_at, None, None))
        self.db.commit()

    def resume(self, run_id: str) -> None:
        row = self.db.execute("SELECT status FROM runs WHERE id=?", (run_id,)).fetchone()
        if not row or row[0] == "complete":
            raise ValueError("run is absent or already complete")
        self.db.execute("UPDATE runs SET status='running', finished_at=NULL WHERE id=?", (run_id,))
        self.db.execute("DELETE FROM relationships WHERE run_id=?", (run_id,))
        self.db.execute("DELETE FROM records WHERE run_id=?", (run_id,))
        # Keep request IDs and reviewer evidence stable across an interrupted run.
        self.db.commit()

    def record(self, run_id: str, ref: Reference) -> None:
        self.db.execute("INSERT OR REPLACE INTO records VALUES (?,?,?,?,?,?,?)", (run_id, ref.stable_id, ref.provider, ref.kind, ref.title, ref.raw_sha256, json.dumps(ref.asdict(), ensure_ascii=False)))
        self.db.commit()

    def relationship(self, run_id: str, from_id: str, to_id: str, relation: str, source_url: str) -> None:
        self.db.execute("INSERT OR IGNORE INTO relationships VALUES (?,?,?,?,?)", (run_id, from_id, to_id, relation, source_url))
        self.db.commit()

    def procurement(self, run_id: str, stable_id: str, source_url: str, status: str, reason: str, updated_at: str) -> None:
        if status not in {"lead", "needs_host_approval", "acquired", "failed", "reviewed"}:
            raise ValueError("invalid procurement status")
        self.db.execute("""INSERT INTO procurement_requests (run_id, stable_id, source_url, status, reason, updated_at)
            VALUES (?,?,?,?,?,?) ON CONFLICT(run_id, stable_id, source_url)
            DO UPDATE SET status=excluded.status, reason=excluded.reason, updated_at=excluded.updated_at
            WHERE NOT (procurement_requests.status='acquired' AND EXISTS
                (SELECT 1 FROM procurement_evidence WHERE request_id=procurement_requests.id))""",
            (run_id, stable_id, source_url, status, reason, updated_at))
        self.db.commit()

    def list_procurement(self, status: str | None = None) -> list[dict]:
        sql = """SELECT p.id, p.run_id, p.stable_id, p.source_url, p.status, p.reason, p.updated_at,
            e.evidence_run_id, e.evidence_stable_id, e.evidence_path, e.evidence_sha256, e.linked_at
            FROM procurement_requests AS p LEFT JOIN procurement_evidence AS e ON e.request_id = p.id"""
        rows = self.db.execute(sql + (" WHERE p.status=?" if status else "") + " ORDER BY p.id DESC", (status,) if status else ()).fetchall()
        names = ("id", "run_id", "stable_id", "source_url", "status", "reason", "updated_at")
        result = []
        for row in rows:
            item = dict(zip(names, row[:7]))
            item["evidence"] = dict(zip(("run_id", "stable_id", "path", "sha256", "linked_at"), row[7:])) if row[7] else None
            result.append(item)
        return result

    def get_procurement(self, request_id: int) -> dict:
        item = next((item for item in self.list_procurement() if item["id"] == request_id), None)
        if item is None:
            raise ValueError("procurement request not found")
        history = self.db.execute("""SELECT evidence_run_id, evidence_stable_id, evidence_path,
            evidence_sha256, linked_at, reviewer_reason, superseded_at
            FROM procurement_evidence_history WHERE request_id=? ORDER BY id""", (request_id,)).fetchall()
        item["evidence_history"] = [dict(zip(("run_id", "stable_id", "path", "sha256", "linked_at", "reason", "superseded_at"), row)) for row in history]
        return item

    def acquired_fulfillment(self, run_id: str, stable_id: str, source_url: str) -> dict | None:
        row = self.db.execute("""SELECT p.id FROM procurement_requests AS p
            JOIN procurement_evidence AS e ON e.request_id=p.id
            WHERE p.run_id=? AND p.stable_id=? AND p.source_url=? AND p.status='acquired'""",
            (run_id, stable_id, source_url)).fetchone()
        if not row:
            return None
        if not self.verify_procurement(row[0])["valid"]:
            raise ValueError("reviewer-linked procurement evidence is missing or changed")
        return self.get_procurement(row[0])

    def _archive_procurement_evidence(self, request_id: int, superseded_at: str) -> None:
        self.db.execute("""INSERT INTO procurement_evidence_history
            (request_id, evidence_run_id, evidence_stable_id, evidence_path, evidence_sha256,
             linked_at, reviewer_reason, superseded_at)
            SELECT e.request_id, e.evidence_run_id, e.evidence_stable_id, e.evidence_path,
                e.evidence_sha256, e.linked_at, p.reason, ?
            FROM procurement_evidence AS e JOIN procurement_requests AS p ON p.id=e.request_id
            WHERE e.request_id=? AND NOT EXISTS
                (SELECT 1 FROM procurement_evidence_history AS h WHERE h.request_id=e.request_id
                 AND h.evidence_run_id=e.evidence_run_id AND h.linked_at=e.linked_at)""",
            (superseded_at, request_id))

    def fulfill_procurement(self, request_id: int, evidence_run_id: str, evidence_stable_id: str, linked_at: str, reviewer_note: str) -> dict:
        if not reviewer_note.strip() or len(reviewer_note) > 1000:
            raise ValueError("fulfillment requires a reviewer note of at most 1000 characters")
        request = self.get_procurement(request_id)
        if request["status"] == "acquired":
            raise ValueError("procurement request is already acquired")
        row = self.db.execute("""SELECT r.data_json, runs.status, runs.provider, runs.manifest_path
            FROM records AS r JOIN runs ON runs.id = r.run_id
            WHERE r.run_id=? AND r.stable_id=?""", (evidence_run_id, evidence_stable_id)).fetchone()
        if not row or row[1] != "complete" or row[2] != "local" or not row[3]:
            raise ValueError("fulfillment requires a complete local evidence run")
        record = json.loads(row[0])
        path = Path(record["raw_path"]).resolve()
        raw_root = Path(row[3]).resolve().parent / "raw"
        if record["access_status"] != "acquired" or not path.is_relative_to(raw_root) or not path.is_file():
            raise ValueError("fulfillment evidence is not a captured local source file")
        sha = _file_sha256(path)
        if sha != record["raw_sha256"]:
            raise ValueError("fulfillment evidence hash mismatch")
        if not _verify_captured_file(path, sha, Path(row[3]), evidence_run_id)["valid"]:
            raise ValueError("fulfillment evidence is absent from a valid capture manifest")
        with self.db:
            self._archive_procurement_evidence(request_id, linked_at)
            self.db.execute("""INSERT INTO procurement_evidence
                (request_id, evidence_run_id, evidence_stable_id, evidence_path, evidence_sha256, linked_at)
                VALUES (?,?,?,?,?,?) ON CONFLICT(request_id) DO UPDATE SET
                    evidence_run_id=excluded.evidence_run_id, evidence_stable_id=excluded.evidence_stable_id,
                    evidence_path=excluded.evidence_path, evidence_sha256=excluded.evidence_sha256,
                    linked_at=excluded.linked_at""", (request_id, evidence_run_id, evidence_stable_id, str(path), sha, linked_at))
            self.db.execute("""UPDATE procurement_requests SET status='acquired', reason=?, updated_at=? WHERE id=?""",
                ("reviewer assertion: " + reviewer_note.strip() + "; local file SHA-256 verified", linked_at, request_id))
        return self.get_procurement(request_id)

    def verify_procurement(self, request_id: int) -> dict:
        request = self.get_procurement(request_id)
        evidence = request["evidence"]
        origin = "reviewer_fulfillment" if evidence else "provider_download"
        if not evidence:
            row = self.db.execute("SELECT data_json FROM records WHERE run_id=? AND stable_id=?",
                                  (request["run_id"], request["stable_id"])).fetchone()
            record = json.loads(row[0]) if row else {}
            attachment = next((item for item in record.get("attachments", [])
                               if item.get("role") == "source"
                               and item.get("request_url", item.get("source_url")) == request["source_url"]), None)
            if not attachment:
                return {"request_id": request_id, "status": request["status"], "valid": False, "reason": "no captured evidence"}
            evidence = {"run_id": request["run_id"], "path": attachment["path"], "sha256": attachment["sha256"]}
        row = self.db.execute("SELECT manifest_path, status FROM runs WHERE id=?", (evidence["run_id"],)).fetchone()
        if not row or not row[0]:
            return {"request_id": request_id, "status": request["status"], "valid": False, "reason": "evidence run has no manifest"}
        result = _verify_captured_file(Path(evidence["path"]), evidence["sha256"], Path(row[0]), evidence["run_id"])
        result["valid"] = result["valid"] and request["status"] == "acquired" and (
            row[1] == "complete" if origin == "reviewer_fulfillment" else row[1] in {"complete", "partial"})
        return {"request_id": request_id, "status": request["status"], "evidence_origin": origin, **result}

    def linked_fulfillments(self, stable_id: str) -> list[dict]:
        rows = self.db.execute("""SELECT p.id, e.evidence_run_id, e.evidence_path, e.evidence_sha256,
            p.reason, runs.manifest_path FROM procurement_requests AS p
            JOIN procurement_evidence AS e ON e.request_id=p.id JOIN runs ON runs.id=e.evidence_run_id
            WHERE p.stable_id=? AND p.status='acquired' ORDER BY p.id""", (stable_id,)).fetchall()
        result = []
        for request_id, run_id, path, sha256, reason, manifest_path in rows:
            if not self.verify_procurement(request_id)["valid"]:
                raise ValueError(f"procurement evidence integrity check failed: request {request_id}")
            result.append({"request_id": request_id, "source_run_id": run_id, "path": path,
                           "sha256": sha256, "reviewer_reason": reason, "manifest_path": manifest_path,
                           "role": "procurement_source"})
        return result

    def set_procurement_status(self, request_id: int, status: str, reason: str, updated_at: str) -> None:
        if status == "acquired":
            raise ValueError("acquired status requires a captured and hashed source file")
        if status not in {"lead", "needs_host_approval", "failed", "reviewed"}:
            raise ValueError("invalid procurement status")
        with self.db:
            self._archive_procurement_evidence(request_id, updated_at)
            cursor = self.db.execute("UPDATE procurement_requests SET status=?, reason=?, updated_at=? WHERE id=?", (status, reason, updated_at, request_id))
            if cursor.rowcount != 1:
                raise ValueError("procurement request not found")

    def finish(self, run_id: str, status: str, finished_at: str, manifest_path: str) -> None:
        self.db.execute("UPDATE runs SET status=?, finished_at=?, manifest_path=? WHERE id=?", (status, finished_at, manifest_path, run_id))
        self.db.commit()

    def search(self, query: str, limit: int = 50) -> list[dict]:
        from .reconciliation import apply_corrections

        if len(query) > 256 or not 1 <= limit <= 1000:
            raise ValueError("search query or limit is outside supported bounds")
        rows = self.db.execute("""SELECT data_json FROM records
            WHERE instr(lower(title), lower(?)) > 0 OR instr(lower(stable_id), lower(?)) > 0
            OR instr(lower(data_json), lower(?)) > 0
            OR EXISTS (SELECT 1 FROM metadata_corrections AS c WHERE c.stable_id=records.stable_id
                AND c.action='correct' AND instr(lower(c.patch_json), lower(?)) > 0
                AND NOT EXISTS (SELECT 1 FROM metadata_corrections AS r WHERE r.reverts_id=c.id))
            ORDER BY rowid DESC LIMIT ?""", (query, query, query, query, limit)).fetchall()
        return [apply_corrections(record, self.correction_history(record["stable_id"]))
                for record in (json.loads(row[0]) for row in rows)]

    def correction_history(self, stable_id: str) -> list[dict]:
        rows = self.db.execute("""SELECT id, stable_id, action, patch_json, reason, created_at,
            base_run_id, base_raw_sha256, previous_values_json, reverts_id
            FROM metadata_corrections WHERE stable_id=? ORDER BY id""", (stable_id,)).fetchall()
        events = []
        for row in rows:
            event = dict(zip(("id", "stable_id", "action", "patch", "reason", "created_at",
                              "base_run_id", "base_raw_sha256", "previous_values", "reverts_id"), row))
            event["patch"] = json.loads(event["patch"])
            event["previous_values"] = json.loads(event["previous_values"])
            events.append(event)
        return events

    def _review_source(self, stable_id: str) -> tuple[str, dict]:
        row = self.db.execute("""SELECT r.run_id, r.data_json FROM records AS r
            JOIN runs ON runs.id=r.run_id WHERE r.stable_id=?
            ORDER BY (runs.status='complete') DESC, runs.started_at DESC, r.rowid DESC LIMIT 1""",
            (stable_id,)).fetchone()
        if not row:
            raise ValueError("reference ID not found")
        return row[0], json.loads(row[1])

    def correct_metadata(self, stable_id: str, patch: dict, reason: str) -> dict:
        from .reconciliation import apply_corrections, field_values, validate_correction

        patch = validate_correction(patch, reason)
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            run_id, source = self._review_source(stable_id)
            effective = apply_corrections(source, self.correction_history(stable_id))
            previous = field_values(effective, patch)
            changed_source_fields = effective.get("extras", {}).get("reviewed_metadata", {}).get("source_changed_fields", [])
            if previous == patch and not any(field in changed_source_fields for field in patch):
                raise ValueError("correction does not change the effective metadata")
            cursor = self.db.execute("""INSERT INTO metadata_corrections
                (stable_id, action, patch_json, reason, created_at, base_run_id, base_raw_sha256, previous_values_json)
                VALUES (?, 'correct', ?, ?, ?, ?, ?, ?)""",
                (stable_id, json.dumps(patch, ensure_ascii=False, sort_keys=True), reason.strip(), now(),
                 run_id, source["raw_sha256"], json.dumps(previous, ensure_ascii=False, sort_keys=True)))
            correction_id = cursor.lastrowid
        return {"correction_id": correction_id, "stable_id": stable_id, "patch": patch,
                "previous_values": previous, "reason": reason.strip()}

    def revert_metadata(self, correction_id: int, reason: str) -> dict:
        from .reconciliation import apply_corrections, field_values

        if not isinstance(reason, str) or not reason.strip() or len(reason) > 1000:
            raise ValueError("metadata review requires a reason of 1..1000 characters")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            row = self.db.execute("SELECT stable_id, action, patch_json FROM metadata_corrections WHERE id=?", (correction_id,)).fetchone()
            if not row or row[1] != "correct":
                raise ValueError("revert requires an existing correction event ID")
            stable_id = row[0]
            history = self.correction_history(stable_id)
            if any(event["reverts_id"] == correction_id for event in history):
                raise ValueError("correction is already reverted")
            run_id, source = self._review_source(stable_id)
            previous = field_values(apply_corrections(source, history), json.loads(row[2]))
            cursor = self.db.execute("""INSERT INTO metadata_corrections
                (stable_id, action, patch_json, reason, created_at, base_run_id, base_raw_sha256,
                 previous_values_json, reverts_id) VALUES (?, 'revert', '{}', ?, ?, ?, ?, ?, ?)""",
                (stable_id, reason.strip(), now(), run_id, source["raw_sha256"],
                 json.dumps(previous, ensure_ascii=False, sort_keys=True), correction_id))
            event_id = cursor.lastrowid
        return {"revert_event_id": event_id, "stable_id": stable_id,
                "reverted_correction_id": correction_id, "reason": reason.strip()}

    def review(self, stable_id: str) -> dict:
        from .citation import bibtex, ris
        from .reconciliation import apply_corrections

        rows = self.db.execute("""SELECT r.run_id, runs.status, runs.finished_at, r.data_json
            FROM records AS r JOIN runs ON runs.id = r.run_id
            WHERE r.stable_id = ? ORDER BY runs.started_at DESC, r.rowid DESC""", (stable_id,)).fetchall()
        if not rows:
            raise ValueError("reference ID not found")
        versions = [{"run_id": run_id, "run_status": status, "finished_at": finished_at, "record": json.loads(data)} for run_id, status, finished_at, data in rows]
        fields = ("kind", "title", "creators", "identifiers", "dates", "citation", "abstract", "source_url", "raw_sha256")
        conflicts = {}
        for field in fields:
            values = [entry["record"].get(field) for entry in versions]
            if len({json.dumps(value, sort_keys=True, ensure_ascii=False) for value in values}) > 1:
                conflicts[field] = values
        preview_run, source = self._review_source(stable_id)
        history = self.correction_history(stable_id)
        effective = apply_corrections(source, history)
        latest = Reference(**effective)
        latest.attachments.extend(self.linked_fulfillments(stable_id))
        procurement = [item for item in self.list_procurement() if item["stable_id"] == stable_id]
        return {"stable_id": stable_id, "version_count": len(versions), "conflicts": conflicts,
                "preview_source_run_id": preview_run, "effective_record": effective, "correction_history": history,
                "citation_preview": {"ris": ris([latest]), "bibtex": bibtex([latest])}, "procurement": procurement, "versions": versions}

    def latest_records(self, provider: str | None = None, dataset: str | None = None) -> list[dict]:
        from .reconciliation import apply_corrections
        clauses = ["runs.status='complete'"]
        params: list[str] = []
        if provider:
            clauses.append("runs.provider=?")
            params.append(provider)
        if dataset:
            clauses.append("runs.dataset=?")
            params.append(dataset)
        rows = self.db.execute("""SELECT r.data_json, r.run_id, runs.manifest_path
            FROM records AS r JOIN runs ON runs.id = r.run_id WHERE """ + " AND ".join(clauses) +
            " ORDER BY runs.started_at DESC, r.rowid DESC", params).fetchall()
        selected: list[dict] = []
        seen: set[str] = set()
        for data, run_id, manifest_path in rows:
            record = json.loads(data)
            if record["stable_id"] not in seen:
                history = self.correction_history(record["stable_id"])
                selected.append({"run_id": run_id, "manifest_path": manifest_path,
                                 "record": apply_corrections(record, history), "correction_history": history})
                seen.add(record["stable_id"])
        return selected

    def close(self) -> None:
        self.db.close()
