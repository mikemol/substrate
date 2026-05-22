# Shadow Architecture — Agda Formalization Arc Plan

**Source document:** `scratch/shadow-architecture.md` (1605 lines, 10 increments,
trilingual rendering).

**Target:** typechecked `--safe --without-K` module hierarchy under
`Substrate.ShadowArchitecture.*` realizing the document's structural content
and tying into existing substrate primitives.

**Motivation:** precursor to the Raven artifact (which uses the
`L₇-añelē` = "pure-composite-diagonal deletion prohibition" terminal as
the "Nevermore" line-marker). Formalizing the architecture's structural
backbone in Agda lets the Raven translation be checked against the same
Fano-plane state-machine instead of taking the linguistic surface at
face value.

## Existing substrate machinery (reuse, do not reinvent)

- `Substrate.Algebra.F2` — F₂ field with case-enumeration axioms.
- `Substrate.Algebra.F2.Vector` — F₂ᴺ, basis, +, dot product (via
  `Substrate.Algebra.F2.Vector.DotProduct`).
- `Substrate.Algebra.F2.FanoPlane` — **named** Point/Line constructors
  (`e₁..e₁₂₃`, `L₁₂..L₁₂-₁₃`), `point-to-vec`, `line-points`, Singer
  cycle as order-7 GL(3,F₂) element.
- `Substrate.Geometry.Fano` — `Point = Fin 7` via Hamming H-cols,
  `Collinear-Three` predicate, 7 lines as `refl` proofs.
- `Substrate.Geometry.PG` — parametric PG(n, F₂), `|GL(3,F₂)| = 168`.
- `Substrate.Geometry.HodgeDim3.Fano` — Hamming H → Fano syndrome.
- `Substrate.Algebra.GL3F2.*` — Sylow decomposition (168 = 2³·3·7),
  full character table, MultiRouteEquivariance, Presented form.
- `Substrate.Algebra.PrimeFactor-168-FieldFanOut` — Z/168 as
  FieldFanOut 3 over (F₂³, F₃, F₇).
- `Substrate.Groups.F2Cubed` — F₂³ as Bool³, Singer ↔ Sylow-7.
- `Substrate.Algebra.F2.HodgeDim3.MetricGauge.S3Stabiliser` — S₃ as
  order-6 stabiliser of metric-id, 6 explicit elements via Coxeter.
- `Substrate.Category.FreeOverBasis` / `Substrate.Linguistic.*` —
  Lojban / TokiPona / Solresol / Kelen / Lambda as `LanguageWitness`
  instances; `RosettaTable` cross-language alignment.

## What's missing (the shadows)

- **Shadow A — Normal-vector map** (`Line → Point`, the self-duality).
- **Shadow B — Hamming weight** + S₃-orbit partition
  {wt-1, wt-2, wt-3=★fixed} on points; same partition on lines via
  the normal-vector map (duality preserves orbits).
- **Shadow C — Self-incidence detector** (`on-line : Point → Line → Set`).
- **Shadow D — Bit-pattern + sequential aliases** over the existing
  FanoPlane naming. The document uses `100..111` for points and `L₁..L₇`
  for lines; the substrate uses `e₁..e₁₂₃` and `L₁₂..L₁₂-₁₃`.
- **Shadow E — Mode-as-line-subset** (decomp / snap / regroup / guard
  as subsets of {L₁..L₇}) + coverage theorem.
- **Shadow F — Realizability 4-gate record** (Constructible / Reachable
  / Observable / Coverable) + the "persists via" time-extension column.
- **Shadow G — Architecture-loop AST** (Steps A-E with W1-W6 warnings).

## Slicing

### Slice 1 — Static Fano structure (THIS SESSION)

Increments 1-3 of the document. Five small modules, all `--safe`:

1. `Substrate.ShadowArchitecture.FanoLabeling` — bit-pattern point
   aliases (`p₁₀₀..p₁₁₁`) and sequential line aliases (`L₁..L₇`) over
   the existing FanoPlane naming. (Shadow D)
