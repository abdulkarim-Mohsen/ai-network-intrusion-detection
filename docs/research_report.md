# Research Report — AI-Based Network Intrusion Detection

**Status (2026-11-18):** Phase 5 includes a read-only aggregate dashboard; software is verified only with synthetic test fixtures; **no experiments on official UNSW data have been executed**. Findings below are methodological, not benchmark results.

## Abstract

This study plans to compare Logistic Regression and Random Forest as baseline binary network-intrusion classifiers using the academic UNSW-NB15 dataset. Phases 2–5 implement local CSV checks, training-only preprocessing, two baseline classifiers, validation-only model selection, selected-model held-out evaluation with aggregate charts, and a read-only Streamlit reporting interface. Numerical evaluation on real data remains pending and no detection performance is claimed.

## Research question

How do Logistic Regression and Random Forest compare at detecting suspicious flow records under a leakage-aware evaluation protocol, including the impact of false alarms and class imbalance?

## Dataset and permission

UNSW Sydney's official dataset page describes 175,341 training and 82,332 testing records. Those are **published dataset descriptions**, not local experiment observations. The data may be used freely for academic research according to the source's terms, with required publications cited; commercial use requires agreement by the dataset authors. No records are distributed here. See [Dataset provenance and references](dataset.md).

## Implemented methodology (Phases 2–4)

The loader reads only local officially named CSV files, requires target values 0/1, and verifies the training/test schema. Feature extraction drops `id`, `label` and `attack_cat`. A train/validation split applies only to the provider-designated training data using stratification and a deterministic seed, while the official test partition is held out. For each baseline, a new scikit-learn Pipeline fits numeric imputation/scaling and categorical imputation/one-hot encoding on training rows only. Logistic Regression uses balanced class weights; Random Forest uses balanced-subsample weights and controlled tree depth. The training script records random states, dataset checksums, software versions, training counts and classifier parameters. No fitting uses validation or test data. **Evaluation protocol:** both classifiers are scored on the internal validation split; the model with higher F1 for attacks (positive label 1) is selected with a documented deterministic tie-breaker. Only the selected model is then scored on the held-out test split. Results include per-class support, precision, recall, F1, macro/weighted F1, confusion matrix, ROC-AUC where defined, false-positive rate among truly normal records, and false-negative rate among truly attack records. The current pipeline does not select its winner using the test results. Verification of source authenticity and terms remains a separate manual step.

## Verification and results

Unit tests with artificial data check source validation, feature exclusions, missing values, deterministic splitting and predictions, independently fitted preprocessors, local trusted model serialization, and unaffected training when official-test fixtures are changed. **These are software tests, not intrusion-detection performance measurements.** The evaluation algorithm, plots and dashboard adapter were exercised on fictional rows; their numeric outputs **must not be reported as UNSW benchmark findings**. Valid benchmark precision, recall, F1, confusion matrices and ROC-AUC remain unavailable until independently verified official files are evaluated.

## Dashboard (Phase 5)

The offline Streamlit interface reads a fixed local `evaluation.json` file and validates consistency between confusion counts and metric values before displaying results. It compares both candidates on validation only; the separate test tab displays the previously selected model only, with a confusion matrix, class support, false-positive/negative rates and ROC-AUC if defined. Empty or corrupt reports are not replaced with invented performance. The display does not load or execute saved models, retrieve private flows, or monitor any live network; successful synthetic UI-mock tests are **not** proof of real-data performance or browser compatibility. See [Dashboard setup and limitations](dashboard.md).

## Limitations

No official records have been inspected or fitted. The preprocessing and training policies reflect expected split schema and could need adjustment after real provider-file validation. The presence of an official partition does not guarantee independence between similar flows; selection bias, leakage at the data-collection level and domain shift will need consideration. The system is not deployment-ready.

## Next phase

After acquiring the permitted official CSVs locally, run the implemented baseline training workflow and record its provenance manifest. Run `nids evaluate --data-dir data/raw --output-dir artifacts/reports` once on the verified official files and record the environment, hashes, and measured results. Do not choose hyperparameters or further tune models based on this held-out test run; that would invalidate its purpose. Do not infer real-world detection quality from synthetic fixture tests.

## References

- UNSW Canberra. [UNSW-NB15 dataset and mandatory citation list](https://research.unsw.edu.au/projects/unsw-nb15-dataset).
- Moustafa N, Slay J. [UNSW-NB15: A comprehensive data set for network intrusion detection systems](https://doi.org/10.1109/MilCIS.2015.7348942). MilCIS; 2015.
- Pedregosa F et al. [Scikit-learn: Machine Learning in Python](https://www.jmlr.org/papers/v12/pedregosa11a.html). JMLR; 2011;12:2825–2830.
- scikit-learn. [Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html).
