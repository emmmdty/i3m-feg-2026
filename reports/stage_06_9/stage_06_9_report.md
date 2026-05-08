# Stage 6.9 Final Consistency and Reproducibility Hardening Report

## 1. Why Stage 6.9 was inserted

Stage 6.9 was inserted after Stage 6.8 to harden final consistency, reproducibility packaging, PDF cleanliness, and submission-material completeness before user acceptance. The paper remains positioned as:

`A Controlled-Replay Prototype for Auditable Versioned Financial Event Graph Updates`

## 2. Scope boundary

- No expanded FewFC/DuEE-Fin/DocFEE benchmark was added.
- No model training was run.
- No model inference was run.
- No external API was called.
- No investment advice, trading signal, market prediction, buy recommendation, or sell recommendation functionality was added.
- The FewFC public mini-case remains a 20-record external sanity case only.

## 3. Start-state checks

Preflight commands were run before edits:

```bash
pwd
git branch --show-current
git status --short
cat AGENTS.md
```

Results:

- cwd: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- initial `git status --short`: clean
- `AGENTS.md`: readable

## 4. Source-of-truth consistency

`paper/i3m_submission/manuscript.tex` contains:

- title: `A Controlled-Replay Prototype for Auditable Versioned Financial Event Graph Updates`
- `\subsection{Public-dataset mini-case}`
- `\input{tables/table_public_mini_case.tex}`
- keyword/framing text including `modeling and simulation`

`paper/i3m_submission/manuscript.tex` contains no matches for:

- `TBD`
- `Stage 06`
- `Stage 6`

After the final rebuild:

- `paper/i3m_submission/manuscript.pdf` and `paper/manuscript_i3m2026_v2.pdf` have identical SHA-256:
  `a46380dfe2bfc6c10ec1c88425f56495fb7b690db007b34509cc9285b0d24bd9`
- byte compare result: `cmp_exit=0`
- extracted-text compare result: `text_diff_exit=0`

## 5. Public mini-case check

`data/samples/public_mini_events.jsonl`:

- exists: yes
- tracked by Git: yes
- records: 20
- validation result: `OK public_mini_events records=20`
- evidence-span containment: passed for all records
- regenerated in Stage 6.9: no, because the committed sample was already valid

Public mini-case provenance files:

- `reports/stage_06_9/public_mini_case_source_manifest.md`
- `reports/stage_06_9/public_mini_case_conversion_notes.md`

FewFC source evidence:

- upstream repository: `https://github.com/TimeBurningFish/FewFC`
- local source path: `data/raw/FewFC`
- local upstream commit observed: `ec6cac90238c04b45d4512a695ee6375fc72af2f`
- license note: FewFC public research dataset; CC BY-SA 4.0; see upstream repository

## 6. Reproducibility package status

Added or updated:

- `REPRODUCE.md`
- `requirements.txt`
- `scripts/reproduce_all.sh`
- `reports/reproducibility_checklist.md`
- `LICENSE.md`
- `.gitignore` entries for generated `reports/reproduce_check/` and `tmp/`

`scripts/reproduce_all.sh`:

- uses bash
- uses `set -euo pipefail`
- runs from the repository root
- creates `outputs`, `tables`, `data/processed`, and `reports/reproduce_check`
- runs the controlled replay, ablation, case study, negative controls, metadata-hidden diagnostic, scale sensitivity, optional public mini-case, submission table refresh, and LaTeX build
- does not download FewFC
- runs the public mini-case only when `data/samples/public_mini_events.jsonl` exists
- prints final PDF paths and `no_gpu_training_required`

`paper/build_pdf.sh` is marked as a legacy Markdown/PDF helper and is not referenced as the final submission build path.

## 7. PDF rebuild and cleanliness

Final local build command:

```bash
bash paper/i3m_submission/build_latex.sh
```

Result:

- build status: success
- final PDF: `paper/manuscript_i3m2026_v2.pdf`
- submission PDF copy: `paper/i3m_submission/manuscript.pdf`
- page count: 8
- final PDF size: 205667 bytes
- page-count target: passed, 3-10 pages

