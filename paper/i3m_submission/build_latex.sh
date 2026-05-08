#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p build_logs
rm -f manuscript.aux manuscript.bbl manuscript.blg manuscript.fdb_latexmk \
  manuscript.fls manuscript.log manuscript.out manuscript.pdf manuscript.synctex.gz

if command -v latexmk >/dev/null 2>&1; then
  latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex
elif command -v pdflatex >/dev/null 2>&1 && command -v bibtex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error -recorder manuscript.tex
  bibtex manuscript
  pdflatex -interaction=nonstopmode -halt-on-error -recorder manuscript.tex
  pdflatex -interaction=nonstopmode -halt-on-error -recorder manuscript.tex
else
  echo "Missing LaTeX builder: install latexmk or pdflatex plus bibtex." >&2
  exit 127
fi

cp manuscript.pdf ../manuscript_i3m2026_v2.pdf
cp manuscript.log build_logs/manuscript.log
[ -f manuscript.blg ] && cp manuscript.blg build_logs/manuscript.blg
