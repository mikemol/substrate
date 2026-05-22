# Algebra Ladder + Module-over-Ring tower (M-arc + Mod-arc) — 20-slice plan

The combined foundational arc producing the substrate's minimum-
surface algebraic infrastructure. Replaces and supersedes the
M-arc-only plan (m_arc_plan.md); covers the full M-arc + the
Module-over-Ring sibling tower that closes the visible-surface
vector/linear gaps.

## Why this arc

Per [[user-rosetta-code-contrastive-pedagogy]] applied to algebra:
the visible surface is currently a high-energy patchwork (each ℚ-
or F₂-law proven per-instance, each MonoidLaws record inlined per-
arc). The minimum surface is the unified tower where every visible-
surface law DERIVES from a single Field / Module instance.

This arc is purely COSTRUCTURE work: no new visible features, but
the existing visible surface collapses by ~60-70% (the audit's
deferred-list dissolves at the appropriate tower level).

Per the user's framing: "Foundational work is some of the most
valuable costructure-work we can do."

## Costructure shadows

- **Algebra ladder** (Magma → ... → Field): 8 records, each one
  axiom away from its parent
- **Module-over-Ring tower**: 5 records, parametric in the Ring
  (Field instance at the leaf)
- **F₁/F₂/ℚ leaf instances**: discharge laws once, inherit
  everywhere
- **Retrofit bridges**: existing FreeLinearizationR (FLQ-arc) and
  F₂.Vector / ℚ.Vector become Module-Hom instances

## Gap-closure mapping (full)

| Gap (from audit)                              | Closed at | How                                       |
|-----------------------------------------------|-----------|-------------------------------------------|
| ℚ-ring-laws (Q-arc deferreds)                 | M10       | Field-accessor projection                 |
| ℚ-vector +-identity (TPQ inherits)            | Mod6 + M10| FreeModule-accessor at ℚⁿ                |
| ℚ-bilinearity (modify-Q-prod)                 | M7 + Mod6 | Ring distrib at ℚ + FreeModule           |
| ℚ-linear-extensionality (FLQ7/TPQ7)           | Mod7      | ModuleHom-extensionality at ℚ-Module     |
| F₂-vector arithmetic (existing scattered)     | Mod5 + M9 | FreeModule-accessor at F₂ⁿ               |
| FreeLinearizationR universal property full    | Mod7 + Mod8 | Module-Hom universal property           |
| F₁ as base case                               | M3        | Trivial-Monoid `{*}` instance            |
| RuleAction operad assoc + identity            | M3        | Monoid laws (operad-as-monoid)           |
| GeneratorOperad right-identity                | M3        | Monoid right-identity                    |
| B-arc IsNatural respect-≈M                    | NOT       | Sibling Setoid tower                     |
| Conway addition / transitivity                | NOT       | Sibling game-induction tower             |

**~7 of 9 audit gaps close at this 20-slice arc.** Remaining two
need sibling towers (Setoid for naturality; surreal-game-induction
for Conway). Both can REFERENCE Ring (M7) once it exists.

## Twenty slices

Annealing discipline: one degree of freedom per slice.
[[feedback-file-size-one-pass-rewrite]]: one Write per file.
[[feedback-minimize-stdlib-deps]]: substrate-native records.

### Phase 1 — Magma → AbelianGroup (M1-M5)

- **M1 `Substrate.Algebra.Magma`** — `record Magma (A : Set) :
  Set` with `_·_ : A → A → A`. Universal generator.

- **M2 `Substrate.Algebra.Semigroup`** — Magma + `assoc : (a b c
  : A) → (a · b) · c ≡ a · (b · c)`.

- **M3 `Substrate.Algebra.Monoid`** — Semigroup + identity + two
  identity laws. **F₁ included as trivial Monoid `{*}`** —
  demonstrates the ladder accommodates the degenerate base case.

- **M4 `Substrate.Algebra.Group`** — Monoid + inverse function +
  inverse laws.

- **M5 `Substrate.Algebra.AbelianGroup`** — Group + comm.

### Phase 2 — Ring → Field (M6-M8)

- **M6 `Substrate.Algebra.Semiring`** — Additive CommMonoid +
  Multiplicative Monoid + distributivity + zero-absorbs.

- **M7 `Substrate.Algebra.Ring`** — Semiring with additive
  AbelianGroup (negation supplied).

- **M8 `Substrate.Algebra.Field`** — Ring + nonzero multiplicative
  inverse + inverse law.

### Phase 3 — Field instances (M9-M10)

- **M9 `Substrate.Algebra.F2.AsField`** — Substrate.Algebra.F2 +
  F2-CommutativeMonoid packaged as a Field instance. All F₂
  ring-laws become Field-accessor projections.

- **M10 `Substrate.Algebra.Q.AsField`** — Q-arc packaged as a
  Field instance. **Closes ℚ-ring-laws gap**: ring-+-comm,
  ring-+-assoc, ring-distrib, mul-inverse become field-accessors.
  Plus M-arc capstone.

### Phase 4 — Module ladder (Mod1-Mod5)

- **Mod1 `Substrate.Algebra.Module`** — record `Module (R : Ring)
  (M : Set)` with: AbelianGroup on M; scalar mult R × M → M;
  4 module axioms (distrib-over-scalar-sum, distrib-over-vector-
  sum, scalar-mult-assoc, identity-scalar).

