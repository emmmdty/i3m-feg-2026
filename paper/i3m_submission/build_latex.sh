#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p build_logs
rm -f manuscript.aux manuscript.bbl manuscript.blg manuscript.fdb_latexmk \
  manuscript.fls manuscript.log manuscript.out manuscript.pdf manuscript.synctex.gz

latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript.tex

cp manuscript.pdf ../manuscript_i3m2026_v2.pdf
cp manuscript.log build_logs/manuscript.log
[ -f manuscript.blg ] && cp manuscript.blg build_logs/manuscript.blg
