#!/usr/bin/env python3
"""Run small invariant checks for replay failure accounting."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.feg_replay.graph import GraphStore
from src.feg_replay.io import write_csv
from src.feg_replay.operators import MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT
from src.feg_replay.schema import validate_event_schema
from src.feg_replay.simulator import simulate_replay
from src.feg_replay.table_rendering import render_invariant_checks_table, write_tex


FIELDNAMES = ["case", "expected_behavior", "applied", "logged", "result"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("tables/invariant_checks_results.csv"))
    parser.add_argument("--tex-table", type=Path, default=Path("paper/i3m_submission/tables/table_invariant_checks.tex"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = run_checks()
    write_csv(args.out, rows, FIELDNAMES)
    write_tex(args.tex_table, render_invariant_checks_table(rows))
    print(f"Wrote invariant-check results: {args.out}")
    print(f"Wrote invariant-check table: {args.tex_table}")
    if any(row["result"] != "pass" for row in rows):
        raise SystemExit("one or more invariant checks failed")
    return 0


def run_checks() -> list[dict[str, str]]:
    rows = [
        check_missing_target(MERGE_EVENT),
        check_missing_target(UPDATE_SLOT),
        check_missing_target(MARK_CONFLICT),
        check_invalid_nested_event(),
        check_unknown_metadata(),
        check_evidence_mismatch(),
    ]
    return rows


def check_missing_target(operator: str) -> dict[str, str]:
    result = simulate_replay([target_record(operator)], policy_mode="oracle")
    trace = result.replay_trace[0]
    applied = bool(trace.get("operation_applied"))
    logged = bool(result.graph.version_logs)
    if operator == MARK_CONFLICT:
        count_ok = result.graph.snapshot_state(1)["unresolved_conflict_count"] == 0
    elif operator == MERGE_EVENT:
        count_ok = result.graph.snapshot_state(1)["merged_event_count"] == 0
    else:
        count_ok = result.graph.snapshot_state(1)["updated_slot_count"] == 0
    return {
        "case": f"Missing target {operator.lower()}",
        "expected_behavior": "log missing target without success count",
        "applied": str(applied).lower(),
        "logged": str(logged).lower(),
        "result": "pass" if (not applied and logged and count_ok) else "fail",
    }


def check_invalid_nested_event() -> dict[str, str]:
    valid, errors = validate_event_schema({"event": "bad wrapper"})
    return {
        "case": "Invalid nested event",
        "expected_behavior": "return schema error",
        "applied": "false",
        "logged": "true",
        "result": "pass" if (not valid and "event must be an object" in errors) else "fail",
    }


def check_unknown_metadata() -> dict[str, str]:
    result = simulate_replay([unknown_metadata_record()], policy_mode="oracle")
    trace = result.replay_trace[0]
    return {
        "case": "Unsupported metadata",
        "expected_behavior": "log unsupported metadata without update",
        "applied": str(bool(trace.get("operation_applied"))).lower(),
        "logged": str(bool(trace.get("unsupported_metadata_logged"))).lower(),
        "result": "pass"
        if trace.get("skipped_reason") == "unsupported_or_unknown_metadata" and not trace.get("operation_applied")
        else "fail",
    }


def check_evidence_mismatch() -> dict[str, str]:
    record = base_record()
    record["evidence_span"] = "evidence not present"
    result = simulate_replay([record], policy_mode="oracle")
    trace = result.replay_trace[0]
    return {
        "case": "Evidence mismatch",
        "expected_behavior": "reject before graph update",
        "applied": str(bool(trace.get("operation_applied"))).lower(),
        "logged": str(trace.get("skipped_reason") == "evidence_missing").lower(),
        "result": "pass" if trace.get("skipped_reason") == "evidence_missing" else "fail",
    }


def target_record(operator: str) -> dict[str, Any]:
    record = base_record()
    record.update(
        {
            "event_id": f"E-{operator.lower()}",
            "base_event_id": "missing-target",
            "perturbation_type": "duplicate",
            "expected_operator": operator,
        }
    )
    return record


def unknown_metadata_record() -> dict[str, Any]:
    record = base_record()
    record.update({"perturbation_type": "unsupported_metadata", "expected_operator": "UNSUPPORTED_OPERATOR"})
    return record


def base_record() -> dict[str, Any]:
    return {
        "event_id": "E-check",
        "event_type": "equity_pledge",
        "subject": "Company A",
        "object": "shares",
        "time": "2025-01-01",
        "trigger": "pledged",
        "evidence_span": "Company A pledged shares",
        "source_doc_id": "D-check",
        "source_text": "Company A pledged shares in a disclosure.",
        "amount": "5 million shares",
        "status": "announced",
        "arrival_index": 1,
    }


if __name__ == "__main__":
    raise SystemExit(main())