PDF dirty-text scan file:

- `reports/stage_06_9/manuscript_i3m2026_v2.txt`

Forbidden/dirty-term grep returned no matches for:

`TBD`, `Stage 06`, `Stage 6`, `GPT-generated`, `Codex-generated`, `AI-generated`, `stock prediction`, `trading signal`, `buy recommendation`, `sell recommendation`, `investment advice`, `outperform`, `state-of-the-art method`, `superior performance`, `Instructions to Authors`, `Insert here your abstract text`, `Check in the contract`, `ThisEmail`, `YueBY-NC-ND`, `BY-NC-ND Zhao`.

The first page was rendered with `pdftoppm` for visual inspection. The previous template dirt was removed; the Procedia page remains visually clean enough for final user acceptance review.

## 8. README update summary

`README.md` was rewritten as final repository documentation. It now covers:

- project title
- controlled-replay prototype positioning
- auditability case-study framing
- not an extraction benchmark
- not market prediction
- final paper files
- reproduction via `REPRODUCE.md` and `scripts/reproduce_all.sh`
- FewFC-derived 20-record public mini-case
- safety and non-goals
- Python and LaTeX environment requirements

## 9. Local reproduction result

Local command:

```bash
bash scripts/reproduce_all.sh
```

Result:

- exit status: 0
- Python used by script: 3.10.20
- controlled stream: 70 records
- demo: 70 processed records, 40 active events, 70 version logs, 10 conflicts
- ablation full row: schema 1.000000, evidence 1.000000, merge 1.000000, conflict 1.000000, replay 1.000000
- negative controls: 20 total cases, 0 crashes
- metadata-hidden diagnostic: operator 0.585714, replay 1.000000
- scale sensitivity: completed for scales 30, 60, 120, 240
- public mini-case: ran, FewFC 20 records, schema 1.000000, evidence 1.000000, replay 1.000000
- final LaTeX build: success
- training: no
- GPU training: `no_gpu_training_required`

## 10. Server reproduction result

Code was synchronized without `--delete` using the requested `rsync -avz` path.

Server reproduce_all command:

```bash
cd /home/TJK/i3m_financial_event_graph_2026
bash scripts/reproduce_all.sh
```

Server command ran in:

`/home/TJK/i3m_financial_event_graph_2026`

Server result:

Server summary:

- server Python check: Python 3.10.20
- `scripts/reproduce_all.sh` Python: Python 3.10.20
- public mini-case status: `public_mini_case_status=ran`
- training: no
- model inference: no
- external API calls: none
- GPU training: `no_gpu_training_required`
- synced PDF page count from `pdfinfo`: 8
- `latexmk`: missing
- `pdflatex`: missing
- `reproduce_all` exit status: 127

Server log path:

`/data/TJK/i3m/reports/stage_06_9/reproduce_all.log`

Server summary path:

`/data/TJK/i3m/reports/stage_06_9/reproduce_all_summary.txt`

Server failure shape:

All Python reproduction steps completed, including the public mini-case. The failure occurs only at the final LaTeX build:

```text
Missing LaTeX builder: install latexmk or pdflatex plus bibtex.
```

This is a server LaTeX environment blocker, not a Python replay or public mini-case blocker.

## 11. Training/GPU/API status

- training: no
- model inference: no
- external API calls: none
- GPU training: `no_gpu_training_required`

## 12. Stage 7 recommendation

Recommendation: proceed to user acceptance review before Stage 7. The local final artifact package is reproducible and PDF-clean. The only unresolved item is server-side PDF rebuilding, blocked by missing LaTeX tools on `gpu-4090`; install `latexmk` or `pdflatex` plus `bibtex` on the server if server-side PDF compilation must be required before acceptance.

## 13. Git status

Final Stage 6.9 validation and Git closeout status are recorded in
`reports/stage_06_9/stage_06_9_validation.md` and in the final acceptance
response.
