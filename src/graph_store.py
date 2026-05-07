"""Lightweight in-memory versioned event graph store."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .schema import normalize_event_record
from .update_ops import ADD_EVENT, MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT, VERSION_LOG


class GraphStore:
    """A small dict/list-backed graph for G_t = (V_t, E_t, L_t)."""

    def __init__(self) -> None:
        self.event_nodes: dict[str, dict[str, Any]] = {}
        self.entity_nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.version_logs: list[dict[str, Any]] = []
        self.conflicts: list[dict[str, Any]] = []
        self.merged_events: list[dict[str, Any]] = []
        self.updated_slot_count = 0

    @property
    def graph_version(self) -> int:
        return len(self.version_logs)

    def add_event(self, record: dict[str, Any], replay_step: int) -> dict[str, Any]:
        event = normalize_event_record(record)
        event_id = str(event["event_id"])
        self.event_nodes[event_id] = deepcopy(event)
        self._upsert_entity(event.get("subject"), "subject")
        self._upsert_entity(event.get("object"), "object")
        self._append_event_edges(event_id, event)
        update = self._update_record(ADD_EVENT, event, replay_step, target_event_id=event_id)
        self.append_version_log(ADD_EVENT, event, replay_step, target_event_id=event_id)
        return update

    def merge_event(
        self,
        record: dict[str, Any],
        replay_step: int,
        target_event_id: str | None = None,
    ) -> dict[str, Any]:
        event = normalize_event_record(record)
        target_event_id = target_event_id or event.get("base_event_id")
        merged = {
            "replay_step": replay_step,
            "incoming_event_id": event.get("event_id"),
            "target_event_id": target_event_id,
            "source_doc_id": event.get("source_doc_id"),
            "gold_group_id": event.get("gold_group_id"),
        }
        self.merged_events.append(merged)
        update = self._update_record(MERGE_EVENT, event, replay_step, target_event_id)
        self.append_version_log(MERGE_EVENT, event, replay_step, target_event_id, {"merged": merged})
        return update

    def update_slot(
        self,
        record: dict[str, Any],
        replay_step: int,
        target_event_id: str | None = None,
    ) -> dict[str, Any]:
        event = normalize_event_record(record)
        target_event_id = target_event_id or event.get("base_event_id")
        changed_fields: dict[str, dict[str, Any]] = {}
        target = self.event_nodes.get(str(target_event_id)) if target_event_id else None
        if target is not None:
            for field in ("amount", "status", "object", "time", "trigger", "evidence_span"):
                new_value = event.get(field)
                if new_value is not None and target.get(field) != new_value:
                    changed_fields[field] = {"old": target.get(field), "new": new_value}
                    target[field] = new_value
            target["last_update_source_doc_id"] = event.get("source_doc_id")
        else:
            for field in ("amount", "status", "object", "time", "trigger", "evidence_span"):
                if field in event:
                    changed_fields[field] = {"old": None, "new": event[field]}

        self.updated_slot_count += 1
        details = {"changed_fields": changed_fields}
        update = self._update_record(UPDATE_SLOT, event, replay_step, target_event_id, details)
        self.append_version_log(UPDATE_SLOT, event, replay_step, target_event_id, details)
        return update

    def mark_conflict(
        self,
        record: dict[str, Any],
        replay_step: int,
        target_event_id: str | None = None,
    ) -> dict[str, Any]:
        event = normalize_event_record(record)
        target_event_id = target_event_id or event.get("base_event_id")
        conflict = {
            "conflict_id": f"C{len(self.conflicts) + 1:06d}",
            "replay_step": replay_step,
            "incoming_event_id": event.get("event_id"),
            "target_event_id": target_event_id,
            "source_doc_id": event.get("source_doc_id"),
            "subject": event.get("subject"),
            "event_type": event.get("event_type"),
            "amount": event.get("amount"),
            "status": event.get("status"),
            "unresolved": True,
        }
        self.conflicts.append(conflict)
        update = self._update_record(MARK_CONFLICT, event, replay_step, target_event_id, {"conflict_id": conflict["conflict_id"]})
        self.append_version_log(MARK_CONFLICT, event, replay_step, target_event_id, {"conflict": conflict})
        return update

    def append_version_log(
        self,
        operator: str,
        event: dict[str, Any],
        replay_step: int,
        target_event_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        log = {
            "log_id": f"L{len(self.version_logs) + 1:06d}",
            "log_operator": VERSION_LOG,
            "operator": operator,
            "graph_version": len(self.version_logs) + 1,
            "replay_step": replay_step,
            "stream_record_id": event.get("stream_record_id"),
            "base_event_id": event.get("base_event_id"),
            "event_id": event.get("event_id"),
            "target_event_id": target_event_id,
            "source_doc_id": event.get("source_doc_id"),
            "details": details or {},
        }
        self.version_logs.append(log)
        return log

    def snapshot_state(self, replay_step: int) -> dict[str, Any]:
        unresolved = sum(1 for conflict in self.conflicts if conflict.get("unresolved"))
        return {
            "graph_version": self.graph_version,
            "active_event_count": len(self.event_nodes),
            "active_entity_count": len(self.entity_nodes),
            "merged_event_count": len(self.merged_events),
            "updated_slot_count": self.updated_slot_count,
            "conflict_count": len(self.conflicts),
            "unresolved_conflict_count": unresolved,
            "replay_step": replay_step,
        }

    def active_events(self) -> list[dict[str, Any]]:
        return [deepcopy(self.event_nodes[key]) for key in sorted(self.event_nodes)]

    def _upsert_entity(self, value: Any, role: str) -> None:
        if not isinstance(value, str) or value.strip() == "":
            return
        node = self.entity_nodes.setdefault(value, {"entity_id": value, "roles": []})
        if role not in node["roles"]:
            node["roles"].append(role)

    def _append_event_edges(self, event_id: str, event: dict[str, Any]) -> None:
        for role, value in (("subject", event.get("subject")), ("object", event.get("object"))):
            if isinstance(value, str) and value.strip():
                self.edges.append({"event_id": event_id, "entity_id": value, "role": role})

    def _update_record(
        self,
        operator: str,
        event: dict[str, Any],
        replay_step: int,
        target_event_id: str | None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "replay_step": replay_step,
            "operator": operator,
            "stream_record_id": event.get("stream_record_id"),
            "base_event_id": event.get("base_event_id"),
            "event_id": event.get("event_id"),
            "target_event_id": target_event_id,
            "source_doc_id": event.get("source_doc_id"),
            "details": details or {},
        }

