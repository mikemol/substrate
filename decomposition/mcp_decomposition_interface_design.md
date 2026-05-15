# MCP Interface Design for Cotype Decomposition

## Contextual Intent Envelope

- Intent type: deferred implementation with preserved design fidelity.
- Why now: the decomposition and retrospective artifacts already contain reusable structure worth preserving before context drift.
- Why not now: implementation is intentionally postponed.
- Resume trigger: when interactive querying, tool integration, or external agent access to decomposition results becomes valuable.
- Success-on-resume: implement the interface exactly against the contracts in this document, then iterate from the "Natural Next Moves" section.

## 1) Decompose-By-Entailment Framing

### Target (Step 1)

Construct a design for a Model Context Protocol interface that exposes the decomposition component and retrospective interpretation in a stable, queryable form.

### Repeatable Form (Step 2)

The repeated pattern across planned capabilities is:

1. Select a scope (source, move, section, line interval, axis signature, theme).
2. Retrieve normalized decomposition facts from SQLite.
3. Return typed, line-anchored evidence.

This pattern appears in all future operations (browse, filter, summarize, compare, segment).

### Named Costructures / Shadows (Step 3)

S1. Source Registry
- Definition: immutable metadata row for each decomposed source (path, hash, line_count, generated_at).
- Current substrate: sources table.

S2. Section Spine
- Definition: hierarchical section index with exact positional coverage.
- Current substrate: sections table.

S3. Triple Evidence Graph
- Definition: subject-predicate-object facts with precise line evidence and extraction method.
- Current substrate: triples table.

S4. Retrospective Move Timeline
- Definition: ordered move sequence with axis profiles and line ranges.
- Current substrate: retrospective_moves table.

S5. Transition Lattice
- Definition: consecutive move transitions in axis-space.
- Current substrate: retrospective_axis_transitions table.

S6. Thematic Signal Layer
- Definition: per-move predicate-weight summaries.
- Current substrate: retrospective_move_themes table.

S7. Interpreter Report Projection
- Definition: human-readable projection of S1-S6.
- Current substrate: decomposition/cotype_retrospective.md.

S8. Query Contract Envelope
- Definition: stable request/response contracts for MCP tools over S1-S7.
- New for MCP implementation.

### Composition Operation (Step 4)

Compose a request path as:

Request Scope -> SQL Retrieval on S1-S7 -> Evidence Anchoring -> Typed MCP Response

This composition is uniform across all MCP tools and preserves line-level traceability.

### Entailment Claim (Step 5)

If each MCP tool is constrained to S1-S7 and always returns evidence anchors (line start/end + source path), then retrospective interpretations served via MCP remain reproducible and auditable against the source markdown and database state.

## 2) Architectural Shape (Deferred Build)

### Components

1. MCP Server Runtime
- Hosts tool endpoints.
- Opens SQLite in read-only mode by default.

2. Decomposition Repository Adapter
- Thin query layer over decomposition/cotype_decomposition.sqlite.
- Centralizes SQL and schema assumptions.

3. Response Normalizer
- Converts DB rows into typed MCP payloads.
- Enforces evidence-first response shape.

4. Intent-Preserving Report Adapter
- Optional endpoint for current markdown report and report regeneration metadata.

### Data Ownership

- Source of truth: decomposition/cotype_decomposition.sqlite.
- Derived artifact: decomposition/cotype_retrospective.md.
- Build scripts remain outside MCP runtime and can be invoked separately.

## 3) Proposed MCP Tool Surface

All tools should return a consistent envelope:

- source_path
- source_sha256
- generated_at
- payload
- evidence (line-anchored references)

### Tool A: decomposition.list_sources

Purpose
- Enumerate available decomposed sources and metadata.

Input
- optional path filter.

Output
- rows from S1.

### Tool B: decomposition.get_sections

Purpose
- Retrieve section spine slices.

Input
- source identifier, optional level, path prefix, line interval.

Output
- rows from S2 with start/end lines.

### Tool C: decomposition.query_triples

Purpose
- Query semantic triples directly.

Input
- source, optional section_index, subject/predicate/object filters, line interval, limit.

Output
- rows from S3 including evidence lines and method.

### Tool D: decomposition.get_move_timeline

Purpose
- Retrieve ordered retrospective moves.

Input
- source, optional move token filter, line window.

Output
- rows from S4.

### Tool E: decomposition.get_axis_transitions

Purpose
- Inspect axis transition dynamics.

