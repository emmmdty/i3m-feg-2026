#!/usr/bin/env python3
"""Run Stage 02 component ablations."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import read_jsonl, write_csv
from src.metrics import ABLATION_FIELDNAMES, build_ablation_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stream", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--tables-dir", type=Path, default=Path("tables"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.stream.exists():
        raise SystemExit("Missing controlled stream. Run scripts/run_demo.py or Stage 1 data preparation first.")
    records = read_jsonl(args.stream)
    rows = build_ablation_rows(records)
    out_path = args.tables_dir / "ablation_results.csv"
    write_csv(out_path, rows, ABLATION_FIELDNAMES)
    print(f"Wrote ablation results: {out_path}")
    for row in rows:
        print(
            f"{row['method']}: schema={row['schema_validity']} "
            f"evidence={row['evidence_coverage']} "
            f"merge={row['merge_accuracy']} conflict={row['conflict_accuracy']} "
            f"replay={row['replay_completeness']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
