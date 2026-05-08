"""Event-record normalization and schema validation."""

from __future__ import annotations

from dataclasses import dataclass
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
    "source_text",
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
    "negative_control_type",
    "expected_rejection",
)


@dataclass(frozen=True)
class NormalizedRecord:
    """Normalized record plus local validation state."""

    data: dict[str, Any]
    is_valid: bool
    errors: list[str]


def normalize_event_record(record: dict[str, Any]) -> NormalizedRecord:
    """Flatten a stream record while preserving metadata fields."""
    if not isinstance(record, dict):
        return NormalizedRecord({}, False, ["record must be an object"])

    nested_event = record.get("event")
    if "event" in record:
        if not isinstance(nested_event, dict):
            return NormalizedRecord({}, False, ["event must be an object"])
        normalized = dict(nested_event)
        for field in STREAM_METADATA_FIELDS:
            if field in record and field not in normalized:
                normalized[field] = record[field]
        return NormalizedRecord(normalized, True, [])

    return NormalizedRecord(dict(record), True, [])


def event_data(record: dict[str, Any]) -> dict[str, Any]:
    """Return normalized event data or an empty mapping for invalid wrappers."""
    return normalize_event_record(record).data


def validate_event_schema(record: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate required fields and date format."""
    normalized = normalize_event_record(record)
    if not normalized.is_valid:
        return False, normalized.errors

    errors: list[str] = []
    data = normalized.data
    for field in REQUIRED_EVENT_FIELDS:
        value = data.get(field)
        if value is None:
            errors.append(f"missing required field: {field}")
        elif isinstance(value, str) and value.strip() == "":
            errors.append(f"empty required field: {field}")

    time_value = data.get("time")
    if isinstance(time_value, str) and time_value.strip():
        try:
            date.fromisoformat(time_value)
        except ValueError:
            errors.append(f"invalid ISO date field: time={time_value!r}")
    elif time_value is not None:
        errors.append("time must be an ISO date string")

    return not errors, errors
