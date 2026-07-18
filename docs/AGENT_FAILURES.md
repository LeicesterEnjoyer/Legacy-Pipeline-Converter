# AGENT_FAILURES

## F-001: Optional error field contradicted the error contract

### Related specification

- [C10. Error message contract](clarifications-v1.md#c10-error-message-contract)
- [C15. Pipeline-level validation errors](clarifications-v1.md#c15-pipeline-level-validation-errors)

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

- [Phase 2 – Validation](dimplementation-plan-v1.md#phase-2-validation)
- [C6. Supported join types](clarifications-v1.md#c6-supported-join-types)

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

## F-003: OrderedPipeline was implemented in the wrong module

### Related specification

- [Phase 3 – Dependency ordering](implementation-plan-v1.md#phase-3-dependency-ordering)
- [Supporting models](implementation-plan-v1.md#supporting-models)

### Context

The AI implemented `OrderedPipeline` directly inside `ordering.py` as a regular class instead of defining it in `models.py` as a domain model.

### Why it was a problem

The approved architecture explicitly defines `OrderedPipeline` as a supporting domain model:

```python
OrderedPipeline:
    pipeline: Pipeline
    execution_order: tuple[str, ...]
```

Placing the model inside ordering.py violated the module responsibilities established by the architecture:

models.py should contain domain models and supporting dataclasses.
ordering.py should contain dependency ordering logic only.

### Resolution

OrderedPipeline was moved to models.py and implemented as a frozen dataclass.

ordering.py now imports and returns the shared domain model instead of defining its own local class.

### Lesson learned

AI-generated code may satisfy functional requirements while still violating architectural boundaries.

## F-004: Diagnostics test module was omitted

### Related specification

- [Phase 1 – Structured warnings and diagnostics](implementation-plan-v2.md#phase-1-structured-warnings-and-diagnostics)
- [Diagnostics test plan](implementation-plan-v2.md#tests)

### Context

The AI implemented `collect_pipeline_warnings()` in `diagnostics.py` but did not create the required `tests/test_diagnostics.py` module.

Instead, it skipped the dedicated diagnostics test suite entirely and placed only a partial orphan-warning test inside `tests/test_report.py`.

### Missing tests

The following approved tests were omitted:

- `test_collect_warnings_returns_no_orphan_warning_for_fully_used_pipeline`
- `test_collect_warnings_emits_orphan_warning`
- `test_orphan_warnings_follow_declaration_order`

### Why it was a problem

The implementation introduced new diagnostics functionality without adding the dedicated test coverage required by the approved Phase 1 implementation plan.

As a result, several required behaviors remained unverified:

- fully used pipelines produce no orphan warnings;
- orphan steps generate structured `WarningInfo` objects;
- orphan warnings are emitted in deterministic declaration order.

Additionally, placing a diagnostics test inside `test_report.py` violated the intended separation of responsibilities:

- `test_report.py` should verify report construction and warning serialization;
- `test_diagnostics.py` should verify diagnostics behavior.

The generated test suite therefore appeared to cover Phase 1 while silently omitting most of the approved diagnostics test plan.

### Resolution

Created `tests/test_diagnostics.py` and implemented the three missing tests defined in the implementation plan.

The orphan-warning test was moved from `test_report.py` to the dedicated diagnostics test module and renamed to match the approved test plan.

### Lesson learned

Do not assume that implementing production code completes a phase.
