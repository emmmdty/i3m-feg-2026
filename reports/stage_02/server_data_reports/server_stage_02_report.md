# Server Stage 02 Report

date: 2026-05-06T23:15:57+08:00
cwd: /home/TJK/i3m_financial_event_graph_2026
env_python: /home/TJK/.conda/envs/tjk-feg/bin/python
gpu_training: no_gpu_training_required
outputs_dir: /data/TJK/i3m/outputs
tables_dir: /data/TJK/i3m/tables

## Ablation Results
method,schema_validity,evidence_coverage,merge_accuracy,conflict_accuracy,replay_completeness,runtime_ms_per_record,num_records
Direct,1.000000,1.000000,NA,NA,NA,0.001799,70
Schema,1.000000,1.000000,NA,NA,NA,0.003222,70
Evidence,1.000000,1.000000,NA,NA,NA,0.005126,70
Full,1.000000,1.000000,1.000000,1.000000,1.000000,0.028974,70
