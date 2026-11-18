# Training Protocol — Phase 3

## What is implemented

The `nids train` command trains **two separate scikit-learn pipelines** on local authorized UNSW-NB15 training records: Logistic Regression and Random Forest. Each pipeline fits an independent feature-preparation transformer on training rows **only**. The provider's test records are not fitted on, evaluated, used for hyperparameter selection, or used for feature selection. The Phase 3 code does not compute measured performance.

## Command

Install in an isolated Python environment:

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Download the officially provided training and testing CSVs from UNSW separately under their academic terms, and place them into `data/raw/` with these exact names:

- `UNSW_NB15_training-set.csv`
- `UNSW_NB15_testing-set.csv`

Inspect files and train (offline):

```bash
nids inspect-data --data-dir data/raw
nids train --data-dir data/raw --output-dir artifacts/models --seed 42 --validation-fraction 0.2 --trees 100 --max-iter 1000
python -m pytest -q
```

The command fails if the official filenames are absent. It never downloads, captures, or scans network traffic. It is intentionally not scheduled to run automatically on the CI runner, because the real dataset is not stored in GitHub.

## Reproducibility design

- **Split:** Preserve the official test set; stratify only the provider training set into fit and validation subsets using the configured seed.
- **Leakage exclusion:** Never use `id`, `attack_cat`, or `label` as predictor features.
- **Preprocessing:** Each model has its own fitted `ColumnTransformer`; train-only median imputation and standard scaling for numerics; train-only modal imputation and one-hot encoding for categoricals (`proto`, `service`, `state`).
- **Logistic Regression:** `solver=lbfgs`, `class_weight=balanced`, configurable `max_iter` (default 1000), fixed seed.
- **Random Forest:** 100 trees by default, `max_depth=18`, `min_samples_leaf=2`, `class_weight=balanced_subsample`, `n_jobs=1`, fixed seed.
- **Same training rows:** Both models receive the identical fit partition, with identical feature names, but they do not share a fitted preprocessor.
- **Provenance:** Local training manifest records the seed, versions, target definition, class counts, training/validation sizes, model hyperparameters, timestamps, and SHA-256 of both original CSVs.
- **No official-test metrics:** The manifest flags `held_out_evaluation_performed=false` and records no classification scores. Do not infer benchmark results from passing software tests.

The manifest and models are stored locally (never automatically uploaded), as:

```
artifacts/models/
├── logistic_regression.joblib
├── random_forest.joblib
└── training_manifest.json
```

**Important:** joblib stores Python pickle-based objects. Never deserialize model files downloaded from unknown sources. Only load pipelines created and kept in your trusted local environment. If the training data change, start a new experiment with new output paths rather than treating old artifacts as comparable.

## Local test evidence

The unit test suite uses **only synthetic records** to exercise both model types, deterministic predictions, expected manifest fields, saving/reloading trusted local models, and independence from changes in official-test fixture values. These software tests are not evidence of detection efficacy on UNSW traffic.

## Known limitations / planned next stage

The current procedure does not select a winner, tune models, compute metrics, analyze distribution shifts, or assess false-positive rates. This is deliberate: **Phase 4** will implement validation-only model selection and held-out evaluation, with uncertainty and limitations clearly documented. Reproducibility across different machines or library versions is not guaranteed by random seeds alone; the manifest captures versions for auditing.
