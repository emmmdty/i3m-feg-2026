# Stage 6.8 Public Dataset Mini-Case Patch Report

## 1. Why Stage 6.8 was inserted

Stage 6.8 was inserted after Stage 6.7 because expert review identified a remaining synthetic-only risk. The patch adds a tiny public-dataset mini-case to test whether externally sourced financial event records can pass the same schema, evidence, and replay path used by the controlled simulation.

## 2. Public dataset used

- public dataset used: yes, locally
- dataset name: FewFC
- upstream repository: `https://github.com/TimeBurningFish/FewFC`
- local source: `data/raw/FewFC`
- local upstream commit observed: `ec6cac90238c`

## 3. Data source and license

FewFC is documented upstream as a public research dataset for Chinese financial event extraction. The local repository includes `LICENSE.txt` for CC BY-SA 4.0 and a README citation note.

Each converted sample record includes:

- `source_dataset`
- `source_license_note`
- `source_doc_id`
- `source_url`

No full raw public dataset archive or raw source directory was moved into committed project outputs.

## 4. Public mini-case records

`scripts/prepare_public_mini_case.py` generated:

- `data/samples/public_mini_events.jsonl`
- records: 20
- source: FewFC
- seed: 42
- max records: 20

The converted records use FewFC sentence text as `source_text` and the event trigger as the exact-match `evidence_span`. When a source record did not provide a stable ISO date, the script used `1970-01-01` and recorded the limitation in `extra_notes`.

## 5. External sanity case only

The public mini-case is only an external sanity case. It is not an extraction benchmark, not an extraction F1 evaluation, not a SOTA comparison, and not mixed with the synthetic controlled-stream result.

## 6. Schema, evidence, and replay results

Local `tables/public_mini_case_results.csv`:

| source_dataset | num_records | schema_validity | evidence_coverage | replay_completeness | active_events | version_logs | conflicts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| FewFC | 20 | 1.000000 | 1.000000 | 1.000000 | 20 | 20 | 0 |

Generated artifacts:

- CSV: `tables/public_mini_case_results.csv`
- LaTeX table: `paper/i3m_submission/tables/table_public_mini_case.tex`
- replay trace: `outputs/public_mini_replay_trace.jsonl`

## 7. Paper modifications

Modified `paper/i3m_submission/manuscript.tex`:

- Added I3M/modeling-and-simulation framing in the Introduction.
- Updated keywords to include `modeling and simulation`.
- Added `\subsection{Public-dataset mini-case}` after the metadata-hidden diagnostic.
- Added `\input{tables/table_public_mini_case.tex}`.
- Replaced the previous camera-ready-only public mini-case limitation with conservative wording that the public mini-case is small and only an external sanity check.

## 8. Reference modifications

Modified `paper/i3m_submission/references.bib`:

- Added `@misc{fewfc,...}` for the FewFC upstream repository.

## 9. Local commands and results

Preflight:

```bash
pwd
git branch --show-current
git status --short
cat AGENTS.md
```

Result:

- cwd: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- initial `git status --short`: clean
- AGENTS.md readable

Core source files are committed and readable:

- `src/graph_store.py`
- `src/evidence.py`
- `src/submission_tables.py`
- `scripts/run_metadata_hidden_replay.py`
- `paper/i3m_submission/manuscript.tex`
- `paper/i3m_submission/build_latex.sh`
- `paper/manuscript_i3m2026_v2.pdf`
- `reports/stage_06_7/stage_06_7_report.md`

Executed locally:

```bash
mkdir -p data/external data/samples outputs tables reports/stage_06_8 paper/i3m_submission/tables
python scripts/prepare_public_mini_case.py --source auto --out data/samples/public_mini_events.jsonl --max-records 20 --seed 42
python scripts/run_public_mini_case.py --input data/samples/public_mini_events.jsonl --out tables/public_mini_case_results.csv --tex-table paper/i3m_submission/tables/table_public_mini_case.tex --trace-out outputs/public_mini_replay_trace.jsonl
python scripts/run_demo.py
python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv
python scripts/run_metadata_hidden_replay.py --input data/processed/controlled_stream.jsonl --out tables/metadata_hidden_results.csv --tex-table paper/i3m_submission/tables/table_metadata_hidden.tex
python scripts/make_submission_tables.py --ablation tables/ablation_results.csv --case-study tables/case_study_updates.csv --sanity tables/sanity_check_results.csv --scale tables/scale_sensitivity_results.csv --metadata-hidden tables/metadata_hidden_results.csv --out-dir paper/i3m_submission/tables
bash paper/i3m_submission/build_latex.sh
```

