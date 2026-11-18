# Testing, Code Quality, and Release Controls — Phase 6

## Scope

This repository contains an **offline research prototype**, not a production intrusion-detection system. Phase 6 adds continuous-integration quality gates and a Git-index hygiene check. Software tests use **synthetic, fictional tabular samples only**; their high pass rate and source coverage **do not measure attack-detection performance**.

## CI on GitHub Actions

On every `push` and `pull_request`, `.github/workflows/ci.yml` runs separate jobs for **Python 3.11 and 3.12**. It:

1. Checks out the repository with read-only `contents` permission.
2. Installs the project with development test requirements.
3. Runs `python -m pip check` to detect inconsistent installed package dependencies.
4. Checks the **Git index** for mistakenly staged datasets, generated models/results, or credential filenames, even if they were force-added despite `.gitignore`.
5. Compiles all application, package, test, and maintenance Python source files.
6. Runs the offline `nids status` smoke test.
7. Runs pytest, requiring at least **90% combined statement coverage** across `nids` and the Streamlit app.

The workflow has a 20-minute job timeout and cancels superseded runs for the same branch or pull request. Passing gates on GitHub are confirmed only when the workflow concludes successfully; committed workflow configuration alone is not proof of successful execution.

## Running locally

Use an isolated Python 3.11 or 3.12 environment. **No official data is necessary** for any quality checks below.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
python scripts/check_repo_hygiene.py --root .
python -m compileall -q src app tests scripts
nids status
python -m pytest -q --cov=nids --cov=app --cov-report=term-missing:skip-covered --cov-fail-under=90
```

The `pip check` result applies to **the current environment**, including unrelated packages, and must be interpreted accordingly. For this reason use a fresh virtual environment to reproduce CI results. Full production runs may require additional memory and processing time.

## Tests and invariants

- **Input validation:** expected local CSV filenames, binary target, required columns, matching train/test schema; no automatic downloads.
- **Leakage prevention:** fit preprocessing only on the training subset; test records and labels do not determine model fitting or selection.
- **Reproducibility:** deterministic seeds, separate estimators/transformers, saved configuration, source hashes and software versions.
- **Metrics:** known precision/recall/F1, FPR/FNR, ROC-AUC and one-class undefined cases; chosen model based only on validation F1.
- **Dashboard:** strict aggregate-report schema, fixed JSON path and size limit, honest empty state, no deserialization of untrusted model objects.
- **Release hygiene:** CI rejects tracked filenames under `data/raw`, `data/processed`, `artifacts/models`, or `artifacts/reports` other than `.gitkeep`; it also rejects common private-key/credential extensions, staged `.env` files, and locally generated synchronization manifests.

**Limitation:** Filename checks do not discover secrets inside ordinary source files and cannot authenticate an externally downloaded dataset. GitHub scans, reviews, and normal secure-development practices are still necessary. Never commit real or confidential traffic, passwords, tokens, or authentic personal data.

## Dependency maintenance

`.github/dependabot.yml` requests weekly pull requests for Python dependency updates and GitHub Actions versions. These updates are **proposals**, not auto-merges; review their changes and require CI to pass. The dependency ranges in `pyproject.toml` support reproducible development within documented version constraints but **are not an exact frozen lockfile**. Published experimental runs should retain the environment version manifest from the training workflow.

## Report status

- Code and tests are intended to run without external datasets.
- A passing unit-test suite confirms internal program behavior on controlled synthetic inputs, **not** the scientific efficacy of an IDS.
- Running Streamlit in a browser and benchmarking on authorized official UNSW records remain separate validations; do not claim either until performed.


## Public evidence and Phase 7 update

The Phase 6 CI workflow completed successfully on the isolated GitHub runners: [workflow run 44338575947](https://github.com/abdulkarim-Mohsen/ai-network-intrusion-detection/actions/runs/44338575947). Phase 7 adds academic-documentation integrity tests; rerun CI on the new commit before claiming Phase 7 GitHub verification. Local Phase 7 verification: 103/103 tests passed, 94.72% coverage. Local `pip check` has an unrelated MoviePy/Pillow conflict in the shared sandbox; this should not be misreported as a failed test on the project's clean CI environment.
