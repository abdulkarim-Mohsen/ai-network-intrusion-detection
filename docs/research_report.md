# Research Report — AI-Based Network Intrusion Detection

**Status (2026-11-18):** Methods implementation in progress; **no experiments with UNSW records or trained models have been executed**. Findings below are methodological, not benchmark results.

## Abstract

This study plans to compare Logistic Regression and Random Forest as baseline binary network-intrusion classifiers using the academic UNSW-NB15 dataset. Phase 2 implements offline dataset checks, a stratified validation partition from the designated training split, explicit feature exclusion, and a preprocessing transformer designed for training-only fitting. Numerical evaluation remains pending and no predictive performance is claimed.

## Research question

How do Logistic Regression and Random Forest compare at detecting suspicious flow records under a leakage-aware evaluation protocol, including the impact of false alarms and class imbalance?

## Dataset and permission

UNSW Sydney's official dataset page describes 175,341 training and 82,332 testing records. Those are **published dataset descriptions**, not local experiment observations. The data may be used freely for academic research according to the source's terms, with required publications cited; commercial use requires agreement by the dataset authors. No records are distributed here. See [Dataset provenance and references](dataset.md).

## Implemented methodology (Phase 2)

The loader reads only local officially named CSV files, requires target values 0/1, and verifies the training/test schema. Feature extraction drops `id`, `label` and `attack_cat`. A train/validation split applies only to the provider-designated training data using stratification and a deterministic seed, while the official test partition is held out. An **unfitted** scikit-learn column transformer is constructed for numeric imputation/scaling and categorical imputation/one-hot encoding. The implementation does not learn statistics on validation/test data.

## Verification and results

Unit tests with artificial data check invalid labels, file/schema errors, excluded ground-truth fields, fixed partitions, missing values, and behavior with previously unseen categories. **These are software tests, not intrusion-detection performance measurements.** Precision, recall, F1, confusion matrix and ROC-AUC are unavailable until the official data and actual trained models are evaluated.

## Limitations

No official records have been inspected. The preprocessing policy reflects the expected schema of the official split and could need adjustment after provider-file validation. The presence of an official partition does not guarantee independence between similar flows; selection bias, leakage at the data-collection level and domain shift will need consideration. The system is not deployment-ready.

## Next phase

Train reproducible Logistic Regression and Random Forest baselines with pipelines fitted exclusively on training records. Record software versions and training parameters. Model evaluation on the official test partition will follow only after model selection.

## References

- UNSW Canberra. [UNSW-NB15 dataset and mandatory citation list](https://research.unsw.edu.au/projects/unsw-nb15-dataset).
- Moustafa N, Slay J. [UNSW-NB15: A comprehensive data set for network intrusion detection systems](https://doi.org/10.1109/MilCIS.2015.7348942). MilCIS; 2015.
- Pedregosa F et al. [Scikit-learn: Machine Learning in Python](https://www.jmlr.org/papers/v12/pedregosa11a.html). JMLR; 2011;12:2825–2830.
- scikit-learn. [Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html).
