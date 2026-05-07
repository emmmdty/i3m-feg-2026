#!/usr/bin/env python3
"""Build compact LaTeX tables for the I3M/EMSS submission manuscript."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.submission_tables import (
    read_csv,
    render_ablation_table,
    render_case_study_table,
    render_metadata_hidden_table,
    render_negative_controls_table,
    render_scale_table,
    write_tex,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ablation", type=Path, required=True)
    parser.add_argument("--case-study", type=Path, required=True)
    parser.add_argument("--sanity", type=Path, required=True)
    parser.add_argument("--scale", type=Path, required=True)
    parser.add_argument("--metadata-hidden", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "table_ablation.tex": render_ablation_table(read_csv(args.ablation)),
        "table_case_study_excerpt.tex": render_case_study_table(read_csv(args.case_study)),
        "table_negative_controls.tex": render_negative_controls_table(read_csv(args.sanity)),
        "table_scale_sensitivity.tex": render_scale_table(read_csv(args.scale)),
    }
    if args.metadata_hidden is not None:
        outputs["table_metadata_hidden.tex"] = render_metadata_hidden_table(read_csv(args.metadata_hidden))
    for filename, content in outputs.items():
        path = args.out_dir / filename
        write_tex(path, content)
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
