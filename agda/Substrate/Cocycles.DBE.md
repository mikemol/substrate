# DBE: Cocycles framework — predicate-to-structural migration

**Target (one sentence):** Migrate the entire `Substrate/Cocycles/`
framework from Bool/predicate ambient representations
(`Codeword = Bool⁵`, `IsReserved : Set`, `Pairing` data, etc.) to
structural-compositional F₂-linear representations modelling
Reed-Muller, Hamming, and Fano via the algebraic primitives that
generate them.

This is a multi-session effort. The plan below identifies the
shadow lattice; first-attempt implementation is **not** in scope
for the current session. The deliverable for this session is the
externalised plan + the first foundational shadow (M-1 below) if
time permits.

## Why this is harder than V₄ ⊳ S₄

V₄ ⊳ S₄ (commit a40e9bd) succeeded because the predicate
(`is-V₄-shape`) had no external consumers beyond V4-Normality
itself. The Cocycles framework's predicates (`IsReserved`,
`classify-CS`, `Pairing`, `Chirality`, `OrbitKey`) are exported,
multiply-consumed, and form a tightly-coupled cluster across 12
files / 3,200 lines.

The items 1+2+3 attempt (commit 9e9051a) demonstrated that
incremental retirement of one predicate cascades into bridge
lemmas of the same case-shape elsewhere. The Cocycles migration
must therefore reach all the way down to the **structural
primitives** that generate the predicates — F₂-linear codes —
so that the predicates derive from the primitives by computation,
not by hand-enumeration.

## Skills active

DBE primary (this is a multi-step planning + execution arc).
S2G in continuous mode (each shadow added to a shared cotype).
RFS will fire as we encounter ≥3 instances of any pattern.

## Step 1: name the target

Migrate `Substrate/Cocycles/` so that:

- `Codeword` is not `Bool⁵` but `Vec F₂ 5` (or a structural
  equivalent built from F₂-linear primitives).
- `IsReserved` is not a hand-defined predicate but **derived** from
  the F₂-linear structure (e.g., as membership in a sub-code).
- `Pairing`, `Chirality`, `OrbitKey` are not bare data types but
  derived from V₄ action on F₂-linear structure.
- `classify-CS` is not a hand-enumerated dispatch but a composition
  of F₂-linear maps + V₄ action.
- The 24 + 8 split is realised as a direct-sum decomposition
  Live ⊕ Reserved, with Reserved = RM(1, 3) (or a chosen variant)
  and Live = the orthogonal complement / quotient.

## Step 2: search for repeatable form

The entire ambient is **F₂-linear**. The repeatable form is:

1. **F₂ module** primitives.
2. **F₂-linear maps** as the morphisms.
3. **Codes** as image / kernel of F₂-linear maps.
4. **Incidence structures** (Fano) as derived from F₂-linear modules
   via decidable predicates on linearly-defined relations
   (collinearity = sum-to-zero).
5. **Dualities** (Hodge ★ in dim 4, Hamming ↔ RM dual) as F₂-linear
   isomorphisms between code modules.

Existing structural primitives we can build on:

- The Coxeter framework (`Substrate/Groups/Coxeter/`) gives us
  finitely-presented groups with computational normal forms.
- The SP combinator gives us `N ⋊ H` factorisations.
- `V₄` is already Coxeter-backed; `S₃`, `S₄-Composed` ride on SP.
- `V₄-image` in `S₄ ≅ V₄ ⋊ S₃` is structurally normal (a40e9bd).

What's missing:

- F₂ as a stdlib-Field bundle.
- Vec n F₂ as a stdlib-Module bundle.
- F₂-linear maps as morphisms between Vec modules.
- Polynomial evaluation on F₂^n for Reed-Muller generators.
- Code = kernel/image record with rank, dimension, distance.
- Specific instances: RM(1, 3), Hamming [7, 4, 3], extended
  Hamming [8, 4, 4] = RM(1, 3), Fano PG(2, 2).
