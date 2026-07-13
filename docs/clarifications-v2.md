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