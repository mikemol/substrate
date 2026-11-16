---
name: substrate-primitives-index
description: "Tree-organized index of the substrate's categorical primitives + group-theoretic objects + key patterns/disciplines. Survives context flushes; load when starting any substrate work to recall available tools. ~34 primitives across the categorical layer; ~20 sporadic groups (1 single descent tree after Z8) + many smaller algebraic objects."
metadata: 
  node_type: memory
  type: project
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Fact.** The substrate's accumulated infrastructure spans 34+ categorical primitives, 20+ concrete group instances (now packaged as a single descent-tree object), and many F₂-linear algebra + Hodge-specific modules. After multiple arcs and context flushes, future sessions may forget which tools are available. This index is the tree-organized reminder.

**Why:** Per the user's observation: "every context flush makes it likely we'll forget useful available tools." A consolidated tree index lets a fresh session know what exists without exploring the codebase.

**How to apply:** Load this memory at the start of any substrate work. Cross-reference module names here against the actual code (paths given below). When in doubt about whether something exists, scan this index first.

## Categorical primitive ladder (27 primitives in `Substrate.Category.*`)

### Original roadmap (#1-#6)

* `Coalgebra` — Endomap + FixedPoint + InvariantSubset; coalgebraic structure baseline.
* `Coalgebra.FiniteOrder` — HasOrder + iterate; FLT-for-dimensional-spaces.
* `Coalgebra.LagrangeOrder` — Action + HasLagrangeOrder.
* `Equalizer` — Equalizer-Of + IsEqualised.
* `Pullback` — Pullback-Of + Wide-Meet.
* `Adjunction` — unit/counit.
* `BeckChevalley` — BCSquare + cell + Compose + Horizontal + ComposeInstance.
* `FreeLinearization` + `.FromImages` — universal property of free F₂-modules.

### Strict2Monoid + GradedMonoid (#7-#8)

* `Strict2Monoid` + `FromCoxeter` + `DirectProduct`.
* `GradedMonoid` (ℕ-graded), `RGradedMonoid` (R-graded), `FromCoxeterHomomorphism`.
* `CommutativeMonoid` (canonical F₂ instance).

### Cone family (#9)

* `Cone` — apex + finite base + legs.
* `Cone.Product` / `Cone.FieldFilling` / `Cone.EdgeApex` / `Cone.WithMorphisms`.
* `Cone.EqualizerInstance` / `Cone.PullbackInstance` (+ `WithMorphisms` variants) — Cone subsumes Equalizer + Pullback.

### Bond / Field family (#10-#14)

* `FieldBond` — oriented inter-field bond.
* `MultiFieldBond` (`FieldTower`) — chain of fields.
* `FieldFanOut` — 1 source, n targets (CRT-style fan-out).
* `FieldContinuum` — 5th gauge class; discrete-to-continuum extension.

### Universal-property unification (#15-#19, from PFG arc)

* `SylowDecomposition` — primes + Sylow predicates + joint-generation; includes `InGenerated` inductive type.
* `PrimeFactoredGauge` — bundles GTorsor + SylowDecomposition; includes derived `atlas-decomposition` (= "extended Euclid for groups").
* `PresentedGroup` — group with custom ∼ equivalence (= no funext required).
* `ConjugationCoalgebra` — top-down primitive (group + conjugacy class structure).
* `GaloisAdjunction` — bridges PresentedGroup ↔ ConjugationCoalgebra.
* `GTorsor` — universal G-torsor (free transitive action).

### Joint-gen via presentation (Y-arc)

* `SylowDecomposition.FromWord` — the LOAD-BEARING lemma: Word → InGenerated chain.
* `PrimeFactoredGauge.FromPresented` — PresentedGroup → joint-gen pipeline.
* `PrimeFactoredGauge.MultiRouteEquivariance` — generic equivariance theorem.

### Continuum + Algebra (X-arc)

* `S1-Lift` / `S2-Lift` — discrete-to-continuum constructors.
* `ConjugationCoalgebra.WithCharacters` — character table extension.
* `ConjugationCoalgebra.CharacterOrthogonality` — orthogonality predicates.
* `CentralizerDescent` — recursive centralizer-of for Happy Family.
* `AbelianPFG` — PFG specialization for abelian groups.
* `CommutativeNonAssociativeAlgebra` — for Griess algebra.

### Grothendieck-closure remediation (Z-arc)

