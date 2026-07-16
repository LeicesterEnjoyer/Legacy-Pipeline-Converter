import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from .models import ConversionReport, GeneratedModel


def read_pipeline_json(path: str | Path) -> dict[str, Any]:
    pipeline_path = Path(path)

    with pipeline_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_sql_models(directory: str | Path, models: Iterable[GeneratedModel]) -> None:
    output_directory = Path(directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    for model in models:
        output_path = output_directory / model.filename
        output_path.write_text(model.sql, encoding="utf-8")


def write_report(path: str | Path, report: ConversionReport) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            asdict(report),
            handle,
            indent=2,
        )