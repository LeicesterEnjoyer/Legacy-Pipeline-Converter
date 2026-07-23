"""Legacy ETL pipeline to dbt-style SQL converter."""

from legacy_pipeline_converter.api import convert_pipeline
from legacy_pipeline_converter.dbt_artifacts import generate_dbt_artifacts
from legacy_pipeline_converter.diagnostics import collect_pipeline_warnings
from legacy_pipeline_converter.ordering import order_steps
from legacy_pipeline_converter.parser import parse_pipeline
from legacy_pipeline_converter.report import build_report
from legacy_pipeline_converter.source_mapping import resolve_source_mappings
from legacy_pipeline_converter.sql_generator import generate_models
from legacy_pipeline_converter.validator import validate_pipeline

__all__ = [
    "parse_pipeline",
    "validate_pipeline",
    "order_steps",
    "generate_models",
    "generate_dbt_artifacts",
    "build_report",
    "collect_pipeline_warnings",
    "resolve_source_mappings",
    "convert_pipeline",
]
