# Model Card — Binary Offline Network-Flow Classifiers

**Status:** Code exists for both candidates; **no official-data trained model or validated performance card is available** in the repository. This is a design-stage model card and must be updated after the empirical evaluation.

## Intended use

Research and instruction on offline classification of *authorized academic network-flow tables* into normal (`label=0`) and attack (`label=1`) classes. The goal is reproducible baseline comparison. Outputs are statistical predictions, not verified security incidents.

## Out-of-scope use

Production monitoring, individual-level surveillance, live packet analysis, attribution of threat actors, medical/legal decision-making, enforcement decisions, unapproved monitoring, automated blocking, or any claim of reliable zero-day protection.

## Models and input assumptions

Two scikit-learn pipelines are implemented: Logistic Regression with balanced class weights, and Random Forest with balanced-subsample class weights. Numeric and categorical features require the official UNSW-NB15 split CSV schema. Identifiers and target-derived fields are excluded. Independent preprocessing is trained separately inside each pipeline using training records only.

## Model selection and evaluation

A fixed stratified internal validation split determines the selected model via attack-class F1. Only that model receives the held-out provider test evaluation. See [evaluation.md](evaluation.md). FPR, FNR, per-class scores, class supports and ROC-AUC (if defined) must accompany any performance claim.

## Training data / performance / fairness

- **Planned data:** UNSW-NB15, provided by UNSW Canberra under academic-use conditions.
- **Actual source records used:** None, as of the documentation date.
- **Measured real-data performance:** Not available.
- **Evaluated subpopulations or deployment regions:** None.
- **Operational false-alarm cost:** Not measured.

## Limitations and mitigation

Static academic partitions may not represent modern traffic, environments, newly emerging attacks, shifting class prevalence, or independent sessions. Domain shift, source-level duplication and false alarms can make offline scores misleading. Predictions should not trigger automated enforcement in this research prototype.

## Accountability

Source repository: https://github.com/abdulkarim-Mohsen/ai-network-intrusion-detection. Review [research_report.md](research_report.md) and [references.md](references.md) for full provenance and methodological disclosure.