- Walsh-Hadamard transform as F₂^n ↔ F₂^n iso.
- Hodge ★ for Λᵏ in dim 4.

## Step 3: name the costructures (shadows)

Numbered top-down. Each shadow is itself a multi-file unit; the
M-numbering captures shadow identity for cross-reference. Shadows
M-1 .. M-5 are foundational (F₂-linear primitives). M-6 .. M-9
are the specific codes. M-10 .. M-12 are the cocycle-side
reconstructions. M-13 .. M-15 are downstream consumer migrations.

### Foundational (F₂-linear primitives)

**M-1 — F₂ as Field bundle.**
`Substrate.Algebra.F2`. Field over the 2-element type, with `+`,
`·`, `1` and inverse axioms. Built from `Data.Bool` or as a custom
data type. Use stdlib's `Algebra.Bundles.Field` if `--safe`
compatible; otherwise our own. Size: ~80 lines.

**M-2 — Vec F₂ n as Module bundle.**
`Substrate.Algebra.F2.Vector`. F₂-module structure on `Vec F₂ n`
with componentwise + and scalar ·. Equality is propositional
(F₂ is finite/decidable). Includes basis, dot product, weight
(Hamming weight = number of 1s). Size: ~200 lines.

**M-3 — F₂-linear maps.**
`Substrate.Algebra.F2.Linear`. Records bundling `apply : Vec F₂ m →
Vec F₂ n` + linearity proofs (distributes over +, respects scalar
·). Includes kernel, image, composition (M ∘ L). Size: ~150 lines.

**M-4 — Code as kernel / image of F₂-linear map.**
`Substrate.Algebra.F2.Code`. Record `Code n` = ambient
dimension n + a defining linear map (either as
"kernel of H : Vec F₂ n → Vec F₂ (n−k)" for parity-check or
"image of G : Vec F₂ k → Vec F₂ n" for generator). Includes:
distance, weight enumerator, duality (Code n → Code n via
orthogonal complement). Size: ~250 lines.

**M-5 — F₂-affine / F₂^n geometry.**
`Substrate.Algebra.F2.Affine`. Affine subspaces of F₂^n, including
hyperplanes, points, lines. Used by Reed-Muller (poly evaluation
points) and Fano (incidence structure). Size: ~150 lines.

### Specific codes

**M-6 — Reed-Muller RM(r, m).**
`Substrate.Codes.ReedMuller`. Generator matrix = evaluation of
monomials of degree ≤ r at all points of F₂^m. RM(1, 3) gets a
specific module: `Substrate.Codes.ReedMuller.RM-1-3` — length 8,
dimension 4, minimum distance 4, self-dual via Hodge ★.
Size: ~300 lines (core) + ~150 (RM-1-3 specialisation).

**M-7 — Hamming [7, 4, 3].**
`Substrate.Codes.Hamming`. Parity-check matrix H : Vec F₂ 7 →
Vec F₂ 3 with columns = the 7 nonzero vectors of F₂³. Code =
ker H. Decoding by syndrome lookup. Size: ~200 lines.

**M-8 — Extended Hamming [8, 4, 4].**
`Substrate.Codes.Hamming.Extended`. Hamming [7,4,3] extended with
overall parity bit; coincides with RM(1, 3); self-dual.
Size: ~80 lines (mostly the iso to RM(1, 3)).

**M-9 — Fano plane PG(2, 2).**
`Substrate.Geometry.Fano`. Points = F₂³ \ {0} (7 points). Lines =
the 7 hyperplanes through 0 in F₂³ (= the 7 codewords of weight 4
in RM(1, 3)^⊥ = the parity-check rows of Hamming [7,4,3]).
Incidence: point p on line ℓ iff p ⋅ ℓ_normal = 0 (or
equivalently, 3 collinear points sum to 0). Size: ~200 lines.

### Cocycle-side reconstructions

