# Pedagogical Export arc (E-arc) — 10-slice plan

Picks up [[user-rosetta-code-contrastive-pedagogy]]: the substrate
now has enough material (six language witnesses + classification
lattice + Rosetta tables + bicategorical apparatus + Conway
surreals) to start producing the contrastive-pedagogy surface
the user has wanted from the start.

## Why this arc

Per the user's framing throughout the conversation: the substrate's
gauge-honest discipline IS contrastive pedagogy in formal guise.
Each substrate primitive instantiates at multiple sites; the
contrast across instances IS the teaching content. After 70+ slices
of substrate-internal material, the pedagogical surface that
RENDERS this contrast for external readers is overdue.

The arc supplies SUBSTRATE-INTERNAL primitives for the
pedagogical layer: a `Section` record, a `MarkdownToken` enum,
a `to-section` family of functions on LanguageWitness / RosettaEntry
/ arc-summary types. The actual markdown RENDERING is an external
tool (Python / shell) that ingests the substrate's data — out of
the Agda --safe scope, deferred to a future companion arc.

Per [[feedback-coalgebraic-not-consumer-driven]]: with 70+ slices
of source material, the pedagogical surface is now forced by
consumer (the user wanting an external presentation layer).

## Costructure shadows

- **`Section`** record — a self-describing pedagogical unit.
- **`MarkdownToken`** enum — substrate-native markdown atoms.
- **`to-section` family** — typeclass-style functions from various
  substrate records to Section.
- **`PageBundle`** — collection of Sections forming a page.

## Ten slices

### Phase 1 — Section primitives (E1-E3)

- **E1 `Substrate.Pedagogy.MarkdownToken`** — substrate-native
  markdown atom enum (heading, paragraph, code-block, link,
  list-item, table-row, table-cell). Avoids stdlib Data.String.
- **E2 `Substrate.Pedagogy.Section`** — record bundling a title +
  Vec MarkdownToken body + metadata.
- **E3 `Substrate.Pedagogy.PageBundle`** — Vec of Sections + page
  title + cross-link manifest.

### Phase 2 — Per-record generators (E4-E6)

- **E4 `Substrate.Pedagogy.Witness-to-Section`** — given a
  LanguageWitness, produce a Section describing the cell + basis +
  carrier + universal property.
- **E5 `Substrate.Pedagogy.Rosetta-to-Section`** — given a
  RosettaEntry, produce a Section displaying the alignment table
  for the language pair.
- **E6 `Substrate.Pedagogy.Arc-to-Section`** — given an arc summary
  record (e.g., YArcSummary, BArcSummary, DArcSummary), produce a
  Section describing the arc's contributions + connections.

### Phase 3 — Page assembly (E7-E8)

- **E7 `Substrate.Pedagogy.LanguagePage`** — assemble per-language
  PageBundle: witness section + per-arc-where-instantiated
  sections + cross-links to sibling cells.
- **E8 `Substrate.Pedagogy.RosettaPage`** — assemble the full
  cross-language Rosetta table page: all 36 pairs of witnesses,
  alignment status, same-class / different-class distinction.

### Phase 4 — Index + capstone (E9-E10)

- **E9 `Substrate.Pedagogy.Index`** — top-level index PageBundle:
  catalogue of all language witnesses + all arc summaries + all
  Rosetta entries. The "table of contents" for the substrate's
  pedagogical surface.

- **E10 `Substrate.Pedagogy.Capstone`** — re-export + smoke tests
  + sample page generation for a worked language (e.g., Lojban)
  demonstrating end-to-end Section assembly.

## Success criteria

1. All ten slices typecheck under `--safe --without-K`.
2. `Section` + `MarkdownToken` + `PageBundle` primitives defined.
3. Generators for the three main source-record types (LanguageWitness,
   RosettaEntry, arc-summary) produce well-formed Sections.
4. E10 demonstrates a worked Lojban page assembled from substrate
   data.

## Deferred (out of arc)

- The external markdown RENDERER (Python / shell tool consuming
  the substrate's PageBundle data). Out of Agda --safe scope.
- HTML / web rendering.
- Search index / cross-reference graph.
- Interactive web interface.

These are companion-arc work; the Agda E-arc just produces the
substrate-internal source data they'd consume.
