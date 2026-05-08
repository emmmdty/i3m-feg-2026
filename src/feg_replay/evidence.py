"""Exact evidence-span checks."""

from __future__ import annotations

from typing import Any

from .schema import event_data


def has_evidence_match(record: dict[str, Any]) -> bool:
    """Return true when the evidence span occurs exactly in the source text."""
    data = event_data(record)
    evidence_span = data.get("evidence_span")
    source_text = data.get("source_text")
    if not isinstance(evidence_span, str) or not evidence_span.strip():
        return False
    if not isinstance(source_text, str) or not source_text:
        return False
    return evidence_span in source_text


def whitespace_normalized_evidence_match(record: dict[str, Any]) -> bool:
    """Optional diagnostic helper; it is not used by the main experiments."""
    data = event_data(record)
    evidence_span = data.get("evidence_span")
    source_text = data.get("source_text")
    if not isinstance(evidence_span, str) or not isinstance(source_text, str):
        return False
    compact_span = " ".join(evidence_span.split())
    compact_text = " ".join(source_text.split())
    return bool(compact_span) and compact_span in compact_text
