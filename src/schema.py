"""Event record normalization and schema validation."""

from __future__ import annotations

from datetime import date
from typing import Any


REQUIRED_EVENT_FIELDS = (
    "event_id",
    "event_type",
    "subject",
    "object",
    "time",
    "trigger",
    "evidence_span",
    "source_doc_id",
)

STREAM_METADATA_FIELDS = (
    "record_id",
    "stream_record_id",
    "base_event_id",
    "gold_group_id",
    "arrival_index",
    "perturbation_type",
    "expected_operator",
    "source_doc_id",
    "source_text",
    "temporal_shuffle",
)


def normalize_event_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return a flat event record from either a sample or controlled stream row."""
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    nested_event = record.get("event")
    if nested_event is not None:
        if not isinstance(nested_event, dict):
            normalized: dict[str, Any] = {}
        else:
            normalized = dict(nested_event)
        for field in STREAM_METADATA_FIELDS:
            if field in record and field not in normalized:
                normalized[field] = record[field]
        return normalized

    return dict(record)


def validate_event_schema(record: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return False, ["record must be a dict"]
    if "event" in record and not isinstance(record.get("event"), dict):
        return False, ["event must be a dict when present"]

    try:
        normalized = normalize_event_record(record)
    except TypeError as exc:
        return False, [str(exc)]

    for field in REQUIRED_EVENT_FIELDS:
        value = normalized.get(field)
        if value is None:
            errors.append(f"missing required field: {field}")
        elif isinstance(value, str) and value.strip() == "":
            errors.append(f"empty required field: {field}")

    time_value = normalized.get("time")
    if isinstance(time_value, str) and time_value.strip():
        try:
            date.fromisoformat(time_value)
        except ValueError:
            errors.append(f"invalid ISO date field: time={time_value!r}")
    elif time_value is not None:
        errors.append("time must be an ISO date string")

    return not errors, errors

