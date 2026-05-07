"""Discrete-event replay simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .conflict import predict_operator, select_target_event_id
from .evidence import has_evidence_match
from .graph_store import GraphStore
from .schema import validate_event_schema
from .update_ops import ADD_EVENT, MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT


@dataclass
class SimulationResult:
    graph: GraphStore
    replay_trace: list[dict[str, Any]]
    updates: list[dict[str, Any]]
    schema_valid_count: int
    evidence_match_count: int
    total_records: int


def ordered_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    indexed = list(enumerate(records, start=1))

    def sort_key(item: tuple[int, dict[str, Any]]) -> tuple[int, int]:
        index, record = item
        arrival_index = record.get("arrival_index")
        return (arrival_index if isinstance(arrival_index, int) else index, index)

    return [record for _, record in sorted(indexed, key=sort_key)]


def simulate_replay(
    records: list[dict[str, Any]],
    require_schema: bool = True,
    require_evidence: bool = True,
) -> SimulationResult:
    graph = GraphStore()
    updates: list[dict[str, Any]] = []
    replay_trace: list[dict[str, Any]] = []
    schema_valid_count = 0
    evidence_match_count = 0

    for replay_step, record in enumerate(ordered_records(records), start=1):
        schema_valid, schema_errors = validate_event_schema(record)
        evidence_match = has_evidence_match(record)
        schema_valid_count += int(schema_valid)
        evidence_match_count += int(evidence_match)

        predicted_operator: str | None = None
        operation_applied = False
        skipped_reason: str | None = None

        if require_schema and not schema_valid:
            skipped_reason = "schema_invalid"
        elif require_evidence and not evidence_match:
            skipped_reason = "evidence_missing"
        else:
            predicted_operator = predict_operator(record, graph)
            target_event_id = select_target_event_id(record, graph)
            if predicted_operator == ADD_EVENT:
                update = graph.add_event(record, replay_step)
            elif predicted_operator == MERGE_EVENT:
                update = graph.merge_event(record, replay_step, target_event_id)
            elif predicted_operator == UPDATE_SLOT:
                update = graph.update_slot(record, replay_step, target_event_id)
            elif predicted_operator == MARK_CONFLICT:
                update = graph.mark_conflict(record, replay_step, target_event_id)
            else:
                raise ValueError(f"unsupported predicted operator: {predicted_operator}")
            updates.append(update)
            operation_applied = True

        snapshot = graph.snapshot_state(replay_step)
        replay_trace.append(
            {
                "replay_step": replay_step,
                "stream_record_id": record.get("stream_record_id"),
                "base_event_id": record.get("base_event_id"),
                "expected_operator": record.get("expected_operator"),
                "predicted_operator": predicted_operator,
                "perturbation_type": record.get("perturbation_type"),
                "schema_valid": schema_valid,
                "schema_errors": schema_errors,
                "evidence_match": evidence_match,
                "operation_applied": operation_applied,
                "skipped_reason": skipped_reason,
                **snapshot,
            }
        )

    return SimulationResult(
        graph=graph,
        replay_trace=replay_trace,
        updates=updates,
        schema_valid_count=schema_valid_count,
        evidence_match_count=evidence_match_count,
        total_records=len(records),
    )