* `Morphism` (Z1) — generic morphism record (function + parametric Preserves predicate); foundational for every per-primitive morphism layer.
* `AutomorphismGroup` (Z2) — Aut(_) primitive; the structure-preserving bijection group. Closes the Monster identification gap.
* `GrothendieckConstruction` (Z3) — the ∫F total-category primitive (Fibration + base/fiber morphisms).
* `CentralizerDescent.Tree` (Z4) — recursive iteration of V1's single-step CentralizerDescent; full descent trees as single substrate objects.
* `CategoryOf` (Z5) — generic "category of substrate-primitive-X" enabler.
* `Cone.Morphism` (Z6) — first concrete morphism instance (cone-morphisms via Z1).
* `GTorsor.Morphism` (Z7) — second concrete morphism instance (G-equivariant maps via Z1).

## F₂-linear algebra (`Substrate.Algebra.F2.*`)

* `F2` — F₂ as data type (𝟘, 𝟙).
* `Vector` — Vec F₂ n + componentwise ops + basis.
* `Vector.Universal` — basis-decomp + sum.
* `Linear` — record bundling apply + linearity proofs; id-L + composition + preserves-𝟎.
* `Linear.Universal` — linear-extensionality (= "agree on basis ⇒ agree everywhere").
* `Linear.Bijection` — F₂-linear bijection record (forward + backward + 2-sided inverse).
* `Linear.FromImages` — `linear-from-images` (= free linearization at substrate sites).
* `Linear.FromImages.Permutation` — basis-permutation-Linear + HasOrder-from-perm + L-iterate + iterate-apply-as-L-iterate (KEY TOOLS for order-k Linear work).
* `Linear.FromImages.Permutation.Cycle3` / `Cycle4` / `Cycle5` — concrete cyclic permutations.
* `FromBool` — F₂ ↔ Bool bridge.
* `Polynomial` / `SymBilinForm` / `Universal` / `Transfer`.
* `Code` + `Code.Universal` — F₂-code infrastructure.
* `V4-Nonzero` / `V4LagrangeInstance`.
* `FanoPlane` — ℙ²(F₂) with 7 points, 7 lines, Singer 7-cycle, singer-Linear.

### Hodge-dimensional infrastructure (`...HodgeDim3.*`, `...HodgeDim4.*`)

* `HodgeDim4.Bivector` (= Vector 6) + `Bivector-F2Graded` (weight-parity).
* `HodgeDim4.HodgeStar` — ★ as basis-permutation-Linear.
* `HodgeDim4.HodgeStar-FreeLinearization` + `HodgeStar-ConeWithMorphisms`.
* `HodgeDim4.SelfDual` — SelfDual-Pred + sd-pair generators.
* `HodgeDim4.ReservedBridge` — vector3-to-selfdual.
* `HodgeDim4.ReservedBridgeAlternatives` — Alt-A (cyclic), Alt-B (swap).
* `HodgeDim4.ReservedBridge.GaugeTorsor` — 168 bridges as GL(3,F₂)-torsor.
* `HodgeDim4.ReservedBridge.AlternativesAsOrbit` — Alt-A/B as torsor orbit points.
* `HodgeDim4.ReservedBridge.SylowOrbitWitnesses` — 3 Sylow-canonical bridges.
* `HodgeDim4.ReservedBridge.AtlasCatalogue` — atlas hub.
* `HodgeDim4.ReservedBridge.AsPFG` — wraps as PrimeFactoredGauge.
* `HodgeDim4.HodgeStar.AsGaugeAction` — ★ acts trivially on torsor.
* `HodgeDim4.MetricGauge` (+ CoxeterRelations).
* `F2.Cone-V4-3plus1` / `F2.Cone-Hamming-7plus1` / `HodgeDim4.Cone-HodgeStar-EdgeApex` — Cone instances.

## Groups (`Substrate.Groups.*` + `Substrate.Algebra.GL3F2.*` + sporadic)

### Coxeter framework

* `Coxeter.Word` — abstract word type over alphabet.
* `Coxeter.Core` — normalize + canonical-is-fixed + normalize-distrib; abstract group ops.
* `Coxeter.ListPresentation` — instantiates Core with List Gen + insert.
* `Coxeter.DirectProduct` — Word₁ × Word₂.
* `Coxeter.GroupAdapter` — Coxeter → stdlib Group bundle.
* `Coxeter.SemidirectProductGroup` — N ⋊_φ H.

### Cyclic Coxeter instances

