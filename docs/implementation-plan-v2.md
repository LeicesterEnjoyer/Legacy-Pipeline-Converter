# Implementation Plan – Version 2

## Purpose

Version 2 evolves the completed v1 prototype into a more realistic ETL-to-ELT migration tool while preserving the stable v1 core.

The v1 pipeline remains the foundation:

```text
read input
→ parse
→ validate
→ order
→ generate SQL
→ build report
→ write outputs
```

Version 2 adds:

- structured diagnostics and real warning propagation;
- configurable source-to-warehouse relation mappings;
- more realistic and deterministic SQL generation;
- minimal dbt artifact generation;
- optional local execution with DuckDB;
- expected-result comparison;
- an adapter interface for future vendor-specific inputs.

This document is the authoritative implementation plan for Version 2.

When information in this document conflicts with a Version 1 plan or recommendation, this document takes precedence for Version 2.

---

## 1. Design principles

### 1.1 Preserve the stable v1 core

The following v1 concepts remain unchanged unless explicitly superseded:

- the current step models;
- parsing into immutable domain models;
- validation before ordering;
- deterministic dependency ordering;
- SQL generation in execution order;
- conversion reports;
- file input and output;
- the high-level conversion API.

### 1.2 Keep separate concerns separate

Version 2 must not mix:

- pipeline definition;
- environment-specific source mapping;
- SQL rendering details;
- diagnostics;
- execution configuration;
- expected-result comparison.

In particular:

- source mappings do not belong inside `SourceStep`;
- generated SQL aliases do not belong inside `JoinStep`;
- warnings are not exceptions;
- DuckDB execution is optional and must not be required for ordinary conversion.

### 1.3 Prefer explicit immutable models

New domain and result models should be frozen dataclasses and should use tuples for immutable collections.

### 1.4 Preserve deterministic output

For identical input and configuration, Version 2 must produce byte-identical:

- SQL models;
- warning order;
- dbt YAML artifacts;
- generated filenames;
- conversion reports, excluding deliberately variable runtime metadata.

### 1.5 Keep Version 2 incremental

Version 2 is divided into two milestones:

```text
v2.0 — Migration output quality
v2.1 — Local execution validation
```

Vendor-specific parsers are not fully implemented in Version 2. Only the adapter contract and the existing JSON adapter are required.

---

## 2. Scope and non-goals

### 2.1 Version 2.0 scope

Version 2.0 includes:

- structured warnings;
- orphan-step diagnostics;
- configurable source mappings;
- deterministic source fallback behaviour;
- conflict detection for source mappings;
- aliases and qualified join predicates;
- deterministic SQL formatting;
- `sources.yml` generation;
- `schema.yml` generation;
- a default JSON adapter;
- an adapter extension contract;
- end-to-end warning and mapping support.

### 2.2 Version 2.1 scope

Version 2.1 includes:

- rendering dbt-style `ref()` expressions for local execution;
- registering source data in DuckDB;
- executing generated models in dependency order;
- comparing output relations with expected datasets;
- producing a validation summary;
- including validation results in the conversion report.

### 2.3 Out of scope

The following remain out of scope:

- complete Informatica, SSIS, Talend, or IICS parsers;
- remote warehouse execution;
- warehouse-specific SQL dialects beyond the supported prototype SQL;
- full dbt project generation;
- `dbt_project.yml` generation;
- dbt packages, macros, snapshots, tests, seeds, exposures, or semantic models;
- lineage visualisation;
- incremental dbt models;
- production deployment or scheduling;
- fuzzy or probabilistic result matching;
- GUI or IDE extension support.

---

## 3. Authoritative Version 2 pipeline flow

### 3.1 Conversion-only flow

```text
Input source
    ↓
Adapter normalisation
    ↓
parse_pipeline
    ↓
validate_pipeline
    ↓
collect_pipeline_warnings
    ↓
resolve_source_mappings
    ↓
order_steps
    ↓
generate_models
    ↓
generate_dbt_artifacts
    ↓
build_report
    ↓
write outputs
```

### 3.2 Optional execution flow

```text
Generated models
    ↓
render_models_for_execution
    ↓
register source data in DuckDB
    ↓
execute models in dependency order
    ↓
compare requested output with expected result
    ↓
ValidationSummary
    ↓
build_report
```

### 3.3 Important ordering decisions

