"""Evidence span matching helpers."""

from __future__ import annotations

from typing import Any

from .schema import normalize_event_record


def has_evidence_match(record: dict[str, Any]) -> bool:
    normalized = normalize_event_record(record)
    evidence_span = normalized.get("evidence_span")
    source_text = normalized.get("source_text")
    if not isinstance(evidence_span, str) or evidence_span.strip() == "":
        return False
    if not isinstance(source_text, str) or source_text == "":
        return False
    return evidence_span in source_text


def evidence_coverage(record: dict[str, Any]) -> float:
    return 1.0 if has_evidence_match(record) else 0.0

