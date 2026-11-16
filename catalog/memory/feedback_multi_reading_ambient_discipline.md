---
name: feedback-multi-reading-ambient-discipline
description: Catalog claims with multiple correct readings (e.g. 24+8 = 32 codewords) should be formalised as ambient + decidable predicate + derived equivalences — never as one privileged definition. The user articulated this on 2026-05-15.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

When the catalog records a structure that has **multiple correct
readings** (Fano/parity, signed axes, ordered triples with S₃, Hodge
1-form ↔ 3-form, etc.), the Agda formalisation must NOT pick one
reading as the primary definition and derive the others. That's
Type-D rigidification at the formalisation layer — exactly the
failure mode rule 11 (strong) exists to prevent.

**The discipline rule** (user, 2026-05-15, articulated in the
24+8/Hodge context):

1. **Define the ambient with the largest natural cardinality.** For
   24+8 this is `Codeword : Set` with |Codeword| = 32 — concretely
   `Bool × Bool × Bool × Bool × Bool` (5 bits, extraction-friendly).

2. **Carve sub-structure with a decidable predicate.** `IsReserved :
   Codeword → Set` picks out the 8; `Live = ¬ IsReserved` is the
   24 as a Σ-type wrapper. The predicate IS the structural
   commitment — the rest is derived.

3. **Each reading is a separate lemma**, none privileged:
   - `Reserved ≃ SignedAxis` (8 ≃ 8) — Hodge 1-form view
   - `Live ≃ UnorderedTriple × S₃` (24 ≃ 4 × 6) — ordered-triple view
   - `Reserved ≃ Λ³(V⁴)` — Hodge 3-form view
   - Multiple readings can be checked simultaneously; none is "the"
     definition.

**Why:** The catalog (cocycles.md § CY-5 v19 update, 2026-05-15)
records the 24+8 split as having "many interpretations and potential
origins, and more than one [is] the correct reading." Privileging
one reading at the type level reintroduces the
choice-rigidification this project exists to eliminate (see
[[feedback-choice-rigidification-in-substrate]]). The ambient +
predicate + equivalences shape mirrors `IsomorphicCocycleStructure`
at the cocycle layer (no canonical fibre representative) — same
discipline, codeword layer.

**How to apply:**

- Before formalising a multi-reading structure, identify the ambient
  with the largest cardinality and the load-bearing decidable
  predicate that carves the parts.
- Resist the temptation to define `Live` and `Reserved` as separate
  data types with their own constructors — that commits to a reading
  before the equivalences are established.
- Each "reading" goes into its own lemma file; none re-exports the
  ambient with extra structure.
- When the catalog adds a new reading (e.g. another Hodge dual,
  another orbit-quotient view), it's an additive lemma — no rewrite
  of the ambient.

**Concrete next-slice application** (24+8 Hodge, if pursued):

- Slice intro: ambient `Codeword`, `IsReserved`, `Live`, cardinality
  lemmas.
- Subsequent slices: each `≃` reading as its own module.
- The Fano/parity bijection lives at the 8↔8 layer (signed-axis ↔
  reserved-codeword). The 24-side gets the S₃-on-unordered-triple
  reading as a separate lemma.

**Cross-references:**

- `Substrate.Cocycle.IsomorphicCocycleStructure` — analogue at the
  cocycle layer (no fibre canonical).
- `Substrate.Discipline.Rule11` — the strong-discipline rule this
  rule extends to a new layer.
- catalog/cocycles.md § CY-5 24+8 reading
- [[feedback-choice-rigidification-in-substrate]]
- [[project-agda-cubical-extraction-discipline]] — the extraction
  mold benefits from this shape since each reading is an extractable
  bidirectional pair.