Key local results:

- public mini-case: FewFC, 20 records, schema/evidence/replay all `1.000000`
- demo replay: 70 records, 40 active events, 70 version logs, 10 conflicts
- ablation Full row: schema `1.000000`, evidence `1.000000`, merge agreement `1.000000`, conflict agreement `1.000000`, replay `1.000000`
- metadata-hidden row: merge `0.200000`, conflict `0.800000`, update `0.700000`, operator `0.585714`, replay `1.000000`

## 10. Server commands and results

Code was synchronized without `--delete`:

```bash
rsync -avz \
  --exclude '.git/' \
  --exclude 'data/raw/' \
  --exclude 'data/processed/' \
  --exclude 'outputs/' \
  --exclude 'logs/' \
  --exclude 'tables/*.csv' \
  --exclude 'models/' \
  ./ gpu-4090:/home/TJK/i3m_financial_event_graph_2026/
```

Server interpreter check after one transient SSH refusal:

```bash
ssh -o ConnectTimeout=10 gpu-4090 'cd /home/TJK/i3m_financial_event_graph_2026 && pwd && /home/TJK/.conda/envs/tjk-feg/bin/python --version'
```

Result:

- server cwd: `/home/TJK/i3m_financial_event_graph_2026`
- Python: `3.10.20`

Executed server public-source preparation attempt:

```bash
ssh -o ConnectTimeout=10 gpu-4090 'set -u
cd /home/TJK/i3m_financial_event_graph_2026
mkdir -p /data/TJK/i3m/outputs /data/TJK/i3m/tables /data/TJK/i3m/reports/stage_06_8
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/prepare_public_mini_case.py --source auto --out data/samples/public_mini_events.jsonl --max-records 20 --seed 42
PREP_STATUS=$?
echo "prepare_status=${PREP_STATUS}"
if [ "${PREP_STATUS}" -eq 0 ]; then
  /home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_public_mini_case.py --input data/samples/public_mini_events.jsonl --out /data/TJK/i3m/tables/public_mini_case_results.csv --tex-table /data/TJK/i3m/reports/stage_06_8/table_public_mini_case.tex --trace-out /data/TJK/i3m/outputs/public_mini_replay_trace.jsonl
  echo "run_status=$?"
else
  echo "server public-data access unavailable; skipping run_public_mini_case.py"
fi'
```

Server result:

- `prepare_status=1`
- message: `No parseable public mini-case source found. Stage 6.8 should report dataset access/format blockage.`
- server public mini-case replay was not run

This is non-fatal for Stage 6.8 because the public mini-case is locally reproducible from the local FewFC source. The server did not have an accessible parseable public dataset source under the checked external/raw paths, and no server result was fabricated.

## 11. Training status

training: no

## 12. GPU status

no_gpu_training_required

## 13. Model/API status

- model inference: no
- external API calls: none

## 14. PDF rebuild status

`bash paper/i3m_submission/build_latex.sh` completed successfully and wrote:

- `paper/i3m_submission/manuscript.pdf`
- `paper/manuscript_i3m2026_v2.pdf`

## 15. PDF page count

`pdfinfo paper/manuscript_i3m2026_v2.pdf` reports:

- Pages: 8

## 16. PDF risk-word check

`pdftotext` output was written to:

`reports/stage_06_8/manuscript_i3m2026_v2.txt`

Forbidden PDF-text checks returned no matches for:

`TBD`, `Stage 06`, `Stage 6`, `GPT-generated`, `Codex-generated`, `AI-generated`, `stock prediction`, `trading signal`, `buy recommendation`, `sell recommendation`, `investment advice`, `outperform`, `state-of-the-art method`, `superior performance`, `Instructions to Authors`, `Insert here your abstract text`.

Expected terms are present in the PDF text:

- `public-dataset mini-case`
- `controlled replay`
- `discrete-event simulation`
- `auditability`

## 17. Recommendation

Stage 6.8 is ready for user acceptance review. The local public mini-case succeeded with FewFC and the paper now includes a conservative external sanity-check subsection.

## 18. Git status

This stage has not been committed. Git submission is intentionally deferred for user acceptance.

