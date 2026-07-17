# Project State

## Current Phase

Version 2.0 – Phase 1: Structured Warnings and Diagnostics.

---

## Completed

### Project setup

- Created repository structure.
- Added `README.md`.
- Added project documentation under `docs/`.
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
  - `ConversionReport`

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

### Conversion report

- Implemented immutable `ConversionReport`.
- Uses immutable tuples for:
  - generated model filenames;
  - errors;
  - warnings.
- Implemented report generation for successful conversions.
- Implemented report generation for failed conversions.
- Populates generated model filenames in dependency order.
- Stores formatted conversion errors.
- Keeps warnings empty in v1.
- Produces a JSON-serializable report structure.

### Conversion report test coverage

- Successful report schema.
- Successful report model population.
- Failed report error population.
- Empty warnings in v1.

**Status:** All conversion report test cases are passing (`4 passed`).

### End-to-end conversion

- Implemented `convert_pipeline` orchestration.
- Composes:
  - parsing;
  - validation;
  - dependency ordering;
  - SQL generation;
  - conversion reporting.
- Returns generated models and a success report for valid pipelines.
- Returns a failed report for expected conversion errors.
- Implemented JSON pipeline file reading.
- Implemented generated SQL file writing.
- Implemented conversion report JSON writing.
- Exposed the approved public API from the package root.

### End-to-end and file I/O test coverage

- Successful conversion of the canonical example pipeline.
- Failed conversion report for invalid input.
- Reading the canonical JSON pipeline from disk.
- Writing generated SQL models and the conversion report.
- Complete file-based conversion round trip.

**Status:** All Phase 6 test cases are passing (`5 passed`).

---

## In Progress

Version 2.0 – Phase 1 – Structured Warnings and Diagnostics

Planned scope:

- Add the `WarningInfo` model.
- Implement deterministic orphan-step diagnostics.
- Implement structured warning propagation.
- Update `ConversionReport` to store structured warnings.
- Add warning JSON serialization.
- Add Phase 1 test coverage.

---

## Next Phase

Version 2.0 – Phase 2: Source Mapping.

Planned scope:

- Add `SourceMapping`.
- Add `ResolvedSource`.
- Implement source-to-relation resolution.
- Implement fallback relation warnings.
- Detect conflicting mappings.
- Integrate source mappings with SQL generation.

---

## Not Implemented

The following Version 2 features are not yet implemented:

### Remaining Version 2.0 phases

- Structured warning generation and propagation.
- Source-to-warehouse relation mappings.
- Improved SQL generation with aliases and qualified joins.
- dbt artifact generation (`sources.yml`, `schema.yml`).
- Adapter extension support.

### Planned Version 2.1 phases

- Executing generated SQL.
- DuckDB-based result validation.
- Comparing generated and expected datasets.

### Future versions

- Parsing real Informatica, SSIS, Talend, or IICS formats.
- Supporting additional transformation types.
- Providing a CLI.
- Building an IDE extension.
- Integrating directly with an LLM API.

---

## Current Status

All six planned implementation phases are complete:

- Parsing and domain models ✅
- Validation ✅
- Dependency ordering and cycle detection ✅
- SQL generation ✅
- Conversion report generation ✅
- End-to-end conversion and file output ✅

Version 1 of the Legacy ETL to ELT Modernisation Prototype is complete.