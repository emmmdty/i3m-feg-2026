#!/usr/bin/env python3
"""Run the Stage 02 minimal replay demo."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import read_jsonl, write_jsonl
from src.simulator import simulate_replay


def ensure_stream(samples_path: Path, stream_path: Path) -> None:
    if stream_path.exists():
        return
    generator = PROJECT_ROOT / "scripts" / "generate_perturbation_stream.py"
    if not samples_path.exists() or not generator.exists():
        raise SystemExit(
            "Missing controlled stream. Run Stage 1 data preparation before run_demo.py."
        )
    command = [
        sys.executable,
        str(generator),
        "--input",
        str(samples_path),
        "--out",
        str(stream_path),
        "--seed",
        "42",
        "--duplicates",
        "10",
        "--conflicts",
        "10",
        "--updates",
        "10",
        "--shuffle",
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=Path("data/samples/seed_financial_events.jsonl"))
    parser.add_argument("--stream", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_stream(args.samples, args.stream)
    records = read_jsonl(args.stream)
    result = simulate_replay(records, require_schema=True, require_evidence=True)

    write_jsonl(args.outputs_dir / "events.jsonl", result.graph.active_events())
    write_jsonl(args.outputs_dir / "updates.jsonl", result.updates)
    write_jsonl(args.outputs_dir / "version_logs.jsonl", result.graph.version_logs)
    write_jsonl(args.outputs_dir / "conflicts.jsonl", result.graph.conflicts)
    write_jsonl(args.outputs_dir / "replay_trace.jsonl", result.replay_trace)

    print(f"Processed records: {result.total_records}")
    print(f"Active events: {len(result.graph.event_nodes)}")
    print(f"Version logs: {len(result.graph.version_logs)}")
    print(f"Conflicts: {len(result.graph.conflicts)}")
    print(f"Wrote outputs to: {args.outputs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

