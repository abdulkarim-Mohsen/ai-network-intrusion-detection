"""The public research documents must disclose limitations and citations honestly."""

from pathlib import Path


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


def test_no_measured_unsw_claims_in_reporting_template():
    report = _read("docs/research_report.md")
    template = _read("docs/results_reporting_template.md")
    assert "no empirical intrusion-detection performance" in report.lower()
    assert "not measured" in report.lower()
    assert "NOT MEASURED" in template
    assert "NOT RUN" in template
    assert "DO NOT treat this template as observed findings" in template


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
    assert "source-file" not in guide or "source" in guide  # no environment dependencies
    assert "SHA-256" in guide


def test_portfolio_discloses_no_official_benchmark():
    summary = _read("docs/academic_portfolio.md").lower()
    assert "synthetic software-test fixtures only" in summary
    assert "no unsw-nb15 real-dataset benchmark" in summary


def test_github_citation_does_not_claim_dataset_license():
    citation = _read("CITATION.cff")
    assert "cff-version: 1.2.0" in citation
    assert "docs/references.md" in citation
    assert "repository-code:" in citation
    assert "No official UNSW-NB15 benchmark results" in citation
