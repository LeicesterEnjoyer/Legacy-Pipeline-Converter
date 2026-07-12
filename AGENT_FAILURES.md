# AGENT_FAILURES

## F-001: Optional error field contradicted the error contract

### Related specification

- [C10. Error message contract](docs/clarifications-v1.md#c10-error-message-contract)
- [C15. Pipeline-level validation errors](docs/clarifications-v1.md#c15-pipeline-level-validation-errors)

### Context

`ConversionError` was initially defined as:

```python
field: str | None
```

### Why it was a problem

The specification requires every error to include:

- the relevant field
- a human-readable message

Even pipeline-level errors still contain a field (for example `steps`). Only `step_id` may be `None`.
Allowing `field = None` weakened the type contract and permitted invalid error objects to be created.

### Resolution

Changed the contract to:

```python
field: str
```

and reserved `step_id = None` exclusively for pipeline-level errors.

### Lesson learned

When the specification guarantees the presence of a value, reflect that guarantee in the type system instead of making the field optional "just in case".

---

## F-002: Validation test generation missed approved test cases

### Related specification

- [Phase 2 – Validation](docs/implementation-plan-v1.md#phase-2--validation)
- [C6. Supported join types](docs/clarifications-v1.md#c6-supported-join-types)

### Context

The AI-generated validation test suite did not fully implement the approved Phase 2 test plan defined in `implementation-plan-v1.md`.

### Missing tests

The following tests were initially omitted:

- `test_validate_join_missing_right_reference_raises_clear_error`
- `test_validate_all_supported_join_types_pass`
- `test_validate_example_pipeline_passes`

### Why it was a problem

The generated suite appeared complete while several approved validation scenarios remained untested.

As a result, the project could have progressed with incomplete test coverage and without fully verifying the agreed Phase 2 requirements.

### Resolution

The omitted tests were identified during manual review and added manually.

### Lesson learned

Do not assume that an AI-generated test suite fully covers the approved implementation plan.