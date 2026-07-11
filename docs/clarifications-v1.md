# Clarifications – Version 1

## Purpose

This document records ambiguities discovered during planning and the decisions made for v1.

## How to use this document

- This file overrides ambiguities in `SPEC.md`.
- New decisions should be appended rather than rewriting previous ones.
- If a decision changes in a future version, add a new entry and mark the old one as superseded.
- Unless explicitly superseded, all decisions in this document are authoritative for v1.

---

## C1. Example pipeline location

### Question

Which file path is canonical?

- `examples/legacy_pipeline.json`
- `data/legacy_pipeline.json`

### Decision

The canonical path is:

`data/legacy_pipeline.json`

### Rationale

The repository structure and prompts reference `data/`, so the example pipeline should live there.

---

## C2. JSON schema

### Question

- Are extra fields allowed or rejected?
- Are step ids required to be unique?
- Can there be multiple output steps?
- Can a pipeline have zero output steps?

### Decision

- Extra fields are ignored.
- Step ids must be globally unique.
- Multiple output steps are allowed.
- Zero output steps are a validation error.

### Rationale

Ignoring unknown fields makes the parser more tolerant to future schema evolution while still validating required fields.

---

## C3. dbt-style SQL generation

### Question

What does "dbt-style SQL" mean?

- Should upstream dependencies use `{{ ref() }}`?
- How should source tables be referenced?
- Should `config()` blocks be generated?
- Should SQL be generated for every step?

### Decision

- Generate one SQL file per non-source step.
- Upstream dependencies use `{{ ref('step_id') }}`.
- Source steps are treated as existing relations.
- No `config()` blocks are generated in v1.

### Rationale

This keeps the first version small while remaining compatible with dbt conventions.

---

## C4. Naming convention

### Question

How should generated SQL files be named?

### Decision

Files are named: 

```text
<step_id>.sql
```

Example: 

```text
filter_orders.sql
join_customers.sql
output_sales.sql
```

### Rationale

Step ids are already required to be unique and therefore produce deterministic filenames.

---

## C5. Expressions and conditions

### Question

Should expressions and conditions be parsed or validated?

### Decision

- Expressions are passed through verbatim.
- Conditions are passed through verbatim.
- Target dialect is ANSI SQL.
- No column quoting is performed.

### Rationale

SQL parsing and expression validation are outside the scope of v1.

---

## C6. Supported join types

### Question

Which join types are supported?

### Decision

Supported values:

- `inner`
- `left`
- `right`
- `full`

Any other value is a validation error.

---

## C7. Conversion report schema

### Question

What is the structure of the conversion report?

### Decision
```json
{
  "pipeline_name": "...",
  "status": "success|failed",
  "models_generated": [],
  "errors": [],
  "warnings": []
}
```

### Rationale

The report should be simple, machine-readable, and sufficient for automated testing.

---

## C8. Result validation

### Question

Should generated SQL be executed and validated against expected data?

### Decision

No.
Execution and data validation are deferred to v2.

### Rationale

The acceptance criteria only require static conversion.

---

## C9. CLI

### Question

Should v1 expose a command-line interface?

### Decision

No.
v1 exposes Python APIs only.

### Rationale

A CLI is not required by the specification and can be added later without affecting the core architecture.

---

## C10. Error message contract

### Question

What qualifies as a "clear error"?

### Decision

Errors must:

- include the step id;
- include the relevant field;
- contain a human-readable message.

### Example

```text
Invalid dependency: step 'filter_orders' references unknown step 'orders_raw'.
```

---

## C11. Orphan steps

### Question

How should orphan steps be handled?

### Decision

- Ignore them in v1.

### Future consideration

Orphan steps may become warnings in v2.

---

## C12. Deterministic ordering

### Question

How should independent steps be ordered when multiple valid topological orders exist?

### Decision

Preserve their declaration order from the input JSON.

### Rationale

This guarantees deterministic ordering and stable generated output.

---

## C13. Source relation naming

### Question

How should a source step with a file path be referenced in generated SQL?

### Decision

The source relation name is the basename of the `path` field without its file extension.

### Examples

- `orders.csv` becomes `orders`
- `customers.csv` becomes `customers`
- `data/products.parquet` becomes `products`

The source relation is referenced directly and does not use `{{ ref() }}`.

### Rationale

Source steps represent existing relations rather than generated dbt models. Using the filename without its extension provides a deterministic relation name for v1.

---

## C14. Conversion report model entries

### Question

What should the `models_generated` field contain?

### Decision

`models_generated` contains generated SQL filenames as strings, in deterministic dependency order.

### Example

```json
[
  "valid_orders.sql",
  "orders_with_revenue.sql",
  "enriched_orders.sql",
  "final_output.sql"
]
```

### Rationale

Generated filenames directly represent the created artifacts and are easy to verify in automated tests.

---

## C15. Pipeline-level validation errors

### Question

How should errors be represented when they are not associated with a specific step?

### Decision

Pipeline-level errors use `step_id: null`.

They must still include:

- the relevant field;
- a human-readable message.

### Example

```json
{
  "step_id": null,
  "field": "steps",
  "message": "Pipeline must contain at least one output step."
}
```

### Rationale

Some validation failures apply to the pipeline as a whole and cannot reference a specific step.

---

---

## C16. Output table handling

### Question

How should the `table` field of an output step affect generated SQL?

### Decision

In v1, the output model SQL selects from its upstream model and does not emit the physical table name.

The `table` value is retained in the domain model for reporting and future versions.

### Example

For:

```json
{
  "id": "final_output",
  "type": "output",
  "input": "enriched_orders",
  "table": "fct_order_revenue"
}
```

generate:

```sql
select *
from {{ ref('enriched_orders') }}
```

### Rationale

dbt model filenames determine model identity in v1. Physical target-table configuration is outside the current scope.
