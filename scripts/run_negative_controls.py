#!/usr/bin/env python3
"""Run negative controls for gate and unsupported-metadata behavior."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.io import read_jsonl, write_csv, write_jsonl
from src.feg_replay.schema import validate_event_schema
from src.feg_replay.simulator import simulate_replay
from src.feg_replay.table_rendering import render_negative_controls_table, write_tex


FIELDNAMES = [
    "total_cases",
    "schema_rejected",
    "evidence_rejected",
    "invalid_date_rejected",
    "unsupported_metadata_logged",
    "crash_count",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-input", type=Path, default=Path("data/samples/seed_financial_events.jsonl"))
    parser.add_argument("--stream-out", type=Path, default=Path("data/processed/negative_control_stream.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("tables/negative_controls_results.csv"))
    parser.add_argument("--tex-table", type=Path, default=Path("paper/i3m_submission/tables/table_negative_controls.tex"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = build_negative_controls(read_jsonl(args.seed_input))
    write_jsonl(args.stream_out, records)
    row = evaluate_negative_controls(records)
    write_csv(args.out, [row], FIELDNAMES)
    write_tex(args.tex_table, render_negative_controls_table([{key: str(value) for key, value in row.items()}]))
    print(f"Wrote negative-control stream: {args.stream_out}")
    print(f"Wrote negative-control results: {args.out}")
    print(f"Wrote negative-control table: {args.tex_table}")
    if row["crash_count"] != 0:
        raise SystemExit("negative controls observed crashes")
    return 0


def build_negative_controls(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not samples:
        raise SystemExit("seed input is empty")
    records: list[dict[str, Any]] = []
    sequence = 1
    control_types = (
        "missing_required_field",
        "evidence_mismatch",
        "invalid_date",
        "unknown_operator_or_unsupported_metadata",
    )
    for control_type in control_types:
        for local_index in range(5):
            sample = samples[(sequence - 1) % len(samples)]
            records.append(make_negative_record(sequence, sample, control_type, local_index))
            sequence += 1
    return records


def make_negative_record(
    sequence: int,
    sample: dict[str, Any],
    control_type: str,
    local_index: int,
) -> dict[str, Any]:
    event = dict(sample)
    event["event_id"] = f"{sample['event_id']}_NEG{sequence:03d}"
    expected_operator = "ADD_EVENT"
    perturbation_type = "base"
    if control_type == "missing_required_field":
        missing_fields = ("event_id", "event_type", "subject", "object", "trigger")
        event.pop(missing_fields[local_index % len(missing_fields)], None)
    elif control_type == "evidence_mismatch":
        event["evidence_span"] = f"unmatched evidence span {sequence:03d}"
    elif control_type == "invalid_date":
        event["time"] = f"2025-99-{local_index + 1:02d}"
    elif control_type == "unknown_operator_or_unsupported_metadata":
        perturbation_type = "unsupported_metadata"
        expected_operator = "UNSUPPORTED_OPERATOR"
    else:
        raise ValueError(f"unsupported control type: {control_type}")

    return {
        "stream_record_id": f"NC{sequence:06d}",
        "base_event_id": sample.get("event_id"),
        "gold_group_id": f"NCG{sequence:06d}",
        "source_doc_id": f"{sample['source_doc_id']}_NC{sequence:03d}",
        "arrival_index": sequence,
        "negative_control_type": control_type,
        "perturbation_type": perturbation_type,
        "expected_operator": expected_operator,
        "source_text": sample.get("source_text", ""),
        "event": event,
    }


def evaluate_negative_controls(records: list[dict[str, Any]]) -> dict[str, int]:
    schema_rejected = 0
    evidence_rejected = 0
    invalid_date_rejected = 0
    unsupported_metadata_logged = 0
    crash_count = 0
    for record in records:
        try:
            schema_valid, schema_errors = validate_event_schema(record)
            result = simulate_replay([record], policy_mode="oracle")
            trace = result.replay_trace[0]
            if not schema_valid:
                schema_rejected += 1
            if schema_valid and trace.get("skipped_reason") == "evidence_missing":
                evidence_rejected += 1
            if any("invalid ISO date" in error for error in schema_errors):
                invalid_date_rejected += 1
            if trace.get("unsupported_metadata_logged"):
                unsupported_metadata_logged += 1
        except Exception:
            crash_count += 1
    return {
        "total_cases": len(records),
        "schema_rejected": schema_rejected,
        "evidence_rejected": evidence_rejected,
        "invalid_date_rejected": invalid_date_rejected,
        "unsupported_metadata_logged": unsupported_metadata_logged,
        "crash_count": crash_count,
    }


if __name__ == "__main__":
    raise SystemExit(main())
