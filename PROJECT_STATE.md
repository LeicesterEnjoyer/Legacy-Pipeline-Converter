# Project State

## Current Phase

Validation.

---

## Completed

### Project setup
- Created repository structure.
- Added `README.md`, `SPEC.md`, `AGENTS.md`, and `AGENT_FAILURES.md`.
- Added `clarifications-v1.md`.
- Configured `pyproject.toml`.
- Added `.gitignore`.
- Set up a local virtual environment.

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

**Status:** All test cases are passing (`20 passed in 0.05s`).

---

## In Progress

---

## Next Phase

Validation.

Planned validation rules:

- unique step IDs;
- valid dependencies;
- supported join types;
- at least one output step;
- multiple output steps allowed.

---

## Not Implemented

- Dependency graph.
- Topological ordering.
- SQL generation.
- Conversion report generation.
- File output.
- End-to-end conversion.
- Execution and result validation.

---

## Current Status

Parser phase is complete and all parser tests are passing.
The next milestone is implementing validation rules.