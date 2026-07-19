import pytest

from legacy_pipeline_converter.errors import ConflictingSourceMappingError
from legacy_pipeline_converter.models import (
    FilterStep,
    OutputStep,
    Pipeline,
    ResolvedSource,
    SourceMapping,
    SourceStep,
)
from legacy_pipeline_converter.source_mapping import resolve_source_mappings


@pytest.fixture
def pipeline() -> Pipeline:
    return Pipeline(
        name="source_mapping_pipeline",
        steps=(
            SourceStep(
                id="orders_source",
                path="data/orders.csv",
            ),
            FilterStep(
                id="valid_orders",
                input="orders_source",
                condition="status != 'cancelled'",
            ),
            OutputStep(
                id="final_output",
                input="valid_orders",
                table="fct_orders",
            ),
        ),
    )


def test_resolve_source_mapping_uses_explicit_relation(pipeline: Pipeline) -> None:
    mapping = SourceMapping(
        source_id="orders_source",
        relation="raw.orders",
    )

    resolution = resolve_source_mappings(pipeline, [mapping])

    assert resolution.sources == (
        ResolvedSource(
            source_id="orders_source",
            relation_name="raw.orders",
            used_fallback=False,
        ),
    )
    assert resolution.warnings == ()


@pytest.mark.parametrize(
    ("mapping", "expected"),
    [
        (
            SourceMapping(
                source_id="orders_source",
                relation="orders",
                database="analytics",
                schema="raw",
            ),
            "analytics.raw.orders",
        ),
        (
            SourceMapping(
                source_id="orders_source",
                relation="orders",
                schema="raw",
            ),
            "raw.orders",
        ),
    ],
)
def test_resolve_source_mapping_builds_qualified_relation(
    pipeline: Pipeline,
    mapping: SourceMapping,
    expected: str,
) -> None:
    resolution = resolve_source_mappings(pipeline, [mapping])

    assert resolution.sources == (
        ResolvedSource(
            source_id="orders_source",
            relation_name=expected,
            used_fallback=False,
        ),
    )
    assert resolution.warnings == ()


def test_missing_source_mapping_uses_filename_fallback_and_warning(pipeline: Pipeline) -> None:
    resolution = resolve_source_mappings(pipeline, [])

    assert resolution.sources == (
        ResolvedSource(
            source_id="orders_source",
            relation_name="orders",
            used_fallback=True,
        ),
    )

    assert len(resolution.warnings) == 1

    warning = resolution.warnings[0]

    assert warning.code == "missing_source_mapping"
    assert warning.message == (
        "Source 'orders_source' has no explicit mapping; "
        "using fallback relation 'orders'."
    )
    assert warning.step_id == "orders_source"
    assert warning.field == "path"


def test_identical_duplicate_mappings_are_deduplicated(pipeline: Pipeline) -> None:
    mapping = SourceMapping(
        source_id="orders_source",
        relation="orders",
        database="analytics",
        schema="raw",
    )

    resolution = resolve_source_mappings(
        pipeline,
        [mapping, mapping],
    )

    assert resolution.sources == (
        ResolvedSource(
            source_id="orders_source",
            relation_name="analytics.raw.orders",
            used_fallback=False,
        ),
    )
    assert resolution.warnings == ()


def test_conflicting_source_mappings_raise_clear_error(pipeline: Pipeline) -> None:
    mappings = [
        SourceMapping(
            source_id="orders_source",
            relation="orders",
            schema="raw",
        ),
        SourceMapping(
            source_id="orders_source",
            relation="orders",
            schema="staging",
        ),
    ]

    with pytest.raises(ConflictingSourceMappingError) as excinfo:
        resolve_source_mappings(pipeline, mappings)

    error_message = str(excinfo.value)

    assert "orders_source" in error_message
    assert "raw" in error_message
    assert "staging" in error_message


def test_source_resolution_follows_pipeline_declaration_order() -> None:
    pipeline = Pipeline(
        name="ordered_sources",
        steps=(
            SourceStep(
                id="first_source",
                path="first.csv",
            ),
            SourceStep(
                id="second_source",
                path="second.csv",
            ),
            OutputStep(
                id="final_output",
                input="second_source",
                table="fct_output",
            ),
        ),
    )

    resolution = resolve_source_mappings(pipeline, [])

    assert resolution.sources == (
        ResolvedSource(
            source_id="first_source",
            relation_name="first",
            used_fallback=True,
        ),
        ResolvedSource(
            source_id="second_source",
            relation_name="second",
            used_fallback=True,
        ),
    )

    assert [warning.step_id for warning in resolution.warnings] == [
        "first_source",
        "second_source",
    ]