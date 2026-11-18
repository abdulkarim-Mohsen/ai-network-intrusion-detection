# AI-Based Network Intrusion Detection Using Machine Learning: A Reproducible Baseline Study

**Research status:** Methods and software implemented; **official-dataset benchmark not yet conducted**  
**Report version:** 2026-11-18 (documentation release)  
**Repository:** https://github.com/abdulkarim-Mohsen/ai-network-intrusion-detection  
**Study type:** Defensive, offline, supervised binary classification research

> **Interpretation notice.** This document is a complete *research-protocol and software-verification report*, not a completed empirical comparison on UNSW-NB15. Real-dataset measurements must not be inferred from passing software tests. All tables explicitly distinguish provider facts, observations of code tests, and pending results.

## Abstract

Intrusion-detection classifiers must identify suspicious network flows while controlling false alarms. This project implements a reproducible, offline methodology to compare Logistic Regression and Random Forest for binary network-flow classification. The proposed benchmark uses the publicly documented UNSW-NB15 research corpus, retaining its provider-designated test partition and reserving an internal stratified validation split for model selection. A scikit-learn pipeline fits imputation, scaling, and categorical encoding exclusively on fitting data. The implementation computes per-class precision, recall, F1, ROC-AUC when defined, confusion matrices, false-positive rate, and false-negative rate; it also includes a read-only Streamlit dashboard and automated CI checks. The software pipeline has been exercised on synthetic fixtures, but the official UNSW-NB15 records have not been obtained or evaluated in this project. Therefore **no empirical intrusion-detection performance or superiority claim is reported**. The contribution at this stage is a transparent and testable baseline protocol with explicit limitations and reproducibility instructions.

**Keywords:** network intrusion detection; supervised machine learning; UNSW-NB15; reproducibility; data leakage; false-positive rate.

## 1. Introduction and research problem

Machine-learning-based network intrusion detection attempts to label network-flow observations as normal or suspicious. Reported performance depends not only on algorithms, but also on dataset composition, evaluation partitions, class imbalance, and how preprocessing is fitted. Leakage between model development and test data can produce overly optimistic estimates [7]. False positives are operationally costly because they require inspection of traffic that may be legitimate. The objective here is to establish an auditable comparison of two widely used baseline classifiers, not to claim a deployable security product.

**Research question.** Under a training-only preprocessing protocol and an untouched, provider-defined test partition, how do Logistic Regression and Random Forest compare on attack-class F1 and false-positive/negative rates?

**Objectives.** (i) Validate local academic dataset files; (ii) control avoidable preprocessing leakage; (iii) train two reproducible baselines; (iv) select a model using validation-only attack F1; (v) report class-aware held-out metrics without exposing flow records; and (vi) document code quality, limitations, and research provenance.

**No prespecified winner is assumed.** A numerical difference in a future single held-out run is not automatically a statistically significant or generalizable improvement.

## 2. Dataset provenance and permission

The planned data source is the **UNSW-NB15** dataset curated by UNSW Canberra [1–5]. The official UNSW source describes a configured partition with **175,341 training records** and **82,332 test records**. These figures are **published provider metadata, not observations made by this project**. The required local filenames are `UNSW_NB15_training-set.csv` and `UNSW_NB15_testing-set.csv` [1].

UNSW states that its dataset may be used for academic research with required attribution, while commercial use requires agreement from the authors. The provider instructs users to cite five specified publications [1–5]. The repository's MIT license covers **original source code only**; it does not relicense or redistribute dataset records. Official file identity and usage rights must be verified independently; matching filenames and local SHA-256 digests establish local file consistency but **do not authenticate a download's origin**. Data is not included in this repository.

## 3. Methods

### 3.1 Classification target and predictors

Binary target `label` uses **0 = normal** and **1 = attack**. The loader checks column consistency and the target encoding. The predictor matrix excludes `label`, `attack_cat` (ground-truth category) and `id` (identifier). The explicit categorical columns are `proto`, `service`, and `state`. Remaining supported numerical fields follow the official split schema. Missing/invalid numeric values are handled by median imputation; numeric features are standardized. Categorical missing values are imputed by the most frequent training value, then one-hot encoded with unknown categories ignored. The meaningful category `-` is retained [6].

### 3.2 Data partitioning and leakage prevention

