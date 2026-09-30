from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from reference_suite.model import Job, digest, json_bytes
from reference_suite.presets import job_from_dict, list_presets, list_revisions, load_preset, preset_job, save_preset


class PresetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "selected-data"
        self.job = Job("web", "mirror", "https://example.org/research", dataset="research",
                       allow_hosts=("example.org", "files.example.org"), max_results=8,
                       max_depth=2, download_files=True)

    def save(self, job=None, **kwargs):
        return save_preset(self.root, "research", job or self.job, reason="Reviewed the exact host and result limit", **kwargs)

    def modify(self, revision, change, *, rehash=False):
        with closing(sqlite3.connect(self.root / "presets.sqlite3")) as connection, connection:
            raw, sha = connection.execute("SELECT record_json, revision_sha256 FROM preset_revisions WHERE name='research' AND revision=?", (revision,)).fetchone()
            record = json.loads(raw)
            change(record)
            payload = json_bytes(record)
            connection.execute("UPDATE preset_revisions SET record_json=?, revision_sha256=? WHERE name='research' AND revision=?",
                               (payload.decode(), digest(payload) if rehash else sha, revision))

    def test_roundtrip_preserves_full_job_and_explicit_review_provenance(self):
        saved = self.save(description="Bounded technical-site review", source="reviewed-job.json", reviewer="Local reviewer")
        self.assertEqual(saved, load_preset(self.root, "research"))
        self.assertEqual(preset_job(self.root, "research"), self.job)
        self.assertEqual(saved["job_sha256"], digest(json_bytes(self.job.asdict())))
        self.assertEqual(saved["provenance"], {"source": "reviewed-job.json", "reviewer": "Local reviewer", "previous_revision": None, "previous_sha256": None})
        self.assertEqual(list_presets(self.root)[0]["operation"], "mirror")
        self.assertEqual(set(self.root.iterdir()), {self.root / "presets.sqlite3"})

    def test_revisions_retain_earlier_jobs_and_link_their_hashes(self):
        first = self.save()
        second_job = Job("openalex", "lookup", "10.1234/example", citation_depth=1)
        second = self.save(second_job)
        self.assertEqual(first, load_preset(self.root, "research", 1))
        self.assertEqual(second, load_preset(self.root, "research"))
        self.assertEqual(preset_job(self.root, "research", 1), self.job)
        self.assertEqual(preset_job(self.root, "research"), second_job)
        self.assertEqual(second["provenance"]["previous_sha256"], first["revision_sha256"])
        self.assertEqual([item["revision"] for item in list_revisions(self.root, "research")], [1, 2])
        self.assertEqual(list_presets(self.root)[0]["revision"], 2)

    def test_missing_presets_are_read_only_and_names_cannot_escape_root(self):
        self.assertEqual(list_presets(self.root), [])
        self.assertEqual(list_revisions(self.root, "missing"), [])
        self.assertFalse(self.root.exists())
        for name in ("", "../escape", "C:\\escape", "a/b", "a\\b", "a:stream", ".", "a b", "Uppercase"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                save_preset(self.root, name, self.job, reason="reviewed")
        self.assertFalse(self.root.exists())
        with self.assertRaises(ValueError):
            load_preset(self.root, "missing")
        self.save()
        for revision in (0, -1, True, "1", 2):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                load_preset(self.root, "research", revision)

    def test_invalid_provider_scope_and_malformed_job_types_are_rejected_before_writing(self):
        invalid = [
            {**self.job.asdict(), "value": "https://unapproved.example/"},
            {**self.job.asdict(), "value": "https://user:password@example.org/"},
            {**self.job.asdict(), "allow_hosts": "example.org"},
            {**self.job.asdict(), "allow_hosts": [42]},
            {**self.job.asdict(), "download_files": 1},
            {**self.job.asdict(), "max_results": True},
            {**self.job.asdict(), "render_js": "false"},
            {**self.job.asdict(), "api_key": "never-store-this"},
            {"provider": "uspto", "operation": "application", "value": "not-a-number"},
            {"provider": "uspto", "operation": "get", "value": "https://unapproved.example/"},
            {"provider": "openalex", "operation": "search"},
        ]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(ValueError):
                save_preset(self.root, "research", data, reason="reviewed")
        with self.assertRaises(ValueError):
            save_preset(self.root, "research", self.job, reason="   ")
        self.assertFalse(self.root.exists())

    def test_stored_job_and_review_metadata_tampering_is_detected(self):
        self.save()
        self.modify(1, lambda record: record["job"].update(value="https://example.org/changed"))
        with self.assertRaisesRegex(ValueError, "integrity"):
            load_preset(self.root, "research")
        with self.assertRaises(ValueError):
            self.save()
        with closing(sqlite3.connect(self.root / "presets.sqlite3")) as connection, connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM preset_revisions").fetchone()[0], 1)

    def test_recomputed_record_hash_does_not_skip_job_or_scope_validation(self):
        self.save()
        self.modify(1, lambda record: record["job"].update(value="https://example.org/changed"), rehash=True)
        with self.assertRaisesRegex(ValueError, "job hash"):
            load_preset(self.root, "research")
        def invalid_scope(record):
            record["job"]["value"] = "https://unapproved.example/"
            record["job_sha256"] = digest(json_bytes(record["job"]))
        self.modify(1, invalid_scope, rehash=True)
        with self.assertRaisesRegex(ValueError, "allowed host"):
            load_preset(self.root, "research")

    def test_missing_or_changed_earlier_revisions_break_the_chain(self):
        self.save()
        self.save()
        self.modify(1, lambda record: record.update(reason="Changed reason"), rehash=True)
        with self.assertRaisesRegex(ValueError, "chain"):
            list_revisions(self.root, "research")
        with closing(sqlite3.connect(self.root / "presets.sqlite3")) as connection, connection:
            connection.execute("DELETE FROM preset_revisions WHERE revision=1")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            list_presets(self.root)

    def test_uspto_presets_require_no_credentials_and_never_acquire(self):
        job = Job("uspto", "application", "14412875")
        with patch.dict("os.environ", {"USPTO_ODP_API_KEY": "credential-canary"}), \
             patch("urllib.request.urlopen", side_effect=AssertionError("network used")), \
             patch("reference_suite.engine.execute", side_effect=AssertionError("acquisition used")):
            record = self.save(job)
            self.assertEqual(preset_job(self.root, "research"), job)
        self.assertNotIn("credential-canary", json.dumps(record))
        self.assertNotIn(b"credential-canary", (self.root / "presets.sqlite3").read_bytes())
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(job_from_dict(job.asdict()), job)

    def test_concurrent_saves_append_distinct_revisions(self):
        self.save()
        with ThreadPoolExecutor(max_workers=4) as pool:
            revisions = list(pool.map(lambda _: self.save()["revision"], range(4)))
        self.assertEqual(sorted(revisions), [2, 3, 4, 5])
        self.assertEqual(len(list_revisions(self.root, "research")), 5)

    def test_database_links_cannot_redirect_storage_outside_the_data_root(self):
        self.root.mkdir()
        outside = self.root.parent / "outside.sqlite3"
        outside.write_bytes(b"retained outside file")
        try:
            (self.root / "presets.sqlite3").symlink_to(outside)
        except OSError as error:
            self.skipTest("Creating a symbolic link is unavailable: " + str(error))
        with self.assertRaisesRegex(ValueError, "symbolic links"):
            self.save()
        self.assertEqual(outside.read_bytes(), b"retained outside file")


if __name__ == "__main__":
    unittest.main()
