# Completing the Empirical UNSW-NB15 Benchmark

**Status (2026-11-19):** One local benchmark was completed on UNSW-NB15 CSVs downloaded via the university-hosted SharePoint link on the official UNSW Research dataset page. Aggregate measurements are in [results/](results/README.md).

## 1. Obtain the source data and check permissions

The [official UNSW-NB15 dataset page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) is the dataset landing page. Its **HERE** link leads to the UNSW-hosted SharePoint/OneDrive location that the researcher used to obtain the pre-partitioned CSVs. Microsoft sign-in may be required in some sessions; this does not make the institutional link unofficial.

UNSW grants free academic research use with required attribution and retains copyright. Commercial use requires agreement with the authors. Refer to [dataset.md](dataset.md) and [references.md](references.md) for the five required citations.

Download the *pre-partitioned* CSV files (not the four raw multi-million-row CSVs):

- `UNSW_NB15_training-set.csv` — UNSW page reports 175,341 rows.
- `UNSW_NB15_testing-set.csv` — UNSW page reports 82,332 rows.

**The observed counts match UNSW's published train/test partition sizes.** The official-link download route is documented; local SHA-256 digests identify the copies used for the experiment. An independent publisher-issued reference digest was not available.

## 2. Put files only in your local clone

```text
data/raw/UNSW_NB15_training-set.csv
data/raw/UNSW_NB15_testing-set.csv
```

Both directories are Git-ignored. **Never commit original CSVs or dataset rows.**

## 3. Reproduce locally (Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip check
nids inspect-data --data-dir data/raw
nids evaluate --data-dir data/raw --output-dir artifacts/reports --seed 42 --trees 100 --max-iter 1000
python -m scripts.render_evaluation_summary --input artifacts/reports/evaluation.json --output artifacts/reports/benchmark_summary.md
streamlit run app/streamlit_app.py
```

On Linux/macOS, activate with `source .venv/bin/activate` and run the same `nids`, `python -m ...`, and `streamlit` commands.

## 4. Interpret the output correctly

- `artifacts/reports/evaluation.json` contains both candidates' *validation* results, plus the **selected model only** on the held-out test partition.
- `artifacts/reports/benchmark_summary.md` is automatically generated from measured aggregates. The exporter checks matrix totals, class counts, derived rates, consistency with model selection, and source SHA-256 **format** before writing. It does not replace independent replication of the experiment.
- `artifacts/reports/confusion_matrix.png` and `roc_curve.png` are generated from the same held-out predictions if relevant. Never imply that synthetic unit-test output is a benchmark.
- Keep input hashes, commit SHA, Python/package versions, and execution commands in the local research notebook.
- Review the summary against raw JSON, record the official download route, and update the research report using measured metrics. Commit only aggregate results, subject to provider conditions and privacy checks.

## 5. If the official download link cannot be accessed

You can run the complete unit-test suite without dataset access:

```bash
python -m pytest -q
```

Do **not** treat passing unit tests or synthetic fixture outputs as real-data benchmark results. If the official link is inaccessible, document the access issue instead of using unrelated mirrors.
