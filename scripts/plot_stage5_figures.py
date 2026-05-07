#!/usr/bin/env python3
"""Generate Stage 05 paper figures and markdown tables."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import struct
import sys
import zlib
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.schema import REQUIRED_EVENT_FIELDS, STREAM_METADATA_FIELDS


FIELD_DESCRIPTIONS = {
    "event_id": "Unique event identifier used as the graph event key.",
    "event_type": "Controlled event category used by matching and update rules.",
    "subject": "Primary entity participating in the event.",
    "object": "Secondary entity or value-bearing object of the event.",
    "time": "ISO date string used for temporal matching.",
    "trigger": "Trigger phrase associated with the event record.",
    "evidence_span": "Text span that must appear in the source text.",
    "source_doc_id": "Identifier of the source document or controlled sample.",
    "record_id": "Optional stream record identifier.",
    "stream_record_id": "Optional replay stream record identifier.",
    "base_event_id": "Optional base event used for perturbation grouping.",
    "gold_group_id": "Optional group identifier in the controlled stream.",
    "arrival_index": "Optional replay ordering index.",
    "perturbation_type": "Optional controlled perturbation family.",
    "expected_operator": "Optional expected graph update operator.",
    "source_text": "Optional source text used by evidence matching.",
    "temporal_shuffle": "Optional flag for temporal replay perturbations.",
}

OPERATOR_ORDER = ["ADD_EVENT", "MERGE_EVENT", "UPDATE_SLOT", "MARK_CONFLICT"]
OPERATOR_COLORS = {
    "ADD_EVENT": (83, 128, 186),
    "MERGE_EVENT": (82, 150, 111),
    "UPDATE_SLOT": (210, 147, 57),
    "MARK_CONFLICT": (190, 82, 75),
    "VERSION_LOG": (105, 92, 155),
}

FONT_5X7 = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    ">": ["10000", "01000", "00100", "00010", "00100", "01000", "10000"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


class Canvas:
    def __init__(self, width: int, height: int, background: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            index = (y * self.width + x) * 3
            self.pixels[index : index + 3] = bytes(color)

    def fill_rect(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int]) -> None:
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + width), min(self.height, y + height)
        row = bytes(color) * max(0, x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.width + x0) * 3
            self.pixels[start : start + len(row)] = row

    def line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: tuple[int, int, int] = (45, 55, 65),
        thickness: int = 3,
    ) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - thickness // 2, y0 - thickness // 2, thickness, thickness, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def arrow(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: tuple[int, int, int] = (45, 55, 65),
    ) -> None:
        self.line(x0, y0, x1, y1, color, 4)
        angle = math.atan2(y1 - y0, x1 - x0)
        for offset in (2.55, -2.55):
            hx = int(x1 + math.cos(angle + offset) * 20)
            hy = int(y1 + math.sin(angle + offset) * 20)
            self.line(x1, y1, hx, hy, color, 4)

    def draw_text(
        self,
        x: int,
        y: int,
        text: str,
        color: tuple[int, int, int] = (30, 40, 50),
        scale: int = 3,
    ) -> None:
        cursor = x
        for char in text.upper():
            pattern = FONT_5X7.get(char, FONT_5X7["?"])
            for row_index, row in enumerate(pattern):
                for col_index, value in enumerate(row):
                    if value == "1":
                        self.fill_rect(
                            cursor + col_index * scale,
                            y + row_index * scale,
                            scale,
                            scale,
                            color,
                        )
            cursor += 6 * scale

    def draw_centered_text(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        color: tuple[int, int, int] = (30, 40, 50),
        scale: int = 3,
    ) -> None:
        lines = wrap_label(text, max(1, width // (6 * scale)))
        line_height = 9 * scale
        start_y = y + max(0, (height - len(lines) * line_height) // 2)
        for index, line in enumerate(lines):
            text_width = len(line) * 6 * scale
            self.draw_text(x + max(0, (width - text_width) // 2), start_y + index * line_height, line, color, scale)

    def box(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        fill: tuple[int, int, int],
        border: tuple[int, int, int] = (45, 55, 65),
        text_color: tuple[int, int, int] = (20, 30, 40),
    ) -> None:
        self.fill_rect(x, y, width, height, fill)
        self.fill_rect(x, y, width, 4, border)
        self.fill_rect(x, y + height - 4, width, 4, border)
        self.fill_rect(x, y, 4, height, border)
        self.fill_rect(x + width - 4, y, 4, height, border)
        self.draw_centered_text(x + 12, y + 8, width - 24, height - 16, label, text_color, 3)

    def save_png(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = bytearray()
        row_len = self.width * 3
        for y in range(self.height):
            raw.append(0)
            start = y * row_len
            raw.extend(self.pixels[start : start + row_len])
        with path.open("wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n")
            write_chunk(fh, b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))
            write_chunk(fh, b"IDAT", zlib.compress(bytes(raw), 9))
            write_chunk(fh, b"IEND", b"")


def write_chunk(fh: Any, tag: bytes, data: bytes) -> None:
    fh.write(struct.pack(">I", len(data)))
    fh.write(tag)
    fh.write(data)
    fh.write(struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def wrap_label(label: str, max_chars: int) -> list[str]:
    words = label.replace("->", "TO").replace("&", "AND").split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [label]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
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


def escape_markdown(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def write_markdown_table(path: Path, headers: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write("| " + " | ".join(headers) + " |\n")
        fh.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
        for row in rows:
            fh.write("| " + " | ".join(escape_markdown(row.get(header, "")) for header in headers) + " |\n")


def write_schema_table(path: Path) -> None:
    rows: list[dict[str, str]] = []
    for field in REQUIRED_EVENT_FIELDS:
        rows.append(
            {
                "field": field,
                "required": "yes",
                "description": FIELD_DESCRIPTIONS.get(field, "Required event record field."),
            }
        )
    for field in STREAM_METADATA_FIELDS:
        if field in REQUIRED_EVENT_FIELDS:
            continue
        rows.append(
            {
                "field": field,
                "required": "no",
                "description": FIELD_DESCRIPTIONS.get(field, "Optional controlled-stream metadata field."),
            }
        )
    write_markdown_table(path, ["field", "required", "description"], rows)


def write_converted_table(csv_path: Path, markdown_path: Path) -> None:
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit(f"CSV has no header: {csv_path}")
        write_markdown_table(markdown_path, list(reader.fieldnames), reader)


def matplotlib_available() -> bool:
    return importlib.util.find_spec("matplotlib") is not None


def draw_framework_fallback(path: Path) -> None:
    canvas = Canvas(1800, 900)
    canvas.draw_text(70, 50, "FIGURE 1. OVERALL FRAMEWORK", (35, 45, 55), 4)
    labels = [
        "Financial Event Samples",
        "Event Record Generation",
        "Schema Validation",
        "Evidence Span Matching",
        "Versioned Event Graph Update",
        "Conflict Marking",
        "Simulation State Transition",
        "Replay Trace and Version Logs",
    ]
    positions = [
        (80, 150),
        (500, 150),
        (920, 150),
        (1340, 150),
        (1340, 520),
        (920, 520),
        (500, 520),
        (80, 520),
    ]
    fills = [
        (221, 234, 246),
        (225, 238, 224),
        (251, 239, 219),
        (240, 228, 242),
        (222, 236, 232),
        (249, 226, 224),
        (232, 232, 245),
        (239, 239, 239),
    ]
    box_w, box_h = 330, 170
    centers: list[tuple[int, int]] = []
    for label, (x, y), fill in zip(labels, positions, fills):
        canvas.box(x, y, box_w, box_h, label, fill)
        centers.append((x + box_w // 2, y + box_h // 2))
    for start, end in zip(centers, centers[1:]):
        canvas.arrow(start[0], start[1], end[0], end[1])
    canvas.save_png(path)


def draw_update_fallback(path: Path) -> None:
    canvas = Canvas(1700, 950)
    canvas.draw_text(70, 50, "FIGURE 2. GRAPH UPDATE OPERATORS AND STATE TRANSITION", (35, 45, 55), 4)
    y0 = 150
    for index, operator in enumerate(["ADD_EVENT", "MERGE_EVENT", "UPDATE_SLOT", "MARK_CONFLICT", "VERSION_LOG"]):
        canvas.box(90, y0 + index * 135, 340, 90, operator, tint(OPERATOR_COLORS[operator], 0.78))
        canvas.arrow(430, y0 + index * 135 + 45, 680, 470)
    canvas.box(700, 350, 300, 120, "G_T", (230, 238, 248))
    canvas.box(1190, 350, 320, 120, "G_T+1", (221, 238, 231))
    canvas.arrow(1000, 410, 1190, 410)
    canvas.draw_text(1050, 370, "GRAPH UPDATE", (35, 45, 55), 3)
    canvas.box(700, 610, 300, 120, "S_T", (246, 235, 222))
    canvas.box(1190, 610, 320, 120, "S_T+1", (242, 230, 244))
    canvas.arrow(1000, 670, 1190, 670)
    canvas.draw_text(1035, 630, "STATE LOGGING", (35, 45, 55), 3)
    canvas.arrow(1350, 470, 1350, 610)
    canvas.draw_centered_text(1050, 180, 520, 100, "EVERY APPLIED OPERATOR APPENDS A VERSION LOG", (35, 45, 55), 3)
    canvas.save_png(path)


def draw_replay_fallback(path: Path, case_rows: list[dict[str, str]], replay_rows: list[dict[str, Any]]) -> None:
    canvas = Canvas(1900, 1000)
    canvas.draw_text(70, 45, "FIGURE 3. CASE STUDY REPLAY TRACE", (35, 45, 55), 4)
    left, right = 250, 1740
    top = 180
    lane_gap = 145
    max_step = max([int(row.get("replay_step") or 0) for row in case_rows] or [1])
    for lane_index, operator in enumerate(OPERATOR_ORDER):
        y = top + lane_index * lane_gap
        canvas.draw_text(55, y - 12, operator, OPERATOR_COLORS[operator], 3)
        canvas.line(left, y, right, y, (185, 190, 195), 2)
    for tick in range(0, max_step + 1, 10):
        if tick == 0:
            continue
        x = left + int((tick / max_step) * (right - left))
        canvas.line(x, top - 40, x, top + lane_gap * (len(OPERATOR_ORDER) - 1) + 40, (225, 228, 232), 1)
        canvas.draw_text(x - 18, top + lane_gap * len(OPERATOR_ORDER), str(tick), (65, 75, 85), 2)
    for row in case_rows:
        operator = row.get("operator", "")
        if operator not in OPERATOR_ORDER:
            continue
        step = int(row.get("replay_step") or 0)
        x = left + int((step / max_step) * (right - left))
        y = top + OPERATOR_ORDER.index(operator) * lane_gap
        color = OPERATOR_COLORS[operator]
        canvas.fill_rect(x - 8, y - 8, 16, 16, color)
    canvas.draw_text(left, 875, "REPLAY STEP", (35, 45, 55), 3)
    summary = summarize_replay(replay_rows)
    canvas.draw_centered_text(1120, 820, 650, 100, summary, (35, 45, 55), 3)
    canvas.save_png(path)


def tint(color: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(int(channel + (255 - channel) * amount) for channel in color)


def write_png_placeholder(path: Path, title: str, lines: list[str]) -> None:
    canvas = Canvas(1200, 720)
    canvas.draw_text(60, 60, title, (35, 45, 55), 4)
    for index, line in enumerate(lines):
        canvas.draw_text(80, 170 + index * 70, line, (35, 45, 55), 3)
    canvas.save_png(path)


def summarize_replay(replay_rows: list[dict[str, Any]]) -> str:
    if not replay_rows:
        return "NO REPLAY ROWS FOUND"
    last = replay_rows[-1]
    return (
        f"{len(replay_rows)} STEPS / "
        f"{last.get('active_event_count', 'NA')} ACTIVE EVENTS / "
        f"{last.get('conflict_count', 'NA')} CONFLICTS"
    )


def draw_with_matplotlib(
    figures_dir: Path,
    case_rows: list[dict[str, str]],
    replay_rows: list[dict[str, Any]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    fig, ax = plt.subplots(figsize=(15, 7))
    ax.axis("off")
    labels = [
        "Financial Event Samples",
        "Event Record Generation",
        "Schema Validation",
        "Evidence Span Matching",
        "Versioned Event Graph Update",
        "Conflict Marking",
        "Simulation State Transition",
        "Replay Trace and Version Logs",
    ]
    coords = [(0.05, 0.65), (0.29, 0.65), (0.53, 0.65), (0.77, 0.65), (0.77, 0.2), (0.53, 0.2), (0.29, 0.2), (0.05, 0.2)]
    for label, (x, y) in zip(labels, coords):
        ax.add_patch(Rectangle((x, y), 0.17, 0.16, facecolor="#e9f0f7", edgecolor="#2f3b45", linewidth=1.5))
        ax.text(x + 0.085, y + 0.08, label, ha="center", va="center", fontsize=10, wrap=True)
    for (x0, y0), (x1, y1) in zip(coords, coords[1:]):
        ax.add_patch(FancyArrowPatch((x0 + 0.17, y0 + 0.08), (x1, y1 + 0.08), arrowstyle="->", mutation_scale=18))
    ax.set_title("Figure 1. Overall Framework", loc="left")
    fig.savefig(figures_dir / "fig1_framework.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(13, 7))
    ax.axis("off")
    for index, operator in enumerate(["ADD_EVENT", "MERGE_EVENT", "UPDATE_SLOT", "MARK_CONFLICT", "VERSION_LOG"]):
        y = 0.8 - index * 0.15
        ax.add_patch(Rectangle((0.05, y), 0.22, 0.08, facecolor="#edf2f7", edgecolor="#2f3b45"))
        ax.text(0.16, y + 0.04, operator, ha="center", va="center", fontsize=10)
        ax.add_patch(FancyArrowPatch((0.27, y + 0.04), (0.48, 0.5), arrowstyle="->", mutation_scale=14))
    ax.text(0.5, 0.56, r"$G_t$", ha="center", fontsize=16)
    ax.text(0.75, 0.56, r"$G_{t+1}$", ha="center", fontsize=16)
    ax.add_patch(FancyArrowPatch((0.54, 0.56), (0.71, 0.56), arrowstyle="->", mutation_scale=18))
    ax.text(0.5, 0.35, r"$S_t$", ha="center", fontsize=16)
    ax.text(0.75, 0.35, r"$S_{t+1}$", ha="center", fontsize=16)
    ax.add_patch(FancyArrowPatch((0.54, 0.35), (0.71, 0.35), arrowstyle="->", mutation_scale=18))
    ax.text(0.62, 0.66, "graph update", ha="center", fontsize=10)
    ax.text(0.62, 0.44, "state transition", ha="center", fontsize=10)
    ax.set_title("Figure 2. Graph Update Operators and State Transition", loc="left")
    fig.savefig(figures_dir / "fig2_update_state_transition.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(15, 5))
    max_step = max([int(row.get("replay_step") or 0) for row in case_rows] or [1])
    for operator in OPERATOR_ORDER:
        xs = [int(row["replay_step"]) for row in case_rows if row.get("operator") == operator]
        ys = [OPERATOR_ORDER.index(operator)] * len(xs)
        color = tuple(channel / 255 for channel in OPERATOR_COLORS[operator])
        ax.scatter(xs, ys, s=28, label=operator, color=color)
    ax.set_xlim(0, max_step + 1)
    ax.set_yticks(range(len(OPERATOR_ORDER)))
    ax.set_yticklabels(OPERATOR_ORDER)
    ax.set_xlabel("Replay step")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(loc="upper center", ncol=4, frameon=False)
    ax.set_title(f"Figure 3. Case Study Replay Trace ({summarize_replay(replay_rows)})", loc="left")
    fig.tight_layout()
    fig.savefig(figures_dir / "fig3_case_study_replay_trace.png", dpi=180)
    plt.close(fig)


def generate_outputs(
    ablation_path: Path,
    case_study_path: Path,
    replay_path: Path,
    figures_dir: Path,
    tables_dir: Path,
) -> dict[str, Any]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    ablation_rows = read_csv_rows(ablation_path)
    case_rows = read_csv_rows(case_study_path)
    replay_rows = read_jsonl(replay_path)

    write_schema_table(tables_dir / "table1_event_record_schema.md")
    write_converted_table(ablation_path, tables_dir / "table2_ablation_results.md")
    write_converted_table(case_study_path, tables_dir / "table3_case_study_update_log.md")

    renderer = "matplotlib" if matplotlib_available() else "stdlib_png"
    if renderer == "matplotlib":
        draw_with_matplotlib(figures_dir, case_rows, replay_rows)
    else:
        draw_framework_fallback(figures_dir / "fig1_framework.png")
        draw_update_fallback(figures_dir / "fig2_update_state_transition.png")
        draw_replay_fallback(figures_dir / "fig3_case_study_replay_trace.png", case_rows, replay_rows)

    return {
        "renderer": renderer,
        "ablation_rows": len(ablation_rows),
        "case_study_rows": len(case_rows),
        "replay_rows": len(replay_rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ablation", type=Path, required=True)
    parser.add_argument("--case-study", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--figures-dir", type=Path, required=True)
    parser.add_argument("--tables-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = generate_outputs(args.ablation, args.case_study, args.replay, args.figures_dir, args.tables_dir)
    print(f"Stage 05 figures renderer: {summary['renderer']}")
    print(f"Read ablation rows: {summary['ablation_rows']}")
    print(f"Read case-study rows: {summary['case_study_rows']}")
    print(f"Read replay rows: {summary['replay_rows']}")
    print(f"Wrote figures: {args.figures_dir}")
    print(f"Wrote tables: {args.tables_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
