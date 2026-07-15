from .models import ConversionReport


def build_report(
    *,
    pipeline_name: str,
    status: str,
    models_generated: list[str],
    errors: list[str],
    warnings: list[str],
) -> ConversionReport:
    return ConversionReport(
        pipeline_name=pipeline_name,
        status=status,
        models_generated=tuple(models_generated),
        errors=tuple(errors),
        warnings=(),
    )
