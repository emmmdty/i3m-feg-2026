#!/usr/bin/env python3
"""Compare oracle-controlled replay with metadata-hidden replay."""

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

from src.feg_replay.io import read_jsonl, write_csv
from src.feg_replay.metrics import format_optional_rate, format_rate, format_runtime, operator_agreement
from src.feg_replay.schema import event_data
from src.feg_replay.simulator import ordered_records, simulate_replay
from src.feg_replay.table_rendering import render_metadata_hidden_table, write_tex


FIELDNAMES = [
    "setting",
    "uses_metadata",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("tables/metadata_hidden_results.csv"))
    parser.add_argument("--tex-table", type=Path, default=Path("paper/i3m_submission/tables/table_metadata_hidden.tex"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = ordered_records(read_jsonl(args.input))
    rows = [
        run_setting("Oracle-controlled", "yes", records, records, "oracle"),
        run_setting("Metadata-hidden", "no", records, [strip_replay_metadata(record) for record in records], "rule_based"),
    ]
    write_csv(args.out, rows, FIELDNAMES)
    write_tex(args.tex_table, render_metadata_hidden_table(rows))
    print(f"Wrote metadata-hidden diagnostics: {args.out}")
    print(f"Wrote metadata-hidden table: {args.tex_table}")
    return 0


def strip_replay_metadata(record: dict[str, Any]) -> dict[str, Any]:
    event = event_data(record)
    return {field: deepcopy(event[field]) for field in EVENT_FIELDS if field in event}


def run_setting(
    setting: str,
    uses_metadata: str,
    gold_records: list[dict[str, Any]],
    decision_records: list[dict[str, Any]],
    policy_mode: str,
) -> dict[str, str]:
    started = time.perf_counter()
    result = simulate_replay(decision_records, policy_mode=policy_mode)
    runtime = time.perf_counter() - started
    trace = result.replay_trace
    total = len(trace)
    applied = sum(1 for item in trace if item.get("operation_applied"))
    patched_trace = attach_expected_labels(gold_records, trace)
    return {
        "setting": setting,
        "uses_metadata": uses_metadata,
        "num_records": str(total),
        "merge_agreement": format_optional_rate(operator_agreement(patched_trace, "MERGE_EVENT")),
        "conflict_agreement": format_optional_rate(operator_agreement(patched_trace, "MARK_CONFLICT")),
        "update_agreement": format_optional_rate(operator_agreement(patched_trace, "UPDATE_SLOT")),
        "operator_agreement": format_optional_rate(operator_agreement(patched_trace, None)),
        "replay_completeness": format_rate(applied, total),
        "runtime_ms_per_record": format_runtime(runtime, total),
    }


def attach_expected_labels(
    gold_records: list[dict[str, Any]],
    trace: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gold_record, trace_item in zip(ordered_records(gold_records), trace):
        row = dict(trace_item)
        row["expected_operator"] = event_data(gold_record).get("expected_operator")
        rows.append(row)
    return rows


if __name__ == "__main__":
    raise SystemExit(main())
