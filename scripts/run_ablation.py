#!/usr/bin/env python3
"""Run component ablations for the reproducible prototype."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import read_jsonl, write_csv
from src.metrics import ABLATION_FIELDNAMES, build_ablation_rows


def read_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"config must be a JSON object: {path}")
    return value


def path_from_config(value: Any, default: Path) -> Path:
    if isinstance(value, str) and value:
        return Path(value)
    return default


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Optional experiment config JSON.")
    parser.add_argument("--stream", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--tables-dir", type=Path, default=Path("tables"))
    parser.add_argument("--out", type=Path, help="Output CSV path. Overrides --tables-dir.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_config(args.config)
    stream_path = args.stream
    if args.config is not None and args.stream == Path("data/processed/controlled_stream.jsonl"):
        stream_path = path_from_config(config.get("stream"), args.stream)
    if args.out is not None:
        out_path = args.out
    elif "ablation_output" in config:
        out_path = path_from_config(config.get("ablation_output"), args.tables_dir / "ablation_results.csv")
    else:
        out_path = args.tables_dir / "ablation_results.csv"

    if not stream_path.exists():
        raise SystemExit("Missing controlled stream. Run scripts/run_demo.py or Stage 1 data preparation first.")
    records = read_jsonl(stream_path)
    rows = build_ablation_rows(records)
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
