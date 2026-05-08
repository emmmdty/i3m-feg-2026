"""Discrete-event replay simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .evidence import has_evidence_match
from .graph import GraphStore
from .operators import ADD_EVENT, MARK_CONFLICT, MERGE_EVENT, TARGET_OPERATORS, UPDATE_SLOT
from .policy import (
    predict_operator_oracle,
    predict_operator_rule_based,
    select_target_oracle,
    select_target_rule_based,
)
from .schema import event_data, validate_event_schema


@dataclass
class SimulationResult:
    """Replay outputs used by scripts and tests."""

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
        arrival_index = event_data(record).get("arrival_index")
        return (arrival_index if isinstance(arrival_index, int) else index, index)

    return [record for _, record in sorted(indexed, key=sort_key)]


def simulate_replay(
    records: list[dict[str, Any]],
    require_schema: bool = True,
    require_evidence: bool = True,
    policy_mode: str = "oracle",
) -> SimulationResult:
    """Replay records through schema, evidence, policy, and graph gates."""
    if policy_mode not in {"oracle", "rule_based"}:
        raise ValueError("policy_mode must be 'oracle' or 'rule_based'")

    graph = GraphStore()
    updates: list[dict[str, Any]] = []
    replay_trace: list[dict[str, Any]] = []
    schema_valid_count = 0
    evidence_match_count = 0

    for replay_step, record in enumerate(ordered_records(records), start=1):
        event = event_data(record)
        schema_valid, schema_errors = validate_event_schema(record)
        evidence_match = has_evidence_match(record) if schema_valid else False
        schema_valid_count += int(schema_valid)
        evidence_match_count += int(evidence_match)

        predicted_operator: str | None = None
        target_event_id: str | None = None
        target_exists = False
        operation_applied = False
        skipped_reason: str | None = None
        unsupported_metadata_logged = False

        if require_schema and not schema_valid:
            skipped_reason = "schema_invalid"
        elif require_evidence and not evidence_match:
            skipped_reason = "evidence_missing"
        else:
            if policy_mode == "oracle":
                predicted_operator = predict_operator_oracle(record, graph)
                target_event_id = select_target_oracle(record, graph)
            else:
                predicted_operator = predict_operator_rule_based(record, graph)
                target_event_id = select_target_rule_based(record, graph)

            if predicted_operator is None:
                skipped_reason = "unsupported_or_unknown_metadata"
                unsupported_metadata_logged = True
                graph.append_version_log(
                    {
                        "replay_step": replay_step,
                        "operator": "UNSUPPORTED_METADATA",
                        "stream_record_id": event.get("stream_record_id"),
                        "base_event_id": event.get("base_event_id"),
                        "event_id": event.get("event_id"),
                        "target_event_id": None,
                        "target_exists": False,
                        "operation_applied": False,
                        "skipped_reason": skipped_reason,
                        "source_doc_id": event.get("source_doc_id"),
                        "details": {"unsupported_metadata_logged": True},
                    }
                )
            else:
                update = apply_operator(graph, record, replay_step, predicted_operator, target_event_id)
                updates.append(update)
                target_value = update.get("target_event_id")
                target_event_id = target_value if isinstance(target_value, str) else None
                operation_applied = bool(update.get("operation_applied"))
                skipped_reason = update.get("skipped_reason")
                target_exists = bool(update.get("target_exists"))

        snapshot = graph.snapshot_state(replay_step)
        replay_trace.append(
            {
                "replay_step": replay_step,
                "stream_record_id": event.get("stream_record_id"),
                "base_event_id": event.get("base_event_id"),
                "event_id": event.get("event_id"),
                "expected_operator": event.get("expected_operator"),
                "predicted_operator": predicted_operator,
                "perturbation_type": event.get("perturbation_type"),
                "schema_valid": schema_valid,
                "schema_errors": schema_errors,
                "evidence_match": evidence_match,
                "target_event_id": target_event_id,
                "target_exists": target_exists,
                "operation_applied": operation_applied,
                "skipped_reason": skipped_reason,
                "unsupported_metadata_logged": unsupported_metadata_logged,
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


def apply_operator(
    graph: GraphStore,
    record: dict[str, Any],
    replay_step: int,
    operator: str,
    target_event_id: str | None,
) -> dict[str, Any]:
    if operator == ADD_EVENT:
        return graph.add_event(record, replay_step)
    if operator == MERGE_EVENT:
        return graph.merge_event(record, replay_step, target_event_id)
    if operator == UPDATE_SLOT:
        return graph.update_slot(record, replay_step, target_event_id)
    if operator == MARK_CONFLICT:
        return graph.mark_conflict(record, replay_step, target_event_id)
    if operator in TARGET_OPERATORS:
        return graph.merge_event(record, replay_step, target_event_id)
    raise ValueError(f"unsupported operator: {operator}")
