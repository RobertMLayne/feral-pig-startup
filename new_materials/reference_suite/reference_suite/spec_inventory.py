"""Offline, bounded JSON OpenAPI/Swagger bundles and verified endpoint diffs.

Only relative JSON files contained in the selected specification's directory and
JSON Pointer fragments are resolved. Remote refs, anchors, missing refs, and
recursive refs are retained and labelled; no endpoint or ref is ever requested.
This is an inventory, not an OpenAPI conformance validator or breaking-change
classifier. Snapshots contain the original bytes, provenance, and hash manifest.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote, urlsplit
import uuid

from .model import digest, now


METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
FORMAT_VERSION = 1


@dataclass(frozen=True)
class SpecLimits:
    max_file_bytes: int = 10 * 1024 * 1024
    max_total_bytes: int = 25 * 1024 * 1024
    max_files: int = 32
    max_operations: int = 10000
    max_ref_depth: int = 32
    max_nodes: int = 200000
    max_document_depth: int = 64

    def __post_init__(self) -> None:
        ceilings = (100 * 1024 * 1024, 250 * 1024 * 1024, 256, 100000, 64, 1000000, 128)
        for (name, value), ceiling in zip(asdict(self).items(), ceilings):
            if type(value) is not int or not 1 <= value <= ceiling:
                raise ValueError(f"{name} must be an integer from 1 to {ceiling}")


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _parse(data: bytes, limits: SpecLimits) -> object:
    def pairs(items: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def bad_constant(value: str) -> None:
        raise ValueError(f"invalid JSON constant: {value}")

    try:
        value = json.loads(data.decode("utf-8-sig"), object_pairs_hook=pairs, parse_constant=bad_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("specification must be bounded UTF-8 JSON") from exc
    stack = [(value, 0)]
    nodes = 0
    while stack:
        node, depth = stack.pop()
        nodes += 1
        if nodes > limits.max_nodes or depth > limits.max_document_depth:
            raise ValueError("JSON document exceeds node or nesting limit")
        children = node.values() if isinstance(node, dict) else node if isinstance(node, list) else ()
        stack.extend((child, depth + 1) for child in children)
    return value


def _read(path: Path, limit: int) -> bytes:
    if not path.is_file():
        raise ValueError(f"JSON file does not exist: {path}")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"JSON file exceeds {limit} byte limit: {path.name}")
    return data


def _pointer_part(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


class _Bundle:
    def __init__(self, source: Path, limits: SpecLimits):
        self.source = source.expanduser().resolve()
        self.base = self.source.parent
        self.limits = limits
        self.documents: dict[Path, tuple[bytes, object]] = {}
        self.issues: dict[tuple[str, str, str, str], dict] = {}
        self.total_bytes = 0
        self.resolved_nodes = 0
        self.load(self.source)

    def load(self, path: Path) -> object:
        if path not in self.documents:
            if len(self.documents) >= self.limits.max_files:
                raise ValueError("specification bundle exceeds file count limit")
            if path.suffix.lower() != ".json":
                raise ValueError("only local JSON specifications and JSON refs are supported")
            data = _read(path, self.limits.max_file_bytes)
            if self.total_bytes + len(data) > self.limits.max_total_bytes:
                raise ValueError("specification bundle exceeds total byte limit")
            document = _parse(data, self.limits)
            self.documents[path] = (data, document)
            self.total_bytes += len(data)
        return self.documents[path][1]

    def issue(self, path: Path, pointer: str, ref: object, reason: str) -> None:
        item = {"document": path.relative_to(self.base).as_posix(), "pointer": pointer,
                "ref": ref, "reason": reason}
        self.issues[(item["document"], pointer, str(ref), reason)] = item

    def target(self, ref: object, current: Path, pointer: str) -> tuple[Path, str, object] | None:
        reason = "invalid_ref"
        if isinstance(ref, str):
            try:
                parsed = urlsplit(ref)
                local = unquote(parsed.path)
                fragment = unquote(parsed.fragment)
                if parsed.scheme or parsed.netloc or local.startswith(("/", "\\")):
                    reason = "external_ref"
                elif parsed.query or "\\" in local or ":" in local or "\0" in local:
                    reason = "unsupported_local_ref"
                elif fragment and not fragment.startswith("/"):
                    reason = "unsupported_anchor"
                else:
                    candidate = (current.parent / local).resolve() if local else current
                    if not candidate.is_relative_to(self.base):
                        reason = "outside_bundle"
                    elif candidate.suffix.lower() != ".json":
                        reason = "unsupported_file_type"
                    elif not candidate.is_file():
                        reason = "missing_local_file"
                    else:
                        value = self.load(candidate)
                        try:
                            for segment in fragment.split("/")[1:] if fragment else ():
                                if re.search(r"~(?![01])", segment):
                                    raise KeyError(segment)
                                key = segment.replace("~1", "/").replace("~0", "~")
                                if isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", key):
                                    value = value[int(key)]
                                elif isinstance(value, dict):
                                    value = value[key]
                                else:
                                    raise KeyError(key)
                            return candidate, fragment, value
                        except (KeyError, IndexError):
                            reason = "missing_pointer"
            except (OSError, UnicodeError) as exc:
                raise ValueError("could not read bounded local reference") from exc
        self.issue(current, pointer, ref, reason)
        return None

    def collect(self) -> None:
        """Capture local refs even when an unused component contains them."""
        visited: set[Path] = set()
        while pending := [path for path in self.documents if path not in visited]:
            for path in pending:
                visited.add(path)
                stack = [(self.documents[path][1], "")]
                while stack:
                    node, pointer = stack.pop()
                    if isinstance(node, dict):
                        if "$ref" in node:
                            self.target(node["$ref"], path, pointer)
                        stack.extend((value, pointer + "/" + _pointer_part(key)) for key, value in node.items())
                    elif isinstance(node, list):
                        stack.extend((value, pointer + "/" + str(i)) for i, value in enumerate(node))

    def resolve(self, value: object, path: Path, pointer: str = "", chain: tuple = ()) -> object:
        self.resolved_nodes += 1
        if self.resolved_nodes > self.limits.max_nodes:
            raise ValueError("resolved specification exceeds node expansion limit")
        if isinstance(value, dict):
            if "$ref" in value:
                target = self.target(value["$ref"], path, pointer)
                if target:
                    ref_path, fragment, referenced = target
                    key = (ref_path, fragment)
                    if key in chain or len(chain) >= self.limits.max_ref_depth:
                        self.issue(path, pointer, value["$ref"], "recursive_ref" if key in chain else "ref_depth_limit")
                    else:
                        resolved = self.resolve(referenced, ref_path, fragment, chain + (key,))
                        # Keep sibling content visible for inventory, without claiming
                        # to implement the version-specific validation semantics.
                        siblings = {k: self.resolve(v, path, pointer + "/" + _pointer_part(k), chain)
                                    for k, v in value.items() if k != "$ref"}
                        if isinstance(resolved, dict):
                            return {**resolved, **siblings}
                        return {"$resolved": resolved, **siblings} if siblings else resolved
                return {key: self.resolve(child, path, pointer + "/" + _pointer_part(key), chain)
                        for key, child in value.items()}
            return {key: self.resolve(child, path, pointer + "/" + _pointer_part(key), chain)
                    for key, child in value.items()}
        if isinstance(value, list):
            return [self.resolve(child, path, pointer + "/" + str(i), chain) for i, child in enumerate(value)]
        return value


def _parameters(inherited: object, own: object) -> list:
    if not isinstance(inherited, list) or not isinstance(own, list):
        raise ValueError("endpoint parameters must be arrays")
    merged: dict[tuple, dict] = {}
    for parameter in inherited + own:
        if not isinstance(parameter, dict):
            raise ValueError("endpoint parameter must be an object")
        identity = (parameter.get("in"), parameter.get("name"))
        if identity == (None, None):
            identity = ("$ref", json.dumps(parameter, sort_keys=True))
        try:
            merged[identity] = parameter
        except TypeError as exc:
            raise ValueError("parameter name and location must be strings") from exc
    return sorted(merged.values(), key=lambda item: (str(item.get("in", "")), str(item.get("name", "")), str(item.get("$ref", ""))))


def _inventory(bundle: _Bundle) -> dict:
    document = bundle.documents[bundle.source][1]
    if not isinstance(document, dict):
        raise ValueError("specification root must be an object")
    if "openapi" in document and "swagger" in document:
        raise ValueError("specification cannot declare both openapi and swagger")
    version = document.get("openapi", document.get("swagger", ""))
    valid_version = (isinstance(version, str) and
                     (bool(re.fullmatch(r"3\.[0-9]+\.[0-9]+(?:[-+].*)?", version)) if "openapi" in document
                      else document.get("swagger") == "2.0"))
    if not valid_version:
        raise ValueError("expected an OpenAPI 3.x or Swagger 2.0 JSON specification")
    if not isinstance(document.get("components", {}), dict) or not isinstance(document.get("info", {}), dict):
        raise ValueError("specification components and info must be objects")
    paths = document.get("paths", {})
    if not isinstance(paths, dict):
        raise ValueError("specification paths must be an object")
    root = bundle.source
    endpoints = []
    for path, raw_item in sorted(paths.items()):
        if path.startswith("x-"):
            continue
        if not path.startswith("/") or not isinstance(raw_item, dict):
            raise ValueError("each endpoint path must start with / and contain an object")
        item = bundle.resolve(raw_item, root, "/paths/" + _pointer_part(path))
        if not isinstance(item, dict):
            raise ValueError("resolved path item must be an object")
        for method in sorted(METHODS.intersection(item)):
            operation = item[method]
            if not isinstance(operation, dict):
                raise ValueError("endpoint operation must be an object")
            if len(endpoints) >= bundle.limits.max_operations:
                raise ValueError("specification exceeds operation limit")
            parameters = _parameters(item.get("parameters", []), operation.get("parameters", []))
            effective = dict(operation)
            effective["parameters"] = parameters
            effective["security"] = operation.get("security", bundle.resolve(document.get("security", []), root, "/security"))
            schemes = document.get("securityDefinitions", {}) if version == "2.0" else document.get("components", {}).get("securitySchemes", {})
            if not isinstance(effective["security"], list) or not isinstance(schemes, dict):
                raise ValueError("security must be an array and security schemes an object")
            names = {name for requirement in effective["security"] if isinstance(requirement, dict) for name in requirement}
            effective["security_schemes"] = bundle.resolve({name: schemes.get(name, {"$missing_security_scheme": name}) for name in sorted(names)}, root)
            if version == "2.0":
                for key in ("host", "basePath", "schemes", "consumes", "produces"):
                    effective[key] = operation.get(key, document.get(key))
            else:
                effective["servers"] = operation.get("servers", item.get("servers", bundle.resolve(document.get("servers", []), root, "/servers")))
            effective["path_summary"] = item.get("summary", "")
            effective["path_description"] = item.get("description", "")
            endpoint = {"id": method.upper() + " " + path, "method": method.upper(), "path": path,
                        "summary": operation.get("summary", ""), "operation_id": operation.get("operationId", ""),
                        "parameters": parameters, "effective_operation": effective,
                        "sha256": digest(_json_bytes(effective))}
            endpoints.append(endpoint)
    return {"format_version": FORMAT_VERSION, "specification_version": version,
            "info": document.get("info", {}), "endpoint_count": len(endpoints), "endpoints": endpoints,
            "unresolved_refs": sorted(bundle.issues.values(), key=lambda issue: (issue["document"], issue["pointer"], str(issue["ref"]), issue["reason"])),
            "scope": "Declared HTTP path operations; excludes callback and webhook operations. No network requests.",
            "ref_semantics": "Local JSON Pointer expansion with sibling overlay for inventory; not a schema validator."}


def import_spec(source: Path, store: Path, *, label: str = "", limits: SpecLimits | None = None) -> dict:
    """Import a selected JSON spec into ``store/spec_snapshots/<id>``.

    Return the inventory plus snapshot_id, snapshot_path, captured_at,
    source_path, source_sha256, documents, and applied limits. Each document has
    source_relative_path, raw_path (snapshot-relative), sha256, and bytes.
    Validation completes before a new snapshot directory is created.
    """
    limits = limits or SpecLimits()
    if not isinstance(label, str) or len(label) > 128 or any(ord(char) < 32 for char in label):
        raise ValueError("snapshot label must be at most 128 printable characters")
    bundle = _Bundle(Path(source), limits)
    bundle.collect()
    try:
        report = _inventory(bundle)
    except RecursionError as exc:
        raise ValueError("resolved specification exceeds safe nesting limit") from exc
    snapshot_id = uuid.uuid4().hex
    directory = Path(store).expanduser().resolve() / "spec_snapshots" / snapshot_id
    documents = [{"source_relative_path": path.relative_to(bundle.base).as_posix(),
                  "raw_path": f"raw/{index:03d}_{digest(data)[:16]}.json", "sha256": digest(data), "bytes": len(data)}
                 for index, (path, (data, _)) in enumerate(sorted(bundle.documents.items()))]
    report.update(snapshot_id=snapshot_id, label=label, captured_at=now(), source_path=str(bundle.source),
                  source_sha256=digest(bundle.documents[bundle.source][0]), documents=documents, limits=asdict(limits))
    inventory_bytes = _json_bytes(report)
    # Derived expansion is bounded independently of raw input bytes.
    if len(inventory_bytes) > limits.max_total_bytes:
        raise ValueError("derived inventory exceeds total byte limit")
    _parse(inventory_bytes, limits)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "raw").mkdir()
    for doc, (_, (data, _)) in zip(documents, sorted(bundle.documents.items())):
        (directory / doc["raw_path"]).write_bytes(data)
    (directory / "inventory.json").write_bytes(inventory_bytes)
    (directory / "manifest.json").write_bytes(_json_bytes({"format_version": FORMAT_VERSION,
                                                          "inventory_sha256": digest(inventory_bytes),
                                                          "documents": documents}))
    return {**report, "snapshot_path": str(directory)}


def _snapshot_file(directory: Path, relative: str) -> Path:
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        raise ValueError("unsafe snapshot file path")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or not parts.parts:
        raise ValueError("unsafe snapshot file path")
    current = directory
    for part in parts.parts:
        current = current / part
        if current.is_symlink() or current.is_junction():
            raise ValueError("snapshot files cannot use links or junctions")
    if not current.resolve().is_relative_to(directory):
        raise ValueError("snapshot file escapes its directory")
    return current


def load_snapshot(snapshot: Path, *, limits: SpecLimits | None = None) -> dict:
    """Read a snapshot directory or inventory.json; verify manifest and raw hashes."""
    limits = limits or SpecLimits()
    directory = Path(snapshot).expanduser().resolve()
    if directory.is_file():
        if directory.name != "inventory.json":
            raise ValueError("select a snapshot directory or inventory.json")
        directory = directory.parent
    manifest = _parse(_read(_snapshot_file(directory, "manifest.json"), limits.max_total_bytes), limits)
    data = _read(_snapshot_file(directory, "inventory.json"), limits.max_total_bytes)
    if not isinstance(manifest, dict) or manifest.get("format_version") != FORMAT_VERSION or digest(data) != manifest.get("inventory_sha256"):
        raise ValueError("snapshot inventory integrity check failed")
    report = _parse(data, limits)
    if not isinstance(report, dict) or report.get("format_version") != FORMAT_VERSION:
        raise ValueError("unsupported snapshot inventory format")
    documents = report.get("documents")
    if not isinstance(documents, list) or not documents or len(documents) > limits.max_files or documents != manifest.get("documents"):
        raise ValueError("snapshot document manifest mismatch or file count limit")
    total = 0
    for doc in documents:
        if not isinstance(doc, dict):
            raise ValueError("invalid snapshot document entry")
        raw = _read(_snapshot_file(directory, doc.get("raw_path")), limits.max_file_bytes)
        total += len(raw)
        if total > limits.max_total_bytes or len(raw) != doc.get("bytes") or digest(raw) != doc.get("sha256"):
            raise ValueError("snapshot raw file integrity check failed or total byte limit")
    endpoints = report.get("endpoints")
    if not isinstance(endpoints, list) or len(endpoints) > limits.max_operations or len(endpoints) != report.get("endpoint_count"):
        raise ValueError("snapshot endpoint count mismatch or operation limit")
    seen = set()
    for endpoint in endpoints:
        if not isinstance(endpoint, dict) or not isinstance(endpoint.get("id"), str) or endpoint["id"] in seen:
            raise ValueError("invalid or duplicate snapshot endpoint")
        seen.add(endpoint["id"])
        if digest(_json_bytes(endpoint.get("effective_operation"))) != endpoint.get("sha256"):
            raise ValueError("snapshot endpoint fingerprint mismatch")
    return {**report, "snapshot_path": str(directory)}


def diff_snapshots(before: Path, after: Path, *, limits: SpecLimits | None = None) -> dict:
    """Verify both snapshots and return added/removed endpoints and changed details.

    Changed entries include id, method, path, changed_fields, before, and after.
    Fields are compared on the expanded effective_operation, so changes to a
    referenced parameter/schema or inherited server/security settings are seen.
    Change detection does not claim that a change is compatible or breaking.
    """
    left, right = load_snapshot(before, limits=limits), load_snapshot(after, limits=limits)
    old = {endpoint["id"]: endpoint for endpoint in left["endpoints"]}
    new = {endpoint["id"]: endpoint for endpoint in right["endpoints"]}
    changed = []
    for key in sorted(old.keys() & new.keys()):
        if old[key]["sha256"] != new[key]["sha256"]:
            a, b = old[key]["effective_operation"], new[key]["effective_operation"]
            fields = sorted(field for field in a.keys() | b.keys() if field not in a or field not in b or a[field] != b[field])
            changed.append({"id": key, "method": new[key]["method"], "path": new[key]["path"],
                            "changed_fields": fields, "before": old[key], "after": new[key]})
    added = [new[key] for key in sorted(new.keys() - old.keys())]
    removed = [old[key] for key in sorted(old.keys() - new.keys())]
    return {"format_version": FORMAT_VERSION, "before_snapshot_id": left["snapshot_id"],
            "after_snapshot_id": right["snapshot_id"], "compared_at": now(),
            "counts": {"added": len(added), "removed": len(removed), "changed": len(changed),
                       "unchanged": len(old.keys() & new.keys()) - len(changed)},
            "added": added, "removed": removed, "changed": changed,
            "metadata_changed": left["info"] != right["info"] or left["specification_version"] != right["specification_version"],
            "unresolved_refs": {"before": left["unresolved_refs"], "after": right["unresolved_refs"]}}
