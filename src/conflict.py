"""Rule-based duplicate, update, and conflict decisions."""

from __future__ import annotations

from datetime import date
from typing import Any

from .graph_store import GraphStore
from .schema import normalize_event_record
from .update_ops import ADD_EVENT, MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT


def predict_operator(record: dict[str, Any], graph: GraphStore) -> str:
    event = normalize_event_record(record)
    perturbation_type = str(event.get("perturbation_type", "")).lower()

    if perturbation_type == "duplicate":
        return MERGE_EVENT
    if perturbation_type == "conflict":
        return MARK_CONFLICT
    if perturbation_type == "update":
        return UPDATE_SLOT
    if perturbation_type in {"base", "temporal_shuffle"}:
        return ADD_EVENT

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


def select_target_event_id(record: dict[str, Any], graph: GraphStore) -> str | None:
    event = normalize_event_record(record)
    base_event_id = event.get("base_event_id")
    if isinstance(base_event_id, str) and base_event_id in graph.event_nodes:
        return base_event_id

    target = find_matching_event(event, graph)
    if target is not None:
        return str(target.get("event_id"))
    if isinstance(base_event_id, str) and base_event_id:
        return base_event_id
    return None


def find_matching_event(event: dict[str, Any], graph: GraphStore) -> dict[str, Any] | None:
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
    conflict_text = "separate filing" in str(event.get("source_text", "")).lower()
    withdrawn = str(event.get("status", "")).lower() == "withdrawn"
    return (amount_differs or status_differs) and (conflict_text or withdrawn or status_differs)


def is_update(event: dict[str, Any], existing: dict[str, Any]) -> bool:
    if event.get("subject") != existing.get("subject"):
        return False
    if event.get("event_type") != existing.get("event_type"):
        return False
    text = str(event.get("source_text", "")).lower()
    update_signal = any(token in text for token in ("revision", "changing", "update", "updated", "prior"))
    if str(event.get("perturbation_type", "")).lower() == "update":
        update_signal = True
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

