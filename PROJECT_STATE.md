# Project State

## Current Phase

Phase 5 – Conversion Report.

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
  - `GeneratedModel`

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

### SQL generation

- Implemented deterministic SQL model generation.
- Generates one `GeneratedModel` for every non-source step.
- Skips SQL generation for source steps.
- Generates SQL for:
  - filter steps;
  - calculated-column steps;
  - join steps;
  - output steps.
- Uses `{{ ref('step_id') }}` for transformed upstream steps.
- Uses relation names derived from source file paths.
- Generates filenames using `<step_id>.sql`.
- Generates models in dependency order.
- Excludes dbt `config()` blocks.
- Returns generated models as an immutable tuple.

### SQL generation test coverage

- Source steps generate no SQL model.
- Filter-step SQL.
- Calculated-column SQL.
- Join-step SQL.
- All supported join types.
- Output-step SQL.
- dbt `ref()` references for transformed upstream steps.
- Existing relation names for source upstream steps.
- Nested source path and extension removal.
- Deterministic model filenames.
- Absence of dbt `config()` blocks.
- Canonical example pipeline models.
- Deterministic SQL generation.

**Status:** All SQL generation test cases are passing (`15 passed`).

---

## In Progress

Phase 5 – Conversion Report.

Planned scope:

- Add the `ConversionReport` domain model.
- Generate successful conversion reports.
- Populate generated model filenames in dependency order.
- Generate failed conversion reports with formatted errors.
- Keep warnings empty in v1.
- Produce a JSON-serializable report structure.

---

## Next Phase

Phase 6 – End-to-End Conversion.

Planned scope:

- Implement pipeline JSON file reading.
- Implement the orchestration API.
- Compose parsing, validation, ordering, SQL generation, and reporting.
- Write generated SQL models to disk.
- Write the conversion report to disk.
- Add end-to-end conversion tests.

---

## Not Implemented

- Conversion report generation.
- File input and output.
- End-to-end orchestration.
- End-to-end conversion tests.
- Execution and result validation.

---

## Current Status

Phases 1 through 4 are complete:

- Parsing and domain models ✅
- Validation ✅
- Validation v2 improvements ✅
- Dependency ordering and cycle detection ✅
- SQL generation ✅

The next milestone is generating JSON-serializable success and failure reports.