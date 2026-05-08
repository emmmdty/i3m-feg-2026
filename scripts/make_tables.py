#!/usr/bin/env python3
"""Refresh submission LaTeX tables from generated CSV artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.io import read_csv, read_jsonl, write_csv
from src.feg_replay.table_rendering import (
    render_case_study_table,
    render_invariant_checks_table,
    render_metadata_hidden_table,
    render_negative_controls_table,
    render_oracle_replay_table,
    render_public_mini_case_table,
    render_scale_sensitivity_table,
    write_tex,
)


CASE_FIELDNAMES = ["replay_step", "operator", "event_transition", "replay_note"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle", type=Path, default=Path("tables/oracle_replay_results.csv"))
    parser.add_argument("--metadata-hidden", type=Path, default=Path("tables/metadata_hidden_results.csv"))
    parser.add_argument("--public-mini", type=Path, default=Path("tables/public_mini_case_results.csv"))
    parser.add_argument("--negative", type=Path, default=Path("tables/negative_controls_results.csv"))
    parser.add_argument("--scale", type=Path, default=Path("tables/scale_sensitivity_results.csv"))
    parser.add_argument("--invariants", type=Path, default=Path("tables/invariant_checks_results.csv"))
    parser.add_argument("--trace", type=Path, default=Path("outputs/replay_trace.jsonl"))
    parser.add_argument("--case-study-out", type=Path, default=Path("tables/case_study_excerpt.csv"))
    parser.add_argument("--out-dir", type=Path, default=Path("paper/i3m_submission/tables"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    case_rows = build_case_rows(read_jsonl(args.trace))
    write_csv(args.case_study_out, case_rows, CASE_FIELDNAMES)
    outputs = {
        "table_oracle_replay.tex": render_oracle_replay_table(read_csv(args.oracle)),
        "table_metadata_hidden.tex": render_metadata_hidden_table(read_csv(args.metadata_hidden)),
        "table_public_mini_case.tex": render_public_mini_case_table(read_csv(args.public_mini)),
        "table_negative_controls.tex": render_negative_controls_table(read_csv(args.negative)),
        "table_scale_sensitivity.tex": render_scale_sensitivity_table(read_csv(args.scale)),
        "table_invariant_checks.tex": render_invariant_checks_table(read_csv(args.invariants)),
        "table_case_study_excerpt.tex": render_case_study_table(case_rows),
    }
    for filename, content in outputs.items():
        write_tex(args.out_dir / filename, content)
        print(f"Wrote {args.out_dir / filename}")
    print(f"Wrote case-study CSV: {args.case_study_out}")
    return 0


def build_case_rows(trace: list[dict[str, Any]]) -> list[dict[str, str]]:
    selected: list[dict[str, Any]] = []
    wanted = ["ADD_EVENT", "MERGE_EVENT", "UPDATE_SLOT", "MARK_CONFLICT"]
    for operator in wanted:
        item = next(
            (
                row
                for row in trace
                if row.get("predicted_operator") == operator and row.get("operation_applied")
            ),
            None,
        )
        if item is not None:
            selected.append(item)
    for item in trace:
        if len(selected) >= 6:
            break
        if item not in selected and item.get("operation_applied"):
            selected.append(item)
    rows: list[dict[str, str]] = []
    for item in sorted(selected, key=lambda row: int(row.get("replay_step", 0))):
        operator = str(item.get("predicted_operator") or "")
        event_id = str(item.get("event_id") or "")
        target = str(item.get("target_event_id") or "")
        transition = f"{event_id} -> {target}" if target and target != event_id else event_id
        rows.append(
            {
                "replay_step": str(item.get("replay_step", "")),
                "operator": operator,
                "event_transition": transition,
                "replay_note": note_for_operator(operator),
            }
        )
    return rows


def note_for_operator(operator: str) -> str:
    if operator == "ADD_EVENT":
        return "accepted evidence-backed record"
    if operator == "MERGE_EVENT":
        return "merged duplicate into target"
    if operator == "UPDATE_SLOT":
        return "updated changed slots"
    if operator == "MARK_CONFLICT":
        return "marked unresolved conflict"
    return "recorded replay operation"


if __name__ == "__main__":
    raise SystemExit(main())
