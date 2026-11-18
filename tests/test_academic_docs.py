"""Documentation must distinguish measured local results from source authentication."""

import json
from pathlib import Path

from scripts.render_evaluation_summary import validate_report


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_report_contains_required_sections():
    report = _read("docs/research_report.md")
    for heading in (
        "## Abstract", "## 1. Introduction and research problem",
        "## 2. Dataset provenance and permission", "## 3. Methods",
        "## 4. Software implementation and verification",
        "## 5. Results", "## 6. Limitations", "## 7. Ethics",
        "## 8. Conclusion", "## References",
    ):
        assert heading in report


def test_results_are_measured_aggregates_with_limitations():
    report = _read("docs/research_report.md")
    template = _read("docs/results_reporting_template.md")
    summary = _read("docs/results/benchmark_summary.md")
    assert "measured" in report.lower()
    assert "source" in report.lower() and "not independently" in report.lower()
    assert "6,419" in report and "17.35%" in report
    assert "8,054" in report  # train/test predictor-vector overlap
    assert "92" not in summary.split("**Validation-selected model:**")[1][:25]
    assert "Random Forest" in template
    assert "NOT MEASURED" not in template


def test_stored_aggregate_report_passes_arithmetic_and_model_selection():
    results = json.loads(_read("docs/results/evaluation.json"))
    checked = validate_report(results)
    assert checked["selected"] == "random_forest"
    assert checked["test"]["n"] == 82332
    assert checked["test"]["fp"] == 6419
    assert checked["test"]["fn"] == 1328
    assert results["dataset_authenticity_verified_by_code"] is False
    assert results["selection_protocol"]["test_models_evaluated"] == ["random_forest"]


def test_dataset_required_citations_present():
    references = _read("docs/references.md")
    required = (
        "10.1109/MilCIS.2015.7348942",
        "10.1080/19393555.2015.1125974",
        "7948715",
        "10.1007/978-3-319-59439-2_5",
        "10.1007/978-3-030-72802-1_9",
    )
    assert all(reference in references for reference in required)
    assert "MIT license" in references


def test_reproducibility_instructions_use_actual_commands():
    guide = _read("docs/reproducibility.md")
    assert "nids inspect-data" in guide
    assert "nids train" in guide
    assert "nids evaluate" in guide
    assert "streamlit run app/streamlit_app.py" in guide
    assert "SHA-256" in guide


def test_portfolio_discloses_source_limitations_and_real_result():
    summary = _read("docs/academic_portfolio.md").lower()
    assert "empirical" not in summary or "local" in summary
    assert "user-provided" in summary
    assert "not independently authenticated" in summary
    assert "91.91%" in summary


def test_github_citation_does_not_claim_dataset_license_or_verified_origin():
    citation = _read("CITATION.cff")
    assert "cff-version: 1.2.0" in citation
    assert "docs/references.md" in citation
    assert "repository-code:" in citation
    assert "not independently verified" in citation


def test_aggregate_artifact_contains_no_raw_network_fields():
    payload = _read("docs/results/evaluation.json")
    assert "source_files_sha256" in payload
    assert "training_run" in payload
    assert '"label_mapping"' in payload
    assert '"srcip"' not in payload
    assert '"dstip"' not in payload


def test_researcher_identity_is_consistent_across_metadata():
    name = "Abdulkarim Mohsen Hussein Alhuos"
    university = "Amran University"
    report = _read("docs/research_report.md")
    portfolio = _read("docs/academic_portfolio.md")
    readme = _read("README.md")
    assert all(name in content and university in content for content in (report, portfolio, readme))
    assert "Alhuos" in _read("CITATION.cff")
    assert name in _read("pyproject.toml")
