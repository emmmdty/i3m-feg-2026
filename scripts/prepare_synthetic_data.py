#!/usr/bin/env python3
"""Prepare deterministic synthetic records and a controlled replay stream."""

from __future__ import annotations

import argparse
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.io import write_jsonl


EVENT_TEMPLATES: list[dict[str, str]] = [
    {
        "event_type": "equity_pledge",
        "object": "shares",
        "trigger": "pledged",
        "amount_unit": "million shares",
        "status": "announced",
        "verb": "pledged",
    },
    {
        "event_type": "share_repurchase",
        "object": "shares",
        "trigger": "repurchased",
        "amount_unit": "million shares",
        "status": "announced",
        "verb": "repurchased",
    },
    {
        "event_type": "executive_change",
        "object": "chief financial officer role",
        "trigger": "appointed",
        "amount_unit": "appointment",
        "status": "approved",
        "verb": "appointed a new chief financial officer",
    },
    {
        "event_type": "asset_acquisition",
        "object": "production assets",
        "trigger": "acquired",
        "amount_unit": "million yuan",
        "status": "announced",
        "verb": "acquired production assets valued at",
    },
    {
        "event_type": "credit_rating_change",
        "object": "corporate credit rating",
        "trigger": "revised",
        "amount_unit": "rating level",
        "status": "updated",
        "verb": "revised its corporate credit rating by",
    },
    {
        "event_type": "lawsuit",
        "object": "commercial contract dispute",
        "trigger": "received",
        "amount_unit": "million yuan claim",
        "status": "filed",
        "verb": "received a commercial contract lawsuit involving",
    },
    {
        "event_type": "financing",
        "object": "working capital financing",
        "trigger": "secured",
        "amount_unit": "million yuan",
        "status": "completed",
        "verb": "secured working capital financing of",
    },
]

COMPANIES = [
    "Company A",
    "Company B",
    "Company C",
    "Company D",
    "Company E",
    "Company F",
    "Company G",
    "Company H",
    "Company I",
    "Company J",
]

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


def build_seed_records(count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    start = date(2025, 1, 3)
    records: list[dict[str, Any]] = []
    for index in range(count):
        template = EVENT_TEMPLATES[index % len(EVENT_TEMPLATES)]
        subject = COMPANIES[index % len(COMPANIES)]
        event_date = start + timedelta(days=index * 3 + rng.randint(0, 1))
        amount = amount_for(template, index)
        evidence_span = evidence_for(subject, template, amount)
        source_text = (
            f"{subject} announced that {evidence_span} on {event_date.isoformat()}. "
            f"The notice stated the status as {template['status']} and did not include financial guidance."
        )
        records.append(
            {
                "record_id": f"R{index + 1:06d}",
                "source_doc_id": f"D{index + 1:06d}",
                "source_text": source_text,
                "event_id": f"E{index + 1:06d}",
                "event_type": template["event_type"],
                "subject": subject,
                "object": template["object"],
                "time": event_date.isoformat(),
                "trigger": template["trigger"],
                "evidence_span": evidence_span,
                "amount": amount,
                "status": template["status"],
            }
        )
    return records


def amount_for(template: dict[str, str], index: int) -> str:
    if template["event_type"] == "executive_change":
        return "one appointment"
    if template["event_type"] == "credit_rating_change":
        levels = ["one rating level", "two rating levels", "one outlook level"]
        return levels[index % len(levels)]
    value = 5 + (index % 9) * 3
    return f"{value} {template['amount_unit']}"


def evidence_for(subject: str, template: dict[str, str], amount: str) -> str:
    event_type = template["event_type"]
    if event_type == "executive_change":
        return f"{subject} appointed a new chief financial officer"
    if event_type in {"asset_acquisition", "credit_rating_change", "lawsuit", "financing"}:
        return f"{subject} {template['verb']} {amount}"
    return f"{subject} {template['verb']} {amount}"


def build_controlled_stream(
    samples: list[dict[str, Any]],
    seed: int,
    perturbation_count: int | None = None,
) -> list[dict[str, Any]]:
    sequence = 1
    stream: list[dict[str, Any]] = []
    count = perturbation_count if perturbation_count is not None else 10
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

    for copy_index, sample in enumerate(take_samples(samples, count), start=1):
        stream.append(make_duplicate(sequence, sample, copy_index))
        sequence += 1
    for copy_index, sample in enumerate(take_samples(samples, count), start=1):
        stream.append(make_conflict(sequence, sample, copy_index))
        sequence += 1
    for copy_index, sample in enumerate(take_samples(samples, count), start=1):
        stream.append(make_update(sequence, sample, copy_index))
        sequence += 1
    for copy_index, sample in enumerate(take_samples(samples, count), start=1):
        stream.append(make_temporal_record(sequence, sample, copy_index))
        sequence += 1

    rng = random.Random(seed)
    rng.shuffle(stream)
    for arrival_index, record in enumerate(stream, start=1):
        record["arrival_index"] = arrival_index
    return stream


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
) -> dict[str, Any]:
    base_number = int(str(sample["event_id"]).lstrip("E"))
    return {
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
    event["time"] = (date.fromisoformat(sample["time"]) + timedelta(days=1)).isoformat()
    evidence_span = f"{sample['subject']} reported {event['amount']} with status {event['status']}"
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
    event["time"] = (date.fromisoformat(sample["time"]) + timedelta(days=2)).isoformat()
    evidence_span = f"{sample['subject']} issued a revision changing the amount to {event['amount']}"
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


def make_temporal_record(sequence: int, sample: dict[str, Any], copy_index: int) -> dict[str, Any]:
    event = event_payload(sample, f"{sample['event_id']}_TS{copy_index:03d}")
    evidence_span = f"{sample['subject']} replay record preserved {sample['event_type']} evidence"
    event["evidence_span"] = evidence_span
    source_text = f"Out-of-order replay input: {evidence_span}. The original event date was {sample['time']}."
    record = stream_record(
        sequence,
        sample,
        "temporal_shuffle",
        "ADD_EVENT",
        f"{sample['source_doc_id']}_TS{copy_index:03d}",
        source_text,
        event,
    )
    record["temporal_shuffle"] = True
    return record


def amount_variant(amount: str, delta: int) -> str:
    parts = amount.split(" ", 1)
    try:
        value = int(parts[0])
    except (ValueError, IndexError):
        return f"revised {amount}"
    unit = parts[1] if len(parts) > 1 else "units"
    return f"{max(1, value + delta)} {unit}"


def take_samples(samples: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    if not samples:
        raise SystemExit("input samples are empty")
    return [samples[index % len(samples)] for index in range(count)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-out", type=Path, default=Path("data/samples/seed_financial_events.jsonl"))
    parser.add_argument("--stream-out", type=Path, default=Path("data/processed/controlled_stream.jsonl"))
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count must be positive")
    samples = build_seed_records(args.count, args.seed)
    stream = build_controlled_stream(samples, args.seed)
    write_jsonl(args.seed_out, samples)
    write_jsonl(args.stream_out, stream)
    print(f"Wrote seed records: {args.seed_out} ({len(samples)} records)")
    print(f"Wrote controlled stream: {args.stream_out} ({len(stream)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