- Parsing remains independent of mappings.
- Validation occurs before mapping resolution.
- Diagnostics are collected after a valid `Pipeline` exists.
- Source mappings are resolved before SQL generation.
- Dependency ordering remains based only on pipeline dependencies.
- The conversion report is built after all requested phases complete.
- Execution is performed only when explicitly requested.

---

## 4. Package layout

```text
src/
└── legacy_pipeline_converter/
    ├── __init__.py
    ├── api.py
    ├── diagnostics.py
    ├── errors.py
    ├── execution.py
    ├── io.py
    ├── models.py
    ├── ordering.py
    ├── parser.py
    ├── report.py
    ├── result_validation.py
    ├── source_mapping.py
    ├── sql_generator.py
    ├── dbt_artifacts.py
    ├── validator.py
    └── adapters/
        ├── __init__.py
        ├── base.py
        └── json_adapter.py
```

### Module responsibilities

| Module | Responsibility |
|---|---|
| `models.py` | Immutable domain, configuration, artifact, diagnostic, and result models |
| `errors.py` | Fatal parsing, validation, mapping, execution, and comparison errors |
| `parser.py` | Normalized dictionary to `Pipeline` |
| `validator.py` | Fatal pipeline validation rules |
| `diagnostics.py` | Non-fatal pipeline diagnostics and warning collection |
| `source_mapping.py` | Validate and resolve source-to-relation mappings |
| `ordering.py` | Deterministic dependency ordering and cycle detection |
| `sql_generator.py` | Generate deterministic SQL models |
| `dbt_artifacts.py` | Generate deterministic `sources.yml` and `schema.yml` artifacts |
| `execution.py` | Render and execute generated models locally with DuckDB |
| `result_validation.py` | Compare actual and expected result relations |
| `report.py` | Build `ConversionReport` |
| `io.py` | Read source files and write SQL, YAML, JSON, and validation outputs |
| `adapters/base.py` | Adapter protocol for normalizing external input |
| `adapters/json_adapter.py` | Adapter for the existing JSON/dict format |
| `api.py` | Orchestrate all requested phases |

---

## 5. Existing v1 models retained unchanged

The following models remain exactly as implemented in Version 1:

```python
@dataclass(frozen=True)
class SourceStep:
    id: str
    path: str


@dataclass(frozen=True)
class FilterStep:
    id: str
    input: str
    condition: str


@dataclass(frozen=True)
class CalculatedColumnStep:
    id: str
    input: str
    column: str
    expression: str


@dataclass(frozen=True)
class JoinStep:
    id: str
    left: str
    right: str
    left_key: str
    right_key: str
    join_type: str


@dataclass(frozen=True)
class OutputStep:
    id: str
    input: str
    table: str


Step = (
    SourceStep
    | FilterStep
    | CalculatedColumnStep
    | JoinStep
    | OutputStep
)


@dataclass(frozen=True)
class Pipeline:
    name: str
    steps: tuple[Step, ...]


@dataclass(frozen=True)
class OrderedPipeline:
    pipeline: Pipeline
    execution_order: tuple[str, ...]


@dataclass(frozen=True)
class GeneratedModel:
    step_id: str
    filename: str
    sql: str
```

### Rationale

Environment-specific source mappings are not part of the legacy pipeline definition.

SQL aliases are rendering details and are not part of the `JoinStep` domain model.

This avoids conflicting sources of truth and keeps Version 1 inputs backward compatible.

---

## 6. New and changed Version 2 models

### 6.1 Warning model

```python
@dataclass(frozen=True)
class WarningInfo:
    code: str
    message: str
    step_id: str | None = None
    field: str | None = None
```

Warnings are structured data.

Warnings:

- do not inherit from `Exception`;
- do not stop conversion;
- are collected in deterministic order;
- are serialized as JSON objects.

### 6.2 Source mapping models

```python
@dataclass(frozen=True)
class SourceMapping:
    source_id: str
    relation: str
    database: str | None = None
    schema: str | None = None


@dataclass(frozen=True)
class ResolvedSource:
    source_id: str
    relation_name: str
    used_fallback: bool
```

`SourceMapping` is configuration.

`ResolvedSource` is the deterministic result of mapping resolution.

The fully qualified relation name is constructed as:

```text
database.schema.relation
schema.relation
relation
```

depending on which optional fields are present.

### 6.3 Resolved mapping result

```python
@dataclass(frozen=True)
class SourceResolution:
    sources: tuple[ResolvedSource, ...]
    warnings: tuple[WarningInfo, ...]
```

