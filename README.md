# A Controlled-Replay Prototype for Auditable Versioned Financial Event Graph Updates

This repository contains the reproducible artifact package for an EMSS/I3M 2026 short paper on controlled replay for auditable versioned financial event graph updates.

## Paper Positioning

The project is a controlled-replay prototype and auditability case study. It studies whether deterministic financial event records can be checked against evidence spans, replayed through a compact graph-update operator set, and exported as auditable state-transition artifacts.

This is not a financial event extraction benchmark, not a market prediction system, and not an investment or trading system. The reported results are limited to controlled replay, negative controls, metadata-hidden diagnostics, runtime scale sensitivity, and a small public mini-case sanity check.

## Final Paper Files

- `paper/i3m_submission/manuscript.tex`
- `paper/i3m_submission/manuscript.pdf`
- `paper/manuscript_i3m2026_v2.pdf`

The submission PDF is rebuilt with:

```bash
bash paper/i3m_submission/build_latex.sh
```

`paper/build_pdf.sh` is a legacy Markdown/PDF helper and is not the final submission build path.

## Reproduction

Use `REPRODUCE.md` for the step-by-step reproduction procedure, or run the bundled script from the repository root:

```bash
bash scripts/reproduce_all.sh
```

The script regenerates the synthetic controlled replay inputs, runs the local diagnostics, refreshes submission tables, optionally runs the public mini-case when the committed sample file is present, and rebuilds the LaTeX PDF.

## Public Mini-Case

`data/samples/public_mini_events.jsonl` contains a FewFC-derived 20-record external sanity case. It is included only to check that externally sourced public financial event records can pass the same schema, evidence-span, and replay path used by the prototype.

The mini-case is not an extraction benchmark, not an F1 evaluation, and not evidence of benchmark-level generalization. The full raw FewFC dataset is not committed; see `reports/stage_06_9/public_mini_case_source_manifest.md` and `reports/stage_06_9/public_mini_case_conversion_notes.md`.

## Safety and Non-Goals

- No investment advice.
- No trading signals.
- No buy or sell recommendations.
- No market prediction.
- No model training or model inference is required for the reported artifact.
- No external API calls are required for reproduction.

## Environment

- Python 3.10 or newer.
- `latexmk` and `pdflatex` for the PDF build.
- Optional Python plotting dependency is listed in `requirements.txt`.

Generated outputs, table CSVs, raw data, processed data, logs, checkpoints, and model artifacts are intentionally excluded from Git.
