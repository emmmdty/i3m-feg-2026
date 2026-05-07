#!/usr/bin/env python3
"""Generate deterministic negative-control records for Stage 06.5."""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import read_jsonl, write_jsonl


EVENT_FIELDS = [
    "event_id",
    "event_type",
    "subject",
    "object",
    "time",
    "trigger",
    "evidence_span",
    "amount",
    "status",
]

NEGATIVE_TYPES = (
    "missing_required_field",
    "evidence_mismatch",
    "invalid_date",
    "unknown_operator_or_unsupported_perturbation",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    samples = read_jsonl(args.input)
    if not samples:
        raise SystemExit("input samples are empty")

    records = build_negative_controls(samples, args.seed)
    write_jsonl(args.out, records)
    print(f"Wrote negative controls: {args.out} ({len(records)} records)")
    return 0


def build_negative_controls(samples: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    ordered = list(samples)
    rng.shuffle(ordered)
    records: list[dict[str, Any]] = []
    sequence = 1
    for negative_type in NEGATIVE_TYPES:
        for local_index in range(5):
            sample = ordered[(sequence - 1) % len(ordered)]
            records.append(make_negative_record(sequence, sample, negative_type, local_index))
            sequence += 1
    return records


def make_negative_record(
    sequence: int,
    sample: dict[str, Any],
    negative_type: str,
    local_index: int,
) -> dict[str, Any]:
    event = {field: sample[field] for field in EVENT_FIELDS if field in sample}
    event["event_id"] = f"{sample['event_id']}_NEG{sequence:03d}"
    source_text = str(sample.get("source_text", ""))
    source_doc_id = f"{sample['source_doc_id']}_NEG{sequence:03d}"
    perturbation_type = negative_type
    expected_operator = "ADD_EVENT"
    expected_rejection = "none"

    if negative_type == "missing_required_field":
        missing_fields = ("event_id", "event_type", "subject", "object", "trigger")
        missing_field = missing_fields[local_index % len(missing_fields)]
        event.pop(missing_field, None)
        expected_rejection = "schema"
    elif negative_type == "evidence_mismatch":
        event["evidence_span"] = f"unmatched negative evidence span {sequence:03d}"
        expected_rejection = "evidence"
    elif negative_type == "invalid_date":
        event["time"] = f"2025-99-{local_index + 1:02d}"
        expected_rejection = "schema"
    elif negative_type == "unknown_operator_or_unsupported_perturbation":
        perturbation_type = "unsupported_perturbation"
        expected_operator = "UNSUPPORTED_OPERATOR"
        expected_rejection = "operator_fallback"
    else:
        raise ValueError(f"unsupported negative control type: {negative_type}")

    return {
        "stream_record_id": f"NC{sequence:06d}",
        "base_event_id": sample.get("event_id"),
        "gold_group_id": f"NCG{sequence:06d}",
        "source_doc_id": source_doc_id,
        "arrival_index": sequence,
        "negative_control_type": negative_type,
        "perturbation_type": perturbation_type,
        "expected_operator": expected_operator,
        "expected_rejection": expected_rejection,
        "source_text": source_text,
        "event": event,
    }


if __name__ == "__main__":
    raise SystemExit(main())
