#!/usr/bin/env python3
"""Prepare a tiny public financial-event mini-case for replay validation."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.io_utils import write_jsonl


FEWFC_SOURCE_URL = "https://github.com/TimeBurningFish/FewFC"
FEWFC_LICENSE_NOTE = "FewFC public research dataset; CC BY-SA 4.0; see upstream repository"
DEFAULT_DATE = "1970-01-01"

FEWFC_PRIORITY_FILES = (
    "original/dev_base.json",
    "rearranged/test_base.json",
    "original/train_base.json",
    "rearranged/train_base.json",
    "original/dev_trans.json",
    "original/test_trans.json",
)

SUBJECT_ROLE_HINTS = ("sub", "subject", "share-org", "share-per")
OBJECT_ROLE_HINTS = ("obj", "target", "collateral", "title")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("auto", "fewfc", "local"), default="auto")
    parser.add_argument("--input-dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-records", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_records < 1:
        raise SystemExit("--max-records must be positive")
    if args.max_records > 30:
        raise SystemExit("--max-records must not exceed 30 for the public mini-case")

    input_dirs = default_input_dirs(args.input_dir)
    candidates: list[dict[str, Any]] = []
    dataset_name = ""

    if args.source in {"auto", "fewfc"}:
        candidates = collect_fewfc_candidates(input_dirs)
        dataset_name = "FewFC"
        if args.source == "fewfc" and not candidates:
            raise SystemExit("FewFC source requested but no parseable FewFC records were found")

    if args.source in {"auto", "local"} and not candidates:
        candidates = collect_docfee_candidates(input_dirs)
        dataset_name = "DocFEE"
        if args.source == "local" and not candidates:
            raise SystemExit("Local source requested but no parseable public financial records were found")

    if not candidates:
        raise SystemExit(
            "No parseable public mini-case source found. Stage 6.8 should report dataset access/format blockage."
        )

    rng = random.Random(args.seed)
    rng.shuffle(candidates)
    selected = candidates[: args.max_records]
    if len(selected) < min(10, args.max_records):
        raise SystemExit(f"Only found {len(selected)} public records; need at least 10 for the mini-case")

    records = [to_public_record(item, index, dataset_name) for index, item in enumerate(selected, start=1)]
    write_jsonl(args.out, records)
    print(f"Wrote public mini-case records: {args.out}")
    print(f"source_dataset: {dataset_name}")
    print(f"num_records: {len(records)}")
    return 0


def default_input_dirs(input_dir: Path | None) -> list[Path]:
    if input_dir is not None:
        return [input_dir]
    return [PROJECT_ROOT / "data" / "raw", PROJECT_ROOT / "data" / "external"]


def collect_fewfc_candidates(input_dirs: list[Path]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for root in find_fewfc_roots(input_dirs):
        for source_file in fewfc_files(root):
            for source_record in iter_json_records(source_file):
                candidates.extend(fewfc_record_candidates(source_record, source_file, root))
    return candidates


def find_fewfc_roots(input_dirs: list[Path]) -> list[Path]:
    roots: list[Path] = []
    for input_dir in input_dirs:
        for candidate in (input_dir, input_dir / "FewFC"):
            if (candidate / "README.md").exists() and (
                (candidate / "original").exists() or (candidate / "rearranged").exists()
            ):
                roots.append(candidate)
    seen: set[Path] = set()
    unique_roots: list[Path] = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_roots.append(root)
    return unique_roots


def fewfc_files(root: Path) -> list[Path]:
    ordered: list[Path] = []
    for relative in FEWFC_PRIORITY_FILES:
        path = root / relative
        if path.exists():
            ordered.append(path)
    fallback = [
        path
        for path in sorted(root.rglob("*.json"))
        if ".git" not in path.parts and path not in ordered
    ]
    return ordered + fallback


def fewfc_record_candidates(record: dict[str, Any], source_file: Path, root: Path) -> list[dict[str, Any]]:
    content = as_text(record.get("content"))
    source_id = as_text(record.get("id"))
    if not content or not source_id:
        return []

    candidates: list[dict[str, Any]] = []
    events = record.get("events")
    if not isinstance(events, list):
        return candidates

    for event_index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            continue
        event_type = as_text(event.get("type"))
        mentions = [mention for mention in event.get("mentions", []) if isinstance(mention, dict)]
        trigger = select_trigger(mentions, content)
        subject = select_role_value(mentions, SUBJECT_ROLE_HINTS, used_values=set())
        used = {subject} if subject else set()
        object_value = select_role_value(mentions, OBJECT_ROLE_HINTS, used_values=used)
        if not object_value:
            object_value = select_any_argument(mentions, used_values=used)
        if not event_type or not trigger or not subject or not object_value:
            continue
        date_value, date_note = extract_date(mentions, content)
        candidates.append(
            {
                "dataset": "FewFC",
                "source_file": source_file.relative_to(root).as_posix(),
                "source_id": source_id,
                "source_text": content,
                "event_type": event_type,
                "subject": subject,
                "object": object_value,
                "time": date_value,
                "trigger": trigger,
                "evidence_span": trigger,
                "amount": select_role_value(mentions, ("money", "number", "proportion"), used_values=set()) or "",
                "status": "observed",
                "event_index": event_index,
                "extra_notes": date_note,
            }
        )
    return candidates


def collect_docfee_candidates(input_dirs: list[Path]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for input_dir in input_dirs:
        for path in sorted(input_dir.rglob("*.jsonl")):
            if ".git" in path.parts or "DocFEE" not in path.parts:
                continue
            for line_index, record in enumerate(iter_json_records(path), start=1):
                content = strip_markup(as_text(record.get("content") or record.get("context")))
                event_type = as_text(record.get("title") or record.get("event_type"))
                trigger = strip_markup(as_text(record.get("question") or record.get("trigger")))
                answer = strip_markup(as_text(record.get("answer")))
                if not content or not event_type or not trigger or trigger not in content or not answer:
                    continue
                date_value, date_note = extract_date([], content)
                candidates.append(
                    {
                        "dataset": "DocFEE",
                        "source_file": path.name,
                        "source_id": f"docfee-{line_index}",
                        "source_text": content,
                        "event_type": event_type,
                        "subject": answer,
                        "object": event_type,
                        "time": date_value,
                        "trigger": trigger,
                        "evidence_span": trigger,
                        "amount": "",
                        "status": "observed",
                        "event_index": line_index,
                        "extra_notes": date_note,
                    }
                )
    return candidates


def iter_json_records(path: Path) -> Iterable[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return
    if text.startswith("["):
        value = json.loads(text)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield item
        return
    for line_number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if isinstance(value, dict):
            yield value


def to_public_record(item: dict[str, Any], index: int, dataset_name: str) -> dict[str, Any]:
    record_id = f"PUB{index:06d}"
    event_id = f"PUB-E{index:06d}"
    source_doc_id = f"{dataset_name}-{item['source_file']}-{item['source_id']}-{item['event_index']}"
    return {
        "record_id": record_id,
        "source_dataset": dataset_name,
        "source_license_note": FEWFC_LICENSE_NOTE if dataset_name == "FewFC" else "public research dataset; see upstream source",
        "source_doc_id": source_doc_id,
        "source_text": item["source_text"],
        "event_id": event_id,
        "event_type": item["event_type"],
        "subject": item["subject"],
        "object": item["object"],
        "time": item["time"],
        "trigger": item["trigger"],
        "evidence_span": item["evidence_span"],
        "amount": item["amount"],
        "status": item["status"],
        "source_url": FEWFC_SOURCE_URL if dataset_name == "FewFC" else "",
        "extra_notes": item["extra_notes"],
    }


def select_trigger(mentions: list[dict[str, Any]], content: str) -> str:
    for mention in mentions:
        if as_text(mention.get("role")).lower() != "trigger":
            continue
        word = as_text(mention.get("word"))
        if word and word in content:
            return word
    return ""


def select_role_value(
    mentions: list[dict[str, Any]],
    role_hints: tuple[str, ...],
    used_values: set[str],
) -> str:
    for mention in mentions:
        role = as_text(mention.get("role")).lower()
        word = as_text(mention.get("word"))
        if not word or word in used_values or role == "trigger":
            continue
        if any(hint in role for hint in role_hints):
            return word
    return ""


def select_any_argument(mentions: list[dict[str, Any]], used_values: set[str]) -> str:
    for mention in mentions:
        role = as_text(mention.get("role")).lower()
        word = as_text(mention.get("word"))
        if word and word not in used_values and role != "trigger":
            return word
    return ""


def extract_date(mentions: list[dict[str, Any]], content: str) -> tuple[str, str]:
    for mention in mentions:
        if as_text(mention.get("role")).lower() == "date":
            date_text = as_text(mention.get("word"))
            normalized = normalize_chinese_date(date_text)
            if normalized:
                return normalized, ""
            return DEFAULT_DATE, f"date unavailable in public mini-case source; original date mention: {date_text}"

    match = re.search(r"(20\d{2})[./-](\d{1,2})[./-](\d{1,2})", content)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}", ""
    match = re.search(r"(20\d{2})年(\d{1,2})月(\d{1,2})日", content)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}", ""
    match = re.search(r"(20\d{2})年(\d{1,2})月", content)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-01", ""
    return DEFAULT_DATE, "date unavailable in public mini-case source"


def normalize_chinese_date(text: str) -> str:
    match = re.search(r"(20\d{2})年(\d{1,2})月(\d{1,2})日", text)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    match = re.search(r"(20\d{2})年(\d{1,2})月", text)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-01"
    match = re.search(r"(20\d{2})", text)
    if match:
        return f"{match.group(1)}-01-01"
    return ""


def strip_markup(text: str) -> str:
    return text.replace("[T]", "").replace("<br>", " ").strip()


def as_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


if __name__ == "__main__":
    raise SystemExit(main())
