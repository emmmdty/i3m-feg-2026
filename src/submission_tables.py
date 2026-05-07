"""LaTeX table helpers for I3M/EMSS submission artifacts."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


LATEX_SPECIALS = {
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


CASE_STUDY_IDS = ("CS0001", "CS0004", "CS0007", "CS0010", "CS0032", "CS0063")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_tex(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def latex_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return "".join(LATEX_SPECIALS.get(ch, ch) for ch in text)


def latex_texttt(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return "--"
    return r"\texttt{" + latex_escape(text) + "}"


def format_count(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if text.upper() in {"", "NA", "--"}:
        return "--"
    try:
        return str(int(float(text)))
    except ValueError:
        return latex_escape(text)


def format_decimal(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if text.upper() in {"", "NA", "--"}:
        return "--"
    try:
        return f"{float(text):.3f}"
    except ValueError:
        return latex_escape(text)


def render_tabular(
    caption: str,
    label: str,
    headers: list[str],
    rows: list[list[str]],
    column_spec: str,
    use_star: bool = True,
) -> str:
    environment = "tabular*" if use_star else "tabular"
    begin = (
        rf"\begin{{tabular*}}{{\hsize}}{{{column_spec}}}"
        if use_star
        else rf"\begin{{tabular}}{{{column_spec}}}"
    )
    lines = [
        r"\begin{table}[t]",
        rf"\caption{{{latex_escape(caption)}}}",
        rf"\label{{{label}}}",
        begin,
        r"\toprule",
        " & ".join(latex_escape(header) for header in headers) + r"\\",
        r"\colrule",
    ]
    lines.extend(" & ".join(row) + r"\\" for row in rows)
    lines.extend(
        [
            r"\botrule",
            rf"\end{{{environment}}}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def render_ablation_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            latex_escape(row.get("method", "")),
            format_decimal(row.get("schema_validity")),
            format_decimal(row.get("evidence_coverage")),
            format_decimal(row.get("merge_accuracy")),
            format_decimal(row.get("conflict_accuracy")),
            format_decimal(row.get("replay_completeness")),
            format_decimal(row.get("runtime_ms_per_record")),
            format_count(row.get("num_records")),
        ]
        for row in rows
    ]
    return render_tabular(
        "Controlled replay agreement under injected perturbations.",
        "tab:ablation",
        ["Method", "Schema", "Evidence", "Merge Agr.", "Conflict Agr.", "Replay", "ms/rec.", "n"],
        table_rows,
        r"@{\extracolsep{\fill}}lrrrrrrr@{}",
    )


def render_metadata_hidden_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            latex_escape(row.get("setting", "")),
            latex_escape(row.get("uses_perturbation_metadata", "")),
            format_decimal(row.get("merge_agreement")),
            format_decimal(row.get("conflict_agreement")),
            format_decimal(row.get("update_agreement")),
            format_decimal(row.get("operator_agreement")),
            format_decimal(row.get("replay_completeness")),
            format_decimal(row.get("runtime_ms_per_record")),
        ]
        for row in rows
    ]
    return render_tabular(
        "Metadata-hidden diagnostic replay agreement.",
        "tab:metadata-hidden",
        ["Setting", "Metadata", "Merge", "Conflict", "Update", "Operator", "Replay", "Runtime"],
        table_rows,
        r"@{\extracolsep{\fill}}llrrrrrr@{}",
    )


def render_negative_controls_table(rows: list[dict[str, str]]) -> str:
    row = rows[0] if rows else {}
    table_rows = [
        [
            format_count(row.get("total_cases")),
            format_count(row.get("schema_rejected")),
            format_count(row.get("evidence_rejected")),
            format_count(row.get("invalid_date_rejected")),
            format_count(row.get("unknown_operator_handled")),
            format_count(row.get("crash_count")),
        ]
    ]
    return render_tabular(
        "Negative-control sanity checks.",
        "tab:negative-controls",
        ["Cases", "Schema rej.", "Evidence rej.", "Bad dates", "Unknown op.", "Crashes"],
        table_rows,
        r"@{\extracolsep{\fill}}rrrrrr@{}",
    )


def render_scale_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            format_count(row.get("scale")),
            format_count(row.get("num_records")),
            format_count(row.get("active_events")),
            format_count(row.get("version_logs")),
            format_count(row.get("conflicts")),
            format_decimal(row.get("replay_completeness")),
            format_decimal(row.get("runtime_ms_per_record")),
            format_decimal(row.get("total_runtime_ms")),
        ]
        for row in rows
    ]
    return render_tabular(
        "Scale sensitivity under controlled streams.",
        "tab:scale",
        ["Scale", "Records", "Active", "Logs", "Conflicts", "Replay", "ms/rec.", "Total ms"],
        table_rows,
        r"@{\extracolsep{\fill}}rrrrrrrr@{}",
    )


def render_case_study_table(rows: list[dict[str, str]]) -> str:
    selected = select_case_study_rows(rows)
    table_rows = [
        [
            format_count(row.get("replay_step")),
            latex_texttt(row.get("operator")),
            render_event_transition(row),
            latex_escape(compact_case_note(row.get("operator", ""))),
        ]
        for row in selected
    ]
    return render_tabular(
        "Case-study replay excerpt.",
        "tab:case-study",
        ["Step", "Operator", "Event transition", "Replay note"],
        table_rows,
        r"@{}rlp{0.31\hsize}p{0.31\hsize}@{}",
        use_star=False,
    )


def select_case_study_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id = {row.get("case_id"): row for row in rows}
    selected = [by_id[case_id] for case_id in CASE_STUDY_IDS if case_id in by_id]
    if len(selected) == len(CASE_STUDY_IDS):
        return selected
    return rows[:6]


def render_event_transition(row: dict[str, str]) -> str:
    event_id = row.get("event_id", "")
    target_event_id = row.get("target_event_id", "")
    if target_event_id and target_event_id != event_id:
        return latex_texttt(event_id) + r" $\rightarrow$ " + latex_texttt(target_event_id)
    return latex_texttt(event_id)


def compact_case_note(operator: str) -> str:
    if operator == "ADD_EVENT":
        return "accepted evidence-backed event"
    if operator == "MERGE_EVENT":
        return "merged duplicate into target"
    if operator == "UPDATE_SLOT":
        return "updated changed slots"
    if operator == "MARK_CONFLICT":
        return "marked unresolved conflict"
    return "recorded replay operation"