This keeps source resolution separate from the immutable `Pipeline`.

### 6.4 dbt artifact model

```python
@dataclass(frozen=True)
class GeneratedArtifact:
    filename: str
    content: str
    artifact_type: Literal["sources_yml", "schema_yml"]
```

### 6.5 Execution configuration

```python
@dataclass(frozen=True)
class ExecutionRequest:
    source_files: tuple[SourceDataFile, ...]
    output_step_id: str
    expected_file: str | None = None


@dataclass(frozen=True)
class SourceDataFile:
    source_id: str
    path: str
```

Execution only occurs when an `ExecutionRequest` is supplied.

### 6.6 Validation result models

```python
@dataclass(frozen=True)
class DifferenceDetail:
    kind: Literal[
        "row_count",
        "column_names",
        "column_types",
        "row_values",
    ]
    message: str


@dataclass(frozen=True)
class ValidationSummary:
    executed: bool
    passed: bool | None
    output_step_id: str | None = None
    actual_row_count: int | None = None
    expected_row_count: int | None = None
    differences: tuple[DifferenceDetail, ...] = ()
```

Semantics:

- `executed=False`, `passed=None` means execution was not requested.
- `executed=True`, `passed=True` means comparison passed.
- `executed=True`, `passed=False` means comparison completed and differences were found.

### 6.7 Conversion report

Version 2 supersedes the Version 1 warning representation.

```python
@dataclass(frozen=True)
class ConversionReport:
    pipeline_name: str
    status: Literal["success", "failed"]
    models_generated: tuple[str, ...]
    errors: tuple[str, ...]
    warnings: tuple[WarningInfo, ...]
    validation: ValidationSummary | None = None
```

A validation mismatch does not make conversion itself fail.

Recommended meaning:

- conversion/report `status="failed"`: parsing, validation, mapping, generation, or execution could not complete;
- `status="success"` with `validation.passed=False`: conversion completed, but generated output did not match the expected result.

---

## 7. Error model

Warnings are not errors.

Fatal Version 2 errors extend the existing `ConversionError` hierarchy.

Recommended additions:

```python
class SourceMappingError(ConversionError):
    """Base class for fatal source-mapping configuration errors."""


class ConflictingSourceMappingError(SourceMappingError):
    """Raised when one source id has multiple different mappings."""


class ExecutionError(ConversionError):
    """Raised when generated SQL cannot be executed."""


class ResultValidationError(ConversionError):
    """Raised when result comparison cannot be performed."""
```

### Duplicate mapping behaviour

- Two identical mappings for the same source may be deduplicated.
- Two different mappings for the same source are a fatal `ConflictingSourceMappingError`.
- The implementation must never silently choose one conflicting mapping.

---

## 8. Warning rules

Warnings are collected by dedicated functions and propagated through the API.

### 8.1 Orphan steps

A step is orphaned when it is not reachable by traversing dependencies backwards from any output step.

For each orphaned step, emit:

```python
WarningInfo(
    code="orphan_step",
    message=f"Step {step_id!r} is not used by any output.",
    step_id=step_id,
    field="steps",
)
```

Ordering:

- preserve pipeline declaration order.

### 8.2 Missing source mapping

When no explicit mapping exists for a source:

- derive the fallback relation from `PurePath(source.path).stem`;
- continue conversion;
- emit:

```python
WarningInfo(
    code="missing_source_mapping",
    message=(
        f"Source {source.id!r} has no explicit mapping; "
        f"using fallback relation {fallback!r}."
    ),
    step_id=source.id,
    field="path",
)
```

### 8.3 Unsupported dbt metadata

Do not create warnings for features that the user did not request.

A warning may be emitted only when supplied metadata cannot be represented in the supported `sources.yml` or `schema.yml` subset.

### 8.4 Execution not requested

No warning is emitted when execution is not requested.

If execution is requested but required execution input is missing, raise a clear fatal error rather than silently skipping it.

---

## 9. Source mapping design

### 9.1 Resolution API

```python
def resolve_source_mappings(
    pipeline: Pipeline,
    mappings: Sequence[SourceMapping],
) -> SourceResolution:
    ...
```

### 9.2 Behaviour

For every `SourceStep`, in pipeline declaration order:

1. Find mappings with matching `source_id`.
2. If none exist:
   - use filename-derived fallback;
   - emit `missing_source_mapping`.
3. If one unique mapping exists:
   - use its fully qualified relation.
