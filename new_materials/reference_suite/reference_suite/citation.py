"""Deterministic citation exports with a lossless sidecar link."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .model import Reference, digest, json_bytes


RIS_TYPES = {"article": "JOUR", "patent": "PAT", "case": "CASE", "decision": "CASE", "web_page": "ELEC", "dataset": "DATA", "document": "GEN"}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def ris(records: list[Reference]) -> str:
    lines: list[str] = []
    for rec in records:
        lines += [f"TY  - {RIS_TYPES.get(rec.kind, 'GEN')}", f"TI  - {_clean(rec.title)}", f"AN  - {_clean(rec.stable_id)}"]
        for creator in rec.creators:
            lines.append(f"AU  - {_clean(creator)}")
        if rec.kind == "patent":
            for label, tag in (("patent_number", "M1"), ("application_number", "M2"), ("publication_number", "M3")):
                if rec.identifiers.get(label):
                    lines.append(f"{tag}  - {label}: {_clean(rec.identifiers[label])}")
        if rec.identifiers.get("doi"):
            lines.append(f"DO  - {_clean(rec.identifiers['doi'])}")
        for label, tag in (("container_title", "JO"), ("volume", "VL"), ("issue", "IS"), ("start_page", "SP"), ("end_page", "EP"), ("publisher", "PB"), ("place", "CY"), ("issn", "SN"), ("isbn", "SN")):
            if rec.citation.get(label):
                lines.append(f"{tag}  - {_clean(rec.citation[label])}")
        date = rec.dates.get("publication") or rec.dates.get("grant") or rec.dates.get("decision") or rec.dates.get("citation")
        if date:
            lines.append(f"PY  - {_clean(date[:4])}")
            lines.append(f"DA  - {_clean(date)}")
        if rec.source_url:
            lines.append(f"UR  - {_clean(rec.source_url)}")
        if rec.abstract:
            lines.append(f"AB  - {_clean(rec.abstract)}")
        for att in rec.attachments:
            if att.get("path"):
                lines.append(f"L1  - {_clean(att['path'])}")
            if att.get("role") == "sidecar" and att.get("sha256"):
                lines.append(f"N1  - Sidecar SHA256: {att['sha256']}")
        lines += ["ER  - ", ""]
    return "\n".join(lines)


def _bib(value: str) -> str:
    replacements = {"\\": "\\textbackslash{}", "{": "\\{", "}": "\\}", "\n": " "}
    return "".join(replacements.get(char, char) for char in str(value))


def bibtex(records: list[Reference]) -> str:
    types = {"article": "article", "patent": "misc", "decision": "misc", "web_page": "misc", "dataset": "misc"}
    chunks = []
    used_keys: set[str] = set()
    for rec in records:
        key = re.sub(r"[^A-Za-z0-9_-]", "_", rec.stable_id)[:80]
        if key in used_keys:
            base = key[:63] + "_" + digest(rec.stable_id.encode("utf-8"))[:16]
            key = base
            serial = 2
            while key in used_keys:
                key = base + "_" + str(serial)
                serial += 1
        used_keys.add(key)
        fields = {"title": rec.title, "url": rec.source_url, "note": "Stable ID: " + rec.stable_id}
        if rec.creators:
            fields["author"] = " and ".join(rec.creators)
        if rec.identifiers.get("doi"):
            fields["doi"] = rec.identifiers["doi"]
        if rec.citation.get("container_title"):
            fields["journal" if rec.kind == "article" else "booktitle"] = rec.citation["container_title"]
        for source, target in (("volume", "volume"), ("issue", "number"), ("publisher", "publisher"), ("place", "address"), ("issn", "issn"), ("isbn", "isbn")):
            if rec.citation.get(source):
                fields[target] = rec.citation[source]
        start_page, end_page = rec.citation.get("start_page"), rec.citation.get("end_page")
        if start_page or end_page:
            fields["pages"] = (start_page or "") + ("--" + end_page if start_page and end_page else (end_page or ""))
        date = rec.dates.get("publication") or rec.dates.get("grant") or rec.dates.get("decision") or rec.dates.get("citation")
        if date:
            fields["year"] = date[:4]
        if rec.abstract:
            fields["abstract"] = rec.abstract
        chunks.append("@" + types.get(rec.kind, "misc") + "{" + key + ",\n" + ",\n".join(f"  {name} = {{{_bib(val)}}}" for name, val in fields.items()) + "\n}")
    return "\n\n".join(chunks) + ("\n" if chunks else "")


def write_endnote_sidecars(run_dir: Path, records: list[Reference], raw_by_id: dict[str, dict]) -> None:
    folder = run_dir / "endnote" / "sidecars"
    folder.mkdir(parents=True, exist_ok=True)
    for rec in records:
        envelope = {
            "schema": "reference-suite.sidecar.v1",
            "schema_version": 1,
            "provider": rec.provider,
            "kind": rec.kind,
            "stable_id": rec.stable_id,
            "exported_at": rec.retrieved_at,
            "data": {"raw": raw_by_id.get(rec.stable_id), "normalized": rec.asdict(), "diagnostics": rec.diagnostics},
        }
        payload = json_bytes(envelope)
        name = digest(payload) + ".json"
        (folder / name).write_bytes(payload)
        rec.attachments.append({"path": str((folder / name).resolve()), "sha256": digest(payload), "role": "sidecar"})


def export(run_dir: Path, records: list[Reference], raw_by_id: dict[str, dict]) -> None:
    write_endnote_sidecars(run_dir, records, raw_by_id)
    target = run_dir / "endnote"
    target.mkdir(parents=True, exist_ok=True)
    (target / "references.ris").write_text(ris(records), encoding="utf-8")
    (target / "references.bib").write_text(bibtex(records), encoding="utf-8")


def validate_sidecars(records: list[Reference]) -> None:
    for rec in records:
        for att in rec.attachments:
            if att.get("role") == "sidecar":
                path = Path(att["path"])
                if digest(path.read_bytes()) != att["sha256"]:
                    raise ValueError(f"sidecar hash mismatch: {path}")
                envelope = json.loads(path.read_text(encoding="utf-8"))
                if envelope["stable_id"] != rec.stable_id:
                    raise ValueError(f"sidecar ID mismatch: {path}")


def endnote_type_table(template: Path, destination: Path, label: str = "Reference Suite", base_type: str = "Generic") -> None:
    """Adapt one empty Unused slot in an actual EndNote-exported RefTypes table."""
    tree = ET.parse(template)
    root = tree.getroot()
    if root.tag != "RefTypes":
        raise ValueError("template is not an EndNote RefTypes table")
    types = root.findall("RefType")
    slots = [x for x in types if x.attrib.get("name", "").startswith("Unused ")]
    if not slots:
        raise ValueError("template has no Unused reference type slot")
    source = next((x for x in types if x.get("name") == base_type), None)
    if source is None or source.find("Fields") is None:
        raise ValueError("base reference type has no field layout")
    fields = copy.deepcopy(source.find("Fields"))
    ids = [x.get("id") for x in fields.findall("Field")]
    if len(ids) > 51 or len(ids) != len(set(ids)):
        raise ValueError("base reference type exceeds field budget or has duplicate field IDs")
    previous = slots[0].find("Fields")
    if previous is not None:
        slots[0].remove(previous)
    slots[0].append(fields)
    slots[0].set("name", label)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tree.write(destination, encoding="utf-8", xml_declaration=True)
