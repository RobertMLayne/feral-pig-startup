from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from reference_suite.model import digest
from reference_suite.spec_inventory import SpecLimits, diff_snapshots, import_spec, load_snapshot


class SpecInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "selected"
        self.source.mkdir()
        self.store = self.root / "library"

    def write(self, name, value):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def spec(self, paths=None):
        return {"openapi": "3.1.0", "info": {"title": "Selected API", "version": "1"}, "paths": paths or {}}

    def test_snapshot_preserves_original_bytes_and_verifies_every_raw_file(self):
        source = self.write("api.json", self.spec({"/items": {"get": {"summary": "List items"}}}))
        source.write_bytes(b"\xef\xbb\xbf" + source.read_bytes() + b"\n  ")
        original = source.read_bytes()
        report = import_spec(source, self.store, label="local API")
        snapshot = Path(report["snapshot_path"])
        self.assertEqual(report["source_sha256"], digest(original))
        self.assertEqual(report["label"], "local API")
        self.assertEqual((snapshot / report["documents"][0]["raw_path"]).read_bytes(), original)
        self.assertEqual(load_snapshot(snapshot / "inventory.json")["endpoints"][0]["id"], "GET /items")
        (snapshot / report["documents"][0]["raw_path"]).write_bytes(original + b" ")
        with self.assertRaisesRegex(ValueError, "integrity"):
            load_snapshot(snapshot)

    def test_diff_detects_added_removed_and_referenced_schema_changes(self):
        api = self.spec({"/items": {"get": {"summary": "Read", "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "models.json#/Item"}}}}}}},
                         "/old": {"delete": {}}})
        source = self.write("api.json", api)
        self.write("models.json", {"Item": {"type": "object", "properties": {"id": {"type": "integer"}}}})
        before = import_spec(source, self.store)
        self.write("models.json", {"Item": {"type": "object", "properties": {"id": {"type": "string"}}}})
        del api["paths"]["/old"]
        api["paths"]["/new"] = {"post": {"summary": "Create"}}
        self.write("api.json", api)
        after = import_spec(source, self.store)
        diff = diff_snapshots(Path(before["snapshot_path"]), Path(after["snapshot_path"]))
        self.assertEqual(diff["counts"], {"added": 1, "removed": 1, "changed": 1, "unchanged": 0})
        self.assertEqual(diff["changed"][0]["changed_fields"], ["responses"])
        self.assertEqual(diff["added"][0]["id"], "POST /new")
        self.assertEqual(diff["removed"][0]["id"], "DELETE /old")
        self.assertEqual(load_snapshot(Path(before["snapshot_path"]))["endpoint_count"], 2)

    def test_json_pointer_escaping_path_refs_and_parameter_overrides(self):
        api = self.spec({"/things/{id}": {"$ref": "parts/paths.json#/a~1b"}})
        source = self.write("api.json", api)
        self.write("parts/paths.json", {"a/b": {"parameters": [{"$ref": "../api.json#/components/parameters/ID"}],
                                                 "get": {"parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}]},
                                                 "post": {}}})
        api["components"] = {"parameters": {"ID": {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}}}
        self.write("api.json", api)
        report = import_spec(source, self.store)
        self.assertEqual(len(report["documents"]), 2)
        self.assertEqual(report["unresolved_refs"], [])
        self.assertEqual(report["endpoints"][0]["parameters"][0]["schema"]["type"], "integer")
        self.assertEqual(report["endpoints"][1]["parameters"][0]["schema"]["type"], "string")

    def test_remote_escaping_missing_and_recursive_refs_are_labelled_without_network(self):
        api = self.spec({"/items": {"get": {"responses": {"200": {"$ref": "https://example.org/api.json#/Response"},
                                                                  "201": {"$ref": "../private.json#/Response"},
                                                                  "202": {"$ref": "#/components/schemas/Cycle"},
                                                                  "203": {"$ref": "#/missing"}}}}})
        api["components"] = {"schemas": {"Cycle": {"type": "object", "properties": {"next": {"$ref": "#/components/schemas/Cycle"}}}}}
        source = self.write("api.json", api)
        (self.root / "private.json").write_text('{"Response":{"secret":"do not read"}}')
        with patch("urllib.request.urlopen", side_effect=AssertionError("network prohibited")), patch("socket.create_connection", side_effect=AssertionError("network prohibited")):
            report = import_spec(source, self.store)
        reasons = {issue["reason"] for issue in report["unresolved_refs"]}
        self.assertTrue({"external_ref", "outside_bundle", "recursive_ref", "missing_pointer"}.issubset(reasons))
        self.assertEqual(len(report["documents"]), 1)
        self.assertNotIn("do not read", json.dumps(report))

    def test_swagger_inherited_settings_are_included_and_diffed(self):
        api = {"swagger": "2.0", "info": {"title": "Legacy", "version": "1"}, "host": "api.example.org", "basePath": "/v1",
               "schemes": ["https"], "produces": ["application/json"], "security": [{"key": []}],
               "securityDefinitions": {"key": {"type": "apiKey", "name": "X-API-Key", "in": "header"}},
               "paths": {"/items": {"get": {}, "post": {"security": [], "produces": ["text/plain"]}}}}
        source = self.write("swagger.json", api)
        before = import_spec(source, self.store)
        api["securityDefinitions"]["key"]["name"] = "X-Updated-Key"
        self.write("swagger.json", api)
        after = import_spec(source, self.store)
        diff = diff_snapshots(Path(before["snapshot_path"]), Path(after["snapshot_path"]))
        self.assertEqual(diff["counts"]["changed"], 1)
        self.assertEqual(diff["counts"]["unchanged"], 1)
        self.assertEqual(diff["changed"][0]["changed_fields"], ["security_schemes"])
        self.assertEqual(after["endpoints"][1]["effective_operation"]["produces"], ["text/plain"])

    def test_formatting_and_unused_metadata_do_not_mark_endpoints_changed(self):
        api = self.spec({"/items": {"get": {"summary": "Read"}}})
        source = self.write("api.json", api)
        before = import_spec(source, self.store)
        api["info"]["version"] = "2"
        source.write_text(json.dumps(api, indent=4), encoding="utf-8")
        after = import_spec(source, self.store)
        result = diff_snapshots(Path(before["snapshot_path"]), Path(after["snapshot_path"]))
        self.assertEqual(result["counts"]["unchanged"], 1)
        self.assertTrue(result["metadata_changed"])

    def test_limits_and_invalid_json_fail_before_creating_snapshot(self):
        source = self.write("api.json", self.spec({"/a": {"get": {}, "post": {}}}))
        with self.assertRaisesRegex(ValueError, "operation limit"):
            import_spec(source, self.store, limits=SpecLimits(max_operations=1))
        with self.assertRaisesRegex(ValueError, "byte limit"):
            import_spec(source, self.store, limits=SpecLimits(max_file_bytes=10))
        source.write_text('{"openapi":"3.0.0","paths":{},"paths":{}}')
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            import_spec(source, self.store)
        self.assertFalse(self.store.exists())

    def test_referenced_file_count_and_total_bundle_bytes_are_bounded(self):
        api = self.spec({"/a": {"get": {"responses": {"200": {"$ref": "response.json"}}}}})
        source = self.write("api.json", api)
        other = self.write("response.json", {"description": "a" * 50})
        with self.assertRaisesRegex(ValueError, "file count"):
            import_spec(source, self.store, limits=SpecLimits(max_files=1))
        with self.assertRaisesRegex(ValueError, "total byte"):
            import_spec(source, self.store, limits=SpecLimits(max_total_bytes=source.stat().st_size + other.stat().st_size - 1))

    def test_declared_dialect_and_nested_objects_are_validated(self):
        for invalid in ({"openapi": "2.0", "paths": {}}, {"swagger": "3.1.0", "paths": {}},
                        {"openapi": "3.1.0", "components": [], "paths": {}}):
            with self.subTest(invalid=invalid):
                source = self.write("api.json", invalid)
                with self.assertRaises(ValueError):
                    import_spec(source, self.store)
        self.assertFalse(self.store.exists())

    def test_modified_inventory_and_snapshot_path_traversal_are_rejected(self):
        source = self.write("api.json", self.spec({"/a": {"get": {}}}))
        report = import_spec(source, self.store)
        directory = Path(report["snapshot_path"])
        inventory = directory / "inventory.json"
        original = inventory.read_bytes()
        inventory.write_bytes(original + b" ")
        with self.assertRaisesRegex(ValueError, "integrity"):
            load_snapshot(directory)
        bad = json.loads(original)
        bad["documents"][0]["raw_path"] = "../outside.json"
        data = json.dumps(bad).encode()
        inventory.write_bytes(data)
        manifest = json.loads((directory / "manifest.json").read_text())
        manifest["inventory_sha256"] = digest(data)
        manifest["documents"] = bad["documents"]
        (directory / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "unsafe snapshot"):
            load_snapshot(directory)


if __name__ == "__main__":
    unittest.main()
