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


def test_measured_unsw_benchmark_is_recorded_consistently():
    report = _read("docs/research_report.md")
    results = _read("docs/results_reporting_template.md")
    assert "one local" in report.lower()
    assert "official unsw" in report.lower()
    assert "91.91%" in report and "17.35%" in report
    assert "completed local benchmark" in results.lower()
    assert "91.91%" in results and "17.35%" in results


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


def test_portfolio_states_measured_benchmark_and_limitations():
    summary = _read("docs/academic_portfolio.md").lower()
    assert "measured local research result" in summary
    assert "91.91%" in summary and "17.35%" in summary
    assert "sharepoint" in summary
    assert "independent generalization" in summary


def test_github_citation_does_not_claim_dataset_license():
    citation = _read("CITATION.cff")
    assert "cff-version: 1.2.0" in citation
    assert "docs/references.md" in citation
    assert "repository-code:" in citation
    assert "local UNSW-NB15 benchmark" in citation
    assert "not a deployed IDS" in citation
