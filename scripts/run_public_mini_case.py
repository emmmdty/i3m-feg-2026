#!/usr/bin/env python3
"""Run schema, evidence, and replay checks on public mini-case records."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evidence import has_evidence_match
from src.graph_store import GraphStore
from src.io_utils import read_jsonl, write_csv, write_jsonl
from src.schema import validate_event_schema
from src.submission_tables import write_tex
from src.update_ops import ADD_EVENT


FIELDNAMES = [
    "source_dataset",
    "num_records",
    "schema_validity",
    "evidence_coverage",
    "replay_completeness",
    "active_events",
    "version_logs",
    "conflicts",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tex-table", type=Path, required=True)
    parser.add_argument("--trace-out", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = read_jsonl(args.input)
    if not records:
        raise SystemExit("public mini-case input is empty")

    result = run_public_mini_case(records)
    row = result["row"]
    write_csv(args.out, [row], FIELDNAMES)
    write_tex(args.tex_table, render_public_mini_case_table(row))
    write_jsonl(args.trace_out, result["trace"])

    print(f"Wrote public mini-case results: {args.out}")
    print(f"Wrote public mini-case LaTeX table: {args.tex_table}")
    print(f"Wrote public mini-case replay trace: {args.trace_out}")
    print(
        f"{row['source_dataset']}: records={row['num_records']} "
        f"schema={row['schema_validity']} evidence={row['evidence_coverage']} "
        f"replay={row['replay_completeness']}"
    )
    return 0


def run_public_mini_case(records: list[dict[str, Any]]) -> dict[str, Any]:
    graph = GraphStore()
    trace: list[dict[str, Any]] = []
    schema_valid_count = 0
    evidence_match_count = 0
    applied_count = 0

    for replay_step, record in enumerate(records, start=1):
        schema_valid, schema_errors = validate_event_schema(record)
        evidence_match = has_evidence_match(record)
        schema_valid_count += int(schema_valid)
        evidence_match_count += int(evidence_match)

        operation_applied = False
        skipped_reason = ""
        if schema_valid and evidence_match:
            graph.add_event(record, replay_step)
            operation_applied = True
            applied_count += 1
        elif not schema_valid:
            skipped_reason = "schema_invalid"
        else:
            skipped_reason = "evidence_missing"

        snapshot = graph.snapshot_state(replay_step)
        trace.append(
            {
                "replay_step": replay_step,
                "record_id": record.get("record_id"),
                "source_dataset": record.get("source_dataset"),
                "source_doc_id": record.get("source_doc_id"),
                "event_id": record.get("event_id"),
                "schema_valid": schema_valid,
                "schema_errors": schema_errors,
                "evidence_match": evidence_match,
                "predicted_operator": ADD_EVENT if operation_applied else None,
                "operation_applied": operation_applied,
                "skipped_reason": skipped_reason,
                **snapshot,
            }
        )

    total = len(records)
    dataset_names = sorted({str(record.get("source_dataset", "")).strip() for record in records if record.get("source_dataset")})
    row = {
        "source_dataset": "; ".join(dataset_names) if dataset_names else "unknown",
        "num_records": str(total),
        "schema_validity": format_rate(schema_valid_count, total),
        "evidence_coverage": format_rate(evidence_match_count, total),
        "replay_completeness": format_rate(applied_count, total),
        "active_events": str(len(graph.event_nodes)),
        "version_logs": str(len(graph.version_logs)),
        "conflicts": str(len(graph.conflicts)),
        "notes": "external sanity case only; no extraction F1 or benchmark claim",
    }
    return {"row": row, "trace": trace}


def format_rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.000000"
    return f"{numerator / denominator:.6f}"


def render_public_mini_case_table(row: dict[str, str]) -> str:
    table_row = [
        latex_escape(row["source_dataset"]),
        format_count(row["num_records"]),
        format_decimal(row["schema_validity"]),
        format_decimal(row["evidence_coverage"]),
        format_decimal(row["replay_completeness"]),
        format_count(row["active_events"]),
        format_count(row["version_logs"]),
        latex_escape(row["notes"]),
    ]
    lines = [
        r"\begin{table}[t]",
        r"\caption{Public-dataset mini-case external sanity check.}",
        r"\label{tab:public-mini-case}",
        r"\begin{tabular}{@{}lrrrrrrp{0.29\hsize}@{}}",
        r"\toprule",
        r"Dataset & Records & Schema & Evidence & Replay & Active events & Logs & Notes\\",
        r"\colrule",
        " & ".join(table_row) + r"\\",
        r"\botrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


def format_count(value: str) -> str:
    try:
        return str(int(float(value)))
    except ValueError:
        return latex_escape(value)


def format_decimal(value: str) -> str:
    try:
        return f"{float(value):.3f}"
    except ValueError:
        return latex_escape(value)


def latex_escape(value: Any) -> str:
    specials = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    return "".join(specials.get(ch, ch) for ch in str(value))


if __name__ == "__main__":
    raise SystemExit(main())
