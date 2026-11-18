# AI-Based Network Intrusion Detection Using Machine Learning: A Reproducible Baseline Study

**Researcher:** Abdulkarim Mohsen Hussein Alhuos  
**University:** Amran University  
**Faculty:** College of Engineering and Information Technology  
**Specialization:** Cybersecurity and Networks  

**Research status:** One local **empirical benchmark completed** using UNSW-NB15 CSVs downloaded through the official UNSW Research page's university-hosted SharePoint/OneDrive link. Independent scientific replication remains outstanding.  
**Execution:** 2026-11-18T22:12:10.975945+00:00  
**Repository:** https://github.com/abdulkarim-Mohsen/ai-network-intrusion-detection  
**Research type:** Defensive, offline supervised binary network-flow classification.

> **Dataset provenance:** The researcher followed the **HERE** link on the [official UNSW-NB15 dataset page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) to the university-hosted SharePoint/OneDrive dataset folder, downloaded `UNSW_NB15_training-set.csv` and `UNSW_NB15_testing-set.csv`, and provided them for this local experiment. Both files match the provider's documented names, schemas, and record counts. The original CSVs are not redistributed on GitHub. All reported metrics were measured on these files, not synthetic fixtures. No publisher-issued reference checksum was available for a separate byte-for-byte comparison.

## Abstract

This study evaluates two supervised machine-learning baselines, Logistic Regression and Random Forest, for offline detection of suspicious network-flow records in UNSW-NB15 data downloaded through the official UNSW-linked repository. The submitted files contained 175,341 designated training records and 82,332 designated test records. A stratified 80/20 split of the designated training file supplied fitting and validation data. The numeric and categorical preprocessing components were fitted on the fitting subset only; `id`, `attack_cat`, and `label` were excluded from predictors. Random Forest was selected using validation attack-class F1 (96.22%) compared with Logistic Regression (95.03%). On the held-out test file, the selected Random Forest achieved 90.59% accuracy, 87.27% attack precision, 97.07% attack recall, 91.91% attack F1, and 98.46% ROC-AUC. Importantly, it produced 6,419 false positives among 37,000 normal test records (17.35% false-positive rate). A post-hoc feature-hash audit identified 8,054 test records sharing exact predictor hashes with records in the fitted subset, challenging the independence assumption. These measurements apply only to this local experiment and do not demonstrate production network reliability.

**Keywords:** network intrusion detection; UNSW-NB15; Logistic Regression; Random Forest; held-out evaluation; false positives; data duplication.

## 1. Introduction and research problem

Intrusion-detection systems must identify malicious activity without overwhelming analysts with false alarms. In machine-learning experiments, class imbalance, correlated or duplicate observations, source provenance, and test-set reuse can lead to misleading claims. Our research question is: **how do Logistic Regression and Random Forest compare on attack F1 when a prespecified validation protocol selects a single model for one held-out test evaluation?** This is a reproducible baseline experiment rather than a production system, novel algorithm, or peer-reviewed publication.

## 2. Dataset provenance and permission

UNSW's public dataset documentation identifies the *UNSW-NB15* train/test partitions [1–5] and specifies conditions for academic use and required references. The dataset is owned and licensed independently of this project's MIT-licensed source code. The researcher downloaded these two official pre-partitioned files via the UNSW website's institutional repository:

| Dataset file | Measured rows | Normal (label 0) | Attack (label 1) | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `UNSW_NB15_training-set.csv` | 175,341 | 56,000 | 119,341 | `bec7dd5ec88dc2a0ccc7a07879d338395ed7421750f675fd0339e07dfe0648fa` |
| `UNSW_NB15_testing-set.csv` | 82,332 | 37,000 | 45,332 | `734fe6642edf758f7c94d7d9149426b49d202fe8e7bf0bef47392489c3c0a559` |

Both files were read successfully from the uploaded ZIP, with 45 columns each including `label` and no pandas-recognized missing cells. The university webpage establishes the official download route; the recorded SHA-256 fingerprints identify the local copies, without a separate publisher-issued reference checksum for comparison. These checks do not establish independence of train/test records. Original CSV data were not committed or included in distributable archives.

## 3. Methods

