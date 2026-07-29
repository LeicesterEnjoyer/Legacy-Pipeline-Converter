from collections import Counter
from pathlib import Path

import duckdb

from .errors import ResultValidationError
from .models import (
    DifferenceDetail,
    ExecutedPipeline,
    ValidationSummary,
)


def _read_expected_csv(
    expected_csv_path: str,
    output_step_id: str,
) -> tuple[tuple[str, ...], tuple[tuple[object, ...], ...]]:
    expected_path = Path(expected_csv_path)

    if not expected_path.is_file():
        raise ResultValidationError(
            step_id=output_step_id,
            field="expected_file",
            message=(
                f"Expected result file does not exist: "
                f"{expected_csv_path}"
            ),
        )

    connection: duckdb.DuckDBPyConnection | None = None

    try:
        connection = duckdb.connect(":memory:")
        relation = connection.read_csv(str(expected_path))
        columns = tuple(relation.columns)
        rows = tuple(
            tuple(row)
            for row in relation.fetchall()
        )
    except (duckdb.Error, OSError) as error:
        raise ResultValidationError(
            step_id=output_step_id,
            field="expected_file",
            message=(
                f"Could not read expected result file "
                f"{expected_csv_path!r}: {error}"
            ),
        ) from error
    finally:
        if connection is not None:
            connection.close()

    return columns, rows


def compare_results(
    executed_pipeline: ExecutedPipeline,
    expected_csv_path: str,
) -> ValidationSummary:
    expected_columns, expected_rows = _read_expected_csv(
        expected_csv_path,
        executed_pipeline.output_step_id,
    )
    expected_row_count = len(expected_rows)
    differences: list[DifferenceDetail] = []

    if executed_pipeline.columns != expected_columns:
        differences.append(
            DifferenceDetail(
                kind="column_names",
                message=(
                    f"Expected columns {expected_columns!r} but received "
                    f"{executed_pipeline.columns!r}."
                ),
            )
        )
    elif executed_pipeline.row_count != expected_row_count:
        expected_row_label = (
            "row"
            if expected_row_count == 1
            else "rows"
        )
        differences.append(
            DifferenceDetail(
                kind="row_count",
                message=(
                    f"Expected {expected_row_count} "
                    f"{expected_row_label} but received "
                    f"{executed_pipeline.row_count}."
                ),
            )
        )
    elif Counter(executed_pipeline.rows) != Counter(expected_rows):
        differences.append(
            DifferenceDetail(
                kind="row_values",
                message="Actual and expected row values differ.",
            )
        )

    return ValidationSummary(
        executed=True,
        passed=not differences,
        output_step_id=executed_pipeline.output_step_id,
        actual_row_count=executed_pipeline.row_count,
        expected_row_count=expected_row_count,
        differences=tuple(differences),
    )