Input
- source, optional from_axis/to_axis filters.

Output
- rows from S5 plus aggregate counts.

### Tool F: decomposition.get_move_themes

Purpose
- Surface thematic signals per move or globally.

Input
- source, optional ordinal/move token, top_n.

Output
- rows from S6.

### Tool G: decomposition.interpret_window

Purpose
- Produce a retrospective interpretation for a selected move/line window.

Input
- source, either move ordinal/token or [line_start, line_end].

Output
- composed response from S2-S6 with compact narrative fields.

### Tool H: decomposition.export_report

Purpose
- Return current report metadata and optional regenerated report content pointer.

Input
- source, optional regenerate flag (default false).

Output
- report path, generation timestamp, summary stats.

## 4) Evidence and Reproducibility Contract

Every MCP response must include at least one evidence item with:

- section_index
- evidence_line_start
- evidence_line_end
- evidence_text

No summary-only responses for retrospective interpretations; summaries must be backed by evidence anchors.

## 5) Failure and Safety Modes

1. Missing source_id
- Return explicit not-found with available sources list.

2. Schema drift
- Return schema-version mismatch diagnostics and required migration steps.

3. Empty result set
- Return empty payload with preserved query echo and source metadata.

4. Write isolation
- MCP query tools are read-only by default; generation/regeneration tools are explicit opt-in.

## 6) Natural Next Moves (Encoded from Prior Proposal)

N1. Query-Mode CLI (high priority)
- Build a local CLI over the same contracts as MCP tools.
- Purpose: validate ergonomics before MCP transport concerns.
- Minimal commands:
  - list-sources
  - moves
  - triples
  - interpret-window

N2. Automatic Phase Segmentation (high priority)
- Add a segmentation pass that infers phase boundaries from axis transitions + thematic shifts.
- Store in new table candidate: retrospective_phases.
- Expose via future MCP tool decomposition.get_phases.

N3. Comparative Windows (medium)
- Add diff-mode interpretation between two move windows.
- Useful for identifying conceptual pivots and method changes.

N4. Schema Versioning (medium)
- Add explicit schema_version table and migration notes.
- Needed before broad MCP consumption.

N5. Performance and Caching (later)
- Add prepared-statement caching and optional materialized aggregates if query latency grows.

## 7) Non-Goals (Now)

- No MCP server implementation in this phase.
- No protocol transport wiring.
- No authentication/authorization layer yet.
- No changes to extraction logic unless required by future phase segmentation.

## 8) Implementation Readiness Checklist (For Later)

1. Confirm DB schema unchanged or migrate with version bump.
2. Implement repository adapter with read-only SQL methods matching Tool A-H.
3. Implement tool handlers with evidence contract enforcement.
4. Add integration tests against current database snapshot.
5. Add docs that map each tool to underlying tables S1-S7.

## 9) Open Questions to Resolve on Resume

1. Should decomposition.export_report support report regeneration inside MCP, or remain external-only?
2. Should interpret_window return markdown narrative, structured JSON, or both?
3. Should phase segmentation be deterministic only, or allow tunable heuristics?
4. Should tool responses support cross-source joins if multiple cotype files are added?

## 10) Persisted Reuse Value Summary

This design preserves a reusable architecture in named substructures (S1-S8), a compositional law, and an entailment contract. The future build can proceed by implementing tool contracts over existing tables with minimal ambiguity and with source-line evidence preserved end-to-end.

---

## Appendix A) Execution Brief (One-Page)

This appendix is an implementation-oriented bridge from design to build. It is still design-only: no protocol runtime decisions are fixed here.

### A.1 Shared Query Inputs

- `source_ref`: one of `source_id` or `source_path`
- `line_start`, `line_end`: optional line-window filter
- `limit`, `offset`: optional pagination controls
- `top_n`: optional top-k selector for aggregate outputs

Resolution rule:
- If `source_path` is provided, resolve to `source_id` first.
- Reject requests with neither `source_id` nor `source_path`.

### A.2 Tool-to-SQL Templates

Tool A: `decomposition.list_sources`

```sql
SELECT source_id, source_path, source_sha256, line_count, generated_at_utc
FROM sources
WHERE (:path_filter IS NULL OR source_path LIKE '%' || :path_filter || '%')
ORDER BY generated_at_utc DESC, source_id DESC;
```

Tool B: `decomposition.get_sections`

