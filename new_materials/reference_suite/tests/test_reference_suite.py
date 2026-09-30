from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

from reference_suite.citation import bibtex, endnote_type_table, ris, validate_sidecars
from reference_suite.engine import Response, execute
from reference_suite.gui import job_from_form
from reference_suite.local_intake import preview_local
from reference_suite.library_export import export_library
from reference_suite.model import Job, Reference, digest
from reference_suite.offline import batch_urls, derive_bytes, extract_urls, inspect_export, normalize_export, write_web_reports
from reference_suite.providers import plan
from reference_suite.procurement import fulfill_request
from reference_suite.rendered import PlaywrightRenderer, RenderedPage, browser_launch_options
from reference_suite.ris_import import parse_ris
from reference_suite.storage import Library


class FakeTransport:
    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    def fetch(self, request, allowed_hosts):
        self.requests.append(request)
        assert request.allowed_host in allowed_hosts
        value = self.responses[request.url]
        if isinstance(value, Exception):
            raise value
        if isinstance(value, Response):
            return value
        if isinstance(value, dict):
            return Response(json.dumps(value).encode(), request.url, 200, "application/json")
        return Response(value, request.url, 200, "text/html")


class PlanningTests(unittest.TestCase):
    def test_browser_override_requires_existing_absolute_executable(self):
        with patch.dict("os.environ", {"REFERENCE_SUITE_BROWSER": ""}):
            self.assertEqual(browser_launch_options(), {"headless": True})
        with patch.dict("os.environ", {"REFERENCE_SUITE_BROWSER": sys.executable}):
            self.assertEqual(browser_launch_options()["executable_path"], str(Path(sys.executable).resolve()))
        for invalid in ("relative-browser.exe", str(Path(tempfile.gettempdir()) / "missing-browser-c7320.exe")):
            with patch.dict("os.environ", {"REFERENCE_SUITE_BROWSER": invalid}):
                with self.assertRaisesRegex(ValueError, "REFERENCE_SUITE_BROWSER"):
                    PlaywrightRenderer().capture("https://example.org/", {"example.org"})

    def test_desktop_job_preserves_host_download_and_mirror_controls(self):
        job = job_from_form({"provider": "web", "operation": "mirror", "value": "https://example.org/",
                             "dataset": "references", "max_results": "8", "citation_depth": "0",
                             "max_depth": "2", "allow_hosts": "example.org, files.example.org",
                             "download_files": True, "render_js": False, "render_pdf": False,
                             "content_selector": ""})
        expected = Job("web", "mirror", "https://example.org/", max_results=8, max_depth=2,
                       allow_hosts=("example.org", "files.example.org"), download_files=True)
        self.assertEqual(job, expected)
        self.assertEqual(plan(job), plan(expected))

    def test_bibtex_keys_remain_unique_after_sanitizing_and_truncation(self):
        identifiers = ["local:a/b", "local:a:b", "local:" + "x" * 90 + "1", "local:" + "x" * 90 + "2"]
        records = [Reference("local", "document", identifier, "Title", "", "2026-09-22", "sha", "raw") for identifier in identifiers]
        keys = re.findall(r"^@\w+\{([^,]+),", bibtex(records), re.M)
        self.assertEqual(len(keys), len(identifiers))
        self.assertEqual(len(set(keys)), len(identifiers))

    def test_xml_derivation_preserves_structure_and_reports_bad_xml(self):
        text, method = derive_bytes(b"<root><item>Value</item></root>", ".xml")
        self.assertEqual(method, "xml:pretty")
        self.assertIn("<item>Value</item>", text)
        raw, fallback = derive_bytes(b"<root><item>", ".xml")
        self.assertEqual(fallback, "xml:unparsed")
        self.assertEqual(raw, "<root><item>")

    def test_ris_parser_rejects_unframed_content(self):
        with self.assertRaises(ValueError):
            parse_ris(b"AU  - Unframed Author\n")

    def test_bibtex_escapes_source_special_characters_once(self):
        rec = Reference("local", "document", "local:test", "Set {A} \\ B", "", "2026-09-22", "sha", "raw")
        citation = bibtex([rec])
        self.assertIn(r"Set \{A\} \textbackslash{} B", citation)
        self.assertNotIn(r"\textbackslash\{\}", citation)

    def test_library_review_shows_versions_and_citation_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = Library(Path(tmp))
            try:
                for run_id, title, started in (("run1", "Early title", "2026-09-21T00:00:00Z"), ("run2", "Revised title", "2026-09-22T00:00:00Z")):
                    library.start(run_id, "openalex", "references", started)
                    library.record(run_id, Reference("openalex", "article", "openalex:W1", title, "https://example.org/", started, run_id, "raw.json"))
                    library.finish(run_id, "complete", started, "manifest.json")
                review = library.review("openalex:W1")
                self.assertEqual(review["version_count"], 2)
                self.assertEqual(review["conflicts"]["title"], ["Revised title", "Early title"])
                self.assertIn("Revised title", review["citation_preview"]["ris"])
            finally:
                library.close()

    def test_manual_review_cannot_claim_unacquired_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = Library(Path(tmp))
            try:
                library.start("run1", "openalex", "references", "2026-09-22T00:00:00Z")
                library.procurement("run1", "openalex:W1", "", "lead", "missing file URL", "2026-09-22T00:00:00Z")
                request_id = library.list_procurement()[0]["id"]
                with self.assertRaises(ValueError):
                    library.set_procurement_status(request_id, "acquired", "manual claim", "2026-09-22T00:00:01Z")
                self.assertEqual(library.list_procurement()[0]["status"], "lead")
            finally:
                library.close()

    def test_offline_url_extraction_deduplicates_selected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "notes.md"
            path.write_text("See https://example.org/a and https://example.org/a. Also https://other.org/b)", encoding="utf-8")
            self.assertEqual(extract_urls([path]), ["https://example.org/a", "https://other.org/b"])

    def test_batch_prevalidates_every_host_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "urls.txt"
            source.write_text("https://example.org/a\nhttps://other.org/b\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                batch_urls(source, root, ("example.org",), execute_jobs=True)
            self.assertFalse((root / "out").exists())
            result = batch_urls(source, root, ("example.org", "other.org"))
            self.assertEqual(result["count"], 2)
            self.assertFalse(result["network_access"])
    def test_endnote_template_copies_real_field_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "exported.xml"
            target = Path(tmp) / "adapted.xml"
            source.write_text('<RefTypes version="22"><RefType id="0" name="Generic"><Fields><Field id="2">Author</Field><Field id="30">Accession Number</Field></Fields></RefType><RefType id="14" name="Unused 1"><Fields /></RefType></RefTypes>')
            endnote_type_table(source, target)
            rendered = target.read_text()
            self.assertIn('name="Reference Suite"', rendered)
            self.assertIn('id="30"', rendered)
    def test_plan_is_bounded_and_requires_allowlist(self):
        with self.assertRaises(ValueError):
            Job("web", "capture", "https://example.org/")
        with self.assertRaises(ValueError):
            plan(Job("web", "capture", "http://example.org/", allow_hosts=("example.org",)))
        with self.assertRaises(ValueError):
            plan(Job("web", "capture", "https://other.org/", allow_hosts=("example.org",)))
        req = plan(Job("web", "capture", "https://example.org/", allow_hosts=("example.org",)))[0]
        self.assertEqual(req.allowed_host, "example.org")

    def test_uspto_search_plan(self):
        req = plan(Job("uspto", "search", "feral pig", max_results=8))[0]
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.body["pagination"]["limit"], 8)
        self.assertEqual(req.auth_env, "USPTO_ODP_API_KEY")

    def test_ptab_and_petition_paths_from_pyuspto(self):
        petition = plan(Job("uspto", "petition", "applicationNumberText:17765301"))[0]
        trial = plan(Job("uspto", "ptab_trials", "trialNumber:IPR2023-00001"))[0]
        self.assertIn("/petition/decisions/search?", petition.url)
        self.assertIn("/patent/trials/proceedings/search?", trial.url)
        self.assertEqual(petition.method, "GET")

    def test_uspto_get_composer_stays_on_api_path(self):
        req = plan(Job("uspto", "get", "/api/v1/patent/applications/14412875"))[0]
        self.assertEqual(req.url, "https://api.uspto.gov/api/v1/patent/applications/14412875")
        with self.assertRaises(ValueError):
            plan(Job("uspto", "get", "//other.example.org/private"))


