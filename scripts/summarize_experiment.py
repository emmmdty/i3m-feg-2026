#!/usr/bin/env python3
"""Summarize Stage 03 ablation, case-study, and replay artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_METHODS = {"Direct", "Schema", "Evidence", "Full"}
CORE_OPERATORS = {"ADD_EVENT", "MERGE_EVENT", "UPDATE_SLOT", "MARK_CONFLICT"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ablation", type=Path, required=True)
    parser.add_argument("--case-study", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ablation_rows = read_csv(args.ablation)
    case_rows = read_csv(args.case_study)
    replay_rows = read_jsonl(args.replay)
    content = render_summary(args, ablation_rows, case_rows, replay_rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(content, encoding="utf-8")
    print(f"Wrote experiment summary: {args.out}")
    return 0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
    return rows


def render_summary(
    args: argparse.Namespace,
    ablation_rows: list[dict[str, str]],
    case_rows: list[dict[str, str]],
    replay_rows: list[dict[str, Any]],
) -> str:
    methods = {row.get("method", "") for row in ablation_rows}
    operators = Counter(row.get("operator", "") for row in case_rows if row.get("operator"))
    replay_count = len(replay_rows)
    full_row = next((row for row in ablation_rows if row.get("method") == "Full"), {})
    missing_methods = sorted(REQUIRED_METHODS - methods)
    core_present = sorted(CORE_OPERATORS & set(operators))
    passed = not missing_methods and len(core_present) >= 2 and replay_count > 0

    lines = [
        "# Stage 03 Experiment Summary",
        "",
        "## Training",
        "",
        "- training: no_gpu_training_required",
        "- gpu_training: no_gpu_training_required",
        "- external_api_calls: none",
        "",
        "## Inputs",
        "",
        f"- ablation: `{args.ablation}`",
        f"- case_study: `{args.case_study}`",
        f"- replay: `{args.replay}`",
        "",
        "## Ablation",
        "",
        f"- methods: {', '.join(sorted(methods))}",
        f"- missing_methods: {', '.join(missing_methods) if missing_methods else 'none'}",
        f"- full_schema_validity: {full_row.get('schema_validity', 'NA')}",
        f"- full_evidence_coverage: {full_row.get('evidence_coverage', 'NA')}",
        f"- full_merge_accuracy: {full_row.get('merge_accuracy', 'NA')}",
        f"- full_conflict_accuracy: {full_row.get('conflict_accuracy', 'NA')}",
        f"- full_replay_completeness: {full_row.get('replay_completeness', 'NA')}",
        "",
        "## Case Study",
        "",
        f"- rows: {len(case_rows)}",
        f"- operators: {', '.join(f'{op}={count}' for op, count in sorted(operators.items()))}",
        f"- core_operators_present: {', '.join(core_present)}",
        "",
        "## Replay",
        "",
        f"- replay_trace_records: {replay_count}",
        "",
        "## Acceptance",
        "",
        f"- status: {'PASS' if passed else 'FAIL'}",
        "- no_gpu_training_required",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
