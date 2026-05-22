# Closure-debt arc (D-arc) — 10-slice plan

Discharges ten genuine deferred obligations from the linguistic
Rosetta arc family (Lojban + Toki Pona + Classification). Each
slice produces real Agda content (not just comment updates) and
verifies no regression. The 20-slice sprint pairs this D-arc with
the Yoneda lift Y-arc ([scratch/yoneda_lift_arc_plan.md](yoneda_lift_arc_plan.md))
in sequence: closure first, then forward.

## Why this arc

Per the deferred-item catalog surveyed in conversation: the
substrate has ~6 inline `-- deferred` comments in the recent arcs,
plus several "shared parent extraction" notes that are now
out-of-date because the Classification arc actually extracted the
parent. Discharging these now keeps the substrate's prose honest
([[feedback-comments-dont-overclaim]]) and ensures downstream arcs
build on a clean foundation rather than inheriting documentation
debt.

Per [[feedback-coalgebraic-not-consumer-driven]] negated/applied
positively: with the parent primitive in place + four new witnesses,
the structural moves that were deferred "until a consumer forces
them" now HAVE a consumer (the Classification arc itself), so the
closures are forced.

## Costructure shadows

- **`RetroactiveAlignment`** — D9's unified module that documents
  the parent-primitive supersedes-deferrals story across all
  witnesses (Lojban L10, TokiPona T10, the classification arc).
- **Per-cell structural closures** — each cell of the lattice
  gets one or more small follow-ups that discharge the most
  obvious obligation (Toki Pona's `WithBasisAction`, Kelen's
  relation composition, Lie's anti-commutativity, etc.).
- **Closure log** — a markdown record of what was closed and how.

## Ten slices

Per [[project-annealing-methodology]]: one degree of freedom per
slice. Per [[feedback-file-size-one-pass-rewrite]]: one Write per
file. Per [[feedback-minimize-stdlib-deps]]-strengthened:
substrate-native throughout.

### Phase 1 — Inline-stub closures (D1-D5)

- **D1 `Substrate.TokiPona.ModifierBilinear.WithBasisAction`** —
  promote the T4 comment-stub into real content. Define the
  2-step bilinear-via-FreeLinearization construction: given a
  basis-pair action `b : Fin n → Fin n → V`, lift to a bilinear
  `V₁ → V₂ → V` via two applications of FreeLinearization
  (specifically, FreeLinearization-applied-twice). Discharges the
  "true bilinear modify" obligation the T4 slice flagged as not
  satisfying. Uses Substrate.Category.FreeLinearization +
  Substrate.Algebra.F2.Linear.

- **D2 `Substrate.Kelen.RelationCompose`** — add the deferred
  relation-composition operation to Kelen. Since Kelen's "free
  relation" cell is fundamentally about relational composition
  (not function composition), supply `_∘ᴿ_ : KelenWord → KelenWord
  → KelenWord` plus the relevant associativity / identity laws at
  the word level. Connects to Substrate.Category.RuleAction for
  the proper Rel-category morphism semantics (deferred to a future
  arc; D2 lands the word-level operation).

- **D3 `Substrate.Invented.LieFragment.AntiCommutativity`** —
  surface the anti-commutativity law `[x, y] = -[y, x]` as an
  equivalence relation on LieExpr. Define `_≈ₐ_ : LieExpr → LieExpr
  → Set` capturing anti-commutativity at the equational level
  (Setoid-style). The first Lie axiom; D4 adds Jacobi.

- **D4 `Substrate.Invented.LieFragment.Jacobi`** — surface the
  Jacobi identity `[x, [y, z]] + [y, [z, x]] + [z, [x, y]] ≡ 0`
  via the same Setoid relation as D3. Combined with D3, this
  gives the full Lie-algebra equational quotient on LieExpr.
  Discharges the "fuller treatment" deferred at C7.

- **D5 `Substrate.Solresol.FreeLinearTransposition`** — promote
  Solresol's `transpose-word` (pointwise transposition by 1
  semitone) to a FreeLinearization-lifted operation: the
  basis-action `Note → Note` extends uniquely to a
  word-transformer `SolresolWord → SolresolWord` via the
  free-monoid universal property (since Word is the free monoid
  over the basis). Discharges the "transposition as universal
  lift" implicit obligation; demonstrates that the parent
  primitive applies here too.