4. If duplicate identical mappings exist:
   - deduplicate deterministically;
   - no warning is required.
5. If multiple different mappings exist:
   - raise `ConflictingSourceMappingError`.

### 9.3 SQL generator input

`generate_models` receives explicit resolution information:

```python
def generate_models(
    ordered: OrderedPipeline,
    source_resolution: SourceResolution | None = None,
) -> tuple[GeneratedModel, ...]:
    ...
```

When no `SourceResolution` is supplied, the generator preserves Version 1 compatibility and derives source relation names from paths.

The high-level Version 2 API should always resolve mappings explicitly before calling `generate_models`.

---

## 10. SQL generation rules

### 10.1 Existing step behaviour

| Step type | SQL generation |
|---|---|
| `source` | No model |
| `filter` | `SELECT * FROM <upstream> WHERE <condition>` |
| `calculated_column` | `SELECT *, <expression> AS <column> FROM <upstream>` |
| `join` | Join two resolved upstream relations with aliases |
| `output` | `SELECT * FROM <upstream>` |

### 10.2 Source references

A source upstream uses its resolved relation name:

```sql
FROM raw.orders
```

A transformed upstream uses dbt `ref()`:

```sql
FROM {{ ref('valid_orders') }}
```

### 10.3 Join aliases

Aliases are generated by the SQL generator, not stored in `JoinStep`.

For every join:

```text
left alias  = "left_relation"
right alias = "right_relation"
```

Version 2 uses these fixed aliases to keep output deterministic.

Example:

```sql
SELECT *
FROM {{ ref('orders_with_revenue') }} AS left_relation
LEFT JOIN raw.customers AS right_relation
    ON left_relation.customer_id = right_relation.id
```

### 10.4 SQL formatting

Canonical formatting:

- uppercase SQL keywords;
- one clause per line;
- four spaces before `ON`;
- exactly one trailing newline;
- no trailing spaces;
- stable aliases;
- stable filename order.

### 10.5 Backward compatibility

Non-join SQL may retain its Version 1 semantics while adopting canonical line formatting.

All Version 1 SQL-generation tests must either remain valid or be intentionally updated where Version 2 explicitly supersedes exact formatting.

---

## 11. dbt artifact generation

### 11.1 Supported artifacts

Version 2 generates only:

```text
sources.yml
schema.yml
```

`dbt_project.yml` is out of scope.

### 11.2 API

```python
def generate_dbt_artifacts(
    pipeline: Pipeline,
    models: Sequence[GeneratedModel],
    source_resolution: SourceResolution,
) -> tuple[GeneratedArtifact, ...]:
    ...
```

### 11.3 `sources.yml`

The generated file contains mapped sources grouped deterministically by:

```text
database
schema
```

For the prototype:

- source names are deterministic;
- tables are sorted by source declaration order;
- relation names come from `SourceResolution`;
- filename-derived fallbacks are included.

### 11.4 `schema.yml`

The generated file contains one entry per generated model in generation order.

Minimum content:

```yaml
version: 2

models:
  - name: valid_orders
  - name: orders_with_revenue
```

### 11.5 Materialization metadata

Version 2 does not add materialization fields to existing step models.

A simple generation configuration may be introduced:

```python
@dataclass(frozen=True)
class DbtGenerationConfig:
    default_materialization: Literal["view", "table"] = "view"
```

If supported, materialization is represented in `schema.yml` model config.

### 11.6 YAML determinism

Use a YAML library with stable insertion ordering.

The generated YAML must be byte-identical for identical inputs and configuration.

---

## 12. Adapter design

### 12.1 Adapter contract

Adapters normalize external input into the existing dictionary format.

```python
class PipelineAdapter(Protocol):
    def normalize(self, source: object) -> dict[str, Any]:
        ...
```

Adapters do not create `Pipeline` directly.

The authoritative domain conversion remains:

```python
normalized = adapter.normalize(source)
pipeline = parse_pipeline(normalized)
```

### 12.2 JSON adapter

```python
class JsonPipelineAdapter:
    def normalize(self, source: object) -> dict[str, Any]:
        ...
```

Supported inputs:

- a dictionary in the existing v1 format;
- optionally a JSON file path, if explicitly included in the final API design.

### 12.3 Vendor adapters

Version 2 requires extension points only.

Do not implement complete vendor parsers.

Future adapters may include:

```text
Informatica XML
SSIS .dtsx
Talend metadata
IICS API responses
```

