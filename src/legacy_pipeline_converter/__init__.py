"""Legacy ETL pipeline to dbt-style SQL converter."""

from legacy_pipeline_converter.parser import parse_pipeline

__all__ = ["parse_pipeline"]
