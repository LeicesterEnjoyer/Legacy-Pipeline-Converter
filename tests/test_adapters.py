from typing import Any

import pytest

from legacy_pipeline_converter.adapters import (
    JsonPipelineAdapter,
    PipelineAdapter,
)
from legacy_pipeline_converter.errors import ParseError


def test_json_adapter_normalizes_current_dictionary_format() -> None:
    source = {
        "name": "orders_pipeline",
        "steps": [
            {
                "id": "orders_source",
                "type": "source",
                "path": "orders.csv",
            }
        ],
    }

    normalized = JsonPipelineAdapter().normalize(source)

    assert normalized == source


def test_adapter_protocol_requires_normalize_method() -> None:
    class ValidAdapter:
        def normalize(self, source: object) -> dict[str, Any]:
            return {"name": "normalized", "steps": []}

    class InvalidAdapter:
        pass

    assert isinstance(ValidAdapter(), PipelineAdapter)
    assert not isinstance(InvalidAdapter(), PipelineAdapter)


def test_json_adapter_rejects_unsupported_source_type() -> None:
    with pytest.raises(ParseError) as exc_info:
        JsonPipelineAdapter().normalize("pipeline.json")

    error = exc_info.value
    assert error.step_id is None
    assert error.field == "source"
    assert "dictionary" in error.message
