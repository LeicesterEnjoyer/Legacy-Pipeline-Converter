import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def example_pipeline_data() -> dict:
    with (FIXTURES_DIR / "legacy_pipeline.json").open(encoding="utf-8") as handle:
        return json.load(handle)
