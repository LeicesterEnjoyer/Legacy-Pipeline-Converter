# Agent Instructions

## General workflow

- Read SPEC.md before making any changes.
- Explain the proposed approach before implementing it.
- Ask for clarification when the specification is ambiguous.
- Do not implement features outside the current specification.
- Make small, focused changes rather than large rewrites.
- Do not modify unrelated files.

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