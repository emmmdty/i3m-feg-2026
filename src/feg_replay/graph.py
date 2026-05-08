"""In-memory versioned event graph."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .operators import ADD_EVENT, MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT, VERSION_LOG
from .schema import event_data


class GraphStore:
    """Dictionary-backed graph with append-only replay logs."""

    def __init__(self) -> None:
        self.event_nodes: dict[str, dict[str, Any]] = {}
        self.entity_nodes: dict[str, dict[str, Any]] = {}
        self.edges: list[dict[str, Any]] = []
        self.version_logs: list[dict[str, Any]] = []
        self.conflicts: list[dict[str, Any]] = []
        self.failed_conflict_attempts: list[dict[str, Any]] = []
        self.merged_events: list[dict[str, Any]] = []
        self.updated_slot_count = 0

    @property
    def graph_version(self) -> int:
        return len(self.version_logs)

    def add_event(self, record: dict[str, Any], replay_step: int) -> dict[str, Any]:
        event = event_data(record)
        event_id = str(event["event_id"])
        self.event_nodes[event_id] = deepcopy(event)
        self._upsert_entity(event.get("subject"), "subject")
        self._upsert_entity(event.get("object"), "object")
        self._append_event_edges(event_id, event)
        update = self._update_record(
            ADD_EVENT,
            event,
            replay_step,
            target_event_id=event_id,
            target_exists=True,
            operation_applied=True,
        )
        self.append_version_log(update)
        return update

    def merge_event(
        self,
        record: dict[str, Any],
        replay_step: int,
        target_event_id: str | None,
    ) -> dict[str, Any]:
        event = event_data(record)
        target_exists = self._target_exists(target_event_id)
        if not target_exists:
            update = self._target_missing_record(MERGE_EVENT, event, replay_step, target_event_id)
            self.append_version_log(update)
            return update

        merged = {
            "replay_step": replay_step,
            "incoming_event_id": event.get("event_id"),
            "target_event_id": target_event_id,
            "source_doc_id": event.get("source_doc_id"),
        }
        self.merged_events.append(merged)
        update = self._update_record(
            MERGE_EVENT,
            event,
            replay_step,
            target_event_id,
            target_exists=True,
            operation_applied=True,
            details={"merged": merged},
        )
        self.append_version_log(update)
        return update

    def update_slot(
        self,
        record: dict[str, Any],
        replay_step: int,
        target_event_id: str | None,
    ) -> dict[str, Any]:
        event = event_data(record)
        target_exists = self._target_exists(target_event_id)
        if not target_exists:
            update = self._target_missing_record(UPDATE_SLOT, event, replay_step, target_event_id)
            self.append_version_log(update)
            return update

        target = self.event_nodes[str(target_event_id)]
        changed_fields: dict[str, dict[str, Any]] = {}
        for field in ("amount", "status", "object", "time", "trigger", "evidence_span"):
            new_value = event.get(field)
            if new_value is not None and target.get(field) != new_value:
                changed_fields[field] = {"old": target.get(field), "new": new_value}
                target[field] = new_value
        target["last_update_source_doc_id"] = event.get("source_doc_id")
        self.updated_slot_count += 1
        update = self._update_record(
            UPDATE_SLOT,
            event,
            replay_step,
            target_event_id,
            target_exists=True,
            operation_applied=True,
            details={"changed_fields": changed_fields},
        )
        self.append_version_log(update)
        return update

    def mark_conflict(
        self,
        record: dict[str, Any],
        replay_step: int,
        target_event_id: str | None,
    ) -> dict[str, Any]:
        event = event_data(record)
        target_exists = self._target_exists(target_event_id)
        if not target_exists:
            update = self._target_missing_record(MARK_CONFLICT, event, replay_step, target_event_id)
            self.failed_conflict_attempts.append(update)
            self.append_version_log(update)
            return update

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
        update = self._update_record(
            MARK_CONFLICT,
            event,
            replay_step,
            target_event_id,
            target_exists=True,
            operation_applied=True,
            details={"conflict": conflict},
        )
        self.append_version_log(update)
        return update

    def append_version_log(self, update: dict[str, Any]) -> dict[str, Any]:
        log = {
            "log_id": f"L{len(self.version_logs) + 1:06d}",
            "log_operator": VERSION_LOG,
            "graph_version": len(self.version_logs) + 1,
            **deepcopy(update),
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
            "failed_conflict_attempt_count": len(self.failed_conflict_attempts),
            "replay_step": replay_step,
        }

    def active_events(self) -> list[dict[str, Any]]:
        return [deepcopy(self.event_nodes[key]) for key in sorted(self.event_nodes)]

    def _target_exists(self, target_event_id: str | None) -> bool:
        return isinstance(target_event_id, str) and target_event_id in self.event_nodes

    def _target_missing_record(
        self,
        operator: str,
        event: dict[str, Any],
        replay_step: int,
        target_event_id: str | None,
    ) -> dict[str, Any]:
        return self._update_record(
            operator,
            event,
            replay_step,
            target_event_id,
            target_exists=False,
            operation_applied=False,
            skipped_reason="target_missing",
        )

    def _upsert_entity(self, value: Any, role: str) -> None:
        if not isinstance(value, str) or not value.strip():
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
        target_exists: bool,
        operation_applied: bool,
        skipped_reason: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "replay_step": replay_step,
            "operator": operator,
            "stream_record_id": event.get("stream_record_id"),
            "base_event_id": event.get("base_event_id"),
            "event_id": event.get("event_id"),
            "target_event_id": target_event_id,
            "target_exists": target_exists,
            "operation_applied": operation_applied,
            "skipped_reason": skipped_reason,
            "source_doc_id": event.get("source_doc_id"),
            "details": details or {},
        }