### 3.1 Binary labels and predictors

The target is `label=1` for an attack and `label=0` for normal. After dropping `id`, `attack_cat`, and the target `label`, 42 predictors remain. Three are categorical (`proto`, `service`, `state`); others are numeric. Numeric imputation is by training medians followed by standardization. Categorical imputation is by training mode followed by one-hot encoding with unknown categories ignored. Training and preprocessing use the scikit-learn pipeline API [8].

### 3.2 Partitions and leakage controls

The supplied pre-designated test file was kept separate, and only the supplied training file was stratified with `random_state=42` and `validation_fraction=0.2`. The fit subset contained **140,272** records (**44,800 normal**, **95,472 attacks**); validation contained **35,069** records (**11,200 normal**, **23,869 attacks**). Each model's transformers were independently fitted on fit data only; there was no preprocessing fitted to validation or testing data. The winner was determined only from validation attack F1. The held-out test was evaluated once for the selected model. This design prevents direct **procedural** fit/test leakage but cannot eliminate duplicated or correlated source observations [7].

### 3.3 Fixed baseline configurations

- Logistic Regression: `solver=lbfgs`, `max_iter=1000`, `class_weight=balanced`, `random_state=42`.
- Random Forest: `n_estimators=100`, `max_depth=18`, `min_samples_leaf=2`, `class_weight=balanced_subsample`, `n_jobs=1`, `random_state=42`.
- Both pipelines use the same fit/validation partition and independent, training-only preprocessing.

The actual invocation was:

```bash
OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=src \
python -m nids.cli evaluate --data-dir data/raw --output-dir artifacts/reports \
  --seed 42 --trees 100 --max-iter 1000
python -m scripts.render_evaluation_summary \
  --input artifacts/reports/evaluation.json \
  --output artifacts/reports/benchmark_summary.md
```

**Measured execution environment:** Python 3.13.5; NumPy 2.3.5; pandas 2.2.3; scikit-learn 1.8.0; joblib 1.5.3. Python 3.11/3.12 software quality is checked separately in CI; this research run used Python 3.13.5. Dependency ranges were not frozen to exact lockfile hashes.

### 3.4 Metrics and model-selection rule

Attack precision is TP/(TP+FP); attack recall is TP/(TP+FN); attack F1 is their harmonic mean. False-positive rate (FPR) is FP/(FP+TN) among actual normals and false-negative rate (FNR) is FN/(FN+TP) among attacks. Confusion matrix rows are true class [0,1], columns predicted [0,1]. ROC-AUC measures discrimination across thresholds. **Only positive-class validation F1 selected the winner**; no official-test score was used to compare both candidates or retune parameters after viewing final outcomes.

## 4. Software implementation and verification

The repository contains a local CSV loader, scikit-learn feature transformer, two baseline learners, validation/test evaluator, Matplotlib confusion and ROC plots, Streamlit aggregate dashboard, and GitHub Actions quality tests. The previous software-only benchmark passed 114 tests on synthetic fixtures; those tests are distinct from measured attack-detection outcomes. The aggregate result summary passed independent arithmetic consistency checks (`scripts.render_evaluation_summary`) on this experiment. The accompanying JSON contains real evaluation metrics and version metadata. Neither the repository nor its documentation redistributes the dataset or serialized model objects.

## 5. Results — local empirical baseline

### 5.1 Validation-only comparison (35,069 records)

| Metric (validation only) | Logistic Regression | Random Forest |
| --- | ---: | ---: |
| Accuracy | 93.24% | 94.92% |
| ROC-AUC | 98.44% | 99.28% |
| False-positive rate | 10.65% | 4.98% |
| Attack precision | 95.01% | 97.60% |
| Attack recall | 95.06% | 94.88% |
| Attack F1 | 95.03% | 96.22% |

**Winner:** Random Forest (validation attack F1 96.22%, compared with Logistic Regression 95.03%). These are *validation metrics*, not both models' test scores. They are not used to claim test superiority.

### 5.2 Held-out test — Random Forest only (82,332 records)