### Phase 2 — Retroactive alignment (D6-D7)

- **D6 `Substrate.Lojban.AsCCC.RetroactiveNote`** — update the
  Lojban L10 AsCCC's "shared parent extraction deferred" prose
  to reference Substrate.Category.FreeOverBasis. Add a small
  alignment lemma showing the Lojban-OpcodeAlgebra IS the same
  shape as the Toki Pona-OpcodeAlgebra under the parent primitive's
  FreeOverBasis abstraction. Real Agda content (the alignment
  lemma), not just commentary.

- **D7 `Substrate.TokiPona.AsLinearBridge.RetroactiveNote`** —
  sister slice to D6 on the Toki Pona side. Updates the BridgeAlignment
  record's commentary to reference the now-existing FreeOverBasis +
  classification machinery, and adds a small alignment lemma
  showing the TokiPona-OpcodeAlgebra structurally aligns with
  Lojban-OpcodeAlgebra via the parent.

### Phase 3 — Unified closure + smoke + capstone (D8-D10)

- **D8 `Substrate.Linguistic.RetroactiveAlignment`** — the unified
  module: states the parent-primitive-supersedes-deferrals story
  as a single Agda record. Each witness gets a "the parent IS
  now extracted; the original deferral note is superseded" entry.
  Companion to D6 + D7's per-arc notes; D8 is the
  classification-arc-level summary.

- **D9 `Substrate.Linguistic.ClosureLog`** — a substrate-internal
  closure log: a Vec of records, each `(deferred-item-name,
  closure-slice-name, brief-description)` documenting what this
  D-arc closed. Substrate-native bookkeeping (not just a markdown
  file). Useful for future arcs that want to query "is X still
  deferred?"

- **D10 `Substrate.Linguistic.ClosureCapstone`** — top-level
  re-export + cross-arc regression module + capstone. Imports D1-D9,
  runs smoke tests demonstrating no regression on the existing
  Lojban / Toki Pona / Classification typechecks, and states the
  closure status as a Vec of refl-proved entries.

## Substrate primitives engaged

- Substrate.Category.FreeOverBasis (D1, D5, D6, D7, D8)
- Substrate.Category.FreeLinearization (D1, D5)
- Substrate.Algebra.F2.Linear (D1)
- Substrate.Category.OpcodeAlgebra (D6, D7)
- Existing Lojban / Toki Pona / Solresol / Kelen / Lie /
  Lambda fragments (everything closes against)

## Deferred (out of D-arc scope)

- Lambda Fragment's "explicit branching" deferral — substantial,
  needs its own follow-up arc (lambda terms as a richer carrier
  than Word over Combinator)
- Lojban SE/TE/VE conversion, attitudinals, MEX — would need a
  Lojban-Phase-2 arc
- Toki Pona's full ~120-word vocabulary expansion — mechanical
  but tedious
- Codec arc P/Z-arc tails (P1-P7, Z2-Z8) — separate effort
- MCP decomposition surface — out of linguistic-arc scope
- Bicategorification of Z/2 — separate arc

## Success criteria

1. All ten D-arc slices typecheck under `--safe --without-K`.
2. D1's bilinear-via-FreeLinearization construction discharges
   the T4 "WithBasisAction" stub.
3. D3 + D4 jointly state the Lie-algebra equational axioms as a
   Setoid on LieExpr.
4. D6 + D7 retroactive lemmas typecheck and reference the
   FreeOverBasis parent primitive.
5. D8's RetroactiveAlignment record is internally consistent
   (refl-provable).
6. D9's closure log lists all 10 closed items with their D-arc
   slice references.
7. D10's regression demonstrates no existing typechecks broke.

## Position in the 20-slice sprint

This D-arc precedes the Yoneda-lift arc Y1-Y10. After closure:
- The substrate's prose matches its current state.
- The deferred-obligation count is reduced from ~10 to ~3
  (substantive items requiring full follow-up arcs).
- The Yoneda lift builds on a clean foundation.

Total sprint: 20 slices (D1-D10 then Y1-Y10).
