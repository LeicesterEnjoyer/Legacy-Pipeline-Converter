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
