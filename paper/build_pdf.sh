#!/usr/bin/env bash
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MD="paper/manuscript.md"
PDF="paper/manuscript_v1.pdf"
HTML="paper/manuscript_v1.html"
STYLE="$(mktemp)"
PY="/home/tjk/.codex/venvs/codex-tools/bin/python"

cleanup() {
  rm -f "$STYLE"
}
trap cleanup EXIT

if ! [ -f "$MD" ]; then
  echo "Missing manuscript: $MD" >&2
  exit 1
fi

echo "Trying direct pandoc PDF build..."
if command -v pandoc >/dev/null 2>&1 && pandoc "$MD" --resource-path=paper:. -o "$PDF"; then
  echo "Wrote $PDF with direct pandoc PDF build."
  exit 0
fi

echo "Direct pandoc PDF build failed; trying pandoc HTML plus headless Chrome..."
if command -v pandoc >/dev/null 2>&1; then
  cat > "$STYLE" <<'CSS'
<style>
@page {
  margin: 0.55in;
}

body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 10.5pt;
  line-height: 1.36;
  color: #20242a;
}

h1 {
  font-size: 19pt;
  margin: 20px 0 10px;
}

h2 {
  font-size: 13.5pt;
  margin: 16px 0 8px;
}

p {
  margin: 0 0 8px;
}

ul {
  margin-top: 4px;
  margin-bottom: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 7.5pt;
  margin: 8px 0 12px;
}

th,
td {
  border: 1px solid #d5d9de;
  padding: 3px 4px;
  vertical-align: top;
  word-break: break-word;
}

th {
  background: #f0f3f6;
}

img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 8px auto 12px;
  page-break-inside: avoid;
}

code {
  font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
  font-size: 0.9em;
}
</style>
CSS
  pandoc "$MD" \
    --standalone \
    --resource-path=paper:. \
    --metadata pagetitle="A Reproducible Versioned Event Graph Prototype for Evidence-Constrained Financial Event Stream Simulation" \
    --include-in-header="$STYLE" \
    -o "$HTML"
  CHROME="$(command -v google-chrome-stable || command -v google-chrome || command -v chromium || command -v chromium-browser || true)"
  if [ -n "$CHROME" ]; then
    "$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer --print-to-pdf="$ROOT/$PDF" "file://$ROOT/$HTML"
    if [ -s "$PDF" ]; then
      echo "Wrote $PDF with headless Chrome fallback."
      exit 0
    fi
  fi
fi

echo "Chrome fallback failed; trying reportlab plain-text fallback..."
if [ -x "$PY" ]; then
  "$PY" - "$MD" "$PDF" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

source = Path(sys.argv[1])
target = Path(sys.argv[2])
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(str(target), pagesize=letter, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=48)
story = []

for raw in source.read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line:
        story.append(Spacer(1, 6))
        continue
    if line.startswith("!["):
        match = re.match(r"!\[(.*?)\]\((.*?)\)", line)
        caption = match.group(1) if match else "Figure"
        path = match.group(2) if match else ""
        story.append(Paragraph(f"{caption} ({path})", styles["Italic"]))
        story.append(Spacer(1, 6))
        continue
    if line.startswith("# "):
        story.append(Paragraph(line[2:], styles["Title"]))
    elif line.startswith("## "):
        story.append(Paragraph(line[3:], styles["Heading2"]))
    elif line.startswith("### "):
        story.append(Paragraph(line[4:], styles["Heading3"]))
    elif line.startswith("|"):
        story.append(Paragraph(line.replace("|", " | "), styles["Code"]))
    elif line.startswith("- "):
        story.append(Paragraph(line, styles["BodyText"]))
    else:
        story.append(Paragraph(line, styles["BodyText"]))
    story.append(Spacer(1, 4))

doc.build(story)
print(f"Wrote {target} with reportlab fallback.")
PY
  if [ -s "$PDF" ]; then
    exit 0
  fi
fi

echo "Unable to generate PDF. Manuscript remains available at $MD." >&2
exit 1
