from collections.abc import Sequence
from typing import Literal

from .models import ConversionReport, ValidationSummary, WarningInfo


def build_report(
    *,
    pipeline_name: str,
    status: Literal["success", "failed"],
    models_generated: Sequence[str],
    errors: Sequence[str],
    warnings: Sequence[WarningInfo],
    validation: ValidationSummary | None = None,
) -> ConversionReport:
    return ConversionReport(
        pipeline_name=pipeline_name,
        status=status,
        models_generated=tuple(models_generated),
        errors=tuple(errors),
        warnings=tuple(warnings),
        validation=validation,
    )
