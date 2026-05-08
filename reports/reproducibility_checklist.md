# Reproducibility Checklist

- Python version: run `python --version`; Stage 6.9 local and server project-env verification used Python 3.10.20.
- Python dependency file: `requirements.txt`.
- LaTeX requirement: `latexmk`, or `pdflatex` plus `bibtex`.
- GPU required: no.
- Training required: no.
- Reproduction label: `no_gpu_training_required`.
- Model inference required: no.
- External API calls required: none.
- Generated outputs are not committed: `outputs/`, `data/processed/`, and `tables/*.csv` are ignored.
- Public mini-case status: `data/samples/public_mini_events.jsonl` is committed, contains 20 FewFC-derived records, and is an external sanity case only.
- Final PDF path: `paper/manuscript_i3m2026_v2.pdf`.
- Canonical build command: `bash paper/i3m_submission/build_latex.sh`.
