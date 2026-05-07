# Stage 04 Report: Methodology and Prototype Implementation Drafts

## Stage Name

Stage 04 - Draft paper methodology sections and engineering documentation from the implemented prototype.

## Preflight

```bash
pwd
git branch --show-current
git status
cat AGENTS.md
```

Observed before Stage 04 execution:

- `pwd`: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- working tree: clean
- project rule checked: this is a reproducible simulation-oriented prototype, not a financial event extraction benchmark system.

## Drafts Written

- `paper/draft_sections/problem_definition.md`
- `paper/draft_sections/methodology.md`
- `paper/draft_sections/prototype_implementation.md`

The drafts describe the implemented event-record constraints, versioned graph, update operators, discrete-event replay, consistency checks, controlled perturbation stream, and reproduction scripts.

## Consistency With Code Structure

The prototype implementation draft is aligned with the current code structure:

- `src/schema.py`: normalization for flat records and nested stream records; required-field and ISO-date validation.
- `src/evidence.py`: exact evidence-span containment check.
- `src/graph_store.py`: in-memory event nodes, entity nodes, edges, version logs, merge records, conflicts, and simulation-state snapshots.
- `src/conflict.py`: rule-based operator prediction and target-event selection.
- `src/simulator.py`: ordered replay with schema/evidence gates and replay trace output.
- `src/metrics.py`: Direct, Schema, Evidence, and Full ablation rows.
- `scripts/run_demo.py`: full replay entry point.
- `scripts/run_ablation.py`: ablation-table entry point.

The methodology draft uses the implemented graph notation `G_t = (V_t, E_t, L_t)`, transition forms `G_t -> G_{t+1}` and `S_t -> S_{t+1}`, and the implemented simulation state indicators:

- `graph_version`
- `active_event_count`
- `active_entity_count`
- `merged_event_count`
- `updated_slot_count`
- `conflict_count`
- `unresolved_conflict_count`
- `replay_step`

The draft lists only the implemented operators:

- `ADD_EVENT`
- `MERGE_EVENT`
- `UPDATE_SLOT`
- `MARK_CONFLICT`
- `VERSION_LOG`

No reversal operator outside the five implemented operators is described.

## Local Reproduction

Commands run locally:

```bash
python scripts/run_demo.py

python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out tables/ablation_results.csv

python scripts/summarize_experiment.py \
  --ablation tables/ablation_results.csv \
  --case-study tables/case_study_updates.csv \
  --replay outputs/replay_trace.jsonl \
  --out reports/stage_04/experiment_summary_check.md
```

Observed local results:

- `run_demo.py`: processed 70 records, active events 40, version logs 70, conflicts 10.
- `run_ablation.py`: wrote `tables/ablation_results.csv`.
- ablation rows: `Direct`, `Schema`, `Evidence`, `Full`.
- component rows use `NA` for non-applicable merge, conflict, and replay metrics.
- `Full`: schema validity `1.000000`, evidence coverage `1.000000`, merge accuracy `1.000000`, conflict accuracy `1.000000`, replay completeness `1.000000`.
- `summarize_experiment.py`: wrote `reports/stage_04/experiment_summary_check.md`.

## Server Reproduction

Code and drafts were synced with:

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

Remote working directory:

- `/home/TJK/i3m_financial_event_graph_2026`

Remote large-output locations:

- `/data/TJK/i3m/outputs`
- `/data/TJK/i3m/tables`
- `/data/TJK/i3m/reports/stage_04`

Remote commands run with `/home/TJK/.conda/envs/tjk-feg/bin/python`:

```bash
python scripts/run_demo.py \
  --outputs-dir /data/TJK/i3m/outputs

python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out /data/TJK/i3m/tables/ablation_results.csv

python scripts/build_case_study.py \
  --replay /data/TJK/i3m/outputs/replay_trace.jsonl \
  --updates /data/TJK/i3m/outputs/updates.jsonl \
  --conflicts /data/TJK/i3m/outputs/conflicts.jsonl \
  --out /data/TJK/i3m/tables/case_study_updates.csv

python scripts/summarize_experiment.py \
  --ablation /data/TJK/i3m/tables/ablation_results.csv \
  --case-study /data/TJK/i3m/tables/case_study_updates.csv \
  --replay /data/TJK/i3m/outputs/replay_trace.jsonl \
  --out /data/TJK/i3m/reports/stage_04/experiment_summary_check.md
```

Observed server results:

- `run_demo.py`: processed 70 records, active events 40, version logs 70, conflicts 10.
- `run_ablation.py`: wrote `/data/TJK/i3m/tables/ablation_results.csv`.
- `build_case_study.py`: wrote `/data/TJK/i3m/tables/case_study_updates.csv` with 70 rows and operators `ADD_EVENT`, `MARK_CONFLICT`, `MERGE_EVENT`, `UPDATE_SLOT`.
- `summarize_experiment.py`: wrote `/data/TJK/i3m/reports/stage_04/experiment_summary_check.md`.
- server report was synced back to `reports/stage_04/server_data_reports/experiment_summary_check.md`.

## Training and GPU Use

- gpu_used: no
- training: no
- gpu_training: no
- external_api_calls: none
- no_gpu_training_required

No GPU training or model inference was started.

## Claim Audit

The Stage 04 drafts and reports were scanned for the high-risk claim phrases named in the Stage 04 checklist.

Result after cleanup: no matches in `paper/draft_sections` or `reports/stage_04`.

The drafts use conservative wording. They describe deterministic replay behavior and controlled-stream agreement, not broad extraction accuracy or market prediction capability.

## Recommendation

Stage 04 is ready for user review. The work should not be committed until user acceptance.
