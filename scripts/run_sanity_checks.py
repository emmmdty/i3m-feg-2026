#!/usr/bin/env python3
"""Run negative-control sanity checks for Stage 06.5."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.conflict import predict_operator
from src.evidence import has_evidence_match
from src.graph_store import GraphStore
from src.io_utils import read_jsonl, write_csv
from src.schema import validate_event_schema
from src.submission_tables import render_negative_controls_table, write_tex
from src.update_ops import ALLOWED_OPERATORS


FIELDNAMES = [
    "total_cases",
    "schema_rejected",
    "evidence_rejected",
    "invalid_date_rejected",
    "unknown_operator_handled",
    "crash_count",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tex-table", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = read_jsonl(args.input)
    row = run_checks(records)
    write_csv(args.out, [row], FIELDNAMES)
    write_tex(args.tex_table, render_negative_controls_table([{key: str(value) for key, value in row.items()}]))
    print(f"Wrote sanity results: {args.out}")
    print(f"Wrote sanity LaTeX table: {args.tex_table}")
    for key in FIELDNAMES:
        print(f"{key}: {row[key]}")
    if row["crash_count"] != 0:
        raise SystemExit("negative-control sanity checks observed crashes")
    return 0


def run_checks(records: list[dict[str, Any]]) -> dict[str, int]:
    schema_rejected = 0
    evidence_rejected = 0
    invalid_date_rejected = 0
    unknown_operator_handled = 0
    crash_count = 0

    for record in records:
        negative_type = record.get("negative_control_type")
        try:
            schema_valid, schema_errors = validate_event_schema(record)
            evidence_match = has_evidence_match(record) if schema_valid else False
            if not schema_valid:
                schema_rejected += 1
            if schema_valid and not evidence_match:
                evidence_rejected += 1
            if negative_type == "invalid_date" and any("invalid ISO date" in error for error in schema_errors):
                invalid_date_rejected += 1
            if negative_type == "unknown_operator_or_unsupported_perturbation":
                predicted = predict_operator(record, GraphStore())
                if predicted in ALLOWED_OPERATORS:
                    unknown_operator_handled += 1
        except Exception:
            crash_count += 1

    return {
        "total_cases": len(records),
        "schema_rejected": schema_rejected,
        "evidence_rejected": evidence_rejected,
        "invalid_date_rejected": invalid_date_rejected,
        "unknown_operator_handled": unknown_operator_handled,
        "crash_count": crash_count,
    }


if __name__ == "__main__":
    raise SystemExit(main())
