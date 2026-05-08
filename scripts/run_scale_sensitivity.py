#!/usr/bin/env python3
"""Run a lightweight scale sanity check."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for candidate in (PROJECT_ROOT, SCRIPT_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from prepare_synthetic_data import build_controlled_stream, build_seed_records
from src.feg_replay.io import write_csv
from src.feg_replay.simulator import simulate_replay
from src.feg_replay.table_rendering import render_scale_sensitivity_table, write_tex


FIELDNAMES = [
    "scale",
    "num_records",
    "active_events",
    "version_logs",
    "conflicts",
    "replay_completeness",
    "runtime_ms_per_record",
    "total_runtime_ms",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("tables/scale_sensitivity_results.csv"))
    parser.add_argument("--tex-table", type=Path, default=Path("paper/i3m_submission/tables/table_scale_sensitivity.tex"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scales", type=int, nargs="+", default=[30, 60, 120, 240])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [run_scale(scale, args.seed) for scale in args.scales]
    write_csv(args.out, rows, FIELDNAMES)
    write_tex(args.tex_table, render_scale_sensitivity_table([{key: str(value) for key, value in row.items()} for row in rows]))
    print(f"Wrote scale sensitivity results: {args.out}")
    print(f"Wrote scale sensitivity table: {args.tex_table}")
    return 0


def run_scale(scale: int, seed: int) -> dict[str, Any]:
    if scale < 1:
        raise SystemExit("--scales values must be positive")
    samples = build_seed_records(scale, seed)
    stream = build_controlled_stream(samples, seed, perturbation_count=max(1, scale // 3))
    started = time.perf_counter()
    result = simulate_replay(stream, policy_mode="oracle")
    elapsed = time.perf_counter() - started
    total_records = len(stream)
    applied = sum(1 for item in result.replay_trace if item.get("operation_applied"))
    total_runtime_ms = elapsed * 1000.0
    return {
        "scale": scale,
        "num_records": total_records,
        "active_events": len(result.graph.event_nodes),
        "version_logs": len(result.graph.version_logs),
        "conflicts": len(result.graph.conflicts),
        "replay_completeness": applied / total_records if total_records else 0.0,
        "runtime_ms_per_record": total_runtime_ms / total_records if total_records else 0.0,
        "total_runtime_ms": total_runtime_ms,
    }


if __name__ == "__main__":
    raise SystemExit(main())
