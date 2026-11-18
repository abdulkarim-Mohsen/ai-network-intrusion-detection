# Academic Portfolio Project Summary

## AI-Based Network Intrusion Detection Using Machine Learning

**Researcher:** Abdulkarim Mohsen Hussein Alhuos  
**University:** Amran University  
**Faculty:** College of Engineering and Information Technology  
**Specialization:** Cybersecurity and Networks  

**Project type:** Defensive cybersecurity + applied machine learning / reproducible offline research prototype  
**Repository:** https://github.com/abdulkarim-Mohsen/ai-network-intrusion-detection

**Implementation:** Developed Python code to validate local academic network-flow data, avoid preprocessing leakage, compare Logistic Regression against Random Forest on stratified validation, evaluate the selected model on a held-out dataset, and render aggregate plots and a Streamlit dashboard. GitHub Actions enforces unit tests, dependency sanity and minimum 90% statement coverage on Python 3.11/3.12.

**Measured local research result:** A single completed benchmark on *user-provided files named for UNSW-NB15 designated partitions* selected Random Forest by attack validation F1 (96.22%); on the 82,332-row held-out test it achieved 91.91% attack F1 and 17.35% FPR. **UNSW file bytes were not independently authenticated.** Model selection and final evaluation were distinct, but a post-hoc feature-fingerprint audit found 8,054 test records matching fitted predictor vectors, raising a substantial independence limitation.

**Research integrity:** This is an implemented, evaluated academic *prototype*, **not** a peer-reviewed contribution or a validated production intrusion-detection system. The results are specific to one local split and must not be presented as external generalization. Only aggregate results are published; datasets and model binaries are kept out of the repository.

**Next research directions:** independently verify provider dataset file bytes, prespecify a group- or time-aware deduplicated protocol on a new holdout, compare baseline stability and false alert burden, and replicate on independent authorized data.

See the [research report](research_report.md), [aggregate results](results/README.md), [model card](model_card.md), and [bibliography](references.md).
