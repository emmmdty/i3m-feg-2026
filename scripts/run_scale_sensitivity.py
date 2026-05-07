#!/usr/bin/env python3
"""Run runtime scale sensitivity checks under controlled streams."""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (PROJECT_ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from build_seed_financial_samples import build_records
from generate_perturbation_stream import build_stream
from src.simulator import simulate_replay
from src.submission_tables import render_scale_table, write_tex


FIELDNAMES = [
    "scale",
    "num_records",
    "active_events",
    "version_logs",
    "conflicts",
    "replay_completeness",
    "runtime_ms_per_record",
    "total_runtime_ms",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--figure", type=Path, required=True)
    parser.add_argument("--tex-table", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--scales", type=int, nargs="+", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [run_scale(scale, args.seed) for scale in args.scales]
    write_scale_csv(args.out, rows)
    write_runtime_pdf(args.figure, rows)
    write_tex(args.tex_table, render_scale_table([{key: str(value) for key, value in row.items()} for row in rows]))
    print(f"Wrote scale sensitivity results: {args.out}")
    print(f"Wrote runtime figure: {args.figure}")
    print(f"Wrote scale LaTeX table: {args.tex_table}")
    for row in rows:
        print(
            f"scale={row['scale']} records={row['num_records']} "
            f"runtime_ms_per_record={row['runtime_ms_per_record']:.6f} "
            f"total_runtime_ms={row['total_runtime_ms']:.6f}"
        )
    return 0


def run_scale(scale: int, seed: int) -> dict[str, Any]:
    if scale < 1:
        raise SystemExit("--scales values must be positive")
    perturbation_count = max(1, scale // 3)
    samples = build_records(scale, seed)
    stream = build_stream(
        samples,
        seed,
        duplicates=perturbation_count,
        conflicts=perturbation_count,
        updates=perturbation_count,
        temporal_shuffles=perturbation_count,
        shuffle=True,
    )
    started = time.perf_counter()
    result = simulate_replay(stream, require_schema=True, require_evidence=True)
    elapsed = time.perf_counter() - started
    total_records = len(stream)
    applied = sum(1 for item in result.replay_trace if item.get("operation_applied"))
    total_runtime_ms = elapsed * 1000.0
    return {
        "scale": scale,
        "num_records": total_records,
        "active_events": len(result.graph.event_nodes),
        "version_logs": len(result.graph.version_logs),
        "conflicts": len(result.graph.conflicts),
        "replay_completeness": applied / total_records if total_records else 0.0,
        "runtime_ms_per_record": total_runtime_ms / total_records if total_records else 0.0,
        "total_runtime_ms": total_runtime_ms,
    }


def write_scale_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_runtime_pdf(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 612
    height = 396
    left = 70
    right = 35
    bottom = 58
    top = 48
    plot_width = width - left - right
    plot_height = height - bottom - top
    x_values = [float(row["num_records"]) for row in rows]
    y_values = [float(row["total_runtime_ms"]) for row in rows]
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = 0.0, max(y_values)
    if y_max <= 0:
        y_max = 1.0

    def sx(value: float) -> float:
        if x_max == x_min:
            return left + plot_width / 2.0
        return left + ((value - x_min) / (x_max - x_min)) * plot_width

    def sy(value: float) -> float:
        return bottom + ((value - y_min) / (y_max - y_min)) * plot_height

    content: list[str] = [
        "0.2 w",
        f"{left} {bottom} m {left + plot_width} {bottom} l S",
        f"{left} {bottom} m {left} {bottom + plot_height} l S",
        "0.9 0.9 0.9 RG",
    ]
    for fraction in (0.25, 0.5, 0.75, 1.0):
        y = bottom + fraction * plot_height
        content.append(f"{left} {y:.2f} m {left + plot_width} {y:.2f} l S")
    content.append("0 0 0 RG")
    points = [(sx(x), sy(y)) for x, y in zip(x_values, y_values)]
    if points:
        x0, y0 = points[0]
        content.append(f"1.2 w {x0:.2f} {y0:.2f} m")
        for x, y in points[1:]:
            content.append(f"{x:.2f} {y:.2f} l")
        content.append("S")
        for x, y in points:
            content.append(f"{x - 2.5:.2f} {y - 2.5:.2f} 5 5 re f")

    add_text(content, 70, 360, 13, "Runtime scaling under controlled streams")
    add_text(content, 230, 18, 10, "Replay records")
    add_text(content, 16, 205, 10, "Total runtime (ms)")
    for row, (x, y) in zip(rows, points):
        add_text(content, x - 10, bottom - 18, 8, str(row["num_records"]))
        add_text(content, x + 4, y + 6, 8, f"{float(row['total_runtime_ms']):.2f}")
    add_text(content, left - 28, bottom - 3, 8, "0")
    add_text(content, left - 48, bottom + plot_height - 3, 8, f"{y_max:.2f}")

    write_minimal_pdf(path, "\n".join(content).encode("ascii"))


def add_text(content: list[str], x: float, y: float, size: int, text: str) -> None:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content.append(f"BT /F1 {size} Tf {x:.2f} {y:.2f} Td ({escaped}) Tj ET")


def write_minimal_pdf(path: Path, stream: bytes) -> None:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 396] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(bytes(output))


if __name__ == "__main__":
    raise SystemExit(main())
