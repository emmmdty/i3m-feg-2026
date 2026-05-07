#!/usr/bin/env python3
"""Run full-control and metadata-hidden controlled replay diagnostics."""

from __future__ import annotations

import argparse
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import read_jsonl, write_csv
from src.schema import normalize_event_record
from src.simulator import ordered_records, simulate_replay
from src.submission_tables import render_metadata_hidden_table, write_tex
from src.update_ops import MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT


FIELDNAMES = [
    "setting",
    "uses_perturbation_metadata",
    "num_records",
    "merge_agreement",
    "conflict_agreement",
    "update_agreement",
    "operator_agreement",
    "replay_completeness",
    "runtime_ms_per_record",
]

EVENT_FIELDS = (
    "event_id",
    "event_type",
    "subject",
    "object",
    "time",
    "trigger",
    "evidence_span",
    "source_doc_id",
    "source_text",
    "amount",
    "status",
)

HIDDEN_METADATA_FIELDS = {
    "perturbation_type",
    "expected_operator",
    "base_event_id",
    "gold_group_id",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tex-table", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = ordered_records(read_jsonl(args.input))
    rows = [
        run_setting("Full-control", "yes", records, records),
        run_setting("Metadata-hidden", "no", records, [strip_replay_metadata(record) for record in records]),
    ]
    write_csv(args.out, rows, FIELDNAMES)
    write_tex(args.tex_table, render_metadata_hidden_table(rows))
    print(f"Wrote metadata-hidden results: {args.out}")
    print(f"Wrote metadata-hidden LaTeX table: {args.tex_table}")
    for row in rows:
        print(
            f"{row['setting']}: metadata={row['uses_perturbation_metadata']} "
            f"merge={row['merge_agreement']} conflict={row['conflict_agreement']} "
            f"update={row['update_agreement']} operator={row['operator_agreement']} "
            f"replay={row['replay_completeness']}"
        )
    return 0


def strip_replay_metadata(record: dict[str, Any]) -> dict[str, Any]:
    """Return an event-only replay record for metadata-hidden prediction."""
    event = normalize_event_record(record)
    stripped = {field: deepcopy(event[field]) for field in EVENT_FIELDS if field in event}
    for field in HIDDEN_METADATA_FIELDS:
        stripped.pop(field, None)
    return stripped


def run_setting(
    setting: str,
    uses_metadata: str,
    gold_records: list[dict[str, Any]],
    decision_records: list[dict[str, Any]],
) -> dict[str, str]:
    started = time.perf_counter()
    result = simulate_replay(decision_records, require_schema=True, require_evidence=True)
    runtime = time.perf_counter() - started
    ordered_gold = ordered_records(gold_records)
    trace = result.replay_trace
    total = len(trace)
    applied = sum(1 for item in trace if item.get("operation_applied"))
    return {
        "setting": setting,
        "uses_perturbation_metadata": uses_metadata,
        "num_records": str(total),
        "merge_agreement": format_optional_rate(operator_agreement(ordered_gold, trace, MERGE_EVENT)),
        "conflict_agreement": format_optional_rate(operator_agreement(ordered_gold, trace, MARK_CONFLICT)),
        "update_agreement": format_optional_rate(operator_agreement(ordered_gold, trace, UPDATE_SLOT)),
        "operator_agreement": format_optional_rate(operator_agreement(ordered_gold, trace, None)),
        "replay_completeness": format_rate(applied, total),
        "runtime_ms_per_record": format_runtime(runtime, total),
    }


def operator_agreement(
    gold_records: list[dict[str, Any]],
    trace: list[dict[str, Any]],
    operator: str | None,
) -> float | None:
    correct = 0
    total = 0
    for gold_record, trace_item in zip(gold_records, trace):
        expected = normalize_event_record(gold_record).get("expected_operator")
        if not isinstance(expected, str):
            continue
        if operator is not None and expected != operator:
            continue
        total += 1
        if trace_item.get("predicted_operator") == expected:
            correct += 1
    if total == 0:
        return None
    return correct / total


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


if __name__ == "__main__":
    raise SystemExit(main())