* `Z2-Coxeter` / `Z3-Coxeter` / `Z4-Coxeter` / `Z5-Coxeter` / `Z7-Coxeter` (each + `-Group` / `-Fin` / `-Strict2Monoid` variants for some).
* `FreeCyclic-Coxeter` (= ℕ as Coxeter monoid; cycle generator).
* `Zn-x-FreeCyclic` parametric + Z3/Z4/Z5 instantiations.
* `Zn-Coxeter-Strict2Monoid` parametric + instantiations.
* `ConsolidatedCyclicCoxeter` — catalog hub.
* `CyclicCoxeterStrict2Monoids` — strict-2-monoid hub.

### V₄ infrastructure

* `V4` (thin Coxeter-backed) + `V4-Coxeter` + `V4-Coxeter-Strict2Monoid`.
* `V4-Coxeter-F2Graded` + `-CountA` + `-CountB`.
* `V4-as-Z2xZ2` + `V4-Cosets` + `V4-Embedding` + `V4-Normality`.
* `F2Cubed` — F₂³ as Bool × Bool × Bool.

### Symmetric / semidirect

* `Symmetric` (Permutation Axis).
* `S3` (= Z₃ ⋊ Z₂ via SemidirectProductGroup).
* `S4` (= Permutation Axis) + `S4-Composed` (= V₄ ⋊ S₃) + `S4-Iso`.
* `Stab-S3-*` family.
* `Subgroup` / `SemidirectProduct`.
* `SFin` / `TwoDimWordAlgebra`.

### GL(3, F₂) ≅ PSL(2, 7)

* `Algebra.GL3F2` — record with two-sided inverse + composition + HasOrder convenience.
* `GL3F2.GaugeGenerators` — swap01-GL + cycle3-GL + singer-GL.
* `GL3F2.SingerOrder` — 8-case Vec enumeration of singer⁷ = id.
* `GL3F2.MultiRouteEquivariance` — joint-generation closure.
* `GL3F2.SylowDecomposition` — Sylow predicates + constructor.
* `GL3F2.JointGenScaffold` — pre-Y4 scaffold (mostly superseded by Y4).
* `GL3F2.AsPresented` — 3-generator data for Y-arc pipeline.
* `GL3F2.JointGenViaPresentation` — full discharge via word structure.
* `GL3F2.Characters` — 6×6 character table (4 of 6 cells ℤ-valued; 2 with α/ᾱ placeholders).

### Abelian (`Substrate.Algebra.Abelian.*`)

* `Z6-as-PFG` + `Z6JointGenViaProduct` (Z/6 = Z/2 × Z/3 CRT).
* `Z30-as-PFG` + `Z30JointGenViaProduct` (Z/30 = Z/2 × Z/3 × Z/5).
* `Z6-FieldBond` + `Z6-FieldTower` + `PrimeFactor-168-FieldFanOut`.

### Sporadic groups (`Substrate.Algebra.Sporadic.*`)

All as parametric ConjugationCoalgebra modules (carrier + ops + class data input):

* `Monster.AsCoalgebra` (T8; 194 classes) + `Monster.WithCharacters` + `Monster.AsPresented` + `Monster.AsGriessAlgebra` + `GriessAlgebra.Aut` (Z9, Monster as Aut(GriessAlgebra)).
* `BabyMonster` (184 classes).
* `Conway` — module with Co1 (101 classes), Co2 (60), Co3 (42).
* `MathieuFischer` — M11 (10), M12 (15), M22 (12), M23 (17), M24 (26), Fi22 (65), Fi23 (98), Fi24' (108).
* `HappyFamily` — re-export hub + HN (54), Th (48), He (33), J2 (21), HS (24), McL (24), Suz (43); 7 remaining HF members.
* `HappyFamily.JointGenViaDescent` — Y9 propagation template.
* `HappyFamily.AsTree` (Z8) — **20 HF members + 19 descent edges as a SINGLE substrate object** (parametric in per-node CCAs + descent witnesses).
* `GriessAlgebra` — 196,884-dim parametric.

**6 Pariahs NOT in substrate**: J₁, J₃, J₄, Ru, O'N, Ly.

## Capstones

* `Substrate.Category.PrimitivesAll` — single import-target for all categorical primitives.
* `Substrate.Category.PrimitiveInstances` — single import-target for all concrete instances.
* `Substrate.Category.PrimitivesAndInstances` — combined re-export.
* `Substrate.Category.PrimitivesRoadmapV2` — documentation of primitives #1-#14 + their roles.

## Patterns / disciplines (memories to consult)

The substrate's accumulated discipline (load these memories when relevant):

### Architectural

