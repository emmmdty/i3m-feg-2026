# Stage 03 Experiment Summary

## Training

- training: no_gpu_training_required
- gpu_training: no_gpu_training_required
- external_api_calls: none

## Inputs

- ablation: `tables/ablation_results.csv`
- case_study: `tables/case_study_updates.csv`
- replay: `outputs/replay_trace.jsonl`

## Ablation

- methods: Direct, Evidence, Full, Schema
- missing_methods: none
- full_schema_validity: 1.000000
- full_evidence_coverage: 1.000000
- full_merge_accuracy: 1.000000
- full_conflict_accuracy: 1.000000
- full_replay_completeness: 1.000000

## Case Study

- rows: 70
- operators: ADD_EVENT=40, MARK_CONFLICT=10, MERGE_EVENT=10, UPDATE_SLOT=10
- core_operators_present: ADD_EVENT, MARK_CONFLICT, MERGE_EVENT, UPDATE_SLOT

## Replay

- replay_trace_records: 70

## Acceptance

- status: PASS
- no_gpu_training_required
