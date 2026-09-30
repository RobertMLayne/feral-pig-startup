"""Explicit reviewer corrections layered over immutable source records."""
from __future__ import annotations

import calendar
import copy
import re


CITATION_FIELDS = {"container_title", "volume", "issue", "start_page", "end_page", "publisher", "place", "issn", "isbn"}
DATE_FIELDS = {"publication", "grant", "decision", "citation", "filing", "priority"}


def validate_correction(patch: dict, reason: str) -> dict:
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 1000:
        raise ValueError("metadata review requires a reason of 1..1000 characters")
    if not isinstance(patch, dict) or not patch:
        raise ValueError("metadata correction must be a nonempty JSON object")
    clean = {}
    for field, value in patch.items():
        if field == "creators":
            if not isinstance(value, list) or len(value) > 200 or any(
                not isinstance(item, str) or not item.strip() or len(item) > 1024 for item in value
            ):
                raise ValueError("creators must be a list of at most 200 nonempty names")
            clean[field] = [item.strip() for item in value]
            continue
        if field in {"title", "abstract"}:
            limit = 4096 if field == "title" else 100000
            if not isinstance(value, str) or len(value) > limit or (field == "title" and not value.strip()):
                raise ValueError(f"{field} must be text within its supported length")
            clean[field] = value.strip()
            continue
        parts = field.split(".") if isinstance(field, str) else []
        if len(parts) != 2 or not (
            parts[0] == "citation" and parts[1] in CITATION_FIELDS
            or parts[0] == "dates" and parts[1] in DATE_FIELDS
        ):
            raise ValueError("unsupported metadata correction field: " + str(field))
        if value is not None and (not isinstance(value, str) or not value.strip() or len(value) > 4096):
            raise ValueError(field + " must be nonempty text or null to remove the field")
        value = value.strip() if isinstance(value, str) else None
        if parts[0] == "dates" and value is not None:
            if not re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", value):
                raise ValueError(field + " must use YYYY, YYYY-MM, or YYYY-MM-DD")
            date = [int(part) for part in value.split("-")]
            if not 1 <= date[0] <= 9999 or len(date) > 1 and not 1 <= date[1] <= 12:
                raise ValueError(field + " is not a valid calendar date")
            if len(date) == 3 and not 1 <= date[2] <= calendar.monthrange(date[0], date[1])[1]:
                raise ValueError(field + " is not a valid calendar date")
        clean[field] = value
    return clean


def field_values(record: dict, fields) -> dict:
    values = {}
    for field in fields:
        parts = field.split(".")
        values[field] = copy.deepcopy(record.get(field) if len(parts) == 1 else (record.get(parts[0]) or {}).get(parts[1]))
    return values


def apply_corrections(record: dict, history: list[dict]) -> dict:
    effective = copy.deepcopy(record)
    reverted = {event["reverts_id"] for event in history if event["action"] == "revert"}
    active = [event for event in history if event["action"] == "correct" and event["id"] not in reverted]
    field_events = {}
    for event in active:
        for field, value in event["patch"].items():
            field_events[field] = event
            parts = field.split(".")
            if len(parts) == 1:
                effective[field] = copy.deepcopy(value)
            elif value is None:
                effective.setdefault(parts[0], {}).pop(parts[1], None)
            else:
                effective.setdefault(parts[0], {})[parts[1]] = value
    if history:
        changed_fields = sorted(field for field, event in field_events.items() if event["base_raw_sha256"] != record["raw_sha256"])
        effective.setdefault("extras", {})["reviewed_metadata"] = {
            "active_correction_ids": [event["id"] for event in active],
            "field_correction_ids": {field: event["id"] for field, event in field_events.items()},
            "source_changed_since_review": bool(changed_fields),
            "source_changed_fields": changed_fields,
        }
    return effective