* [[universal-property-discipline]] — reach for universal properties before per-instance unfolding.
* [[categorical-name-first]] — check categorical naming before inventing substrate-local names.
* [[expose-generator-not-orbit]] — when code starts looking like N-case enumeration, expose the generator.
* [[composable-primitives-over-flat-enumeration]] — composable abstractions over flat listings.
* [[coalgebraic-not-consumer-driven]] — substrate is built coalgebraically.
* [[continuous-via-discrete-inference-rules]] — formalize the constructor, not the continuous content.
* [[homology-cohomology-recursion]] — observed = homology, cataloged = cohomology, recursive.

### Group-theoretic

* [[roll-our-own-via-word-algebra]] — "stdlib too heavy" ≠ "blocked"; Coxeter Word handles most cases.
* [[prefer-coxeter-backed]] — Coxeter-backed > Permutation-on-Fin / matrix carriers (perf + scale).
* [[v4-typeclass-architecture]] — V₄ and finitely-presented small groups via Coxeter framework.
* [[minimize-stdlib-deps]] — basic stdlib OK; avoid Data.Fin.Permutation, Data.Nat.DivMod, deep ecosystems.

### Process

* [[annealing-methodology]] — anneal, don't leap; one DOF per step, monotonic asymmetry decrease.
* [[dbe-failure-rule-and-inline-format]] — every second failure triggers DBE.
* [[file-size-one-pass-rewrite]] — files should fit in one Write call; decompose via submodule + re-export.
* [[substrate-memory-file-format]] — YAML frontmatter only, no H1; MD041 ignored.
* [[voice-prompts-via-spd-say]] — spd-say at genuine pause points.
* [[reject-lem-in-substrate]] — intuitionistic; ¬P needs P ⊢ ⊥.
* [[choice-rigidification-in-substrate]] / [[agreement-without-yielding]] / [[negative-findings-in-corpus]] — anti-patterns.

### Structural-content

* [[multi-route-equivariance-recovery]] — atlas-of-charts via simple-group generation.
* [[prime-factored-gauge-arc]] — the unifying primitive arc memo.
* [[q1-q5-entailment-chain]] — derivation of the PFG arc.
* [[3plus1-parity-universal]] — every 2-dim F₂-subspace gives 3:1 ratio.
* [[reserved-selfdual-bijection-gauge]] — 168 gauge family (operationally subsumed by PFG).
* [[klein-quartic-kinematic-anatomy]] — Sylow targets of GL(3, F₂) ≅ PSL(2, 7).
* [[kinematic-gauge-sacrifice-catalog]] — 16+ CV joints across 3 Sylow targets.
* [[continuous-limit-lift-framework]] — discrete-to-continuum Lie-group framing.

## Top-3 most-useful tools by use-case

When you need to...
1. **Lift an order-k permutation to a linear map**: `Linear.FromImages.Permutation` (basis-permutation-Linear + HasOrder-from-perm).
2. **Discharge joint-gen for any group**: `SylowDecomposition.FromWord` (Y1) — joint-gen IS word structure.
3. **Add a sporadic group**: copy the `Monster.AsCoalgebra` pattern (parametric ConjugationCoalgebra module).

When you build a new group:
1. **Cyclic Z/n**: copy `Z7-Coxeter` pattern + `Coxeter.ListPresentation`.
2. **Semidirect product**: `Coxeter.SemidirectProductGroup` combinator (see S3, S4-Composed).
3. **Generic presented group (no normal form)**: `PresentedGroup` (T2) with custom ∼.

When you reach for equivariance:
1. **Single-group at a torsor**: `GTorsor` (T2) + your group's action.
2. **Multi-prime joint equivariance**: `PrimeFactoredGauge` (T1) + `SylowDecomposition` + `MultiRouteEquivariance`.
3. **Bottom-up + top-down both available**: `GaloisAdjunction` (T4).

When you reach for morphisms between primitive instances (Z-arc):
1. **Generic morphism record**: `Morphism` (Z1) — parametric in Preserves predicate; build per-primitive morphism layer by supplying Preserves.
2. **Aut(X) of any structure**: `AutomorphismGroup` (Z2) — gives the structure-preserving bijection group; Monster ≅ Aut(GriessAlgebra) is the canonical extreme instance (Z9).
3. **Recursive descent / Grothendieck construction**: `CentralizerDescent.Tree` (Z4) for descent hierarchies (HappyFamily Z8); `GrothendieckConstruction` (Z3) for fibered categories.

## Maintenance

When new primitives land, add a line to the relevant section above. Keep the tree shallow (≤3 levels). Cross-references to memories live in [[link]] form.
