# Project State

## Current Phase

Phase 3 – Dependency Ordering.

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

---

## In Progress

---

## Next Phase

Phase 4 – SQL Generation.

Planned scope:
- Build the dependency graph.
- Produce deterministic topological ordering.
- Detect cyclic dependencies.

---

## Not Implemented

- Dependency graph.
- Topological ordering.
- Cycle detection.
- SQL generation.
- Conversion report generation.
- File output.
- End-to-end conversion.
- Execution and result validation.

---

## Current Status

Phases 1 and 2 are complete:

- Parsing and domain models ✅
- Validation ✅
- Validation v2 improvements ✅

The next milestone is implementing deterministic dependency ordering and cycle detection.