class EngineTests(unittest.TestCase):
    def test_ris_import_enforces_job_limit_in_preview_and_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "two.ris"
            source.write_bytes(b"TY  - JOUR\nTI  - One\nER  - \nTY  - JOUR\nTI  - Two\nER  - \n")
            job = Job("local", "import_ris", str(source), max_results=1)
            with self.assertRaisesRegex(ValueError, "record limit"):
                preview_local(job, root)
            result = execute(job, root)
            self.assertEqual(result["status"], "failed")
            self.assertFalse((root / "out" / "local" / "references" / "latest.txt").exists())

    def test_ris_generic_tags_are_not_patent_identifiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "article.ris"
            source.write_bytes(b"TY  - JOUR\nTI  - Article\nDO  - DOI: 10.1000/example\nM1  - 12\nM3  - Review\nER  - \n")
            result = execute(Job("local", "import_ris", str(source)), root)
            record = json.loads((Path(result["run_dir"]) / "normalized_canonical.jsonl").read_text())
            self.assertEqual(record["identifiers"], {"doi": "10.1000/example"})
            self.assertEqual(record["extras"]["ris_fields"]["M3"], ["Review"])

    def test_resume_preserves_manual_fulfillment_and_request_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = Job("openalex", "lookup", "W123", download_files=True, allow_hosts=("files.example.org",))
            url, pdf = plan(job)[0].url, "https://files.example.org/paper.pdf"
            item = {"id": "https://openalex.org/W123", "title": "Paper", "best_oa_location": {"pdf_url": pdf}}
            first = execute(job, root, FakeTransport({url: item, pdf: RuntimeError("not available")}))
            library = Library(root)
            request_id = library.list_procurement()[0]["id"]
            library.close()
            source = root / "reviewed.txt"
            source.write_text("Reviewed source")
            fulfill_request(root, request_id, source, "Identity reviewed")
            resumed = FakeTransport({url: item})
            result = execute(job, root, resumed, resume_run_id=first["run_id"])
            self.assertEqual(result["status"], "complete")
            self.assertEqual([request.url for request in resumed.requests], [url])
            library = Library(root)
            try:
                self.assertEqual(len(library.list_procurement()), 1)
                self.assertTrue(library.verify_procurement(request_id)["valid"])
            finally:
                library.close()

    def test_replacing_reviewed_fulfillment_retains_previous_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = Job("openalex", "lookup", "W123", download_files=True)
            execute(job, root, FakeTransport({plan(job)[0].url: {"id": "https://openalex.org/W123", "title": "Paper"}}))
            library = Library(root)
            request_id = library.list_procurement()[0]["id"]
            library.close()
            source = root / "reviewed.txt"
            source.write_text("First reviewed source")
            first = fulfill_request(root, request_id, source, "First identity review")["request"]["evidence"]
            library = Library(root)
            library.set_procurement_status(request_id, "reviewed", "Replacement needed", "2026-09-22")
            library.close()
            source.write_text("Replacement source")
            second = fulfill_request(root, request_id, source, "Corrected identity review")["request"]
            self.assertNotEqual(first["sha256"], second["evidence"]["sha256"])
            self.assertEqual(second["evidence_history"][0]["sha256"], first["sha256"])
            self.assertIn("First identity review", second["evidence_history"][0]["reason"])
            self.assertTrue(Path(first["path"]).is_file())

    def test_normalized_export_chunks_reconstruct_full_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "long.txt"
            source.write_text("A" * 2501, encoding="utf-8")
            result = execute(Job("local", "ingest", str(source)), root)
            run = Path(result["run_dir"])
            regenerated = normalize_export(run, split_chars=1000)
            self.assertEqual(regenerated["chunks"], 3)
            index_path = next((run / "derived" / "splits").rglob("index.json"))
            index = json.loads(index_path.read_text())
            chunks = "".join((run / item["path"]).read_text(encoding="utf-8") for item in index["chunks"])
            self.assertEqual(chunks, (run / index["full_derived"]).read_text(encoding="utf-8"))
            self.assertTrue(inspect_export(run)["valid"])

    def test_direct_web_pdf_is_a_document_with_derived_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            url = "https://example.org/source.pdf"
            job = Job("web", "capture", url, allow_hosts=("example.org",))
            fake = FakeTransport({url: Response(b"%PDF-1.7\nfixture", url, 200, "application/pdf")})
            with patch("reference_suite.offline._pdf_text", return_value=("Extracted page text\n", "pdf:test")):
                result = execute(job, Path(tmp), fake)
            self.assertEqual(result["status"], "complete")
            record = json.loads((Path(result["run_dir"]) / "normalized_canonical.jsonl").read_text())
            self.assertEqual(record["kind"], "document")
            self.assertEqual(record["extras"]["derivation_method"], "pdf:test")
            self.assertIn("Extracted page text", Path(record["extras"]["derived_markdown"]).read_text())
            self.assertTrue(record["raw_path"].endswith(".pdf"))

    def test_combined_library_export_selects_latest_and_bundles_verified_attachments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = Job("openalex", "lookup", "W123")
            url = plan(job)[0].url
            first = execute(job, root, FakeTransport({url: {"id": "https://openalex.org/W123", "title": "Earlier"}}))
            second = execute(job, root, FakeTransport({url: {"id": "https://openalex.org/W123", "title": "Later"}}))
            self.assertEqual(first["status"], "complete")
            self.assertEqual(second["status"], "complete")
            result = export_library(root, include_attachments=True)
            self.assertEqual(result["records"], 1)
            folder = Path(result["export_dir"])
            record = json.loads((folder / "records.jsonl").read_text())
            self.assertEqual(record["title"], "Later")
            self.assertTrue(Path(record["raw_path"]).is_relative_to(folder))
            self.assertTrue(Path(record["attachments"][0]["path"]).is_relative_to(folder))
            manifest = json.loads((folder / "manifest.json").read_text())
            self.assertTrue(all(digest((folder / item["path"]).read_bytes()) == item["sha256"] for item in manifest["artifacts"]))
            self.assertIn("Later", (folder / "references.ris").read_text())
            self.assertNotIn("Earlier", (folder / "references.ris").read_text())

    def test_local_tree_intake_previews_and_excludes_its_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nested").mkdir()
            (root / "a.txt").write_text("Same content", encoding="utf-8")
            (root / "nested" / "b.txt").write_text("Same content", encoding="utf-8")
            job = Job("local", "ingest_tree", str(root), max_results=2)
            self.assertEqual(preview_local(job, root)["file_count"], 2)
            result = execute(job, root)
            self.assertEqual(result["status"], "complete")
            self.assertEqual(result["records"], 2)
            records = [json.loads(line) for line in (Path(result["run_dir"]) / "normalized_canonical.jsonl").read_text().splitlines()]
            self.assertEqual(len({record["stable_id"] for record in records}), 2)
            self.assertEqual(preview_local(job, root)["file_count"], 2)
            self.assertTrue(inspect_export(Path(result["run_dir"]))["valid"])
            with self.assertRaises(ValueError):
                preview_local(Job("local", "ingest_tree", str(root), max_results=1), root)

    def test_procurement_fulfillment_links_hashed_local_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = Job("openalex", "lookup", "W123", download_files=True)
            url = plan(job)[0].url
            result = execute(job, root, FakeTransport({url: {"id": "https://openalex.org/W123", "title": "Paper"}}))
            self.assertEqual(result["status"], "complete")
            library = Library(root)
            pending = library.list_procurement()[0]
            self.assertEqual(pending["status"], "lead")
            library.close()
            source = root / "reviewed-source.pdf"
            source.write_bytes(b"%PDF-1.7\nreviewed file")
            fulfilled = fulfill_request(root, pending["id"], source, "Matched source title and DOI manually")
            self.assertEqual(fulfilled["status"], "acquired")
            library = Library(root)
            try:
                request = library.get_procurement(pending["id"])
                self.assertEqual(request["status"], "acquired")
                self.assertEqual(request["evidence"]["sha256"], digest(source.read_bytes()))
                self.assertTrue(Path(request["evidence"]["path"]).is_file())
                self.assertTrue(library.verify_procurement(pending["id"])["valid"])
                self.assertEqual(library.review(pending["stable_id"])["procurement"][0]["id"], pending["id"])
                self.assertIn(request["evidence"]["path"], library.review(pending["stable_id"])["citation_preview"]["ris"])
                exported = export_library(root, provider="openalex", include_attachments=True)
                exported_record = json.loads((Path(exported["export_dir"]) / "records.jsonl").read_text())
                linked = next(item for item in exported_record["attachments"] if item["role"] == "procurement_source")
                self.assertEqual(digest(Path(linked["path"]).read_bytes()), request["evidence"]["sha256"])
                self.assertTrue(Path(linked["path"]).is_relative_to(Path(exported["export_dir"])))
                self.assertEqual(exported_record["access_status"], "acquired")
                with self.assertRaises(ValueError):
                    library.set_procurement_status(pending["id"], "acquired", "claim", "2026-09-22")
                Path(request["evidence"]["path"]).write_bytes(b"changed")
                self.assertFalse(library.verify_procurement(pending["id"])["valid"])
                with self.assertRaisesRegex(ValueError, "procurement evidence integrity"):
                    export_library(root, provider="openalex")
            finally:
                library.close()

    def test_ris_import_preserves_original_and_unverified_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "existing.ris"
            source.write_bytes(b"TY  - JOUR\r\nTI  - Imported Study\r\nAU  - Ada Author\r\nDO  - 10.1000/example\r\nDA  - 2024-03-04\r\nJO  - Example Journal\r\nVL  - 12\r\nIS  - 2\r\nSP  - 101\r\nEP  - 109\r\nL1  - C:/missing/source.pdf\r\nER  - \r\n\r\nTY  - PAT\r\nAN  - prior:patent1\r\nTI  - Patent Record\r\nM2  - application_number: 14412875\r\nER  - \r\n")
            result = execute(Job("local", "import_ris", str(source)), root)
            self.assertEqual(result["status"], "complete")
            self.assertEqual(result["records"], 2)
            run = Path(result["run_dir"])
            records = [json.loads(line) for line in (run / "normalized_canonical.jsonl").read_text().splitlines()]
            self.assertEqual(records[0]["dates"], {"citation": "2024-03-04"})
            self.assertEqual(records[0]["citation"]["container_title"], "Example Journal")
            self.assertEqual(records[0]["extras"]["unverified_file_links"], ["C:/missing/source.pdf"])
            self.assertEqual(len(records[0]["attachments"]), 1)
            self.assertEqual(records[0]["attachments"][0]["role"], "sidecar")
            self.assertEqual(records[1]["identifiers"]["application_number"], "14412875")
            self.assertEqual(records[1]["stable_id"], "prior:patent1")
            self.assertIn("DA  - 2024-03-04", (run / "endnote" / "references.ris").read_text())
            self.assertIn("pages = {101--109}", (run / "endnote" / "references.bib").read_text())
            self.assertTrue(inspect_export(run)["valid"])

    def test_rendered_capture_preserves_html_and_screenshot(self):
        class FakeRenderer:
            def capture(self, url, allowed_hosts, *, render_pdf=False, content_selector=""):
                assert allowed_hosts == {"example.org"}
                assert render_pdf and content_selector == "main"
                return RenderedPage(b"<title>Rendered</title><nav>Boilerplate</nav><main><p>Dynamic content</p></main>", b"\x89PNGfake", url, b"%PDF-fake", b"<main><p>Dynamic content</p></main>", "main")

        with tempfile.TemporaryDirectory() as tmp:
            job = Job("web", "capture", "https://example.org/page", allow_hosts=("example.org",), render_js=True, render_pdf=True, content_selector="main")
            result = execute(job, Path(tmp), FakeTransport({}), renderer=FakeRenderer())
            self.assertEqual(result["status"], "complete")
            rec = json.loads((Path(result["run_dir"]) / "normalized_canonical.jsonl").read_text())
            self.assertEqual(rec["title"], "Rendered")
            self.assertEqual(rec["attachments"][1]["role"], "screenshot")
            self.assertTrue(Path(rec["attachments"][1]["path"]).exists())
            self.assertEqual(rec["attachments"][2]["role"], "rendered_pdf")
            self.assertEqual(Path(rec["attachments"][2]["path"]).read_bytes(), b"%PDF-fake")
            self.assertEqual(rec["extras"]["content_selector"], "main")
            markdown = Path(rec["extras"]["derived_markdown"]).read_text()
            self.assertIn("Dynamic content", markdown)
            self.assertNotIn("Boilerplate", markdown)
            self.assertTrue(inspect_export(Path(result["run_dir"]))["valid"])

    def test_rendered_options_require_rendered_web_capture(self):
        with self.assertRaises(ValueError):
            Job("web", "capture", "https://example.org/", allow_hosts=("example.org",), render_pdf=True)
        with self.assertRaises(ValueError):
            Job("web", "capture", "https://example.org/", allow_hosts=("example.org",), content_selector="main")

    def test_renderer_cannot_return_an_offhost_page(self):
        class OffhostRenderer:
            def capture(self, url, allowed_hosts, **kwargs):
                return RenderedPage(b"<p>Unexpected page</p>", b"", "https://other.org/")

        with tempfile.TemporaryDirectory() as tmp:
            job = Job("web", "capture", "https://example.org/", allow_hosts=("example.org",), render_js=True)
            result = execute(job, Path(tmp), FakeTransport({}), renderer=OffhostRenderer())
            self.assertEqual(result["status"], "failed")
            self.assertIn("outside approved HTTPS hosts", result["error"])

    def test_local_ingest_uses_same_run_and_citation_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "saved.html"
            source.write_text("<title>Saved source</title><p>Offline evidence</p>", encoding="utf-8")
            job = Job("local", "ingest", str(source))
            self.assertEqual(plan(job), [])
            result = execute(job, root)
            self.assertEqual(result["status"], "complete")
            run = Path(result["run_dir"])
            self.assertTrue((run / "endnote" / "references.ris").exists())
            rec = json.loads((run / "normalized_canonical.jsonl").read_text())
            self.assertEqual(rec["provider"], "local")
            self.assertIn("Offline evidence", Path(rec["extras"]["derived_markdown"]).read_text())
            self.assertTrue(inspect_export(run)["valid"])

    def test_openalex_run_keeps_versions_and_sidecars(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = Job("openalex", "lookup", "W123")
            url = plan(job)[0].url
            item = {"id": "https://openalex.org/W123", "title": "A test paper", "ids": {"openalex": "https://openalex.org/W123", "doi": "https://doi.org/10.1000/example"}, "doi": "https://doi.org/10.1000/example", "authorships": [{"author": {"display_name": "Ada Writer"}}], "publication_date": "2025-02-03", "abstract_inverted_index": {"An": [0], "abstract": [1]}, "referenced_works": ["https://openalex.org/W456"], "primary_location": {"source": {"display_name": "Journal of Examples"}}, "biblio": {"volume": "8", "issue": "3", "first_page": "12", "last_page": "18"}, "custom": 7}
            first = execute(job, root, FakeTransport({url: item}))
            second = execute(job, root, FakeTransport({url: item}))
            self.assertEqual(first["status"], "complete")
            self.assertEqual(second["status"], "complete")
            self.assertNotEqual(first["run_id"], second["run_id"])
            run = Path(first["run_dir"])
            manifest = json.loads((run / "manifest.json").read_text())
            self.assertEqual(manifest["record_count"], 1)
            self.assertEqual(manifest["relationship_count"], 0)
            for artifact in manifest["artifacts"]:
                self.assertEqual(digest((run / artifact["path"]).read_bytes()), artifact["sha256"])
            rec = json.loads((run / "normalized_canonical.jsonl").read_text().splitlines()[0])
            self.assertEqual(rec["extras"]["custom"], 7)
            self.assertEqual(rec["dates"]["publication"], "2025-02-03")
            self.assertEqual(rec["abstract"], "An abstract")
            self.assertEqual(rec["identifiers"]["doi"], "10.1000/example")
            self.assertEqual(rec["source_url"], "https://doi.org/10.1000/example")
            self.assertEqual(rec["retrieval_url"], url)
            self.assertEqual(rec["citation"], {"container_title": "Journal of Examples", "volume": "8", "issue": "3", "start_page": "12", "end_page": "18"})
            self.assertTrue(Path(rec["attachments"][0]["path"]).exists())
            self.assertIn("TY  - JOUR", (run / "endnote" / "references.ris").read_text())
            lib = Library(root)
            self.assertEqual(len(lib.search("test paper")), 2)
            self.assertEqual(len(lib.search("Ada Writer")), 2)
            self.assertEqual(len(lib.search("10.1000/example")), 2)
            lib.close()

    def test_openalex_network_expansion_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = Job("openalex", "lookup", "W123", citation_depth=1, max_results=1)
            url = plan(job)[0].url
            citing_url = "https://api.openalex.org/works?filter=cites%3AW123&per-page=1"
            responses = {
                url: {"id": "https://openalex.org/W123", "title": "Root", "referenced_works": ["https://openalex.org/W456", "https://openalex.org/W789"]},
                "https://api.openalex.org/works/W456": {"id": "https://openalex.org/W456", "title": "Cited"},
                citing_url: {"results": [{"id": "https://openalex.org/W999", "title": "Citing"}]},
            }
            fake = FakeTransport(responses)
            result = execute(job, Path(tmp), fake)
            self.assertEqual(result["status"], "complete")
            self.assertEqual(len(fake.requests), 3)
            manifest = json.loads((Path(result["run_dir"]) / "manifest.json").read_text())
            self.assertEqual(manifest["record_count"], 3)
            self.assertEqual(manifest["relationship_count"], 2)

    def test_uspto_number_is_not_an_author(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = Job("uspto", "application", "14412875")
            url = plan(job)[0].url
            payload = {"patentFileWrapperDataBag": [{"applicationNumberText": "14412875", "applicationMetaData": {"inventionTitle": "Test mechanism", "filingDate": "2024-01-01"}, "inventorBag": [{"inventorNameText": "Grace Inventor"}]}]}
            result = execute(job, Path(tmp), FakeTransport({url: payload}))
            self.assertEqual(result["status"], "complete")
            citation = (Path(result["run_dir"]) / "endnote" / "references.ris").read_text()
            self.assertIn("AU  - Grace Inventor", citation)
            self.assertIn("M2  - application_number: 14412875", citation)
            self.assertNotIn("AU  - 14412875", citation)

    def test_web_capture_retains_original_and_derived_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = Job("web", "capture", "https://example.org/page", allow_hosts=("example.org",))
            result = execute(job, Path(tmp), FakeTransport({job.value: b"<html><title>Source</title><p>Useful text</p><script>ignore</script></html>"}))
            self.assertEqual(result["status"], "complete")
            rec = json.loads((Path(result["run_dir"]) / "normalized_canonical.jsonl").read_text())
            self.assertIn("Useful text", Path(rec["extras"]["derived_markdown"]).read_text())
            self.assertNotIn("ignore", Path(rec["extras"]["derived_markdown"]).read_text())
            self.assertEqual(rec["access_status"], "acquired")
            run = Path(result["run_dir"])
            normalized = normalize_export(run)
            self.assertGreater(normalized["derived_files"], 0)
            report = write_web_reports(run)
            self.assertEqual(report["urls"], 1)
            self.assertTrue(inspect_export(run)["valid"])
            Path(rec["raw_path"]).write_bytes(b"tampered")
            self.assertFalse(inspect_export(run)["valid"])
            with self.assertRaisesRegex(ValueError, "raw artifact is missing or changed"):
                normalize_export(run)
            with self.assertRaisesRegex(ValueError, "raw artifact is missing or changed"):
                write_web_reports(run)

    def test_web_mirror_stays_on_allowlisted_host_and_page_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = Job("web", "mirror", "https://example.org/", max_results=2, allow_hosts=("example.org",), max_depth=2)
            fake = FakeTransport({
                "https://example.org/": b'<title>Root</title><a href="/one">One</a><a href="/two">Two</a><a href="https://offhost.org/private">Offhost</a>',
                "https://example.org/one": b'<title>One</title><p>Second page</p>',
            })
            result = execute(job, Path(tmp), fake)
            self.assertEqual(result["status"], "complete")
            self.assertEqual(len(fake.requests), 2)
            self.assertEqual(result["records"], 2)
            events = (Path(result["run_dir"]) / "acquisition.jsonl").read_text()
            self.assertIn("discovered_offhost", events)
            self.assertNotIn("offhost.org/private\"", str([x.url for x in fake.requests]))

    def test_unallowed_pdf_is_logged_not_fetched(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = Job("openalex", "lookup", "W123", download_files=True)
            url = plan(job)[0].url
            item = {"id": "https://openalex.org/W123", "title": "Paper", "best_oa_location": {"pdf_url": "https://files.example.org/paper.pdf"}}
            fake = FakeTransport({url: item})
            result = execute(job, Path(tmp), fake)
            self.assertEqual(result["status"], "partial")
            self.assertEqual(len(fake.requests), 1)
            rec = json.loads((Path(result["run_dir"]) / "normalized_canonical.jsonl").read_text())
            self.assertIn("requires explicit allowed host", rec["diagnostics"][0])
            lib = Library(Path(tmp))
            self.assertEqual(lib.list_procurement()[0]["status"], "needs_host_approval")
            lib.close()

    def test_partial_run_can_resume_with_same_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = Job("openalex", "lookup", "W123", download_files=True, allow_hosts=("files.example.org",))
            url = plan(job)[0].url
            pdf = "https://files.example.org/paper.pdf"
            item = {"id": "https://openalex.org/W123", "title": "Paper", "best_oa_location": {"pdf_url": pdf}}
            first = execute(job, root, FakeTransport({url: item, pdf: RuntimeError("temporary failure")}))
            self.assertEqual(first["status"], "partial")
            second = execute(job, root, FakeTransport({url: item, pdf: b"%PDF-1.7"}), resume_run_id=first["run_id"])
            self.assertEqual(second["status"], "complete")
            self.assertEqual(first["run_id"], second["run_id"])
            latest = root / "out" / "openalex" / "references" / "latest.txt"
            self.assertEqual(latest.read_text().strip(), first["run_id"])
            library = Library(root)
            try:
                request_id = library.list_procurement()[0]["id"]
                verified = library.verify_procurement(request_id)
                self.assertTrue(verified["valid"])
                self.assertEqual(verified["evidence_origin"], "provider_download")
                manifest = Path(second["run_dir"]) / "manifest.json"
                manifest.write_text("broken JSON")
                self.assertFalse(library.verify_procurement(request_id)["valid"])
            finally:
                library.close()


if __name__ == "__main__":
    unittest.main()
