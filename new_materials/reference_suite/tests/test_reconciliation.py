from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from reference_suite.cli import main
from reference_suite.engine import execute
from reference_suite.library_export import export_library
from reference_suite.model import Job, digest
from reference_suite.offline import inspect_export
from reference_suite.storage import Library


class MetadataReviewTests(unittest.TestCase):
    def import_source(self, root: Path, title: str = "Source title") -> dict:
        source = root / "source.ris"
        source.write_text("TY  - JOUR\nAN  - local:reviewed\nTI  - " + title +
                          "\nAU  - Source Author\nJO  - Source Journal\nDO  - 10.1000/source\n"
                          "DA  - 2024-01-02\nUR  - https://example.org/source\nER  - \n", encoding="utf-8")
        result = execute(Job("local", "import_ris", str(source)), root)
        self.assertEqual(result["status"], "complete")
        return result

    def test_corrected_preview_search_and_export_preserve_original_source_and_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.import_source(root)
            run = Path(result["run_dir"])
            original_files = {path: digest(path.read_bytes()) for path in run.rglob("*") if path.is_file()}
            patch_file = root / "correction.json"
            patch_file.write_text(json.dumps({"title": "Reviewed title", "creators": ["Reviewed Author"],
                                             "citation.volume": "12", "dates.citation": "2024-03-04"}), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--root", str(root), "review-correct", "local:reviewed", str(patch_file),
                                       "--reason", "Checked against retained article title page"]), 0)
            correction_id = json.loads(output.getvalue())["correction_id"]
            library = Library(root)
            try:
                reviewed = library.review("local:reviewed")
                source = reviewed["versions"][0]["record"]
                effective = reviewed["effective_record"]
                self.assertEqual(source["title"], "Source title")
                self.assertEqual(effective["title"], "Reviewed title")
                for field in ("stable_id", "provider", "identifiers", "source_url", "retrieval_url", "raw_path", "raw_sha256"):
                    self.assertEqual(effective[field], source[field])
                self.assertIn("TI  - Reviewed title", reviewed["citation_preview"]["ris"])
                self.assertIn("author = {Reviewed Author}", reviewed["citation_preview"]["bibtex"])
                self.assertEqual(library.search("Reviewed title")[0]["title"], "Reviewed title")
                self.assertEqual(reviewed["correction_history"][0]["previous_values"]["title"], "Source title")
                original_database_record = library.db.execute("SELECT data_json FROM records WHERE run_id=?", (result["run_id"],)).fetchone()[0]
                self.assertEqual(json.loads(original_database_record), source)
            finally:
                library.close()
            exported = export_library(root, include_attachments=True)
            folder = Path(exported["export_dir"])
            record = json.loads((folder / "records.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(record["title"], "Reviewed title")
            self.assertEqual(record["extras"]["reviewed_metadata"]["active_correction_ids"], [correction_id])
            audit_attachment = next(item for item in record["attachments"] if item["role"] == "metadata_review")
            audit_path = Path(audit_attachment["path"])
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(audit["events"][0]["reason"], "Checked against retained article title page")
            self.assertEqual(digest(audit_path.read_bytes()), audit_attachment["sha256"])
            self.assertIn(str(audit_path), (folder / "references.ris").read_text(encoding="utf-8"))
            provenance = json.loads((folder / "provenance.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(provenance["correction_history"][0]["id"], correction_id)
            self.assertEqual(original_files, {path: digest(path.read_bytes()) for path in run.rglob("*") if path.is_file()})
            self.assertTrue(inspect_export(run)["valid"])

    def test_superseding_and_reverting_corrections_preserve_append_only_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.import_source(root)
            library = Library(root)
            try:
                first = library.correct_metadata("local:reviewed", {"title": "First correction", "citation.publisher": "Verified Publisher"}, "Initial review")["correction_id"]
                second = library.correct_metadata("local:reviewed", {"title": "Second correction"}, "Rechecked spelling")["correction_id"]
                self.assertEqual(library.review("local:reviewed")["effective_record"]["title"], "Second correction")
                reverted = library.revert_metadata(second, "Restore first reviewed spelling")
                current = library.review("local:reviewed")["effective_record"]
                self.assertEqual(current["title"], "First correction")
                self.assertEqual(current["citation"]["publisher"], "Verified Publisher")
                with self.assertRaisesRegex(ValueError, "already reverted"):
                    library.revert_metadata(second, "Duplicate reversal")
                with self.assertRaisesRegex(ValueError, "correction event"):
                    library.revert_metadata(reverted["revert_event_id"], "Wrong event type")
                with self.assertRaises(sqlite3.IntegrityError):
                    library.db.execute("UPDATE metadata_corrections SET reason='changed' WHERE id=?", (first,))
                library.db.rollback()
                with self.assertRaises(sqlite3.IntegrityError):
                    library.db.execute("DELETE FROM metadata_corrections WHERE id=?", (first,))
                library.db.rollback()
            finally:
                library.close()
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--root", str(root), "review-revert", str(first), "--reason", "Return to source metadata"]), 0)
            library = Library(root)
            try:
                review = library.review("local:reviewed")
                self.assertEqual(review["effective_record"]["title"], "Source title")
                self.assertNotIn("publisher", review["effective_record"]["citation"])
                self.assertEqual([event["action"] for event in review["correction_history"]], ["correct", "correct", "revert", "revert"])
                self.assertEqual(review["effective_record"]["extras"]["reviewed_metadata"]["active_correction_ids"], [])
            finally:
                library.close()
            folder = Path(export_library(root)["export_dir"])
            self.assertIn("TI  - Source title", (folder / "references.ris").read_text())
            self.assertEqual(len(json.loads((folder / "provenance.jsonl").read_text())["correction_history"]), 4)

    def test_corrections_reject_identity_changes_invalid_values_and_no_ops(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.import_source(root)
            library = Library(root)
            try:
                invalid = [{"stable_id": "other"}, {"source_url": "https://other.example/"}, {"identifiers.doi": "10.1/other"},
                           {"raw_path": "other"}, {"citation": {"volume": "1"}}, {"title": ""}, {"creators": [42]},
                           {"dates.citation": "2023-02-29"}, {"dates.retrieval": "2024-03-04"}, {"citation.volume": 12}, {}]
                for patch in invalid:
                    with self.subTest(patch=patch), self.assertRaises(ValueError):
                        library.correct_metadata("local:reviewed", patch, "Review")
                with self.assertRaises(ValueError):
                    library.correct_metadata("local:reviewed", {"title": "Reviewed"}, " ")
                with self.assertRaisesRegex(ValueError, "does not change"):
                    library.correct_metadata("local:reviewed", {"title": "Source title"}, "No edit")
                with self.assertRaisesRegex(ValueError, "not found"):
                    library.correct_metadata("absent", {"title": "Reviewed"}, "Review")
                self.assertEqual(library.correction_history("local:reviewed"), [])
                library.correct_metadata("local:reviewed", {"citation.container_title": None, "creators": []}, "Remove unsupported journal and author mapping")
                current = library.review("local:reviewed")["effective_record"]
                self.assertNotIn("container_title", current["citation"])
                self.assertEqual(current["creators"], [])
            finally:
                library.close()

    def test_new_source_version_keeps_correction_and_flags_changed_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.import_source(root)
            library = Library(root)
            library.correct_metadata("local:reviewed", {"title": "Reviewed title"}, "First source review")
            self.assertFalse(library.review("local:reviewed")["effective_record"]["extras"]["reviewed_metadata"]["source_changed_since_review"])
            library.close()
            second = self.import_source(root, "Refreshed source title")
            library = Library(root)
            try:
                review = library.review("local:reviewed")
                self.assertEqual(review["version_count"], 2)
                self.assertEqual(review["preview_source_run_id"], second["run_id"])
                self.assertEqual(review["effective_record"]["title"], "Reviewed title")
                self.assertTrue(review["effective_record"]["extras"]["reviewed_metadata"]["source_changed_since_review"])
                self.assertEqual(review["correction_history"][0]["base_run_id"], first["run_id"])
                confirmation = library.correct_metadata("local:reviewed", {"title": "Reviewed title"}, "Confirmed against refreshed source")
                metadata = library.review("local:reviewed")["effective_record"]["extras"]["reviewed_metadata"]
                self.assertFalse(metadata["source_changed_since_review"])
                self.assertEqual(metadata["field_correction_ids"]["title"], confirmation["correction_id"])
            finally:
                library.close()


if __name__ == "__main__":
    unittest.main()
