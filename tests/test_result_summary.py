"""Synthetic fixtures only: no empirical research numbers are produced."""

import json

import pytest

from nids.models.evaluate import calculate_metrics
from scripts.render_evaluation_summary import InvalidEvaluation, main, render_markdown, validate_report


def _local_fixture():
    # All fixture scores are synthetic sanity checks, never research evidence.
    normal = calculate_metrics([0, 0, 1, 1], [0, 1, 1, 1], [0.1, 0.8, 0.7, 0.9])
    better = calculate_metrics([0, 0, 1, 1], [0, 0, 1, 1], [0.1, 0.2, 0.7, 0.9])
    return {
        "status": "evaluation_completed",
        "selected_model": "random_forest",
        "selection_protocol": {"test_models_evaluated": ["random_forest"]},
        "validation": {"logistic_regression": normal, "random_forest": better},
        "official_test_selected_model": better,
        "source_files_sha256": {
            "UNSW_NB15_training-set.csv": "a" * 64,
            "UNSW_NB15_testing-set.csv": "b" * 64,
        },
    }


def test_local_fixture_passes_arithmetic_checks():
    report = _local_fixture()
    assert validate_report(report)["selected"] == "random_forest"
    summary = render_markdown(report)
    assert "Validation-selected model" in summary
    assert "not" in summary.lower()
    assert "independently authenticate" in summary
    assert "False positives" in summary


def test_missing_test_report_rejected():
    data = _local_fixture()
    del data["official_test_selected_model"]
    with pytest.raises(InvalidEvaluation):
        validate_report(data)


def test_tampered_confusion_matrix_rejected():
    data = _local_fixture()
    data["official_test_selected_model"]["confusion_matrix"][0][1] = 8
    with pytest.raises(InvalidEvaluation, match="confusion-matrix total"):
        validate_report(data)


def test_tampered_precision_rejected():
    data = _local_fixture()
    data["official_test_selected_model"]["per_class"]["1"]["precision"] = 0.0
    with pytest.raises(InvalidEvaluation, match="precision"):
        validate_report(data)


def test_wrong_winner_rejected():
    data = _local_fixture()
    data["selected_model"] = "logistic_regression"
    with pytest.raises(InvalidEvaluation, match="Selected model"):
        validate_report(data)


def test_unrecognized_report_and_unverified_hash_rejected():
    data = _local_fixture()
    data["status"] = "fitted_models_without_evaluation"
    with pytest.raises(InvalidEvaluation):
        validate_report(data)
    data = _local_fixture()
    data["source_files_sha256"]["UNSW_NB15_testing-set.csv"] = "fake"
    with pytest.raises(InvalidEvaluation, match="SHA-256"):
        validate_report(data)


def test_cli_generates_only_local_summary(tmp_path):
    source = tmp_path / "evaluation.json"
    source.write_text(json.dumps(_local_fixture()), encoding="utf-8")
    output = tmp_path / "artifacts" / "summary.md"
    assert main(["--input", str(source), "--output", str(output)]) == 0
    assert output.is_file()
    assert "UNSW" in output.read_text(encoding="utf-8")


def test_cli_missing_input_does_not_create_a_summary(tmp_path):
    destination = tmp_path / "summary.md"
    with pytest.raises(SystemExit) as exc:
        main(["--input", str(tmp_path / "missing.json"), "--output", str(destination)])
    assert exc.value.code == 2
    assert not destination.exists()


def test_single_class_auc_none_works():
    data = _local_fixture()
    oneclass = calculate_metrics([0, 0, 0], [0, 0, 1], [0.1, 0.2, 0.9])
    data["official_test_selected_model"] = oneclass
    summary = render_markdown(data)
    assert "Undefined" in summary


def test_rejects_fabricated_nonfinite_or_invalid_metrics():
    data = _local_fixture()
    data["official_test_selected_model"]["accuracy"] = float("nan")
    with pytest.raises(InvalidEvaluation, match="accuracy"):
        validate_report(data)
    data = _local_fixture()
    data["official_test_selected_model"]["false_positive_rate"] = 0.98
    with pytest.raises(InvalidEvaluation, match="FPR"):
        validate_report(data)


def test_tie_always_selects_logistic_regression():
    data = _local_fixture()
    data["validation"]["logistic_regression"] = data["validation"]["random_forest"]
    data["selected_model"] = "logistic_regression"
    data["selection_protocol"]["test_models_evaluated"] = ["logistic_regression"]
    assert validate_report(data)["selected"] == "logistic_regression"
