#!/usr/bin/env python3
"""Draw TikZ vector figures for the submission manuscript."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import tempfile
from pathlib import Path


BLUE = "1b4f72"
LIGHT_BLUE = "eaf2f8"
GRAY = "566573"
LIGHT_GRAY = "f2f3f4"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("paper/i3m_submission/figures"))
    parser.add_argument("--metadata", type=Path, default=Path("tables/metadata_hidden_results.csv"))
    parser.add_argument("--scale", type=Path, default=Path("tables/scale_sensitivity_results.csv"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    compile_figure(workflow_tikz(), args.out_dir / "fig_workflow.pdf")
    compile_figure(state_transition_tikz(), args.out_dir / "fig_state_transition.pdf")
    compile_figure(
        diagnostic_results_tikz(read_csv(args.metadata), read_csv(args.scale)),
        args.out_dir / "fig_diagnostic_results.pdf",
    )
    print(f"Wrote {args.out_dir / 'fig_workflow.pdf'}")
    print(f"Wrote {args.out_dir / 'fig_state_transition.pdf'}")
    print(f"Wrote {args.out_dir / 'fig_diagnostic_results.pdf'}")
    return 0


def workflow_tikz() -> str:
    return standalone(
        r"""
\begin{tikzpicture}[
  font=\sffamily,
  box/.style={draw=gray!55, rounded corners=1pt, minimum width=2.05cm, minimum height=1.05cm, align=center, line width=0.4pt},
  arrow/.style={-{Latex[length=2.1mm]}, line width=0.55pt, draw=I3MBlue}
]
\node[font=\sffamily\bfseries, anchor=west] at (-0.35,1.52) {Controlled replay workflow};
\node[box, fill=I3MLightBlue] (input) at (0,0) {Input\\event records};
\node[box, fill=I3MLightGray] (schema) at (2.35,0) {Schema\\gate};
\node[box, fill=I3MLightGray] (evidence) at (4.70,0) {Evidence\\gate};
\node[box, fill=I3MLightGray] (policy) at (7.05,0) {Replay\\policy};
\node[box, fill=I3MLightBlue] (graph) at (9.40,0) {Versioned\\graph};
\node[box, fill=I3MLightGray] (log) at (11.75,0) {Version\\log};
\node[box, fill=I3MLightBlue] (trace) at (14.10,0) {Audit\\trace};
\draw[arrow] (input) -- (schema);
\draw[arrow] (schema) -- (evidence);
\draw[arrow] (evidence) -- (policy);
\draw[arrow] (policy) -- (graph);
\draw[arrow] (graph) -- (log);
\draw[arrow] (log) -- (trace);
\node[font=\sffamily\footnotesize, text=I3MGray, align=center] at (7.05,-1.25)
  {Exact evidence checks and deterministic policy decisions produce replayable graph artifacts.};
\end{tikzpicture}
"""
    )


def state_transition_tikz() -> str:
    return standalone(
        r"""
\begin{tikzpicture}[
  font=\sffamily,
  box/.style={draw=gray!55, rounded corners=1pt, minimum width=2.8cm, minimum height=1.1cm, align=center, line width=0.4pt},
  arrow/.style={-{Latex[length=2.1mm]}, line width=0.55pt, draw=I3MBlue}
]
\node[font=\sffamily\bfseries, anchor=west] at (-0.2,3.2) {Simulation state transition};
\node[box, fill=I3MLightBlue] (left) at (0,1.6) {$G_t$\\$S_t$};
\node[box, fill=I3MLightBlue] (right) at (9.8,1.6) {$G_{t+1}$\\$S_{t+1}$};
\draw[arrow] (left) -- node[above, font=\sffamily\footnotesize, text=I3MBlue] {operator $o_t$} (right);
\node[box, fill=I3MLightGray] (target) at (4.9,0.35) {Target\\resolution};
\node[box, fill=I3MLightGray] (invariant) at (4.9,-1.3) {Invariant\\check};
\node[box, fill=I3MLightGray] (version) at (9.8,-1.3) {Version log\\append};
\draw[arrow] (4.9,1.18) -- (target);
\draw[arrow] (target) -- (invariant);
\draw[arrow] (invariant) -- (version);
\draw[arrow] (invariant.east) .. controls (7.1,-0.5) and (8.0,0.8) .. (right.south);
\node[font=\sffamily\footnotesize, text=I3MGray, align=center] at (4.9,-2.45)
  {Failed target resolution is logged without increasing successful update counts.};
\end{tikzpicture}
"""
    )


def diagnostic_results_tikz(metadata_rows: list[dict[str, str]], scale_rows: list[dict[str, str]]) -> str:
    bar_lines = metadata_bar_lines(metadata_rows)
    line_lines = scale_line_lines(scale_rows)
    return standalone(
        rf"""
