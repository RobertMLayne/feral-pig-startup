"""Offline RIS intake. Imported file links remain unverified pointers."""
from __future__ import annotations

from dataclasses import dataclass
import re

from .model import Reference, stable_id


TAG = re.compile(r"^([A-Z][A-Z0-9])  - ?(.*)$")


@dataclass(frozen=True)
class RisEntry:
    raw: bytes
    fields: dict[str, list[str]]


def parse_ris(data: bytes, max_records: int = 10000) -> list[RisEntry]:
    if not 1 <= max_records <= 10000:
        raise ValueError("RIS record limit must be 1..10000")
    entries: list[RisEntry] = []
    current: list[bytes] = []
    fields: dict[str, list[str]] = {}
    last_tag = ""

    def finish() -> None:
        nonlocal current, fields, last_tag
        if not current:
            return
        if not fields.get("TY"):
            raise ValueError("RIS record has no TY type")
        if len(entries) >= max_records:
            raise ValueError(f"RIS file exceeds the {max_records} record limit")
        entries.append(RisEntry(b"".join(current), fields))
        current, fields, last_tag = [], {}, ""

    for raw_line in data.splitlines(keepends=True):
        line = raw_line.decode("utf-8-sig" if not current else "utf-8", errors="replace").rstrip("\r\n")
        match = TAG.match(line)
        if match and match.group(1) == "TY":
            finish()
            current = [raw_line]
            fields = {"TY": [match.group(2).strip()]}
            last_tag = "TY"
            continue
        if not current:
            if line.strip():
                raise ValueError("RIS content appears before the first TY record")
            continue
        current.append(raw_line)
        if match:
            tag, value = match.group(1), match.group(2).strip()
            if tag == "ER":
                finish()
            else:
                fields.setdefault(tag, []).append(value)
                last_tag = tag
        elif line.strip() and last_tag:
            fields[last_tag][-1] += "\n" + line.strip()
    finish()
    if not entries:
        raise ValueError("RIS file contains no records")
    return entries


def normalize_ris(entry: RisEntry, raw_sha256: str, raw_path: str, retrieved_at: str, used_ids: set[str], source_file: str) -> Reference:
    fields = entry.fields

    def first(*tags: str) -> str:
        return next((item for tag in tags for item in fields.get(tag, []) if item), "")

    type_code = first("TY").upper()
    kind = {"JOUR": "article", "PAT": "patent", "CASE": "case", "ELEC": "web_page", "DATA": "dataset"}.get(type_code, "document")
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", first("DO"), flags=re.I).strip()
    accession = first("AN")
    identifier = accession or stable_id("local", "ris:" + (doi or raw_sha256))
    diagnostics: list[str] = []
    if identifier in used_ids:
        base = identifier + ":" + raw_sha256[:12]
        identifier = base
        serial = 2
        while identifier in used_ids:
            identifier = base + ":" + str(serial)
            serial += 1
        diagnostics.append("duplicate RIS accession in the same import; raw hash suffix added")
    used_ids.add(identifier)
    identifiers = {"doi": doi} if doi else {}
    for tag, expected in ((("M1", "patent_number"), ("M2", "application_number"), ("M3", "publication_number")) if kind == "patent" else ()):
        value = first(tag)
        if value:
            label, separator, number = value.partition(":")
            identifiers[expected] = number.strip() if separator and label.strip() == expected else value
    date = first("DA", "PY")
    citation = {}
    for label, tags in (
        ("container_title", ("JO", "JF", "T2")), ("volume", ("VL",)), ("issue", ("IS",)),
        ("start_page", ("SP",)), ("end_page", ("EP",)), ("publisher", ("PB",)), ("place", ("CY",)),
        (("issn" if kind == "article" else "isbn"), ("SN",)),
    ):
        value = first(*tags)
        if value:
            citation[label] = value
    source_paths = {"title": "TI|T1", "creators": "AU|A1", "dates.citation": "DA|PY", "source_url": "UR"}
    return Reference(
        provider="local", kind=kind, stable_id=identifier, title=first("TI", "T1") or "Untitled RIS record",
        source_url=first("UR"), retrieved_at=retrieved_at, raw_sha256=raw_sha256, raw_path=raw_path,
        creators=fields.get("AU", []) + fields.get("A1", []), identifiers=identifiers,
        dates={"citation": date} if date else {}, abstract=first("AB"),
        extras={"ris_fields": fields, "import_source": source_file, "unverified_file_links": fields.get("L1", [])},
        source_paths=source_paths, diagnostics=diagnostics, access_status="metadata_only", citation=citation,
    )
