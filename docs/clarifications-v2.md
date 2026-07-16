# Clarifications – Version 2

## Purpose

This document records decisions that supersede or extend the v1 behavior.

## How to use this document

- This file supplements `docs/clarifications-v1.md`.
- Decisions in this file take precedence over conflicting decisions from previous versions.
- New decisions should be appended rather than rewriting previous ones.
- Superseded behavior should remain documented for historical context.

---

## C17. Calculated column dependency validation

### Question

Should `CalculatedColumnStep.input` references be validated?

### Previous behavior (v1)

`CalculatedColumnStep.input` dependencies were not validated.

A pipeline such as:

```json
{
  "name": "invalid_pipeline",
  "steps": [
    {
      "id": "calc",
      "type": "calculated_column",
      "input": "missing_step",
      "column": "revenue",
      "expression": "price * quantity"
    }
  ]
}
```

If the referenced step does not exist, validation must raise:

- `MissingReferenceError`
- `field="input"`
- `step_id=<calculated_column_step_id>`


### Required test coverage

Add:

- `test_validate_calculated_column_missing_input_reference_raises_clear_error`

### Scope

This change affects:

- `src/legacy_pipeline_converter/validator.py`
- `tests/test_validator.py`

---

## C18. Conversion report collection immutability

### Question

Should collection fields in `ConversionReport` use mutable lists or immutable tuples?

### Previous behaviour

The v1 architecture defined:

- `models_generated: list[str]`
- `errors: list[str]`
- `warnings: list[str]`

while the dataclass itself was frozen.

### Decision

Starting with v2, these fields use immutable tuples:

- `models_generated: tuple[str, ...]`
- `errors: tuple[str, ...]`
- `warnings: tuple[str, ...]`

### Rationale

A frozen dataclass containing mutable lists is only shallowly immutable. Using tuples makes the model fully immutable and consistent with the rest of the domain model.

---

## C19. Conversion report immutability and warning support

### Question

How should `ConversionReport` store collection fields, and should warnings be supported?

### Previous behaviour

The v1 architecture defined:

- `models_generated: list[str]`
- `errors: list[str]`
- `warnings: list[str]`

while the dataclass itself was frozen.

Additionally, `warnings` existed in the report schema but no warning-producing behaviour was defined.

### Decision

Starting with v2:

- `models_generated` uses `tuple[str, ...]`;
- `errors` uses `tuple[str, ...]`;
- `warnings` uses `tuple[str, ...]`.

The conversion pipeline should also support real warning generation and propagation instead of always producing an empty collection.

### Previous behavior (v1)

In v1:

```python
warnings=()
```

The warnings parameter of build_report() is intentionally ignored because no warning conditions are defined.

### Rationale

Using tuples makes ConversionReport fully immutable and consistent with the rest of the domain model.

Keeping warnings empty in v1 avoids introducing behaviour that is not specified, while preserving the report schema for future expansion.

### Future work (v2)

A future version should:

- define warning-producing conditions;
- propagate warnings through `build_report`;
- populate `ConversionReport.warnings` instead of always returning an empty tuple;
- add dedicated warning test coverage.

### Scope

This affects:

- `src/legacy_pipeline_converter/models.py`
- `src/legacy_pipeline_converter/report.py`
- future report generation and validation logic.