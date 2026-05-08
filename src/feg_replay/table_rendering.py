"""LaTeX table rendering helpers."""

from __future__ import annotations

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


def write_tex(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def latex_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return "".join(LATEX_SPECIALS.get(ch, ch) for ch in text)


def latex_texttt(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if not text or text.upper() in {"NA", "--"}:
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


def render_table(
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
        r"\midrule",
    ]
    lines.extend(" & ".join(row) + r"\\" for row in rows)
    lines.extend(
        [
            r"\bottomrule",
            rf"\end{{{environment}}}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def render_oracle_replay_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            latex_escape(row.get("method", "")),
            format_decimal(row.get("schema_validity")),
            format_decimal(row.get("evidence_coverage")),
            format_decimal(row.get("merge_agreement")),
            format_decimal(row.get("conflict_agreement")),
            format_decimal(row.get("update_agreement")),
            format_decimal(row.get("operator_agreement")),
            format_decimal(row.get("replay_completeness")),
            format_count(row.get("num_records")),
        ]
        for row in rows
    ]
    return render_table(
        "Controlled replay diagnostics; agreement compares replay decisions with injected operator labels, not extraction accuracy.",
        "tab:oracle-replay",
        ["Method", "Schema", "Evidence", "Merge", "Conflict", "Update", "Operator", "Replay", "n"],
        table_rows,
        r"@{\extracolsep{\fill}}lrrrrrrrr@{}",
    )


def render_metadata_hidden_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            latex_escape(row.get("setting", "")),
            latex_escape(row.get("uses_metadata", "")),
            format_decimal(row.get("merge_agreement")),
            format_decimal(row.get("conflict_agreement")),
            format_decimal(row.get("update_agreement")),
            format_decimal(row.get("operator_agreement")),
            format_decimal(row.get("replay_completeness")),
        ]
        for row in rows
    ]
    return render_table(
        "Metadata-hidden diagnostic agreement; gold labels are used only after replay for comparison.",
        "tab:metadata-hidden",
        ["Setting", "Metadata", "Merge", "Conflict", "Update", "Operator", "Replay"],
        table_rows,
        r"@{\extracolsep{\fill}}llrrrrr@{}",
    )


def render_public_mini_case_table(rows: list[dict[str, str]]) -> str:
    row = rows[0] if rows else {}
    return render_table(
        "FewFC-derived public mini-case, reported as an external sanity check only.",
        "tab:public-mini-case",
        ["Records", "Schema", "Evidence", "Replay", "Active events", "Logs"],
        [
            [
                format_count(row.get("num_records")),
                format_decimal(row.get("schema_validity")),
                format_decimal(row.get("evidence_coverage")),
                format_decimal(row.get("replay_completeness")),
                format_count(row.get("active_events")),
                format_count(row.get("version_logs")),
            ]
        ],
        r"@{\extracolsep{\fill}}rrrrrr@{}",
    )


def render_negative_controls_table(rows: list[dict[str, str]]) -> str:
    row = rows[0] if rows else {}
    return render_table(
        "Negative controls verify rejection and logging paths without successful graph updates.",
        "tab:negative-controls",
        ["Cases", "Schema rej.", "Evidence rej.", "Bad dates", "Unsupported logged", "Crashes"],
        [
            [
                format_count(row.get("total_cases")),
                format_count(row.get("schema_rejected")),
                format_count(row.get("evidence_rejected")),
                format_count(row.get("invalid_date_rejected")),
                format_count(row.get("unsupported_metadata_logged")),
                format_count(row.get("crash_count")),
            ]
        ],
        r"@{\extracolsep{\fill}}rrrrrr@{}",
    )


def render_scale_sensitivity_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            format_count(row.get("scale")),
            format_count(row.get("num_records")),
            format_count(row.get("active_events")),
            format_count(row.get("version_logs")),
            format_count(row.get("conflicts")),
            format_decimal(row.get("replay_completeness")),
            format_decimal(row.get("runtime_ms_per_record")),
        ]
        for row in rows
    ]
    return render_table(
        "Scale sanity run over deterministic controlled streams.",
        "tab:scale",
        ["Seed records", "Replay records", "Active", "Logs", "Conflicts", "Replay", "ms/rec."],
        table_rows,
        r"@{\extracolsep{\fill}}rrrrrrr@{}",
    )


def render_invariant_checks_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            latex_escape(row.get("case", "")),
            latex_escape(row.get("expected_behavior", "")),
            latex_escape(row.get("applied", "")),
            latex_escape(row.get("logged", "")),
            latex_escape(row.get("result", "")),
        ]
        for row in rows
    ]
    return render_table(
        "Invariant checks for failed target resolution and unsupported metadata.",
        "tab:invariant-checks",
        ["Case", "Expected behavior", "Applied", "Logged", "Result"],
        table_rows,
        r"@{}p{0.21\hsize}p{0.34\hsize}lll@{}",
        use_star=False,
    )


def render_case_study_table(rows: list[dict[str, str]]) -> str:
    table_rows = [
        [
            format_count(row.get("replay_step")),
            latex_texttt(row.get("operator")),
            latex_escape(row.get("event_transition", "")),
            latex_escape(row.get("replay_note", "")),
        ]
        for row in rows[:6]
    ]
    return render_table(
        "Replay trace excerpt showing representative graph transitions.",
        "tab:case-study",
        ["Step", "Operator", "Event transition", "Replay note"],
        table_rows,
        r"@{}rlp{0.28\hsize}p{0.34\hsize}@{}",
        use_star=False,
    )