---

## 13. DuckDB execution contract

### 13.1 Execution is optional

Ordinary conversion does not require DuckDB.

Execution occurs only when the caller supplies an `ExecutionRequest`.

### 13.2 dbt reference rendering

DuckDB cannot execute dbt Jinja directly.

Before execution:

```text
{{ ref('valid_orders') }}
```

is rendered as:

```text
valid_orders
```

This renderer supports only the exact generated `ref()` syntax produced by the project.

It is not a general Jinja renderer.

### 13.3 Source registration

Each `SourceDataFile` is matched by `source_id`.

Supported Version 2.1 source format:

```text
CSV only
```

For every source:

- create a DuckDB view or table using `read_csv_auto`;
- register it under the resolved relation's final relation component;
- reject missing source files with `ExecutionError`.

Database/schema-qualified mapping names are used for generated dbt SQL, but local DuckDB execution may normalize them to deterministic local relation names through an explicit execution lookup.

### 13.4 Model execution

For each generated model in dependency order:

```sql
CREATE OR REPLACE VIEW <step_id> AS
<rendered SQL>;
```

Output models are executed like all other non-source models.

### 13.5 Execution API

```python
def execute_models(
    ordered: OrderedPipeline,
    models: Sequence[GeneratedModel],
    source_resolution: SourceResolution,
    request: ExecutionRequest,
) -> ExecutedPipeline:
    ...
```

Recommended result:

```python
@dataclass(frozen=True)
class ExecutedPipeline:
    output_step_id: str
    output_relation: str
    row_count: int
```

---

## 14. Result comparison contract

### 14.1 Expected result format

Version 2.1 supports expected results from a CSV file.

### 14.2 Comparison target

The caller explicitly supplies:

```python
ExecutionRequest.output_step_id
```

The selected id must reference an `OutputStep`.

### 14.3 Comparison rules

Comparison checks, in order:

1. column names;
2. column order;
3. row count;
4. row values.

Rows are compared as multisets unless a future specification introduces an explicit ordering rule.

This means:

- row order is ignored;
- duplicate rows are preserved and counted;
- column order is significant;
- exact values are compared;
- `NULL` values compare equal to `NULL`;
- floating-point tolerance is not supported in Version 2.1.

### 14.4 Validation behaviour

A completed mismatch returns:

```python
ValidationSummary(
    executed=True,
    passed=False,
    ...
)
```

It does not raise an exception.

An inability to perform comparison, such as an unreadable expected file, raises `ResultValidationError`.

---

## 15. Conversion report and serialization

### 15.1 Report building API

```python
def build_report(
    *,
    pipeline_name: str,
    status: Literal["success", "failed"],
    models_generated: Sequence[str],
    errors: Sequence[str],
    warnings: Sequence[WarningInfo],
    validation: ValidationSummary | None = None,
) -> ConversionReport:
    ...
```

The function stores immutable tuples.

### 15.2 Warning serialization

Warnings are serialized as objects:

```json
{
  "code": "orphan_step",
  "message": "Step 'unused_filter' is not used by any output.",
  "step_id": "unused_filter",
  "field": "steps"
}
```

### 15.3 Validation serialization

Example:

```json
{
  "executed": true,
  "passed": false,
  "output_step_id": "final_output",
  "actual_row_count": 10,
  "expected_row_count": 9,
  "differences": [
    {
      "kind": "row_count",
      "message": "Expected 9 rows but received 10."
    }
  ]
}
```

---

## 16. Public API

Exposed from `legacy_pipeline_converter/__init__.py`:

```python
parse_pipeline
validate_pipeline
collect_pipeline_warnings
resolve_source_mappings
order_steps
generate_models
generate_dbt_artifacts
execute_models
compare_results
build_report
convert_pipeline
```

### Recommended Version 2 API

```python
def convert_pipeline(
    source: object,
    *,
    adapter: PipelineAdapter | None = None,
    mappings: Sequence[SourceMapping] = (),
    dbt_config: DbtGenerationConfig | None = None,
    execution_request: ExecutionRequest | None = None,
) -> ConversionResult:
    ...
```

Recommended result model:

```python
@dataclass(frozen=True)
class ConversionResult:
    ordered_pipeline: OrderedPipeline | None
    models: tuple[GeneratedModel, ...]
    artifacts: tuple[GeneratedArtifact, ...]
    report: ConversionReport
```

### Failure behaviour

