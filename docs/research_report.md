# Research Report — AI-Based Network Intrusion Detection

**Status (2026-11-18):** Phase 3 methods completed, with model fitting verified only against synthetic test fixtures; **no experiments on official UNSW data have been executed**. Findings below are methodological, not benchmark results.

## Abstract

This study plans to compare Logistic Regression and Random Forest as baseline binary network-intrusion classifiers using the academic UNSW-NB15 dataset. Phases 2–3 implement local CSV checks, a stratified validation partition from the official training split, explicit feature exclusion, and two distinct pipelines that fit preprocessing and classifiers on training-only data. Numerical evaluation remains pending and no predictive performance is claimed.

## Research question

How do Logistic Regression and Random Forest compare at detecting suspicious flow records under a leakage-aware evaluation protocol, including the impact of false alarms and class imbalance?

## Dataset and permission

UNSW Sydney's official dataset page describes 175,341 training and 82,332 testing records. Those are **published dataset descriptions**, not local experiment observations. The data may be used freely for academic research according to the source's terms, with required publications cited; commercial use requires agreement by the dataset authors. No records are distributed here. See [Dataset provenance and references](dataset.md).

## Implemented methodology (Phases 2–3)

The loader reads only local officially named CSV files, requires target values 0/1, and verifies the training/test schema. Feature extraction drops `id`, `label` and `attack_cat`. A train/validation split applies only to the provider-designated training data using stratification and a deterministic seed, while the official test partition is held out. For each baseline, a new scikit-learn Pipeline fits numeric imputation/scaling and categorical imputation/one-hot encoding on training rows only. Logistic Regression uses balanced class weights; Random Forest uses balanced-subsample weights and controlled tree depth. The training script records random states, dataset checksums, software versions, training counts and classifier parameters. No fitting uses validation or test data.

## Verification and results

Unit tests with artificial data check source validation, feature exclusions, missing values, deterministic splitting and predictions, independently fitted preprocessors, local trusted model serialization, and unaffected training when official-test fixtures are changed. **These are software tests, not intrusion-detection performance measurements.** Precision, recall, F1, confusion matrix and ROC-AUC are unavailable until the official data and actual trained models are evaluated.

## Limitations

No official records have been inspected or fitted. The preprocessing and training policies reflect expected split schema and could need adjustment after real provider-file validation. The presence of an official partition does not guarantee independence between similar flows; selection bias, leakage at the data-collection level and domain shift will need consideration. The system is not deployment-ready.

## Next phase

After acquiring the permitted official CSVs locally, run the implemented baseline training workflow and record its provenance manifest. Phase 4 will add validation-set model selection, false-positive analysis and a final held-out test evaluation. Do not infer real-world detection quality from synthetic fixture tests.

## References

- UNSW Canberra. [UNSW-NB15 dataset and mandatory citation list](https://research.unsw.edu.au/projects/unsw-nb15-dataset).
- Moustafa N, Slay J. [UNSW-NB15: A comprehensive data set for network intrusion detection systems](https://doi.org/10.1109/MilCIS.2015.7348942). MilCIS; 2015.
- Pedregosa F et al. [Scikit-learn: Machine Learning in Python](https://www.jmlr.org/papers/v12/pedregosa11a.html). JMLR; 2011;12:2825–2830.
- scikit-learn. [Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html).
