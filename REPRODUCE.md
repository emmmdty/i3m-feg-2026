# Reproducing the I3M/EMSS Controlled-Replay Artifact

Run all commands from the repository root.

## Environment

Use Python 3.10 or newer. The replay code uses the Python standard library. The PDF build requires `latexmk` or `pdflatex` plus `bibtex`.

```bash
python --version
```

## One-Command Reproduction

```bash
bash scripts/reproduce_all.sh
```

This command runs the complete artifact pipeline:

1. Prepare deterministic synthetic seed records and a 70-record controlled replay stream.
2. Run oracle-controlled replay and write trace artifacts.
3. Generate oracle-controlled replay diagnostics.
4. Generate metadata-hidden diagnostics.
5. Run negative controls.
6. Run invariant checks.
7. Run the 560-record scale sanity check.
8. Run the 20-record FewFC-derived public mini-case.
9. Refresh LaTeX tables and vector figures.
10. Build the final PDF.

## Key Outputs

- `tables/oracle_replay_results.csv`
- `tables/metadata_hidden_results.csv`
- `tables/public_mini_case_results.csv`
- `tables/negative_controls_results.csv`
- `tables/invariant_checks_results.csv`
- `tables/scale_sensitivity_results.csv`
- `paper/i3m_submission/tables/table_oracle_replay.tex`
- `paper/i3m_submission/tables/table_metadata_hidden.tex`
- `paper/i3m_submission/tables/table_public_mini_case.tex`
- `paper/i3m_submission/tables/table_negative_controls.tex`
- `paper/i3m_submission/tables/table_invariant_checks.tex`
- `paper/i3m_submission/tables/table_scale_sensitivity.tex`
- `paper/i3m_submission/tables/table_case_study_excerpt.tex`
- `paper/i3m_submission/figures/fig_workflow.pdf`
- `paper/i3m_submission/figures/fig_state_transition.pdf`
- `paper/i3m_submission/figures/fig_diagnostic_results.pdf`
- `paper/manuscript_i3m2026_v2.pdf`

Generated CSVs, replay traces, and processed streams are ignored by Git and can be regenerated.

## Public Mini-Case

The committed public mini-case is a small converted FewFC-derived sanity sample. It checks replay-path compatibility only. If regenerating from a local FewFC JSON file:

```bash
python scripts/prepare_public_mini_case.py --input path/to/fewfc.json --out data/samples/public_mini_events.jsonl --max-records 20
```

Do not fabricate public mini-case records if the source file is unavailable or unparsable.

## Reproducibility Boundaries

The artifact performs no model training, no model inference, and no external API calls. It reports controlled replay diagnostics and auditability evidence only.