```sql
SELECT section_index, level, title, path, parent_index,
       heading_line, content_start_line, start_line, end_line
FROM sections
WHERE source_id = :source_id
  AND (:level IS NULL OR level = :level)
  AND (:path_prefix IS NULL OR path LIKE :path_prefix || '%')
  AND (:line_start IS NULL OR end_line >= :line_start)
  AND (:line_end   IS NULL OR start_line <= :line_end)
ORDER BY start_line ASC
LIMIT COALESCE(:limit, 1000)
OFFSET COALESCE(:offset, 0);
```

Tool C: `decomposition.query_triples`

```sql
SELECT section_index, subject, predicate, object,
       evidence_line_start, evidence_line_end, evidence_text,
       method, confidence
FROM triples
WHERE source_id = :source_id
  AND (:section_index IS NULL OR section_index = :section_index)
  AND (:subject   IS NULL OR subject   LIKE '%' || :subject || '%')
  AND (:predicate IS NULL OR predicate = :predicate)
  AND (:object    IS NULL OR object    LIKE '%' || :object || '%')
  AND (:line_start IS NULL OR evidence_line_end   >= :line_start)
  AND (:line_end   IS NULL OR evidence_line_start <= :line_end)
ORDER BY evidence_line_start ASC
LIMIT COALESCE(:limit, 1000)
OFFSET COALESCE(:offset, 0);
```

Tool D: `decomposition.get_move_timeline`

```sql
SELECT ordinal, section_index, move_title, move_token,
       section_path, start_line, end_line,
       primary_axis, all_axes, focus_text, probe_sections
FROM retrospective_moves
WHERE source_id = :source_id
  AND (:move_token IS NULL OR move_token = :move_token)
  AND (:line_start IS NULL OR end_line >= :line_start)
  AND (:line_end   IS NULL OR start_line <= :line_end)
ORDER BY ordinal ASC;
```

Tool E: `decomposition.get_axis_transitions`

```sql
SELECT from_axis, to_axis, COUNT(*) AS transition_count
FROM retrospective_axis_transitions
WHERE source_id = :source_id
  AND (:from_axis IS NULL OR from_axis = :from_axis)
  AND (:to_axis   IS NULL OR to_axis   = :to_axis)
GROUP BY from_axis, to_axis
ORDER BY transition_count DESC, from_axis, to_axis;
```

Tool F: `decomposition.get_move_themes`

```sql
SELECT ordinal, move_title, predicate, weight
FROM retrospective_move_themes
WHERE source_id = :source_id
  AND (:ordinal IS NULL OR ordinal = :ordinal)
  AND (:move_token IS NULL OR move_title LIKE '%' || :move_token || '%')
ORDER BY weight DESC, predicate ASC
LIMIT COALESCE(:top_n, 100);
```

Tool G: `decomposition.interpret_window`

Window resolution query:

```sql
SELECT section_index
FROM sections
WHERE source_id = :source_id
  AND start_line <= :line_end
  AND end_line   >= :line_start
ORDER BY start_line ASC;
```

Then compose response from Tool B/C/D/F templates using the resolved section set and line interval.

Tool H: `decomposition.export_report`

```sql
SELECT source_path, source_sha256, line_count, generated_at_utc
FROM sources
WHERE source_id = :source_id;
```

Report metadata may be read from filesystem sidecar data; DB remains the canonical semantic store.

### A.3 Response Contract Skeleton

```json
{
  "source": {
    "source_id": 1,
    "source_path": "...",
    "source_sha256": "...",
    "generated_at": "..."
  },
  "query": { "tool": "...", "params": { } },
  "payload": [ ],
  "evidence": [
    {
      "section_index": 0,
      "evidence_line_start": 0,
      "evidence_line_end": 0,
      "evidence_text": "..."
    }
  ]
}
```

Validation rule:
- If `payload` is non-empty for interpretive tools, `evidence` must be non-empty.

### A.4 Build Order for Minimal Viable MCP Slice

1. Implement Tool A + Tool C first (source discovery + factual query).
2. Implement Tool D + Tool E second (retrospective dynamics).
3. Implement Tool G third (composed interpretation).
4. Keep Tool H metadata-only until regeneration policy is settled.

### A.5 Done-Criteria for the Deferred Resume

- All A-H tools implemented against these SQL contracts.
- Evidence contract enforced uniformly.
- Integration tests verify deterministic outputs for a pinned DB snapshot.
- CLI mirror confirms ergonomics before MCP transport hardening.