2. `Substrate.ShadowArchitecture.Duality` — `normal-vector : Line →
   Point`, with `refl`-proofs that the normal is F₂-orthogonal to each
   of the three points on its line (via existing DotProduct).
   (Shadow A + C foundation)
3. `Substrate.ShadowArchitecture.Weight` — `weight : Point → ℕ` (count
   of 𝟙 components); orbit predicates `wt₁`, `wt₂`, `wt₃`;
   `point-orbit : Point → Fin 3` decision; same on lines via normal-
   vector. (Shadow B)
4. `Substrate.ShadowArchitecture.SelfReference` — ★ load-bearing facts:
   `L₆-normal-is-110`, `L₇-normal-is-111`, `L₇-111-non-incident`,
   `S₃-fixed-pair-axiom`. (Shadow C completion)
5. `Substrate.ShadowArchitecture.AxisDualLine` — `axis-dual : Fin 3
   → Line`, with `refl`-proofs that the dual line consists exactly of
   signatures not on the given axis.

### Slice 2 — Mode-as-line-subset

Increment 6. One module + coverage theorem:

- `Substrate.ShadowArchitecture.Mode` — four named modes (decomp, snap,
  regroup, guard) as `Line → Bool` predicates. Coverage theorem: the
  union covers all 7 lines, with overlaps exactly at L₄ and L₅, and
  the guard's "full star" {L₂, L₃, L₆} = lines through 001.

### Slice 3 — Realizability charter + 6-distinction audit

Increments 8-9. Two modules:

- `Substrate.ShadowArchitecture.Charter` — `Realizability` record
  (4 fields: Constructible / Reachable / Observable / Coverable +
  optional `Persists-via`).
- `Substrate.ShadowArchitecture.Distinction` — the 6 audited rows
  (7 axis-sigs, 7 Fano-lines, guard response, e₁ adjunction,
  e₂ symmetric lens, L₆ reconstitution). Each row as a
  `Realizability` instance.

### Slice 4 — Symmetry frame (S₃ ⊂ PSL(2,7))

Increment 7. Bridges into existing GL3F2 infrastructure:

- `Substrate.ShadowArchitecture.S3-vs-PSL27` — re-export the existing
  S₃Stabiliser and PSL(2,7) machinery; state the 168/6 = 28-coset count;
  formalize the "reachable subgroup vs constructible group" distinction.

### Slice 5 — Architecture loop AST

Increment 5. One module:

- `Substrate.ShadowArchitecture.Loop` — Steps A-E as constructors;
  warning signs W1-W6 as attached failure-mode tags; characteristic-
  failure mapping; non-firing predicate (Increment 4 boundaries).

### Slice 6 — Time-extension / persistence (skeletal)

Increment 10. One module:

- `Substrate.ShadowArchitecture.Persistence` — the inversion claim
  ("the architecture is the cotype, not the conversation"); cotype as
  abstract type with monotonic-growth predicate; persistence-via column
  for each distinction.

## Out of scope (deferred)

- Trilingual renderings as Agda-checked language outputs. The
  `Substrate.Linguistic.*` machinery is the right substrate for this if
  ever needed, but the document's Lojban/Toki Pona/Kēlen prose isn't
  load-bearing for the structural claim and would be a separate arc.
- Formalizing the document's appendix (fibration audit matrix).
  Mechanical but not load-bearing.
- Operational hooks (the cotype file at `.claude/cotype/...`). That's
  an operational discipline, not an Agda fact.

## Charter check for the arc itself

- **Constructible:** each slice has named modules and proof obligations.
- **Reachable:** each module imports existing substrate primitives;
  no module depends on yet-to-be-built infrastructure.
- **Observable:** each module is typechecked under `--safe --without-K`.
- **Coverable:** the 6 slices cover the document's 10 increments
  (1-3→slice 1, 6→slice 2, 8-9→slice 3, 7→slice 4, 5→slice 5,
  10→slice 6); Increment 4 (firing conditions) folded into Slice 5.
