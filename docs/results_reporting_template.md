# Empirical Results Reporting Template (UNFILLED)

> **DO NOT treat this template as observed findings.** Complete it only after independently verifying the official UNSW-NB15 download and actually running `nids evaluate` on those authorized files. Do not copy synthetic fixture scores from unit tests into this table.

## Experiment identity

| Field | Actual value (to be recorded) |
| --- | --- |
| Date/time of final evaluation (UTC) | NOT RUN |
| Source provider and download/access details | NOT VERIFIED LOCALLY |
| Git commit SHA | NOT RECORDED |
| Python / NumPy / pandas / scikit-learn versions | NOT RECORDED |
| Training CSV SHA-256 | NOT RECORDED |
| Test CSV SHA-256 | NOT RECORDED |
| Train / validation / held-out observed class counts | NOT MEASURED |
| Seed and classifier parameters | See default protocol; confirm actual run flags |

## Validation-only model comparison

| Validation metric | Logistic Regression | Random Forest |
| --- | --- | --- |
| Attack precision | NOT MEASURED | NOT MEASURED |
| Attack recall | NOT MEASURED | NOT MEASURED |
| Attack F1 (selection criterion) | NOT MEASURED | NOT MEASURED |
| ROC-AUC (when defined) | NOT MEASURED | NOT MEASURED |
| Class support | NOT MEASURED | NOT MEASURED |

**Selected model by attack F1:** NOT DETERMINED.

## Held-out evaluation — selected model only

| Field | Observation |
| --- | --- |
| Model name | NOT DETERMINED |
| TN, FP, FN, TP | NOT MEASURED |
| Attack precision | NOT MEASURED |
| Attack recall | NOT MEASURED |
| Attack F1 | NOT MEASURED |
| Macro / weighted F1 | NOT MEASURED |
| False-positive rate `FP/(FP+TN)` | NOT MEASURED |
| False-negative rate `FN/(FN+TP)` | NOT MEASURED |
| ROC-AUC or undefined reason | NOT MEASURED |

The repository intentionally does **not** calculate final test metrics for both candidates. A validation-only comparison is appropriate; selecting a new winner using the held-out test is not.

## Interpretation and limitations (complete with verified evidence)

Describe the observed class balance and false-alarm burden, dataset-split dependence, dataset authenticity verification, whether the reported scope is limited to synthetic testbed flows, and which conclusions **cannot** be drawn about live networks.
