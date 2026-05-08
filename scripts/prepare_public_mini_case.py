#!/usr/bin/env python3
"""Convert a small local FewFC sample into replay records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.io import write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("data/samples/public_mini_events.jsonl"))
    parser.add_argument("--max-records", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = load_public_rows(args.input)
    converted = [convert_row(index, row) for index, row in enumerate(rows[: args.max_records], start=1)]
    if not converted:
        raise SystemExit("no parseable FewFC records found; public mini-case was not fabricated")
    write_jsonl(args.out, converted)
    print(f"Wrote public mini-case records: {args.out} ({len(converted)} records)")
    return 0


def load_public_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"input file does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"input must be JSON: {exc}") from exc
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        candidates = value.get("data") or value.get("records") or value.get("events")
        if isinstance(candidates, list):
            return [row for row in candidates if isinstance(row, dict)]
    return []


def convert_row(index: int, row: dict[str, Any]) -> dict[str, Any]:
    text = str(row.get("content") or row.get("text") or row.get("sentence") or "")
    trigger = str(row.get("trigger") or row.get("event_type") or "event")
    subject = str(row.get("subject") or row.get("company") or row.get("entity") or f"Entity {index}")
    evidence_span = trigger if trigger and trigger in text else text[: min(12, len(text))]
    if not evidence_span:
        evidence_span = subject
        text = subject
    return {
        "record_id": f"PUB{index:06d}",
        "source_dataset": "FewFC",
        "source_doc_id": f"FewFC-local-{index:06d}",
        "source_url": "https://github.com/TimeBurningFish/FewFC",
        "source_license_note": "FewFC public research dataset; see upstream repository",
        "source_text": text,
        "event_id": f"PUB-E{index:06d}",
        "event_type": str(row.get("event_type") or "financial_event"),
        "subject": subject,
        "object": str(row.get("object") or row.get("target") or "reported event"),
        "time": str(row.get("time") or row.get("date") or "1970-01-01"),
        "trigger": trigger,
        "evidence_span": evidence_span,
        "amount": str(row.get("amount") or ""),
        "status": str(row.get("status") or "observed"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