The *provider's official test set* is held aside. Only the official training set is stratified into a model-fitting subset and a validation subset (`validation_fraction=0.2`, `seed=42` by default). Each algorithm receives an independent scikit-learn `Pipeline` containing a fresh, unfitted preprocessing transformer. All fitted statistics and learned categorical vocabularies come from the fitting subset only. Neither validation nor test observations are used to fit transformations. The test set is not used for hyperparameter search, feature selection or winner selection. Checking the file schema is not evidence of absence of source-level duplicates or temporally correlated flows [7].

### 3.3 Baseline models

- **Logistic Regression:** `solver=lbfgs`, `class_weight=balanced`, default `max_iter=1000`, `random_state=42`.
- **Random Forest:** default `n_estimators=100`, `max_depth=18`, `min_samples_leaf=2`, `class_weight=balanced_subsample`, `n_jobs=1`, `random_state=42`.

These are fixed baseline settings, not an exhaustive hyperparameter search. Both models train on the same fitting subset. The separate `nids train` command saves locally trusted serialized pipelines and a manifest; the `nids evaluate` command fits fresh models rather than loading those serialized objects. Dataset hashes, parameters, class counts, software versions and timestamps are recorded with the generated artifacts.

### 3.4 Model selection and final evaluation

Both classifiers are scored on the **validation** subset. The winner maximizes **attack-class F1** (`positive_class=1`); the predetermined exact-tie rule chooses Logistic Regression. After this selection, **only the selected model** is scored on the official held-out test set. The classifier's native `predict` decision rule is used; no threshold search is performed. The protocol does not implement a repeated cross-validation, confidence intervals, calibration procedure or cross-dataset generalization test. Changing models after viewing the official test score would compromise its independent interpretation.

### 3.5 Evaluation measures

For the positive/attack class, `TP` denotes detected attacks, `FP` normal records flagged as attacks, `TN` correctly recognized normal records, and `FN` missed attacks.

| Measure | Definition / purpose |
| --- | --- |
| Attack precision | `TP / (TP + FP)`; proportion of alerts corresponding to attacks |
| Attack recall | `TP / (TP + FN)`; fraction of attacks detected |
| Attack F1 | `2 × precision × recall / (precision + recall)`; validation selection criterion |
| False-positive rate | `FP / (FP + TN)`; proportion of truly normal records incorrectly alerted |
| False-negative rate | `FN / (FN + TP)`; proportion of actual attacks missed |
| Confusion matrix | `[[TN, FP], [FN, TP]]` with true classes as rows |
| ROC-AUC | Threshold-independent ranking summary; undefined when only one true class appears |

Class support, macro F1, weighted F1 and accuracy are recorded for context. Precision and F1 definitions require conventional handling of zero-denominator cases; the code uses scikit-learn's `zero_division=0`. A large accuracy value alone would not be sufficient evidence under class imbalance [6,7].

## 4. Software implementation and verification

The codebase separates file loading, feature transformation, training, evaluation, chart generation, dashboard validation, and tests. Its Streamlit interface reads an offline aggregate `evaluation.json`; it does not scan networks, capture packets, deserialize downloaded models or display individual network records. The dashboard validates the basic arithmetic consistency of submitted confusion-matrix summaries but **cannot certify dataset origin**. GitHub Actions tests Python 3.11 and 3.12, installs project dependencies, checks dependency consistency, compiles Python, runs a tracked-file hygiene check, and enforces at least 90% coverage [8].

**Observed software evidence (2026-11-18):** The full locally rerun suite passed **103 tests** (including documentation integrity tests), with **94.72%** source coverage. The Phase 6 GitHub Actions workflow completed successfully for both Python-version jobs; the Phase 7 workflow must be verified independently after upload. These numbers describe **software quality only**, not classification results. Documentation-only changes should be rechecked with the same CI gate and the new run identified in the experiment log. Sources for CI evidence are linked in [quality_assurance.md](quality_assurance.md).

## 5. Results — empirical benchmark status

**No official UNSW-NB15 experiments have been run.** No measured model performance figures, confusion matrices, or performance graphs from official data are available. Any numbers in synthetic unit tests demonstrate expected behavior of software functions rather than benchmark effectiveness.

| Benchmark output | Logistic Regression | Random Forest | Basis |
| --- | --- | --- | --- |
| Validation attack-class F1 | Not measured | Not measured | Official records unavailable |
| Validation ROC-AUC | Not measured | Not measured | Official records unavailable |
| Selected model | Not determined | Not determined | No official validation results |
| Held-out attack precision / recall / F1 | Not measured | Not measured | Final test run not performed |
| Held-out FPR / FNR / ROC-AUC | Not measured | Not measured | Final test run not performed |

