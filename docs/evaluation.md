# Evaluation Protocol — Phase 4

## Academic objective and status

The offline evaluation code has been **implemented and tested exclusively with synthetic fixtures**. It has **not** measured UNSW-NB15 performance. The CLI cannot authenticate a CSV by its filename. Obtain authorized official data, verify its research terms and contents, and retain the source-file SHA-256 hashes from the generated report.

## Run once on verified local official data

```bash
python -m pip install -r requirements-dev.txt
nids inspect-data --data-dir data/raw
nids evaluate --data-dir data/raw --output-dir artifacts/reports --seed 42 --validation-fraction 0.2 --trees 100 --max-iter 1000
```

`--no-plots` skips PNG creation if needed. The command is intentionally **offline**; no internet traffic capture, scanning or probing occurs. It trains fresh pipelines rather than loading potentially unsafe pickle/joblib artifacts. It may take some time on large datasets. Models trained with `nids train` are separate artifacts and are not implicitly loaded or measured here.

## Avoiding leakage

1. Load the two CSV files in their provider-designated split. Header/schema verification does inspect both sources before selection, but does **not** fit, score, or tune on test data.
2. Stratify only the designated training set into model-fitting and validation subsets using a fixed seed.
3. Fit each scikit-learn `Pipeline` (imputer, encoder, scaler, classifier) on the fitting subset; never fit it on validation/test data.
4. Evaluate **both** candidate models on the validation subset; select the larger **attack-class F1**. Logistic Regression is the predetermined winner on exact ties.
5. **After** selection, score **only** the chosen model on the held-out test partition. Do not choose hyperparameters from this score or repeatedly select models after viewing it. Test-time metrics are a final report, not a search objective.
6. Note that even a held-out provider partition cannot rule out duplicate flows, time correlation or distribution shift. Investigate those issues separately.

## Outputs (aggregate only)

`artifacts/reports/evaluation.json` contains the validation score tables, selected model, final held-out metrics, class counts, split sizes, training config, Python/library versions, SHA-256 hashes of the local input files, UTC timestamp, and limitations. No raw records, network identifiers, or per-row predictions are saved.

`artifacts/reports/confusion_matrix.png` shows **rows=true / columns=predicted** in class order `[0 (normal), 1 (attack)]`. `artifacts/reports/roc_curve.png` is written only when both true classes are present; otherwise `roc_auc` is JSON `null` with a reason and the ROC PNG is absent. All outputs are ignored by Git.

### Metrics and interpretation

- **Precision (attack)** = TP / (TP + FP); how many intrusion alarms are truly attacks.
- **Recall (attack)** = TP / (TP + FN); how many attacks were detected.
- **F1 (attack)** = harmonic mean of the two, used for validation-only selection.
- **False-positive rate (FPR)** = FP / (FP + TN), conditional on *actually normal* traffic, and is `null` if there are no normal samples.
- **False-negative rate (FNR)** = FN / (FN + TP), conditional on *actually attack* traffic, and is `null` if there are no attack samples.
- **ROC-AUC** uses positive-class probability scores (class 1). It is **undefined** if only one class appears in the evaluated split.
- **Macro F1** averages per-class F1 equally; **weighted F1** weights by observed class support.
- **Accuracy** can look artificially high under class imbalance and should not be quoted alone.

The default decision threshold is the classifier's built-in `predict` rule. Threshold calibration and uncertainty quantification are not currently implemented. All numerical results from synthetic unit tests are **software tests, not benchmark estimates**.

## References

- UNSW Sydney, [UNSW-NB15 Dataset](https://research.unsw.edu.au/projects/unsw-nb15-dataset) (check exact required citation and use terms).
- Pedregosa F et al., [Scikit-learn: Machine Learning in Python](https://www.jmlr.org/papers/v12/pedregosa11a.html), *JMLR*, 2011.
- scikit-learn: [Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html) and [Pipelines](https://scikit-learn.org/stable/modules/compose.html).