\begin{{tikzpicture}}[
  font=\sffamily,
  axis/.style={{draw=black!75, line width=0.45pt}},
  guide/.style={{draw=gray!35, line width=0.35pt}},
  bar/.style={{draw=I3MBlue, fill=I3MBlue}},
  point/.style={{draw=I3MBlue, fill=I3MBlue}},
  arrow/.style={{line width=0.65pt, draw=I3MBlue}}
]
\node[font=\sffamily\bfseries, anchor=west] at (-0.1,5.1) {{Diagnostic results}};
\node[font=\sffamily\small, anchor=west] at (0,4.45) {{Operator agreement}};
\draw[axis] (2.0,0.65) -- (5.8,0.65);
\node[font=\sffamily\scriptsize, text=I3MGray] at (2.0,0.32) {{0.000}};
\node[font=\sffamily\scriptsize, text=I3MGray] at (5.8,0.32) {{1.000}};
{bar_lines}
\node[font=\sffamily\small, anchor=west] at (7.15,4.45) {{Runtime scale sanity}};
\draw[axis] (7.7,0.65) -- (12.25,0.65);
\draw[axis] (7.7,0.65) -- (7.7,3.9);
\node[font=\sffamily\scriptsize, text=I3MGray, rotate=90] at (7.1,2.3) {{milliseconds}};
\node[font=\sffamily\scriptsize, text=I3MGray] at (10.0,0.1) {{Replay records}};
{line_lines}
\end{{tikzpicture}}
"""
    )


def metadata_bar_lines(rows: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for index, row in enumerate(rows):
        y = 3.55 - index * 1.25
        label = tex_escape(row["setting"].replace("-", " "))
        value = float(row["operator_agreement"])
        width = 3.8 * value
        lines.append(rf"\node[font=\sffamily\scriptsize, anchor=east] at (1.85,{y + 0.13:.2f}) {{{label}}};")
        lines.append(rf"\draw[guide, fill=I3MLightGray] (2.0,{y:.2f}) rectangle (5.8,{y + 0.32:.2f});")
        lines.append(rf"\draw[bar] (2.0,{y:.2f}) rectangle ({2.0 + width:.2f},{y + 0.32:.2f});")
        lines.append(rf"\node[font=\sffamily\scriptsize, anchor=west] at ({2.08 + width:.2f},{y + 0.13:.2f}) {{{value:.3f}}};")
    return "\n".join(lines)


def scale_line_lines(rows: list[dict[str, str]]) -> str:
    records = [float(row["num_records"]) for row in rows]
    runtimes = [float(row["total_runtime_ms"]) for row in rows]
    x_min, x_max = min(records), max(records)
    y_max = max(runtimes) or 1.0
    points = []
    for record_count, runtime in zip(records, runtimes):
        x = 7.7 + ((record_count - x_min) / (x_max - x_min)) * 4.55
        y = 0.65 + (runtime / y_max) * 3.25
        points.append((x, y, int(record_count), runtime))

    lines: list[str] = []
    for y_value in (0.65, 2.28, 3.9):
        lines.append(rf"\draw[guide] (7.7,{y_value:.2f}) -- (12.25,{y_value:.2f});")
    for left, right in zip(points, points[1:]):
        lines.append(rf"\draw[arrow] ({left[0]:.2f},{left[1]:.2f}) -- ({right[0]:.2f},{right[1]:.2f});")
    for x, y, record_count, runtime in points:
        lines.append(rf"\draw[point] ({x:.2f},{y:.2f}) circle (1.5pt);")
        lines.append(rf"\node[font=\sffamily\tiny, text=I3MGray] at ({x:.2f},0.38) {{{record_count}}};")
        lines.append(rf"\node[font=\sffamily\tiny, anchor=south] at ({x:.2f},{y + 0.08:.2f}) {{{runtime:.1f}}};")
    return "\n".join(lines)


def standalone(body: str) -> str:
    return rf"""\documentclass[tikz,border=6pt]{{standalone}}
\usepackage{{tikz}}
\usetikzlibrary{{arrows.meta,calc,positioning}}
\definecolor{{I3MBlue}}{{HTML}}{{{BLUE}}}
\definecolor{{I3MLightBlue}}{{HTML}}{{{LIGHT_BLUE}}}
\definecolor{{I3MGray}}{{HTML}}{{{GRAY}}}
\definecolor{{I3MLightGray}}{{HTML}}{{{LIGHT_GRAY}}}
\begin{{document}}
{body.strip()}
\end{{document}}
"""


def compile_figure(source: str, out_path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="i3m-figure-") as temp_name:
        temp_dir = Path(temp_name)
        tex_path = temp_dir / "figure.tex"
        tex_path.write_text(source, encoding="utf-8")
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=temp_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(temp_dir / "figure.pdf", out_path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def tex_escape(value: str) -> str:
    return (
        value.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
    )


if __name__ == "__main__":
    raise SystemExit(main())
