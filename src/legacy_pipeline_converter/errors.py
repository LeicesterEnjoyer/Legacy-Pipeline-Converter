from dataclasses import dataclass


@dataclass
class ConversionError(Exception):
    step_id: str | None
    field: str
    message: str

    def __str__(self) -> str:
        if self.step_id is None:
            return f"{self.message} (field: {self.field})"
        return f"{self.message} (step: {self.step_id!r}, field: {self.field})"


class ParseError(ConversionError):
    """Raised when pipeline JSON cannot be parsed into domain models."""


class UnsupportedStepTypeError(ParseError):
    """Raised when a step has an unknown type value."""