Expected conversion errors are collected into a failed report.

Unexpected programming errors are not swallowed.

The API catches only known `ConversionError` subclasses.

---

## 17. Implementation phases

## Milestone v2.0 — Migration output quality

### Phase 1 — Structured warnings and diagnostics

Goal:

- replace ignored warnings with structured warning propagation.

Deliverables:

- `WarningInfo`;
- `diagnostics.py`;
- orphan detection;
- `ConversionReport.warnings: tuple[WarningInfo, ...]`;
- warning serialization;
- deterministic warning order.

### Phase 2 — Source mapping

Goal:

- support explicit source-to-relation configuration without changing core step models.

Deliverables:

- `SourceMapping`;
- `ResolvedSource`;
- `SourceResolution`;
- fallback relation warnings;
- conflict detection;
- integration with SQL generation.

### Phase 3 — Improved SQL generation

Goal:

- produce realistic deterministic SQL.

Deliverables:

- resolved source relations;
- fixed join aliases;
- qualified join predicates;
- canonical formatting;
- updated SQL tests.

### Phase 4 — dbt artifacts

Goal:

- generate the minimal supported dbt metadata.

Deliverables:

- deterministic `sources.yml`;
- deterministic `schema.yml`;
- optional default materialization config;
- YAML file output.

### Phase 5 — Adapter extension contract

Goal:

- preserve the JSON flow while introducing future vendor input extensibility.

Deliverables:

- `PipelineAdapter` protocol;
- `JsonPipelineAdapter`;
- API adapter support;
- no complete vendor parser.

### Phase 6 — v2.0 integration

Goal:

- combine diagnostics, mappings, SQL, dbt artifacts, and reports.

Deliverables:

- `ConversionResult`;
- updated `convert_pipeline`;
- end-to-end v2.0 test;
- all v1 tests passing unless explicitly superseded.

## Milestone v2.1 — Local execution validation

### Phase 7 — DuckDB rendering and execution

Goal:

- execute generated models locally.

Deliverables:

- exact `ref()` renderer;
- CSV source registration;
- dependency-order model execution;
- selected output relation;
- execution error handling.

### Phase 8 — Result comparison

Goal:

- compare one generated output with one expected CSV.

Deliverables:

- multiset row comparison;
- column and row-count checks;
- `ValidationSummary`;
- mismatch diagnostics.

### Phase 9 — v2.1 integration

Goal:

- expose optional execution through the high-level API.

Deliverables:

- `ExecutionRequest`;
- validation report integration;
- end-to-end execution pass test;
- end-to-end mismatch test;
- complete Version 2 test suite.

---

## 18. Final ordered TDD test plan

Tests must be written before their minimum production component.

The section below is the authoritative test plan for Version 2.

### Phase 1 — Structured warnings and diagnostics

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 1 | `tests/test_report.py` | `test_build_report_populates_structured_warnings` | Report preserves warnings as immutable structured values | `WarningInfo`, `ConversionReport`, `build_report` |
| 2 | `tests/test_report.py` | `test_warning_serializes_to_expected_json_object` | Warning fields serialize to JSON keys | report serialization |
| 3 | `tests/test_diagnostics.py` | `test_collect_warnings_returns_no_orphan_warning_for_fully_used_pipeline` | Fully connected example emits no orphan warning | `collect_pipeline_warnings` |
| 4 | `tests/test_diagnostics.py` | `test_collect_warnings_emits_orphan_warning` | One unreachable step emits one warning | orphan analysis |
| 5 | `tests/test_diagnostics.py` | `test_orphan_warnings_follow_declaration_order` | Multiple warnings are deterministic | diagnostics ordering |

### Phase 2 — Source mapping

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 6 | `tests/test_source_mapping.py` | `test_resolve_source_mapping_uses_explicit_relation` | Explicit mapping overrides filename fallback | `SourceMapping`, resolver |
| 7 | `tests/test_source_mapping.py` | `test_resolve_source_mapping_builds_qualified_relation` | Database/schema/relation form is deterministic | resolver |
| 8 | `tests/test_source_mapping.py` | `test_missing_source_mapping_uses_filename_fallback_and_warning` | Missing mapping continues with warning | resolver |
| 9 | `tests/test_source_mapping.py` | `test_identical_duplicate_mappings_are_deduplicated` | Identical duplicates are harmless | resolver |
| 10 | `tests/test_source_mapping.py` | `test_conflicting_source_mappings_raise_clear_error` | Different mappings for one source fail | `ConflictingSourceMappingError` |
| 11 | `tests/test_source_mapping.py` | `test_source_resolution_follows_pipeline_declaration_order` | Resolved sources are deterministic | resolver |