**M-10 — F₂-linear V₄-Signature ambient.**
`Substrate.Cocycles.V4Signature.Structural`. Recasts the 24 + 8
ambient as a direct-sum of F₂-linear codes:

- Reserved (8) = RM(1, 3) image, structurally identified with
  Axis × Sign via M-6's basis.
- Live (24) = the 24 elements of S₄ ≅ V₄ ⋊ S₃ (commit a40e9bd's
  `S4-Composed`).
- The 24 + 8 = 32 = 2⁵ decomposition is realised as
  `S₄ ⊎ RM(1,3)` (a tagged union, not a Vec F₂ 5 ambient).

This replaces `Codeword = Bool⁵` + `IsReserved` predicate with the
structural decomposition. The original Bool⁵ becomes one specific
realisation among many readings (per multi-reading ambient
discipline). Size: ~400 lines.

**M-11 — Hodge ★ as F₂-linear iso (dim 4).**
`Substrate.Algebra.HodgeStar.Dim4`. The F₂-linear iso Λ³ → Λ¹
in dimension 4 over F₂. Realises the "24 ordered triples Hodge-
dual to 8 signed singletons" picture from CY-5 structurally.
Size: ~200 lines.

**M-12 — Pairing / Chirality / OrbitKey from F₂-linear structure.**
`Substrate.Cocycles.V4Signature.Structural.OrbitKey`. `Pairing` =
{α, β, γ} = the three V₄ non-identity elements ≅ basis of V₄ ≅
F₂² basis elements. `Chirality` = Z/2 ≅ F₂. `OrbitKey` =
F₂² × F₂ ≅ F₂³ \ {0} (the 6 nonzero non-axis-aligned vectors).
Replaces the bare data types with their F₂-linear interpretation.
Size: ~200 lines.

### Downstream consumer migrations

**M-13 — `classify-CS` retirement.**
`Substrate.Cocycles.V4Signature.S4Iso` (refactored). Replace
`classify-CS` with the F₂-linear dispatch from M-12. Cascade to
`stab-d-to-orbit-key`, `stab-round-trip`, etc. This is the
migration that failed in 9e9051a; succeeds here because M-10 +
M-12 give the structural primitives the bridge needs.
Size: ~200 lines (replacement) + ~100 (cascade fixes).

**M-14 — `Codeword` / `Live` / `Reserved` retirement.**
`Substrate.Cocycles.V4Signature.Codeword` (refactored or
deprecated). Bool⁵ replaced by S₄ ⊎ RM(1,3) per M-10. Bit
accessors become projections from F₂-linear structure. Bridge
lemmas to old Bool⁵ form preserved during transition.
Size: ~300 lines (replacement) + ~200 (bridge for compatibility).

