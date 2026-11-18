# Research Report — AI-Based Network Intrusion Detection

**Document status:** Research-report template. **No experiments have been executed**, so results and conclusions are intentionally not fabricated.

## Abstract

This planned study will examine whether Logistic Regression and Random Forest baselines can distinguish normal from suspicious network-flow records in a public academic dataset. Reproducibility and avoidance of test-data leakage will be central to the method. Quantitative findings will be added only after the experiments run.

## Research Question

How do Logistic Regression and Random Forest compare for binary network-intrusion classification when evaluated under a clearly specified, leakage-aware data protocol?

## Dataset and Ethics

Dataset selection is pending Phase 2 verification of source, terms, columns, permitted use, and official partitions. No private traffic or sensitive data will be collected.

## Methodology (Planned)

Training-only fit of imputation/encoding/scaling in scikit-learn pipelines; fixed random seed; identical hold-out protocol for both baselines; explicit label balance and leakage checks. Training and evaluation implementations are pending.

## Results

**Not available.** No accuracy, precision, recall, F1, confusion matrix, or ROC-AUC values have been measured.

## Limitations

The current state is only a project skeleton; offline benchmarks may not generalize to changing real networks, and false positives must be analyzed after execution.

## References

1. UNSW Sydney. UNSW-NB15 dataset. https://research.unsw.edu.au/projects/unsw-nb15-dataset
2. Pedregosa F, et al. Scikit-learn: Machine Learning in Python. *JMLR*. 2011;12:2825–2830. https://www.jmlr.org/papers/v12/pedregosa11a.html
3. Scikit-learn documentation. Pipelines and composite estimators. https://scikit-learn.org/stable/modules/compose.html
