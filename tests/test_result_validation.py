from pathlib import Path

import pytest

from legacy_pipeline_converter.errors import ResultValidationError
from legacy_pipeline_converter.models import (
    DifferenceDetail,
    ExecutedPipeline,
    ValidationSummary,
)
from legacy_pipeline_converter.result_validation import compare_results


def _executed_pipeline(
    *,
    columns: tuple[str, ...] = ("id", "name"),
    rows: tuple[tuple[object, ...], ...] = (
        (1, "alpha"),
        (2, "beta"),
    ),
) -> ExecutedPipeline:
    return ExecutedPipeline(
        output_step_id="final_output",
        output_relation="final_output",
        columns=columns,
        rows=rows,
        row_count=len(rows),
    )


def test_compare_results_passes_for_equal_multisets(
    tmp_path: Path,
) -> None:
    expected_path = tmp_path / "expected.csv"
    expected_path.write_text(
        "id,name\n"
        "2,beta\n"
        "1,alpha\n",
        encoding="utf-8",
    )

    summary = compare_results(
        _executed_pipeline(),
        str(expected_path),
    )

    assert summary == ValidationSummary(
        executed=True,
        passed=True,
        output_step_id="final_output",
        actual_row_count=2,
        expected_row_count=2,
        differences=(),
    )


def test_compare_results_detects_column_mismatch(
    tmp_path: Path,
) -> None:
    expected_path = tmp_path / "expected.csv"
    expected_path.write_text(
        "name,id\n"
        "alpha,1\n"
        "beta,2\n",
        encoding="utf-8",
    )

    summary = compare_results(
        _executed_pipeline(),
        str(expected_path),
    )

    assert summary.passed is False
    assert summary.differences == (
        DifferenceDetail(
            kind="column_names",
            message=(
                "Expected columns ('name', 'id') but received "
                "('id', 'name')."
            ),
        ),
    )


def test_compare_results_detects_row_count_mismatch(
    tmp_path: Path,
) -> None:
    expected_path = tmp_path / "expected.csv"
    expected_path.write_text(
        "id,name\n"
        "1,alpha\n",
        encoding="utf-8",
    )

    summary = compare_results(
        _executed_pipeline(),
        str(expected_path),
    )

    assert summary.passed is False
    assert summary.actual_row_count == 2
    assert summary.expected_row_count == 1
    assert summary.differences == (
        DifferenceDetail(
            kind="row_count",
            message="Expected 1 row but received 2.",
        ),
    )


def test_compare_results_detects_value_mismatch(
    tmp_path: Path,
) -> None:
    expected_path = tmp_path / "expected.csv"
    expected_path.write_text(
        "id,name\n"
        "1,alpha\n"
        "2,gamma\n",
        encoding="utf-8",
    )

    summary = compare_results(
        _executed_pipeline(),
        str(expected_path),
    )

    assert summary.passed is False
    assert summary.differences == (
        DifferenceDetail(
            kind="row_values",
            message="Actual and expected row values differ.",
        ),
    )


def test_compare_results_preserves_duplicate_rows(
    tmp_path: Path,
) -> None:
    expected_path = tmp_path / "expected.csv"
    expected_path.write_text(
        "id,name\n"
        "1,alpha\n"
        "2,beta\n"
        "2,beta\n",
        encoding="utf-8",
    )
    executed = _executed_pipeline(
        rows=(
            (1, "alpha"),
            (1, "alpha"),
            (2, "beta"),
        ),
    )

    summary = compare_results(executed, str(expected_path))

    assert summary.passed is False
    assert summary.actual_row_count == summary.expected_row_count == 3
    assert summary.differences == (
        DifferenceDetail(
            kind="row_values",
            message="Actual and expected row values differ.",
        ),
    )


def test_unreadable_expected_file_raises_clear_error(
    tmp_path: Path,
) -> None:
    expected_path = tmp_path / "missing.csv"

    with pytest.raises(ResultValidationError) as exc_info:
        compare_results(
            _executed_pipeline(),
            str(expected_path),
        )

    error = exc_info.value
    assert error.step_id == "final_output"
    assert error.field == "expected_file"
    assert str(expected_path) in error.message
