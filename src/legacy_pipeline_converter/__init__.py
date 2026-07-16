"""Legacy ETL pipeline to dbt-style SQL converter."""

from legacy_pipeline_converter.api import convert_pipeline
from legacy_pipeline_converter.ordering import order_steps
from legacy_pipeline_converter.parser import parse_pipeline
from legacy_pipeline_converter.report import build_report
from legacy_pipeline_converter.sql_generator import generate_models
from legacy_pipeline_converter.validator import validate_pipeline

__all__ = [
    "parse_pipeline",
    "validate_pipeline",
    "order_steps",
    "generate_models",
    "build_report",
    "convert_pipeline",
]