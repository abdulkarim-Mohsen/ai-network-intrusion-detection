# Academic Portfolio Project Summary

## AI-Based Network Intrusion Detection Using Machine Learning

**Type:** Defensive cybersecurity / applied machine learning research software  
**Repository:** https://github.com/abdulkarim-Mohsen/ai-network-intrusion-detection

**Project description.** Developed a structured Python research prototype for comparing Logistic Regression and Random Forest on *authorized academic network-flow records*. The software includes local dataset/schema validation, leakage-aware training-only preprocessing, deterministic model baselines, validation-only model selection, held-out metrics, a read-only Streamlit dashboard, unit/integration tests, and Python 3.11/3.12 continuous integration.

**Demonstrable engineering work.** Source-controlled modules and documentation, automated test quality gates (minimum 90% source coverage), checks against accidentally committing private datasets or secrets, and explicit preservation of dataset-provider terms and citations. Reproducibility metadata includes a fixed seed, installed software versions, configuration, class counts and file hashes when genuine local experiments are executed.

**Research-integrity statement.** As of the documentation release, verification has used **synthetic software-test fixtures only**; **no UNSW-NB15 real-dataset benchmark or empirical detection performance is claimed**. This is suitable for explaining an implemented research methodology and software engineering skills, but it should not be described as a published or experimentally validated detection algorithm.

**Future empirical milestone.** Independently obtain official UNSW-NB15 CSVs under UNSW's academic-use conditions, run the existing leakage-aware pipeline, document measured precision/recall/F1, ROC-AUC, false-positive and false-negative rates, and discuss generalization limitations.

For details, see [research report](research_report.md), [reproducibility instructions](reproducibility.md) and [model card](model_card.md).
