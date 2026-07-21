import yaml

from legacy_pipeline_converter.dbt_artifacts import generate_dbt_artifacts
from legacy_pipeline_converter.models import (
    DbtGenerationConfig,
    GeneratedModel,
    Pipeline,
    ResolvedSource,
    SourceResolution,
    SourceStep,
)


def _pipeline() -> Pipeline:
    return Pipeline(
        name="orders_pipeline",
        steps=(
            SourceStep(id="orders_source", path="orders.csv"),
            SourceStep(id="customers_source", path="customers.csv"),
            SourceStep(id="products_source", path="products.csv"),
        ),
    )


def _models() -> tuple[GeneratedModel, ...]:
    return (
        GeneratedModel(
            step_id="valid_orders",
            filename="valid_orders.sql",
            sql="SELECT *\nFROM analytics.raw.orders\n",
        ),
        GeneratedModel(
            step_id="final_output",
            filename="final_output.sql",
            sql="SELECT *\nFROM {{ ref('valid_orders') }}\n",
        ),
    )


def _source_resolution() -> SourceResolution:
    return SourceResolution(
        sources=(
            ResolvedSource(
                source_id="orders_source",
                relation_name="analytics.raw.orders",
                used_fallback=False,
            ),
            ResolvedSource(
                source_id="customers_source",
                relation_name="analytics.raw.customers",
                used_fallback=False,
            ),
            ResolvedSource(
                source_id="products_source",
                relation_name="products",
                used_fallback=True,
            ),
        ),
        warnings=(),
    )


def test_generate_sources_yml_contains_resolved_sources() -> None:
    artifacts = generate_dbt_artifacts(
        _pipeline(),
        _models(),
        _source_resolution(),
    )
    sources_artifact = next(
        artifact for artifact in artifacts if artifact.filename == "sources.yml"
    )

    assert sources_artifact.artifact_type == "sources_yml"
    assert yaml.safe_load(sources_artifact.content) == {
        "version": 2,
        "sources": [
            {
                "name": "analytics_raw",
                "database": "analytics",
                "schema": "raw",
                "tables": [
                    {"name": "orders"},
                    {"name": "customers"},
                ],
            },
            {
                "name": "legacy_sources",
                "tables": [
                    {"name": "products"},
                ],
            },
        ],
    }


def test_generate_sources_yml_is_deterministic() -> None:
    first = generate_dbt_artifacts(
        _pipeline(),
        _models(),
        _source_resolution(),
    )
    second = generate_dbt_artifacts(
        _pipeline(),
        _models(),
        _source_resolution(),
    )

    first_sources = next(
        artifact for artifact in first if artifact.filename == "sources.yml"
    )
    second_sources = next(
        artifact for artifact in second if artifact.filename == "sources.yml"
    )

    assert first_sources.content == second_sources.content


def test_generate_schema_yml_contains_generated_models_in_order() -> None:
    artifacts = generate_dbt_artifacts(
        _pipeline(),
        _models(),
        _source_resolution(),
    )
    schema_artifact = next(
        artifact for artifact in artifacts if artifact.filename == "schema.yml"
    )

    assert schema_artifact.artifact_type == "schema_yml"
    schema_data = yaml.safe_load(schema_artifact.content)
    assert [model["name"] for model in schema_data["models"]] == ["valid_orders", "final_output"]


def test_generate_schema_yml_uses_default_materialization() -> None:
    artifacts = generate_dbt_artifacts(
        _pipeline(),
        _models(),
        _source_resolution(),
        DbtGenerationConfig(default_materialization="table"),
    )
    schema_artifact = next(
        artifact for artifact in artifacts if artifact.filename == "schema.yml"
    )

    schema_data = yaml.safe_load(schema_artifact.content)

    assert [model["config"]["materialized"] for model in schema_data["models"]] == ["table", "table"]
