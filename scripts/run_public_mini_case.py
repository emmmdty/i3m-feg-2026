#!/usr/bin/env python3
"""Run the committed FewFC-derived mini-case as an external sanity check."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.io import read_jsonl, write_csv, write_jsonl
from src.feg_replay.metrics import format_rate, format_runtime
from src.feg_replay.simulator import simulate_replay
from src.feg_replay.table_rendering import render_public_mini_case_table, write_tex


FIELDNAMES = [
    "num_records",
    "schema_validity",
    "evidence_coverage",
    "replay_completeness",
    "active_events",
    "version_logs",
    "runtime_ms_per_record",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/samples/public_mini_events.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("tables/public_mini_case_results.csv"))
    parser.add_argument("--tex-table", type=Path, default=Path("paper/i3m_submission/tables/table_public_mini_case.tex"))
    parser.add_argument("--trace-out", type=Path, default=Path("outputs/public_mini_replay_trace.jsonl"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = read_jsonl(args.input)
    started = time.perf_counter()
    result = simulate_replay(records, policy_mode="rule_based")
    runtime = time.perf_counter() - started
    total = len(records)
    applied = sum(1 for item in result.replay_trace if item.get("operation_applied"))
    row = {
        "num_records": str(total),
        "schema_validity": format_rate(result.schema_valid_count, total),
        "evidence_coverage": format_rate(result.evidence_match_count, total),
        "replay_completeness": format_rate(applied, total),
        "active_events": str(len(result.graph.event_nodes)),
        "version_logs": str(len(result.graph.version_logs)),
        "runtime_ms_per_record": format_runtime(runtime, total),
    }
    write_csv(args.out, [row], FIELDNAMES)
    write_jsonl(args.trace_out, result.replay_trace)
    write_tex(args.tex_table, render_public_mini_case_table([row]))
    print(f"Wrote public mini-case results: {args.out}")
    print(f"Wrote public mini-case table: {args.tex_table}")
    print(f"Wrote public mini-case trace: {args.trace_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
