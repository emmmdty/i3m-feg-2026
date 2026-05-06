#!/usr/bin/env python3
"""Validate Stage 1 data artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


SAMPLE_REQUIRED_FIELDS = {
    "record_id",
    "source_doc_id",
    "source_text",
    "event_id",
    "event_type",
    "subject",
    "object",
    "time",
    "trigger",
    "evidence_span",
    "amount",
    "status",
}
STREAM_REQUIRED_FIELDS = {
    "stream_record_id",
    "base_event_id",
    "gold_group_id",
    "source_doc_id",
    "arrival_index",
    "perturbation_type",
    "expected_operator",
    "source_text",
    "event",
}
EVENT_REQUIRED_FIELDS = {
    "event_id",
    "event_type",
    "subject",
    "object",
    "time",
    "trigger",
    "evidence_span",
    "amount",
    "status",
}
ALLOWED_OPERATORS = {"ADD_EVENT", "MERGE_EVENT", "UPDATE_SLOT", "MARK_CONFLICT"}
REQUIRED_PERTURBATIONS = {"duplicate", "conflict", "update", "temporal_shuffle"}


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records, [f"missing file: {path}"]

    with path.open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(value, dict):
                errors.append(f"{path}:{line_number}: JSONL record must be an object")
                continue
            records.append(value)
    return records, errors


def evidence_matches(source_text: Any, evidence_span: Any) -> bool:
    return isinstance(source_text, str) and isinstance(evidence_span, str) and evidence_span != "" and evidence_span in source_text


def validate_samples(path: Path) -> tuple[dict[str, Any], list[str]]:
    records, errors = read_jsonl(path)
    schema_valid = 0
    evidence_valid = 0

    for index, record in enumerate(records, start=1):
        missing = SAMPLE_REQUIRED_FIELDS - record.keys()
        if missing:
            errors.append(f"{path}:{index}: missing sample fields: {sorted(missing)}")
            continue
        schema_valid += 1
        if evidence_matches(record["source_text"], record["evidence_span"]):
            evidence_valid += 1
        else:
            errors.append(f"{path}:{index}: evidence_span not found in source_text")

    summary = {
        "file": path.as_posix(),
        "num_records": len(records),
        "num_schema_valid": schema_valid,
        "evidence_match_rate": evidence_valid / len(records) if records else 0.0,
        "num_base": 0,
        "num_duplicate": 0,
        "num_conflict": 0,
        "num_update": 0,
        "num_temporal_shuffle": 0,
    }
    return summary, errors


def validate_stream(path: Path) -> tuple[dict[str, Any], list[str]]:
    records, errors = read_jsonl(path)
    schema_valid = 0
    evidence_valid = 0
    counts: Counter[str] = Counter()

    for index, record in enumerate(records, start=1):
        missing = STREAM_REQUIRED_FIELDS - record.keys()
        if missing:
            errors.append(f"{path}:{index}: missing stream fields: {sorted(missing)}")
            continue
        if record["expected_operator"] not in ALLOWED_OPERATORS:
            errors.append(f"{path}:{index}: invalid expected_operator: {record['expected_operator']}")
            continue
        if not isinstance(record["event"], dict):
            errors.append(f"{path}:{index}: event must be an object")
            continue
        event_missing = EVENT_REQUIRED_FIELDS - record["event"].keys()
        if event_missing:
            errors.append(f"{path}:{index}: missing event fields: {sorted(event_missing)}")
            continue

        schema_valid += 1
        perturbation_type = str(record["perturbation_type"])
        counts[perturbation_type] += 1
        if evidence_matches(record["source_text"], record["event"]["evidence_span"]):
            evidence_valid += 1
        else:
            errors.append(f"{path}:{index}: event.evidence_span not found in source_text")

    for perturbation in REQUIRED_PERTURBATIONS:
        if counts[perturbation] < 10:
            errors.append(f"{path}: expected at least 10 {perturbation} records, found {counts[perturbation]}")

    summary = {
        "file": path.as_posix(),
        "num_records": len(records),
        "num_schema_valid": schema_valid,
        "evidence_match_rate": evidence_valid / len(records) if records else 0.0,
        "num_base": counts["base"],
        "num_duplicate": counts["duplicate"],
        "num_conflict": counts["conflict"],
        "num_update": counts["update"],
        "num_temporal_shuffle": counts["temporal_shuffle"],
    }
    return summary, errors


def write_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "file",
        "num_records",
        "num_schema_valid",
        "evidence_match_rate",
        "num_base",
        "num_duplicate",
        "num_conflict",
        "num_update",
        "num_temporal_shuffle",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row = dict(row)
            row["evidence_match_rate"] = f"{row['evidence_match_rate']:.6f}"
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--stream", type=Path, required=True)
    parser.add_argument("--summary", type=Path, default=Path("tables/stage1_data_summary.csv"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sample_summary, sample_errors = validate_samples(args.samples)
    stream_summary, stream_errors = validate_stream(args.stream)
    rows = [sample_summary, stream_summary]
    write_summary(args.summary, rows)

    errors = sample_errors + stream_errors
    if errors:
        print("Stage 1 data validation failed:")
        for error in errors:
            print(f"- {error}")
        print(f"Wrote summary: {args.summary}")
        return 1

    print(f"Stage 1 data validation passed. Wrote summary: {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
