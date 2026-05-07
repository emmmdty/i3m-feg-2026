#!/usr/bin/env python3
"""Generate a deterministic controlled perturbation stream."""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any


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


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            records.append(record)
    return records


def event_payload(sample: dict[str, Any], event_id: str | None = None) -> dict[str, Any]:
    event = {field: sample[field] for field in EVENT_FIELDS}
    if event_id is not None:
        event["event_id"] = event_id
    return event


def stream_record(
    sequence: int,
    sample: dict[str, Any],
    perturbation_type: str,
    expected_operator: str,
    source_doc_id: str,
    source_text: str,
    event: dict[str, Any],
    temporal_shuffle: bool = False,
) -> dict[str, Any]:
    base_number = int(str(sample["event_id"]).lstrip("E"))
    record = {
        "stream_record_id": f"S{sequence:06d}",
        "base_event_id": sample["event_id"],
        "gold_group_id": f"G{base_number:06d}",
        "source_doc_id": source_doc_id,
        "arrival_index": sequence,
        "perturbation_type": perturbation_type,
        "expected_operator": expected_operator,
        "source_text": source_text,
        "event": event,
    }
    if temporal_shuffle:
        record["temporal_shuffle"] = True
    return record


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def amount_variant(amount: str, delta: int) -> str:
    parts = amount.split(" ", 1)
    try:
        value = int(parts[0])
    except (ValueError, IndexError):
        return f"revised {amount}"
    unit = parts[1] if len(parts) > 1 else "units"
    return f"{max(1, value + delta)} {unit}"


def make_duplicate(sequence: int, sample: dict[str, Any], copy_index: int) -> dict[str, Any]:
    event = event_payload(sample, f"{sample['event_id']}_DUP{copy_index:03d}")
    evidence_span = f"{sample['subject']} reported the same {sample['event_type']} with {sample['amount']}"
    event["evidence_span"] = evidence_span
    source_text = (
        f"Follow-up notice: {evidence_span} on {sample['time']}. "
        f"The status remained {sample['status']}."
    )
    return stream_record(
        sequence,
        sample,
        "duplicate",
        "MERGE_EVENT",
        f"{sample['source_doc_id']}_DUP{copy_index:03d}",
        source_text,
        event,
    )


def make_conflict(sequence: int, sample: dict[str, Any], copy_index: int) -> dict[str, Any]:
    event = event_payload(sample, f"{sample['event_id']}_CON{copy_index:03d}")
    event["amount"] = amount_variant(str(sample["amount"]), 7)
    event["status"] = "withdrawn" if sample["status"] != "withdrawn" else "announced"
    conflict_date = parse_date(sample["time"]) + timedelta(days=1)
    event["time"] = conflict_date.isoformat()
    evidence_span = (
        f"{sample['subject']} reported {event['amount']} with status {event['status']}"
    )
    event["evidence_span"] = evidence_span
    source_text = (
        f"Separate filing: {evidence_span} for the same {sample['event_type']} case. "
        f"The filing date was {event['time']}."
    )
    return stream_record(
        sequence,
        sample,
        "conflict",
        "MARK_CONFLICT",
        f"{sample['source_doc_id']}_CON{copy_index:03d}",
        source_text,
        event,
    )


def make_update(sequence: int, sample: dict[str, Any], copy_index: int) -> dict[str, Any]:
    event = event_payload(sample, f"{sample['event_id']}_UPD{copy_index:03d}")
    event["amount"] = amount_variant(str(sample["amount"]), 2)
    event["status"] = "revised"
    if sample["event_type"] == "executive_change":
        event["object"] = "chief operating officer role"
    update_date = parse_date(sample["time"]) + timedelta(days=2)
    event["time"] = update_date.isoformat()
    evidence_span = (
        f"{sample['subject']} issued a revision changing the amount to {event['amount']}"
    )
    event["evidence_span"] = evidence_span
    source_text = (
        f"Revision notice: {evidence_span} and set the status to {event['status']}. "
        f"The revision referred to the prior {sample['event_type']} disclosure."
    )
    return stream_record(
        sequence,
        sample,
        "update",
        "UPDATE_SLOT",
        f"{sample['source_doc_id']}_UPD{copy_index:03d}",
        source_text,
        event,
    )


def make_temporal_shuffle(sequence: int, sample: dict[str, Any], copy_index: int) -> dict[str, Any]:
    event = event_payload(sample, f"{sample['event_id']}_TS{copy_index:03d}")
    evidence_span = f"{sample['subject']} replay record preserved {sample['event_type']} evidence"
    event["evidence_span"] = evidence_span
    source_text = (
        f"Out-of-order replay input: {evidence_span}. "
        f"The original event date was {sample['time']}."
    )
    return stream_record(
        sequence,
        sample,
        "temporal_shuffle",
        "ADD_EVENT",
        f"{sample['source_doc_id']}_TS{copy_index:03d}",
        source_text,
        event,
        temporal_shuffle=True,
    )


def take_samples(samples: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    if not samples:
        raise SystemExit("input samples are empty")
    return [samples[i % len(samples)] for i in range(count)]


def build_stream(
    samples: list[dict[str, Any]],
    seed: int,
    duplicates: int,
    conflicts: int,
    updates: int,
    temporal_shuffles: int,
    shuffle: bool,
) -> list[dict[str, Any]]:
    sequence = 1
    stream: list[dict[str, Any]] = []

    for sample in samples:
        stream.append(
            stream_record(
                sequence,
                sample,
                "base",
                "ADD_EVENT",
                sample["source_doc_id"],
                sample["source_text"],
                event_payload(sample),
            )
        )
        sequence += 1

    for copy_index, sample in enumerate(take_samples(samples, duplicates), start=1):
        stream.append(make_duplicate(sequence, sample, copy_index))
        sequence += 1

    for copy_index, sample in enumerate(take_samples(samples, conflicts), start=1):
        stream.append(make_conflict(sequence, sample, copy_index))
        sequence += 1

    for copy_index, sample in enumerate(take_samples(samples, updates), start=1):
        stream.append(make_update(sequence, sample, copy_index))
        sequence += 1

    for copy_index, sample in enumerate(take_samples(samples, temporal_shuffles), start=1):
        stream.append(make_temporal_shuffle(sequence, sample, copy_index))
        sequence += 1

    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(stream)
        for arrival_index, record in enumerate(stream, start=1):
            record["arrival_index"] = arrival_index

    return stream


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--duplicates", type=int, default=10)
    parser.add_argument("--conflicts", type=int, default=10)
    parser.add_argument("--updates", type=int, default=10)
    parser.add_argument("--temporal-shuffles", type=int, default=10)
    parser.add_argument("--shuffle", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    samples = read_jsonl(args.input)
    stream = build_stream(
        samples,
        args.seed,
        args.duplicates,
        args.conflicts,
        args.updates,
        args.temporal_shuffles,
        args.shuffle,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for record in stream:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"Wrote controlled perturbation stream: {args.out} ({len(stream)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