### Phase 3 — Improved SQL generation

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 12 | `tests/test_sql_generator.py` | `test_generate_filter_uses_mapped_source_relation` | Source mapping appears in SQL | generator integration |
| 13 | `tests/test_sql_generator.py` | `test_generate_join_uses_fixed_aliases` | Join uses deterministic aliases | SQL generator |
| 14 | `tests/test_sql_generator.py` | `test_generate_join_uses_qualified_key_references` | Join predicate qualifies both keys | SQL generator |
| 15 | `tests/test_sql_generator.py` | `test_generate_join_with_transformed_and_source_upstreams` | `ref()` and mapped source relation work together | SQL generator |
| 16 | `tests/test_sql_generator.py` | `test_generate_sql_uses_canonical_formatting` | Exact line breaks, indentation, and trailing newline | SQL generator |
| 17 | `tests/test_sql_generator.py` | `test_generate_sql_is_byte_deterministic` | Repeated generation is identical | SQL generator |

### Phase 4 — dbt artifacts

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 18 | `tests/test_dbt_artifacts.py` | `test_generate_sources_yml_contains_resolved_sources` | All resolved sources appear | artifact generator |
| 19 | `tests/test_dbt_artifacts.py` | `test_generate_sources_yml_is_deterministic` | Repeated generation is byte-identical | artifact generator |
| 20 | `tests/test_dbt_artifacts.py` | `test_generate_schema_yml_contains_generated_models_in_order` | Model metadata follows generation order | artifact generator |
| 21 | `tests/test_dbt_artifacts.py` | `test_generate_schema_yml_uses_default_materialization` | Requested default materialization appears | config + artifact generator |
| 22 | `tests/test_io.py` | `test_write_dbt_artifacts_creates_yaml_files` | YAML artifacts are written to disk | `io.py` |

### Phase 5 — Adapter extension contract

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 23 | `tests/test_adapters.py` | `test_json_adapter_normalizes_current_dictionary_format` | Existing v1 dict remains supported | JSON adapter |
| 24 | `tests/test_adapters.py` | `test_adapter_protocol_requires_normalize_method` | Adapter contract is explicit | adapter protocol |
| 25 | `tests/test_api.py` | `test_convert_pipeline_uses_supplied_adapter` | API delegates normalization to adapter | API integration |

### Phase 6 — v2.0 integration

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 26 | `tests/test_api.py` | `test_convert_pipeline_v2_returns_models_artifacts_and_warnings` | Full v2.0 result is populated | `ConversionResult`, API |
| 27 | `tests/test_api.py` | `test_convert_pipeline_v2_preserves_v1_json_compatibility` | Existing example still converts | API |
| 28 | `tests/test_api.py` | `test_convert_pipeline_v2_conflicting_mapping_returns_failed_report` | Known mapping error is reported, not raised | API |
| 29 | `tests/test_api.py` | `test_convert_pipeline_v2_is_deterministic` | Models, artifacts, and warnings are stable | API |

### Phase 7 — DuckDB execution

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 30 | `tests/test_execution.py` | `test_render_ref_for_execution_replaces_generated_ref` | Exact generated `ref()` becomes local relation | renderer |
| 31 | `tests/test_execution.py` | `test_register_csv_sources_in_duckdb` | Source CSV is queryable | source registration |
| 32 | `tests/test_execution.py` | `test_execute_models_runs_in_dependency_order` | Multi-step SQL executes successfully | executor |
| 33 | `tests/test_execution.py` | `test_execute_models_returns_selected_output_relation` | Requested output is returned | executor |
| 34 | `tests/test_execution.py` | `test_missing_source_file_raises_clear_execution_error` | Missing source input is fatal and clear | `ExecutionError` |

### Phase 8 — Result comparison

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 35 | `tests/test_result_validation.py` | `test_compare_results_passes_for_equal_multisets` | Row order differences do not fail | comparator |
| 36 | `tests/test_result_validation.py` | `test_compare_results_detects_column_mismatch` | Column difference is reported | comparator |
| 37 | `tests/test_result_validation.py` | `test_compare_results_detects_row_count_mismatch` | Row-count difference is reported | comparator |
| 38 | `tests/test_result_validation.py` | `test_compare_results_detects_value_mismatch` | Value difference is reported | comparator |
| 39 | `tests/test_result_validation.py` | `test_compare_results_preserves_duplicate_rows` | Duplicate multiplicity matters | comparator |
| 40 | `tests/test_result_validation.py` | `test_unreadable_expected_file_raises_clear_error` | Comparison setup failure is fatal | `ResultValidationError` |

