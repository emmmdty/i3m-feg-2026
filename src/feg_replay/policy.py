"""Oracle and rule-based replay policies."""

from __future__ import annotations

from datetime import date
from typing import Any

from .graph import GraphStore
from .operators import ADD_EVENT, APPLIED_OPERATORS, MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT
from .schema import event_data


PERTURBATION_TO_OPERATOR = {
    "base": ADD_EVENT,
    "temporal_shuffle": ADD_EVENT,
    "duplicate": MERGE_EVENT,
    "update": UPDATE_SLOT,
    "conflict": MARK_CONFLICT,
}


def has_unsupported_replay_metadata(record: dict[str, Any]) -> bool:
    """Return true when controlled replay metadata names an unsupported decision."""
    event = event_data(record)
    expected = event.get("expected_operator")
    if isinstance(expected, str) and expected and expected not in APPLIED_OPERATORS:
        return True
    perturbation_type = event.get("perturbation_type")
    if isinstance(perturbation_type, str) and perturbation_type:
        return perturbation_type.lower() not in PERTURBATION_TO_OPERATOR
    return False


def predict_operator_oracle(record: dict[str, Any], graph: GraphStore) -> str | None:
    """Predict using controlled replay metadata."""
    event = event_data(record)
    if has_unsupported_replay_metadata(event):
        return None
    expected = event.get("expected_operator")
    if isinstance(expected, str) and expected in APPLIED_OPERATORS:
        return expected
    perturbation_type = str(event.get("perturbation_type", "")).lower()
    if perturbation_type:
        return PERTURBATION_TO_OPERATOR.get(perturbation_type)
    return predict_operator_rule_based(event, graph)


def predict_operator_rule_based(record: dict[str, Any], graph: GraphStore) -> str | None:
    """Predict from event fields and graph state only."""
    event = event_data(record)
    if has_unsupported_replay_metadata(event):
        return None
    target = find_matching_event(event, graph)
    if target is None:
        return ADD_EVENT
    if is_update(event, target):
        return UPDATE_SLOT
    if is_conflict(event, target):
        return MARK_CONFLICT
    if is_duplicate(event, target):
        return MERGE_EVENT
    return ADD_EVENT


def select_target_oracle(record: dict[str, Any], graph: GraphStore) -> str | None:
    """Resolve a target with direct controlled metadata when present."""
    event = event_data(record)
    base_event_id = event.get("base_event_id")
    if isinstance(base_event_id, str) and base_event_id in graph.event_nodes:
        return base_event_id
    target = find_matching_event(event, graph)
    if target is not None:
        return str(target.get("event_id"))
    return None


def select_target_rule_based(record: dict[str, Any], graph: GraphStore) -> str | None:
    """Resolve a target from event similarity only."""
    target = find_matching_event(event_data(record), graph)
    if target is None:
        return None
    return str(target.get("event_id"))


def find_matching_event(event: dict[str, Any], graph: GraphStore) -> dict[str, Any] | None:
    """Find the closest existing event by subject, type, and date."""
    same_subject_type: list[dict[str, Any]] = []
    for existing in graph.event_nodes.values():
        if event.get("subject") != existing.get("subject"):
            continue
        if event.get("event_type") != existing.get("event_type"):
            continue
        same_subject_type.append(existing)
        if times_close(event.get("time"), existing.get("time")):
            if event.get("amount") == existing.get("amount") and event.get("status") == existing.get("status"):
                return existing

    for existing in same_subject_type:
        if times_close(event.get("time"), existing.get("time")):
            return existing
    return same_subject_type[0] if same_subject_type else None


def is_duplicate(event: dict[str, Any], existing: dict[str, Any]) -> bool:
    return (
        event.get("subject") == existing.get("subject")
        and event.get("event_type") == existing.get("event_type")
        and times_close(event.get("time"), existing.get("time"))
        and event.get("amount") == existing.get("amount")
        and event.get("status") == existing.get("status")
    )


def is_conflict(event: dict[str, Any], existing: dict[str, Any]) -> bool:
    if event.get("subject") != existing.get("subject"):
        return False
    if event.get("event_type") != existing.get("event_type"):
        return False
    if not times_close(event.get("time"), existing.get("time")):
        return False
    amount_differs = event.get("amount") != existing.get("amount")
    status_differs = event.get("status") != existing.get("status")
    text = str(event.get("source_text", "")).lower()
    conflict_signal = "separate filing" in text or str(event.get("status", "")).lower() == "withdrawn"
    return (amount_differs or status_differs) and (conflict_signal or status_differs)


def is_update(event: dict[str, Any], existing: dict[str, Any]) -> bool:
    if event.get("subject") != existing.get("subject"):
        return False
    if event.get("event_type") != existing.get("event_type"):
        return False
    text = str(event.get("source_text", "")).lower()
    update_signal = any(token in text for token in ("revision", "changing", "update", "updated", "prior"))
    changed = any(event.get(field) != existing.get(field) for field in ("amount", "status", "object", "time"))
    return update_signal and changed


def times_close(left: Any, right: Any, max_days: int = 2) -> bool:
    if left == right:
        return True
    left_date = parse_date(left)
    right_date = parse_date(right)
    if left_date is None or right_date is None:
        return False
    return abs((left_date - right_date).days) <= max_days


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
