# Agent Instructions

## General workflow

- Read `SPEC.md`, `PROJECT_STATE.md`, the active implementation plan, and
  `AGENT_FAILURES.md` before making any changes.
- Use `PROJECT_STATE.md` to determine the current phase.
- Treat the active implementation plan as authoritative for phase scope and sequencing.
- Explain the proposed approach before implementing it.
- Ask for clarification when the specification is ambiguous.
- Do not implement features outside the current specification.
- Make small, focused changes rather than large rewrites.
- Do not modify unrelated files.

## Requirements for Every Phase

- Read `PROJECT_STATE.md`, `implementation-plan-v2.md`, and `AGENT_FAILURES.md` before implementing the current phase.
- Treat `implementation-plan-v2.md` as the authoritative specification.
- Work strictly within the current implementation phase.
- Follow the approved TDD workflow:
  1. Write the planned tests.
  2. Verify they fail for the expected reason.
  3. Implement the minimum production code required.
  4. Keep all existing tests passing.
- Do not implement functionality from future phases.
- Do not modify public APIs unless explicitly required by the implementation plan.
- Preserve deterministic behaviour.
- Preserve backward compatibility unless the specification explicitly changes it.
- Do not introduce or modify tests that belong to a different implementation phase.

## Engineering rules

- Use Python 3.11 or newer.
- Prefer simple, explicit, and readable Python code.
- Use type hints for public functions and methods.
- Use dataclasses for structured domain objects where appropriate.
- Prefer composition over inheritance.
- Keep parsing, validation, dependency ordering, SQL generation, reporting,
  and file I/O separated.
- Avoid unnecessary abstractions and design patterns.
- Do not add external dependencies without explaining why they are required.
- Do not invent schema fields, APIs, or requirements.

## Testing rules

- Write or update tests before implementing production code.
- Derive tests from the acceptance criteria in SPEC.md.
- Add tests for invalid inputs and edge cases.
- Run the complete test suite after every meaningful change.
- Do not weaken or remove a test simply to make the implementation pass.

## AI output review

- Treat generated code as a proposal that requires human review.
- Keep all logic understandable and easy to explain.
- Clearly state assumptions and uncertainties.
- Flag unsupported cases instead of silently guessing.
- Summarize what changed, why it changed, and which tests verify it.