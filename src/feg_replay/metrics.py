"""Controlled replay metrics."""

from __future__ import annotations

import time
from typing import Any

from .evidence import has_evidence_match
from .operators import MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT
from .schema import event_data, validate_event_schema
from .simulator import ordered_records, simulate_replay


ORACLE_FIELDNAMES = [
    "method",
    "schema_validity",
    "evidence_coverage",
    "merge_agreement",
    "conflict_agreement",
    "update_agreement",
    "operator_agreement",
    "replay_completeness",
    "runtime_ms_per_record",
    "num_records",
]


def build_oracle_replay_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        run_component("Direct records", records, use_schema=False, use_evidence=False),
        run_component("Schema gate", records, use_schema=True, use_evidence=False),
        run_component("Evidence gate", records, use_schema=True, use_evidence=True),
        run_oracle_controlled(records),
    ]


def run_component(
    method: str,
    records: list[dict[str, Any]],
    use_schema: bool,
    use_evidence: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    accepted = 0
    for record in ordered_records(records):
        schema_valid, _ = validate_event_schema(record)
        evidence_match = has_evidence_match(record) if schema_valid else False
        if use_schema and not schema_valid:
            continue
        if use_evidence and not evidence_match:
            continue
        event_data(record)
        accepted += 1
    runtime = time.perf_counter() - started
    total = len(records)
    schema_valid_count = sum(1 for record in records if validate_event_schema(record)[0])
    evidence_count = sum(1 for record in records if has_evidence_match(record))
    return {
        "method": method,
        "schema_validity": format_rate(schema_valid_count, total),
        "evidence_coverage": format_rate(evidence_count, total),
        "merge_agreement": "NA",
        "conflict_agreement": "NA",
        "update_agreement": "NA",
        "operator_agreement": "NA",
        "replay_completeness": format_rate(accepted, total) if method == "Evidence gate" else "NA",
        "runtime_ms_per_record": format_runtime(runtime, total),
        "num_records": total,
    }


def run_oracle_controlled(records: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    result = simulate_replay(records, require_schema=True, require_evidence=True, policy_mode="oracle")
    runtime = time.perf_counter() - started
    total = len(records)
    applied = sum(1 for item in result.replay_trace if item.get("operation_applied"))
    return {
        "method": "Oracle-controlled",
        "schema_validity": format_rate(result.schema_valid_count, total),
        "evidence_coverage": format_rate(result.evidence_match_count, total),
        "merge_agreement": format_optional_rate(operator_agreement(result.replay_trace, MERGE_EVENT)),
        "conflict_agreement": format_optional_rate(operator_agreement(result.replay_trace, MARK_CONFLICT)),
        "update_agreement": format_optional_rate(operator_agreement(result.replay_trace, UPDATE_SLOT)),
        "operator_agreement": format_optional_rate(operator_agreement(result.replay_trace, None)),
        "replay_completeness": format_rate(applied, total),
        "runtime_ms_per_record": format_runtime(runtime, total),
        "num_records": total,
    }


def operator_agreement(trace: list[dict[str, Any]], operator: str | None) -> float | None:
    relevant = []
    for item in trace:
        expected = item.get("expected_operator")
        if not isinstance(expected, str):
            continue
        if operator is not None and expected != operator:
            continue
        relevant.append(item)
    if not relevant:
        return None
    correct = sum(1 for item in relevant if item.get("predicted_operator") == item.get("expected_operator"))
    return correct / len(relevant)


def format_rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.000000"
    return f"{numerator / denominator:.6f}"


def format_optional_rate(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{value:.6f}"


def format_runtime(runtime_seconds: float, total_records: int) -> str:
    if total_records == 0:
        return "0.000000"
    return f"{(runtime_seconds * 1000.0) / total_records:.6f}"
