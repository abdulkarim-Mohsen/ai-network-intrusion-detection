# Reproducible Aggregate Results — UNSW-NB15 Official-Linked Download

**Researcher:** Abdulkarim Mohsen Hussein Alhuos (Cybersecurity and Networks, College of Engineering and Information Technology, Amran University).

This directory contains **aggregate results only**; no original CSVs, traffic records, identifying flow data or model binaries. The researcher downloaded the two designated CSVs by following the **HERE** link on the [official UNSW-NB15 dataset page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) to its university-hosted SharePoint/OneDrive repository. Their observed names, schemas and counts match UNSW's published partitions. SHA-256 fingerprints identify the local copies; a separate publisher-issued reference checksum was not available. The measured results are from one local benchmark.

- [evaluation.json](evaluation.json) — actual validation scores for both models, held-out scores for only the selected model, class counts, parameters, software versions and input SHA-256 digests.
- [benchmark_summary.md](benchmark_summary.md) — arithmetic-checked human-readable metrics.
- [dataset_overlap_audit.json](dataset_overlap_audit.json) — post-hoc duplicate-predictor fingerprints; potential optimism in validation and testing is a key limitation.
- [Research report](../research_report.md) — full methodology and discussion.

**Observed held-out test summary:** Random Forest chosen by validation attack F1; N=82,332, attack F1=91.91%, accuracy=90.59%, false-positive rate=17.35%. False positives=6,419 out of 37,000 normal test records. This must not be misrepresented as operational real-world detection performance.

For scientific replication, download the same pre-partitioned CSVs using UNSW's institutional link and rerun the documented procedure. Do not tune a model on the published held-out test results and call that an unbiased first evaluation.