- **Mod2 `Substrate.Algebra.Module.Hom`** — `record ModuleHom
  {R : Ring} (M N : Module R)`: function M → N preserving + and
  scalar mult.

- **Mod3 `Substrate.Algebra.Module.Hom.Compose`** — identity-Hom
  + Hom composition + category laws.

- **Mod4 `Substrate.Algebra.Module.Free`** — `FreeModule R n` =
  the canonical R-module of dimension n (carriers: Vec R n;
  componentwise ops). Module-instance witness.

- **Mod5 `Substrate.Algebra.Module.Free.Basis`** — basis-i :
  Fin n → FreeModule R n + universal property (any image map
  `Fin n → ModuleHom (FreeModule R n) M` lifts uniquely).

### Phase 5 — Module instances + bridges (Mod6-Mod10)

- **Mod6 `Substrate.Algebra.F2.AsModule`** — F₂-Vector as
  FreeModule over F₂-Field (M9). The existing
  Substrate.Algebra.F2.Vector + Substrate.Algebra.F2.Linear get
  retrofitted as Module + ModuleHom instance witnesses.

- **Mod7 `Substrate.Algebra.Q.AsModule`** — ℚ-Vector + ℚ-Linear
  as FreeModule + ModuleHom over ℚ-Field (M10). **Closes the
  ℚ-linear-extensionality gap**: the Mod5 universal-property
  field IS the lemma that was deferred at FLQ7 / TPQ7.

- **Mod8 `Substrate.Algebra.Module.Free.UniqueExtension`** — the
  generic linear-extensionality theorem: at any FreeModule R n
  with any ModuleHom target, two homs agreeing on basis are
  pointwise equal. Substrate-native proof (not per-R).

- **Mod9 `Substrate.Category.FreeLinearizationR.AsModule`** —
  bridge: the FLQ-arc's parametric FreeLinearizationR record IS
  a special case of FreeModule-Hom universal property. Retrofits
  FLQ's data + sketches as ModuleHom witnesses, completing the
  ℚ-FreeLinearBuilder via Mod8.

- **Mod10 `Substrate.Algebra.Module.Capstone`** — full capstone:
  re-export the tower + summary of gap closures + retroactive
  bridges (FLQ-arc, F₂-Vector ecosystem, Q-arc, TPQ-arc all
  become Module-tower instances).

## Substrate primitives engaged (retrofitted)

- Substrate.Algebra.F2 + F2-CommutativeMonoid + F2.Vector + F2.Linear
- Substrate.Algebra.Z + Substrate.Algebra.Q.*
- Substrate.Category.FreeLinearization + FreeLinearizationR
- Substrate.Lojban.WordAlgebra.MonoidLaws (inline → import M3)
- Substrate.Category.OpcodeAlgebra (will reference M3 for
  free-monoid-of-opcodes)
- Substrate.TokiPona.QModifierBilinear (becomes Module-bilinear)

## Success criteria

1. All 20 slices typecheck under `--safe --without-K`.
2. F₁ + F₂ + ℚ instantiate as Field at M3 / M9 / M10.
3. F₂-Vector + ℚ-Vector instantiate as FreeModule at Mod6 / Mod7.
4. ℚ-linear-extensionality discharged at Mod8 (closes the
   substrate's only true sketch gap from the audit).
5. FLQ-arc's QFreeLinearizationSketch retroactively closes via
   Mod9.
6. F₂.Vector's existing arithmetic lemmas become FreeModule-
   accessor projections (Mod6).
7. Mod10 demonstrates ≥5 currently-deferred laws becoming tower-
   projection accessors.

## Sibling towers (NOT this arc — staged for follow-up)

- **Setoid / Equivalence tower** (~5 slices): closes B-arc
  IsNatural respect-≈M + extension to NaturalTransformation
  Yoneda. Independent of Ring tower.
- **Game-induction tower** (~10 slices): closes Conway addition +
  transitivity. References birthday induction; independent of
  Ring tower (different shape).
- **F₁-modules-as-pointed-sets** (~5 slices): the deeper F₁
  semantics where `GL(n, F₁) = S_n` etc. Builds on M3's trivial-
  Monoid + Mod4's FreeModule shape.

All three sibling towers can reference Ring (M7) or Module
(Mod1) once this 20-slice arc lands. Each closes its corner of
the substrate's remaining surface.

## Surface-tension framing

The substrate's algebraic surface is currently under high tension
— each per-instance law proof is a local stretch. The minimum
surface is the unified two-tower architecture where:

- Visible-surface RING laws are Field-accessor projections (the
  whole Q-arc / F₂ ring-side dissolves into accessors)
- Visible-surface VECTOR/LINEAR laws are Module-accessor
  projections (F₂.Vector / ℚ.Vector / FreeLinearizationR all
  reduce to instance witnesses)
- F₁/F₂/ℚ/future-carriers are leaf instances; laws cascade

The 20 slices are exactly the SUPPORT STRUCTURE for that minimum
surface. Each slice is minimal: one new operation or one new law,
following the unidirectional waterfall.

After the arc:
- ~7 of 9 audit-flagged substrate gaps close
- 2 sibling towers can launch (Setoid, Conway) — each ~5-10 slices
- The substrate's algebraic + linear-algebraic codebase is
  structurally consistent with universal-algebra discipline
