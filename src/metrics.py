"""Metrics and ablation helpers for the Stage 02 prototype."""

from __future__ import annotations

import time
from typing import Any

from .evidence import has_evidence_match
from .schema import normalize_event_record, validate_event_schema
from .simulator import ordered_records, simulate_replay
from .update_ops import MARK_CONFLICT, MERGE_EVENT


ABLATION_FIELDNAMES = [
    "method",
    "schema_validity",
    "evidence_coverage",
    "merge_accuracy",
    "conflict_accuracy",
    "replay_completeness",
    "runtime_ms_per_record",
    "num_records",
]


def build_ablation_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        run_direct(records),
        run_schema(records),
        run_evidence(records),
        run_full(records),
    ]


def run_direct(records: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    independent_events = [normalize_event_record(record) for record in ordered_records(records)]
    runtime = time.perf_counter() - started
    return component_row("Direct", records, runtime, len(independent_events))


def run_schema(records: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    accepted = [record for record in ordered_records(records) if validate_event_schema(record)[0]]
    runtime = time.perf_counter() - started
    return component_row("Schema", records, runtime, len(accepted))


def run_evidence(records: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    accepted = [
        record
        for record in ordered_records(records)
        if validate_event_schema(record)[0] and has_evidence_match(record)
    ]
    runtime = time.perf_counter() - started
    return component_row("Evidence", records, runtime, len(accepted))


def run_full(records: list[dict[str, Any]]) -> dict[str, Any]:
    started = time.perf_counter()
    result = simulate_replay(records, require_schema=True, require_evidence=True)
    runtime = time.perf_counter() - started
    total = len(records)
    return {
        "method": "Full",
        "schema_validity": format_rate(result.schema_valid_count, total),
        "evidence_coverage": format_rate(result.evidence_match_count, total),
        "merge_accuracy": format_optional_rate(operator_accuracy(result.replay_trace, MERGE_EVENT)),
        "conflict_accuracy": format_optional_rate(operator_accuracy(result.replay_trace, MARK_CONFLICT)),
        "replay_completeness": format_rate(
            sum(1 for item in result.replay_trace if item.get("operation_applied")),
            total,
        ),
        "runtime_ms_per_record": format_runtime(runtime, total),
        "num_records": total,
    }


def component_row(method: str, records: list[dict[str, Any]], runtime: float, _: int) -> dict[str, Any]:
    total = len(records)
    schema_valid = sum(1 for record in records if validate_event_schema(record)[0])
    evidence_valid = sum(1 for record in records if has_evidence_match(record))
    return {
        "method": method,
        "schema_validity": format_rate(schema_valid, total),
        "evidence_coverage": format_rate(evidence_valid, total),
        "merge_accuracy": "NA",
        "conflict_accuracy": "NA",
        "replay_completeness": "NA",
        "runtime_ms_per_record": format_runtime(runtime, total),
        "num_records": total,
    }


def operator_accuracy(trace: list[dict[str, Any]], operator: str) -> float | None:
    relevant = [item for item in trace if item.get("expected_operator") == operator]
    if not relevant:
        return None
    correct = sum(1 for item in relevant if item.get("predicted_operator") == operator)
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

