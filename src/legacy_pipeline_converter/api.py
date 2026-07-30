from collections.abc import Sequence
from typing import Any

from .adapters import JsonPipelineAdapter, PipelineAdapter
from .dbt_artifacts import generate_dbt_artifacts
from .diagnostics import collect_pipeline_warnings
from .errors import ConversionError
from .execution import execute_models
from .models import (
    ConversionResult,
    DbtGenerationConfig,
    ExecutionRequest,
    SourceMapping,
    ValidationSummary,
)
from .ordering import order_steps
from .parser import parse_pipeline
from .report import build_report
from .result_validation import compare_results
from .source_mapping import resolve_source_mappings
from .sql_generator import generate_models
from .validator import validate_pipeline


def convert_pipeline(
    source: object,
    *,
    adapter: PipelineAdapter | None = None,
    mappings: Sequence[SourceMapping] = (),
    dbt_config: DbtGenerationConfig | None = None,
    execution_request: ExecutionRequest | None = None,
) -> ConversionResult:
    data: dict[str, Any] = {}

    try:
        selected_adapter = (
            adapter
            if adapter is not None
            else JsonPipelineAdapter()
        )
        data = selected_adapter.normalize(source)
        parsed_pipeline = parse_pipeline(data)
        validated_pipeline = validate_pipeline(parsed_pipeline)
        pipeline_warnings = collect_pipeline_warnings(validated_pipeline)
        source_resolution = resolve_source_mappings(
            validated_pipeline,
            mappings,
        )
        ordered_pipeline = order_steps(validated_pipeline)
        models = generate_models(ordered_pipeline, source_resolution)
        artifacts = generate_dbt_artifacts(
            validated_pipeline,
            models,
            source_resolution,
            dbt_config,
        )
        warnings = pipeline_warnings + source_resolution.warnings
        validation: ValidationSummary | None = None

        if execution_request is not None:
            executed_pipeline = execute_models(
                ordered_pipeline,
                models,
                source_resolution,
                execution_request,
            )

            if execution_request.expected_file is None:
                validation = ValidationSummary(
                    executed=True,
                    passed=None,
                    output_step_id=executed_pipeline.output_step_id,
                    actual_row_count=executed_pipeline.row_count,
                )
            else:
                validation = compare_results(
                    executed_pipeline,
                    execution_request.expected_file,
                )

        report = build_report(
            pipeline_name=validated_pipeline.name,
            status="success",
            models_generated=tuple(model.filename for model in models),
            errors=(),
            warnings=warnings,
            validation=validation,
        )

        return ConversionResult(
            ordered_pipeline=ordered_pipeline,
            models=models,
            artifacts=artifacts,
            report=report,
        )

    except ConversionError as error:
        report = build_report(
            pipeline_name=data.get("name", ""),
            status="failed",
            models_generated=(),
            errors=(str(error),),
            warnings=(),
        )

        return ConversionResult(
            ordered_pipeline=None,
            models=(),
            artifacts=(),
            report=report,
        )