### Phase 9 — v2.1 integration

| # | Test file | Test name | Behaviour tested | Min. production component |
|---|---|---|---|---|
| 41 | `tests/test_api.py` | `test_convert_pipeline_without_execution_has_no_execution_warning` | Optional execution stays silent | API |
| 42 | `tests/test_api.py` | `test_convert_pipeline_with_matching_expected_result_passes_validation` | End-to-end validation passes | API |
| 43 | `tests/test_api.py` | `test_convert_pipeline_with_mismatch_returns_failed_validation_summary` | Conversion succeeds but validation fails | API |
| 44 | `tests/test_api.py` | `test_convert_pipeline_execution_error_returns_failed_report` | Known execution error is captured | API |
| 45 | `tests/test_api.py` | `test_v2_complete_suite_preserves_v1_regressions` | All v1 and v2 tests pass | complete project |

---

## 19. Acceptance criteria

Version 2.0 is complete when:

1. Warnings are structured, deterministic, serialized, and propagated.
2. Orphan steps emit warnings without failing conversion.
3. Explicit source mappings are supported.
4. Missing mappings use deterministic fallbacks with warnings.
5. Conflicting mappings fail clearly.
6. Core v1 step models remain unchanged.
7. Join SQL uses deterministic aliases and qualified predicates.
8. SQL generation is byte-deterministic.
9. `sources.yml` and `schema.yml` are generated deterministically.
10. The JSON adapter preserves the current input format.
11. The high-level API returns a `ConversionResult`.
12. All v1 and v2.0 tests pass.

Version 2.1 is complete when:

1. Generated `ref()` expressions can be rendered for DuckDB.
2. CSV sources can be registered and queried locally.
3. Generated models execute in dependency order.
4. One requested output can be compared with an expected CSV.
5. Comparison checks columns, row count, duplicate multiplicity, and values.
6. Validation results are included in `ConversionReport`.
7. Execution remains optional and produces no warning when not requested.
8. All v1, v2.0, and v2.1 tests pass.

---

## 20. Estimated effort

These estimates assume implementation with AI assistance, manual review, debugging, and documentation.

| Phase | Estimated focused time |
|---|---:|
| Structured warnings and diagnostics | 5–9 hours |
| Source mapping | 6–10 hours |
| Improved SQL generation | 5–9 hours |
| dbt artifacts | 8–14 hours |
| Adapter contract | 4–7 hours |
| v2.0 integration and cleanup | 5–9 hours |
| DuckDB execution | 10–18 hours |
| Result comparison | 8–14 hours |
| v2.1 integration and cleanup | 6–10 hours |

Estimated total:

```text
57–100 focused hours
```

Reasonable calendar estimates:

```text
2 hours/day  → approximately 6–10 weeks
4 hours/day  → approximately 3–6 weeks
```

---

## 21. Implementation workflow

For each phase:

1. Read this document and the current `PROJECT_STATE.md`.
2. Use the final ordered TDD test plan as the authoritative test source.
3. Write only the tests for the current phase.
4. Run the targeted tests and confirm they fail for the expected reason.
5. Implement the minimum production code.
6. Run targeted tests.
7. Run the complete test suite.
8. Review the diff manually for:
   - scope adherence;
   - architectural boundaries;
   - unnecessary abstractions;
   - unused imports;
   - swallowed exceptions;
   - accidental documentation changes.
9. Update `PROJECT_STATE.md` only after the phase is accepted.
10. Commit the completed phase separately.

---

## 22. Summary

Version 2 must improve the migration prototype without weakening the completed Version 1 architecture.

The key architectural decisions are:

- keep existing step models unchanged;
- keep source mapping outside the pipeline definition;
- keep SQL aliases inside SQL generation;
- represent warnings as structured immutable values;
- treat mapping conflicts as errors;
- generate only `sources.yml` and `schema.yml`;
- keep execution optional;
- define an exact DuckDB rendering and comparison contract;
- normalize adapter input before using the existing parser;
- implement Version 2 through a strict ordered TDD plan.