from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class PipelineAdapter(Protocol):
    def normalize(self, source: object) -> dict[str, Any]:
        """Normalize an external source into the supported pipeline dictionary."""
        ...
