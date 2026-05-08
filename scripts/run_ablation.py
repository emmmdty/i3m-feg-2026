#!/usr/bin/env python3
"""Run controlled replay diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.io import read_jsonl, write_csv
from src.feg_replay.metrics import ORACLE_FIELDNAMES, build_oracle_replay_rows
from src.feg_replay.table_rendering import render_oracle_replay_table, write_tex


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("tables/oracle_replay_results.csv"))
    parser.add_argument("--tex-table", type=Path, default=Path("paper/i3m_submission/tables/table_oracle_replay.tex"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_oracle_replay_rows(read_jsonl(args.input))
    write_csv(args.out, rows, ORACLE_FIELDNAMES)
    write_tex(args.tex_table, render_oracle_replay_table([{key: str(value) for key, value in row.items()} for row in rows]))
    print(f"Wrote oracle replay diagnostics: {args.out}")
    print(f"Wrote oracle replay table: {args.tex_table}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