A complete future empirical results table must identify the tested official files, their SHA-256 digests, model selection criterion, observed class counts, confusion matrix, runtime environment and exact commands. The report should not be updated to state that UNSW results exist until those steps actually occur. Use [results_reporting_template.md](results_reporting_template.md) for that future update.

## 6. Limitations and threats to validity

1. **External validity:** UNSW-NB15 was created in a controlled research environment. Even a high future benchmark score would not establish effectiveness against contemporary production traffic.
2. **Source authenticity:** CSV filenames and hashes are insufficient to prove an official download; provenance must be checked manually.
3. **Evaluation dependence:** Related or duplicated flows, collection-period dependencies, and distribution changes can undermine apparent train/test independence.
4. **Class imbalance:** Overall accuracy can hide missed attacks; FPR is conditional on normal records and must not be confused with the false-discovery rate (`FP/(TP+FP)`).
5. **Model scope:** This is binary flow classification, not attack-category attribution or live incident response. Decision thresholds are not calibrated and class probabilities may be miscalibrated.
6. **Uncertainty:** The protocol does not currently calculate confidence intervals or perform external replication; a single test split is inadequate for broad causal or production claims.
7. **Evaluation status:** All present verification uses synthetic fixtures; it cannot establish predictive utility on official data.
8. **Dependency reproducibility:** Compatible versions are bounded but not fully pinned to exact lockfile hashes. Environment versions are recorded when training/evaluation is actually run.

## 7. Ethics, security and responsible research

Only lawfully obtained, authorized academic records are in scope. Raw traffic, user identifiers, credentials, operational logs and trained models are omitted from Git history; Git index hygiene checks help prevent accidental inclusion. The software performs **no active scanning, exploitation, surveillance or live monitoring**. Generated reports contain only aggregate results. The project is not a certified intrusion-detection product or an operational security guarantee. Research limitations and data-source obligations must accompany any portfolio or scholarship presentation.

## 8. Conclusion and next empirical step

The project delivers a modular, tested research implementation and an explicit validation/test protocol. **The software is implemented; the empirical research question remains unanswered** until the authorized original UNSW-NB15 CSVs are independently verified and evaluated. Once data are available, run the documented commands, preserve the artifact manifest and experiment outputs locally, and replace the results table only with measured values. See [reproducibility.md](reproducibility.md) for exact steps.

## References

The five dataset-provider-requested research citations are report items **[2]–[6]** (the original UNSW webpage is item [1]). Complete details are maintained in [references.md](references.md).

1. UNSW Canberra. *The UNSW-NB15 Dataset.* https://research.unsw.edu.au/projects/unsw-nb15-dataset (official source and citation conditions).
2. Moustafa N, Slay J. *UNSW-NB15: A Comprehensive Data Set for Network Intrusion Detection Systems.* MilCIS, 2015. https://doi.org/10.1109/MilCIS.2015.7348942
3. Moustafa N, Slay J. *The Evaluation of Network Anomaly Detection Systems: Statistical Analysis of the UNSW-NB15 Dataset and the Comparison with the KDD99 Dataset.* Information Security Journal, 2016. https://doi.org/10.1080/19393555.2015.1125974
4. Moustafa N, et al. *Novel Geometric Area Analysis Technique for Anomaly Detection Using Trapezoidal Area Estimation on Large-Scale Networks.* IEEE Transactions on Big Data, 2017. https://ieeexplore.ieee.org/document/7948715
5. Moustafa N, Creech G, Slay J. *Big Data Analytics for Intrusion Detection System: Statistical Decision-Making Using Finite Dirichlet Mixture Models.* Springer, 2017. https://doi.org/10.1007/978-3-319-59439-2_5
6. Sarhan M, Layeghy S, Moustafa N, Portmann M. *NetFlow Datasets for Machine Learning-Based Network Intrusion Detection Systems.* 2021. https://doi.org/10.1007/978-3-030-72802-1_9
7. Kapoor S, Narayanan A. *Leakage and the Reproducibility Crisis in Machine-Learning-Based Science.* Patterns, 2023. https://doi.org/10.1016/j.patter.2023.100804
8. Pedregosa F, et al. *Scikit-learn: Machine Learning in Python.* JMLR. 2011;12:2825–2830. https://www.jmlr.org/papers/v12/pedregosa11a.html

