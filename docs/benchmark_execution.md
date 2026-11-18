# Completing the Empirical UNSW-NB15 Benchmark

**Status (2026-11-19):** The code, CLI, dashboard, and unit tests are implemented. **The official CSV files have not been obtained in this execution environment, so no authentic UNSW-NB15 model-accuracy measurements can be reported.**

## 1. Obtain the source data and check permissions

The [UNSW-NB15 research page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) is the original dataset landing page. Its dataset download link currently redirects to a Microsoft sign-in page in the available browser session. If that link is unavailable, follow the provider's access instructions or contact the provider. **Do not substitute an arbitrary mirror while claiming official provenance.**

UNSW grants free academic research use with required attribution and retains copyright. Commercial use requires agreement with the authors. Refer to [dataset.md](dataset.md) and [references.md](references.md) for the five required citations.

Download the *pre-partitioned* CSV files (not the four raw multi-million-row CSVs):

- `UNSW_NB15_training-set.csv` — UNSW page reports 175,341 rows.
- `UNSW_NB15_testing-set.csv` — UNSW page reports 82,332 rows.

**Those counts come from UNSW's page and have not been measured in our local environment.** The observed rows must be checked after the files are obtained. Retain an independent record of where and when the files were downloaded; a SHA-256 digest validates local identity, not authenticity.

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
- `artifacts/reports/benchmark_summary.md` is automatically generated from measured aggregates. The exporter checks matrix totals, class counts, derived rates, consistency with model selection, and source SHA-256 **format** before writing. It cannot authenticate UNSW files or independently reproduce results.
- `artifacts/reports/confusion_matrix.png` and `roc_curve.png` are generated from the same held-out predictions if relevant. Never imply that synthetic unit-test output is a benchmark.
- Keep input hashes, commit SHA, Python/package versions, and execution commands in the local research notebook.
- Review summary against the raw JSON manually, then **only after provenance verification** update `docs/research_report.md` and `docs/results_reporting_template.md` with the actual measured figures. Commit aggregate results only after checking data-provider permissions and privacy implications.

## 5. If official download is unavailable

You can run the complete unit-test suite without dataset access:

```bash
python -m pytest -q
```

Do **not** treat passing unit tests, synthetic fixture metrics, or unverified mirror-based measurements as official research results. A missing dataset is an access blocker, not a failure of the verified software tests.
