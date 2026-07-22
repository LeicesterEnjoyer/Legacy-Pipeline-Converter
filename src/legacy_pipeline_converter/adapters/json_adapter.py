from typing import Any, cast

from ..errors import ParseError


class JsonPipelineAdapter:
    def normalize(self, source: object) -> dict[str, Any]:
        if not isinstance(source, dict):
            raise ParseError(
                step_id=None,
                field="source",
                message="JSON pipeline source must be a dictionary.",
            )

        return cast(dict[str, Any], source)
