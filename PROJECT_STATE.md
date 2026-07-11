# Project State

## Current Phase

Parser implementation and test coverage expansion.

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

### Tests
- Added parser tests for:
  - valid example pipeline;
  - all supported transformation types;
  - unsupported step types;
  - missing required fields;
  - ignored extra fields;
  - missing pipeline name;
  - empty pipeline parsing.

---

## In Progress

- Expanding parser test coverage for parser edge cases:
  - missing `steps`;
  - invalid `steps` container;
  - non-object steps;
  - missing step `id`;
  - missing step `type`.

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

Parser implementation is functional and under test coverage expansion.
Validation will begin after parser coverage is completed.