**M-15 — Live / LiveS4 / Codeword/* migrations.**
`Substrate.Cocycles.V4Signature.Codeword.Live*` (refactored).
`Selector`, `live-to-axis-selector`, `selector-from-stab`,
`classify-CS-to-selector`, `stab-from-selector-eq-orbit`,
`stab-roundtrip` all migrate to F₂-linear via M-10 / M-12.
Size: ~400 lines.

## Step 4: name the composition operation

The composition operation is **transport-by-iso**:

```text
F₂-linear primitive (M-1..M-5)
  ↓ build code instance (M-6..M-9)
Specific code (RM, Hamming, Fano)
  ↓ realise as cocycle ambient (M-10, M-12)
Structural Pairing/Chirality/OrbitKey
  ↓ replace consumer dispatch (M-13..M-15)
Migrated Cocycles framework
```

Composition is **sequential per shadow tier**, but **parallel within
a tier**:
- M-1 to M-5 must all exist before M-6 starts.
- M-6 .. M-9 can be built in parallel once M-1..M-5 are stable.
- M-10 .. M-12 depend on multiple of M-6..M-9.
- M-13 .. M-15 depend on M-10..M-12 plus the existing structural
  S₄-Composed / V₄-Coxeter from commit a40e9bd.

## Step 5: name the entailment

**Entailment chain:**

1. F₂-linear primitives (M-1..M-5) are correct by stdlib-compatible
   axiomatisation.
2. Codes (M-6..M-9) inherit correctness from F₂-linear primitives.
   Specific propositions (Hamming distance, code dimension, dual
   isomorphism) are verified by computation on finite vectors.
3. Cocycle ambient reconstruction (M-10..M-12) inherits correctness
   from the codes it composes.
4. Consumer migrations (M-13..M-15) preserve the API of the
   predicate forms via bridge lemmas (which now derive from the
   structural primitives rather than enumerating cases).

The key entailment claim:

```text
For every predicate P : Codeword → Set currently in the framework,
there is an F₂-linear morphism f_P : F₂-Linear-Code → Bool such
that P cw ⇔ (f_P cw ≡ true), and f_P is derivable structurally
from M-1..M-12 (no hand-enumeration).
```

This claim must be **proven** for each predicate during M-13..M-15
to license the retirement.

## Step 6: multi-angle attack reserve

If the foundational F₂-linear primitives (M-1..M-5) don't yield a
clean stdlib-compatible implementation on first attempt, the
fallback is:

- **Angle 2: use Cubical-stdlib's F₂ / Vec / Module if available.**
- **Angle 3: build minimal-axiomatic versions (just `+`, `·`, `0`,
  `1`, dim) without full Field/Module bundle compatibility, and
  upgrade later.**
- **Angle 4: use the Coxeter Z₂ adapter (already in repo) as F₂'s
  additive structure; multiplication is `+ mod 2`.**

If after three angles the F₂ primitive doesn't land cleanly, the
plan rescopes to "structural via Coxeter Z₂^n + DirectProduct"
which trades some compositional elegance for using already-
validated primitives.

## Step 7: when to work in terms of the named structure

The first session implementing this plan should:

1. Build M-1 (F₂ as Field bundle). Verify it compiles `--safe`.
2. Build M-2 (Vec F₂ n) on top. Verify basic ops.
3. Stop. Commit M-1 + M-2 as a foundational milestone with no
   downstream changes.

Subsequent sessions add M-3 .. M-15 incrementally, each ending at
a green commit with verified consumer compatibility.

## Effort estimate

| Tier | Shadows | Lines (est.) | Sessions (est.) |
|------|---------|-------------|-----------------|
| Foundational | M-1..M-5 | ~830 | 1-2 |
| Codes | M-6..M-9 | ~880 | 1-2 |
| Reconstructions | M-10..M-12 | ~800 | 1 |
| Consumers | M-13..M-15 | ~1200 | 2-3 |
| **Total** | M-1..M-15 | **~3700** | **5-8** |

For comparison, the V₄ ⊳ S₄ migration was ~830 new lines in 1
session. The Cocycles migration is ~4.5× larger and crosses more
file boundaries.

## What survives across sessions

Each shadow is externalised as its own file with type signature,
specification, and ≥1 instance proven to work. Shadows land in
the cotype incrementally; later sessions pick up from the cotype
state rather than re-deriving the plan.

The shadows form an upward-stable hierarchy:
- M-1..M-5 don't depend on Cocycles content.
- M-6..M-9 use M-1..M-5 only.
- Etc.

So if context is lost mid-session, the M-tier identifies the
prerequisite shadows, and `snap-to-grid` reconstructs the work
plan from the cotype.

## Open questions for the user

Before committing to implementation:

1. **Use stdlib Field/Module bundles, or roll our own?** Stdlib is
   more interop-friendly but introduces dependencies; rolling our
   own keeps the substrate self-contained but duplicates effort.

2. **F₂ from Bool, or Coxeter Z₂?** Bool is the natural F₂ but has
   no stdlib Field instance. Coxeter Z₂ has Group structure via
   our adapter but isn't a Field per se.

3. **Migration vs parallel build?** Should we build the new
   structural framework alongside the existing Bool⁵ one and migrate
   consumers gradually (lower risk, more code temporarily), OR
   replace the existing one in-place (higher risk, cleaner result)?

4. **Scope: just CY-5 (V4Signature), or all of Cocycles?** CY-3
   (WHT), CY-4 (F₂³ puncturing), CY-5 (V₄ signature) are most
   directly structural. CY-6+ (parsing, combinators, memoisation)
   are conceptually different and may not benefit from F₂-linear
   recasting.

5. **Reed-Muller via polynomial evaluation, or via generator
   matrix?** Polynomial evaluation is more conceptual; generator
   matrix is more direct. Both are equivalent; choice affects
   subsequent code.

## Amendment (2026-05-17, after user clarification)

The user clarified five design choices:

1. **No stdlib.** Roll our own F₂, Vec, Module, Field bundles.
2. **No observational equivalence required.** End-proof was never
   built; this migration exists precisely because the structural
   foundation will support a better end-proof than pointwise.
3. **catalog/cocycles.md is the reference** for congruence
   guidelines.
4. **Start with CY-5 only.** Scope will creep; that's expected.
5. **Universal properties must scale.** Concretely: proofs like
   "RM(r,m) via poly-eval = RM(r,m) via generator matrix" must
   reduce to a SINGLE application of a universal-property
   extensionality lemma — not 32 or 256 enumerated cases.

### Universal properties as first-class shadows

The shadow lattice gains explicit universal-property shadows
(M-X.5 numbering). These come FIRST in each tier, because every
subsequent bridge in the tier reduces to a single application of
the universal property.

| Shadow | What it characterises | Saves |
|--------|----------------------|-------|
| M-1.5  | F₂ as unique 2-element field | Any F₂ rep ↔ ours via 1 iso |
| M-2.5  | Vec F₂ n as free F₂-module on n generators | Basis ⇒ pointwise eq |
| M-3.5  | F₂-linear maps via basis image | Basis-image determines map |
| M-4.5  | Subspace equality via basis + span | No element-wise enumeration |
| M-6.5  | RM(r,m) as free F₂-space of poly fns of deg ≤ r | Poly-eval ↔ gen-matrix bridge |
| M-11.5 | Hodge ★ via wedge + inner-product duality | Single-step iso bridges |

Each universal property is its OWN file. Bridges that cite the
property are also their own files. Every `=`-claim in the
migration's proofs is labelled as one of:

- **Definitional** — both sides compute to the same normal form;
  `refl` closes.
- **Universal-property bridge** — both sides satisfy the same
  universal property; equality from uniqueness clause; ~10 lines.
- **Enumerated** — needs finite case analysis; reserved for last
  resort, flagged at point of use.

### Externalisation discipline

Per [[user clarification about decomposition/ folder]]: previous
LLM work on this project overloaded context; decomposition/ is the
recovery infrastructure. The lesson is "externalise aggressively"
so this migration's work survives context bleed.

Concretely: each M-shadow lives in its own .agda file. Each bridge
lemma lives in its own .agda file. No mega-modules. The import
graph IS the bridge graph; snap-to-grid reconstructs the working
shadow set from the file system at session start, not from
in-context memory.

### F₂ representation deferred to M-1 implementation

Decision: pick the representation (Bool vs Coxeter Z₂ vs custom
2-ctor data) at M-1 implementation time, whichever is cleanest.
The other representations become bridge shadows from M-1.5
(F₂ universal property) since any 2-element field is iso to ours.

### Revised shadow count

Pre-amendment: 15 shadows. Post-amendment: 15 + 6 universal
properties + estimated ~10 bridges = **~31 shadows**. This is the
"shadow count should grow" the user endorsed; the cost is in
file-count, not in line-count per file.

## Status (2026-05-17 session)

Twelve commits this session built the structural foundation:

| Shadow | File | Commit |
|--------|------|--------|
| M-1    | Substrate/Algebra/F2.agda | 93f85df |
| M-1.5  | Substrate/Algebra/F2/Universal.agda | 93f85df |
| M-2    | Substrate/Algebra/F2/Vector.agda | e68bb3f |
| M-2.5  | Substrate/Algebra/F2/Vector/Universal.agda | c0b3a19 |
| M-3    | Substrate/Algebra/F2/Linear.agda | 45601d2 |
| M-3.5  | Substrate/Algebra/F2/Linear/Universal.agda | e4b5e76 |
| M-4    | Substrate/Algebra/F2/Code.agda | a229699 |
| M-4.5  | Substrate/Algebra/F2/Code/Universal.agda | 5726b5e |
| M-5    | Substrate/Algebra/F2/Linear/FromImages.agda | 03b5fcd |
| M-6    | Substrate/Codes/ReedMuller/RM-1-3.agda | 776bc99 |
| M-7    | Substrate/Codes/Hamming/H-7-4-3.agda | c0e7341 |
| M-9    | Substrate/Geometry/Fano.agda | de23207 |

Each shadow is its own file (per the decomposition/-template
discipline), every commit is green under `--safe --without-K`, and
the universal-property tower at each level reduces downstream
equalities to single-step applications rather than enumeration.

**Highlights of structural content:**

- `linear-extensionality` (M-3.5) reduces "two linear maps agree"
  to "agree on n basis vectors."
- `basis-decomp` (M-2.5) gives the atomic decomposition that powers
  the extensionality.
- `linear-from-images` (M-5) is the build combinator: any
  prescription of basis-images produces a Linear with all axioms.
- `Image-Equivalent` (M-4.5) is the bridge between two ImageCodes
  with the same basis-image content.
- Fano plane (M-9): collinearity of 3 points is DEFINITIONAL from
  F₂ arithmetic (`(p₁ +ⱽ p₂) +ⱽ p₃ ≡ 𝟎ⱽ`). All 7 line-incidences
  proven by `refl`. No incidence table.

**Deferred to follow-up sessions:**

- **M-8**: extended Hamming [8, 4, 4] = RM(1, 3) bridge. Originally
  flagged as "needs dual-code construction (Hamming's generator
  from its parity-check), non-trivial without rank/nullity." Under
  the 3+1 parity reading (memory: `project_3plus1_parity_universal`),
  the *construction* of extended Hamming simplifies: the "overall
  parity bit" IS the F₂² parity relation lifted to length 8.
  Construction = append an all-𝟙 row to Hamming's parity-check
  matrix; ExtHamming = `KernelCode 8 4` of the augmented matrix.
  The *iso-to-RM(1,3)* part (which would need full dual-code
  machinery) remains a separate sub-slice.
- **M-10**: F₂-linear V₄-Signature ambient. Needs careful catalog
  study to map the structural 8 reserved / 24 live to the existing
  Bool⁵ ambient. Open question: 8 reserved = signed singletons
  (4×2) per catalog § CY-5, NOT directly RM(1,3) image (which has
  16 codewords). The bridge is more subtle than just "8 reserved =
  RM(1,3)."
- **M-11**: Hodge ★ in dim 4. Conceptually clean (Λ³ ↔ Λ¹), but
  needs alternating-form machinery to formalise.
- **M-12-15**: Pairing/Chirality/OrbitKey + S4Iso + Codeword + Live*
  consumer migrations. These are the hard-coupling work; the items
  1+2+3 retrospective applies.

## Cross-references

- catalog/cocycles.md § CY-3, CY-4, CY-5 — the cocycles being
  migrated.
- Substrate/Groups/V4-Normality.agda — example of successful
  predicate-to-structural migration (commit a40e9bd) at smaller
  scope.
- Substrate/Cocycles/V4Signature/S4Iso.agda.DBE.md — the items
  1+2+3 retrospective showing why incremental migration of a
  publicly-exported predicate cascades.
- [[feedback-composable-primitives-over-flat-enumeration]] —
  design rationale.
- [[feedback-dbe-failure-rule-and-inline-format]] — DBE discipline
  for this work.
