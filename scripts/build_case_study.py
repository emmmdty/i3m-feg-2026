#!/usr/bin/env python3
"""Build a compact case-study table from replay artifacts."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import read_jsonl


FIELDNAMES = [
    "case_id",
    "replay_step",
    "operator",
    "stream_record_id",
    "base_event_id",
    "event_id",
    "target_event_id",
    "conflict_id",
    "source_doc_id",
    "summary",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--updates", type=Path, required=True)
    parser.add_argument("--conflicts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    replay = read_jsonl(args.replay)
    updates = read_jsonl(args.updates)
    conflicts = read_jsonl(args.conflicts)

    replay_by_step = {item.get("replay_step"): item for item in replay}
    conflict_by_step = {item.get("replay_step"): item for item in conflicts}
    rows = build_rows(updates, replay_by_step, conflict_by_step)
    if not rows:
        raise SystemExit("No case-study rows could be built from update artifacts.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    operators = sorted({row["operator"] for row in rows})
    print(f"Wrote case study: {args.out} ({len(rows)} rows; operators={','.join(operators)})")
    return 0


def build_rows(
    updates: list[dict[str, Any]],
    replay_by_step: dict[Any, dict[str, Any]],
    conflict_by_step: dict[Any, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, update in enumerate(sorted(updates, key=lambda item: int(item.get("replay_step", 0))), start=1):
        replay = replay_by_step.get(update.get("replay_step"), {})
        conflict = conflict_by_step.get(update.get("replay_step"), {})
        operator = str(update.get("operator", ""))
        rows.append(
            {
                "case_id": f"CS{index:04d}",
                "replay_step": update.get("replay_step", ""),
                "operator": operator,
                "stream_record_id": update.get("stream_record_id") or replay.get("stream_record_id", ""),
                "base_event_id": update.get("base_event_id") or replay.get("base_event_id", ""),
                "event_id": update.get("event_id", ""),
                "target_event_id": update.get("target_event_id", ""),
                "conflict_id": conflict.get("conflict_id", ""),
                "source_doc_id": update.get("source_doc_id") or conflict.get("source_doc_id", ""),
                "summary": summarize_row(operator, update, replay, conflict),
            }
        )
    return rows


def summarize_row(
    operator: str,
    update: dict[str, Any],
    replay: dict[str, Any],
    conflict: dict[str, Any],
) -> str:
    if operator == "ADD_EVENT":
        return "Added an evidence-backed event node to the active graph."
    if operator == "MERGE_EVENT":
        return f"Merged duplicate event into target {update.get('target_event_id', '')}."
    if operator == "UPDATE_SLOT":
        changed = sorted((update.get("details") or {}).get("changed_fields", {}).keys())
        return "Updated slots: " + (", ".join(changed) if changed else "recorded update operation")
    if operator == "MARK_CONFLICT":
        return f"Marked unresolved conflict {conflict.get('conflict_id', '')}."
    expected = replay.get("expected_operator", "")
    return f"Recorded operation; expected operator was {expected}."


if __name__ == "__main__":
    raise SystemExit(main())
