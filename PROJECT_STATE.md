# Project State

## Current Phase

Phase 4 – SQL Generation.

---

## Completed

### Project setup
- Created repository structure.
- Added `README.md`, `SPEC.md`, `AGENTS.md`, and `AGENT_FAILURES.md`.
- Added `docs/clarifications-v1.md`.
- Added `docs/clarifications-v2.md`.
- Added `docs/implementation-plan-v1.md`.
- Configured `pyproject.toml`.
- Added `.gitignore`.
- Set up a local virtual environment.

### Architecture and planning
- Defined the approved v1 architecture in `docs/implementation-plan-v1.md`.
- Defined module responsibilities and public APIs.
- Defined the phased implementation plan and ordered test plan.
- Documented the TDD workflow and agent handoff process.

### Domain model
- Implemented immutable domain models:
  - `SourceStep`
  - `FilterStep`
  - `CalculatedColumnStep`
  - `JoinStep`
  - `OutputStep`
  - `Pipeline`
  - `OrderedPipeline`

### Error handling
- Implemented `ConversionError`.
- Implemented `ParseError`.
- Implemented `UnsupportedStepTypeError`.
- Implemented validation-specific errors:
  - `ValidationError`
  - `DuplicateStepIdError`
  - `MissingReferenceError`
  - `InvalidJoinTypeError`
  - `NoOutputStepError`
- Implemented ordering-specific errors:
  - `CyclicDependencyError`

### Parser
- Implemented JSON-to-domain-model parsing.
- Supports all v1 transformation types.
- Ignores unknown fields.
- Keeps parsing and validation responsibilities separate.
- Provides clear parse errors, including invalid step indexes.

### Parser test coverage
- Valid example pipeline.
- All supported transformation types.
- Unsupported step types.
- Missing required fields.
- Missing pipeline name.
- Missing `steps`.
- Non-list `steps`.
- Non-object step entries.
- Missing step `id`.
- Missing step `type`.
- Ignored extra fields.
- Empty pipeline parsing.

**Status:** All parser test cases are passing (`20 passed`).

### Validation
- Implemented pipeline validation for:
  - unique step IDs;
  - valid dependencies for filter, calculated-column, and output steps;
  - valid left and right dependencies for join steps;
  - supported join types;
  - at least one output step;
  - multiple output steps allowed;
  - orphan steps allowed.

### Validation test coverage
- Duplicate step IDs.
- Missing input dependencies.
- Missing calculated-column dependencies.
- Missing join references.
- Invalid join types.
- All supported join types.
- Zero output steps.
- Multiple output steps.
- Orphan steps.
- Canonical example pipeline.

**Status:** All validation test cases are passing (`14 passed`).

### Dependency ordering
- Implemented dependency graph construction.
- Implemented deterministic topological ordering using Kahn's algorithm.
- Preserves JSON declaration order when multiple steps are ready.
- Supports dependencies for:
  - filter steps;
  - calculated-column steps;
  - join steps;
  - output steps.
- Implemented cyclic dependency detection.
- Returns an immutable `OrderedPipeline`.

### Dependency ordering test coverage
- Canonical example pipeline dependency order.
- Declaration-order tie-breaking for independent steps.
- Cyclic dependency errors.
- Deterministic ordering across repeated calls.

**Status:** All dependency ordering test cases are passing (`4 passed`).

---

## In Progress

Phase 4 – SQL Generation.

Planned scope:
- Add the `GeneratedModel` domain model.
- Generate no SQL model for source steps.
- Generate SQL for filter steps.
- Generate SQL for calculated-column steps.
- Generate SQL for join steps.
- Generate SQL for output steps.
- Use `{{ ref('step_id') }}` for transformed upstream models.
- Use source relation names derived from source paths.
- Generate filenames using `<step_id>.sql`.
- Exclude dbt `config()` blocks.
- Preserve deterministic SQL formatting and model ordering.

---

## Next Phase

Phase 5 – Conversion Report.

Planned scope:
- Add the `ConversionReport` domain model.
- Generate successful conversion reports.
- Populate generated model filenames in dependency order.
- Generate failed conversion reports with formatted errors.
- Keep warnings empty in v1.

---

## Not Implemented

- SQL generation.
- Generated SQL model representation.
- Conversion report generation.
- File output.
- End-to-end conversion.
- Execution and result validation.

---

## Current Status

Phases 1 through 3 are complete:

- Parsing and domain models ✅
- Validation ✅
- Validation v2 improvements ✅
- Dependency ordering and cycle detection ✅

The next milestone is generating deterministic dbt-style SQL models from the ordered pipeline.