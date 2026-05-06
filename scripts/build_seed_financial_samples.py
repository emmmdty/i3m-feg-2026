#!/usr/bin/env python3
"""Build deterministic synthetic financial event samples."""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any


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
        "verb": "appointed a new chief financial officer for one appointment",
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
    if event_type == "asset_acquisition":
        return f"{subject} acquired production assets valued at {amount}"
    if event_type == "credit_rating_change":
        return f"{subject} revised its corporate credit rating by {amount}"
    if event_type == "lawsuit":
        return f"{subject} received a commercial contract lawsuit involving {amount}"
    if event_type == "financing":
        return f"{subject} secured working capital financing of {amount}"
    return f"{subject} {template['verb']} {amount}"


def build_records(n: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    start = date(2025, 1, 3)
    records: list[dict[str, Any]] = []

    for i in range(n):
        template = EVENT_TEMPLATES[i % len(EVENT_TEMPLATES)]
        subject = COMPANIES[i % len(COMPANIES)]
        event_date = start + timedelta(days=i * 3 + rng.randint(0, 1))
        amount = amount_for(template, i)
        evidence_span = evidence_for(subject, template, amount)
        source_text = (
            f"{subject} announced that {evidence_span} on {event_date.isoformat()}. "
            f"The notice stated the status as {template['status']} and did not include market guidance."
        )

        records.append(
            {
                "record_id": f"R{i + 1:06d}",
                "source_doc_id": f"D{i + 1:06d}",
                "source_text": source_text,
                "event_id": f"E{i + 1:06d}",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("data/samples/seed_financial_events.jsonl"))
    parser.add_argument("--n", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.n < 1:
        raise SystemExit("--n must be positive")

    records = build_records(args.n, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"Wrote seed financial samples: {args.out} ({len(records)} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
