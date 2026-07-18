from collections.abc import Sequence

from .models import ConversionReport, WarningInfo


def build_report(
    *,
    pipeline_name: str,
    status: str,
    models_generated: Sequence[str],
    errors: Sequence[str],
    warnings: Sequence[WarningInfo],
) -> ConversionReport:
    return ConversionReport(
        pipeline_name=pipeline_name,
        status=status,
        models_generated=tuple(models_generated),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
