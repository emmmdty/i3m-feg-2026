#!/usr/bin/env python3
"""Run oracle-controlled replay and write trace artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.io import read_jsonl, write_jsonl
from src.feg_replay.simulator import simulate_replay


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--trace-out", type=Path, default=Path("outputs/replay_trace.jsonl"))
    parser.add_argument("--updates-out", type=Path, default=Path("outputs/updates.jsonl"))
    parser.add_argument("--conflicts-out", type=Path, default=Path("outputs/conflicts.jsonl"))
    parser.add_argument("--logs-out", type=Path, default=Path("outputs/version_logs.jsonl"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = read_jsonl(args.input)
    result = simulate_replay(records, policy_mode="oracle")
    write_jsonl(args.trace_out, result.replay_trace)
    write_jsonl(args.updates_out, result.updates)
    write_jsonl(args.conflicts_out, result.graph.conflicts)
    write_jsonl(args.logs_out, result.graph.version_logs)
    print(f"Wrote replay trace: {args.trace_out}")
    print(f"Wrote update records: {args.updates_out}")
    print(f"Wrote conflict records: {args.conflicts_out}")
    print(f"Wrote version logs: {args.logs_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