| Measure | Observed value |
| --- | ---: |
| Accuracy | 90.59% |
| Attack precision | 87.27% |
| Attack recall | 97.07% |
| Attack F1 | 91.91% |
| Macro F1 | 90.33% |
| Weighted F1 | 90.49% |
| ROC-AUC | 98.46% |
| False-positive rate (FPR) | 17.35% |
| False-negative rate (FNR) | 2.93% |
| True negatives (TN) | 30,581 |
| False positives (FP) | 6,419 |
| False negatives (FN) | 1,328 |
| True positives (TP) | 44,004 |

**Confusion matrix** (true rows normal/attack, predicted columns normal/attack):

| Actual \ predicted | Normal | Attack |
| --- | ---: | ---: |
| Normal | 30,581 | 6,419 |
| Attack | 1,328 | 44,004 |

**Operational interpretation:** The held-out sample contains 37,000 genuinely normal records, of which 6,419 were incorrectly flagged as attacks (FPR 17.35%). The classifier missed 1,328 of 45,332 attacks (FNR 2.93%). Thus the high attack recall coexists with a notable false-alert burden. Class proportions differ between the training and test files; accuracy is insufficient on its own.

### 5.3 Post-hoc feature-duplication audit — threats to independence

Using `pandas.util.hash_pandas_object(..., index=False)` on the 42 selected predictors, **8,054 of 82,332 test records** shared an exact predictor fingerprint with at least one row in the fitted subset. In addition, 16,342 validation records shared a feature fingerprint with the fitted subset. The full designated training file contained 74,301 repeated feature-vector occurrences beyond the unique vectors. A matching 64-bit fingerprint is a practical near-exact proxy, not a formal proof of record provenance or identity, and identical feature vectors need not represent the same network event.

This diagnostic was performed **after** the completed test evaluation, not to choose or retune either model. The overlap raises concerns that validation and test metrics could be optimistic and should be treated as **benchmark-specific**, not as estimates of performance on independent or unseen live flows. Results could change under source-aware deduplication, temporal grouping or external data; such checks require a *new, separately specified experiment*, not post-hoc replacement of this final held-out score. See [overlap audit](results/dataset_overlap_audit.json).

## 6. Limitations and threats to validity

1. **Reference checksums:** The researcher used the university-hosted download repository linked from the official UNSW webpage. No publisher-issued SHA-256 reference was available for independent byte-for-byte comparison of the local copies.
2. **Correlated / duplicate observations:** Predictor-vector overlaps appear in training, validation and the held-out test. This may lead to optimistically biased metrics even without procedural preprocessing leakage.
3. **False alarms and prevalence:** The false-positive rate is 17.35%; precision is prevalence-dependent and should not be conflated with FPR. An operational false alarm count per hour cannot be inferred from this static dataset.
4. **Generalization:** The research dataset represents a historical controlled environment, not modern production infrastructure, zero-day attacks or an externally replicated deployment.
5. **Uncertainty:** There are no bootstrap confidence intervals, repeated trials, additional holdouts, threshold calibration, or independently verified robustness studies.
6. **Model scope:** Binary classification only, no attack attribution, network scanning, automatic blocking or real-time inference.
7. **Reproducibility:** Seeds and software version snapshots were preserved, but cross-platform bitwise reproducibility has not been demonstrated and no exact lockfile exists.

## 7. Ethics, security and responsible research

The experiment uses uploaded academic tabular data only; the original datasets, row-level traffic records, serialized models, credentials and sensitive inputs are excluded from Git history and generated releases. GitHub hosts only source code, academic documentation, and aggregate evaluations. This is defensive educational research software and does not conduct active scanning, exploit hosts or inspect any live system. Academic attribution and dataset-provider restrictions continue to apply.

## 8. Conclusion and next empirical step

For this one local benchmark, Random Forest exceeded Logistic Regression on the prespecified **validation attack-F1 selection metric** (96.22% versus 95.03%). Its held-out test attack F1 was 91.91%, with a substantial 17.35% FPR. The results answer the narrow, predeclared local classification comparison, but they do **not** establish superiority on the test set over Logistic Regression, generalization to deployment traffic, or external generalization. Next steps should include a newly pre-specified source-aware deduplicated evaluation. The existing held-out test results must not be reused to tune the present model and portrayed as an unbiased first evaluation.

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

