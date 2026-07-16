from typing import Any

from .errors import ConversionError
from .models import (
    ConversionReport,
    GeneratedModel,
    OrderedPipeline,
)
from .ordering import order_steps
from .parser import parse_pipeline
from .report import build_report
from .sql_generator import generate_models
from .validator import validate_pipeline


def convert_pipeline(data: dict[str, Any]) -> tuple[OrderedPipeline | None, tuple[GeneratedModel, ...], ConversionReport]:
    try:
        parsed_pipeline = parse_pipeline(data)
        validated_pipeline = validate_pipeline(parsed_pipeline)
        ordered_pipeline = order_steps(validated_pipeline)
        models = generate_models(ordered_pipeline)

        report = build_report(
            pipeline_name=validated_pipeline.name,
            status="success",
            models_generated=[
                model.filename
                for model in models
            ],
            errors=[],
            warnings=[],
        )

        return ordered_pipeline, models, report

    except ConversionError as error:
        report = build_report(
            pipeline_name=data.get("name", ""),
            status="failed",
            models_generated=[],
            errors=[str(error)],
            warnings=[],
        )

        return None, (), report