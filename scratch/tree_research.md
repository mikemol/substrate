# Witness-tower + rig-tree research map (2026-07-12)

Compaction-safe synthesis of the 4-agent research sweep. **Rig-internal map = PENDING (agent 4).**

## 1. Witness-tower CORE (agda/Substrate/WitnessTower/*.agda — 48 top-level modules)

**Trunk (the Sₙ enumeration spine):** `Enumerate` → `IsPermutation` → `Decompose`.
- `Enumerate` (THE root, in-deg ≈18): `Perm n = Vec (Fin n) n`; `insert-at p σ = p ∷ map (punchIn p) σ` (the witnessing-insertion move); `perms`, `all-positions`, `mapL`.
- `IsPermutation` (soundness gate): `IsPerm v = (i j) → lookup v i ≡ lookup v j → i≡j` (= apply injective); `insert-at-preserves`.
- `Decompose` (the inverse move): `decompose : (σ) IsPerm σ → Σ p σ'. σ ≡ insert-at p σ'`; `lookup-ext`.
- Bricks on the trunk: `Complete` (perms-complete), `DuplicateFree` (|Sₙ|=n!, `insert-at-inj`), `Surjective` (`perm-surjective`).
- Capstones: `SnGroup` (`apply=lookup`, `apply-compose/id/injective`, `compose-id-*`), `Sn` (Fin(n!)≅Sₙ), `SymBridge` (record iso to `Groups.Symmetric (Fin n)` — `to-Sym`/`from-Sym`, group hom).
- Companion: `LehmerPath` (`start`/`_◂_`; `decode (l◂p)=insert-at p (decode l)`; `encode`; `decode-encode`/`encode-decode` = the {σ∣IsPerm}≅LehmerPath iso). `FirstAppearance` actually DEFINES `id-perm`/`compose`/`moved-count`/`is-involution` (+ cycle census).
**Cluster B (census/grading):** CycleType, KleinCensus, B3Split, SupportGrading, V4Grounding, CyclicGrounding (`pow`=word gᵏ, `pow-hom`), CyclicCollapse.
**Primitive spine + geometry:** `Core` (`WSimplex`/`Path`/`witnessing` — the abstract root the 3 tower-reductions decorate), FaceSet (`Face`, `★`=Hodge dual = wedge residue, `★-involution`), FaceCount (Pascal), Hodge (`dual-grade` k↦n−k), WedgeStep, SimplicialBoundary (`delAt`, ∂∘∂=0), PhiMultiplicity (`mult2`), Puncture, Link, WholeTower (S₄=V₄⋊(Z₃⋊Z₂)), AlgebraLadder.
**EEA/ℚ:** EEATower (ℚ of the witnessing step), EEAFoldTable (`digits-is-catamorphism`), EEAUnitBezout, CofreeDual (ana/terminal-coalgebra dual).
**M40 (A₄×ℤ₂ seam):** M40Closure/Action/Iso/Contrast/NoIso/Gauge/Group/Groupoid.

## 2. Witness-tower IMPORT NEIGHBORHOOD

**(A) External consumers — strikingly FEW (only 10 modules outside WitnessTower/):**
- `Category/UniversalProperty/` (8): Extrude{CoEmitGraded,DecodeNerve,NerveDegeneracy,NerveIdentities,SKIFVector,SKIKFaces,SKITernaryAtom} — use `SimplicialBoundary.delAt/simplicial`, `FaceSet.Face/with-apex`, `Hodge.dual-grade₃`, `Wedge.V4Seam`, `Wedge.Factoradic.tower-quotient`, `M40Closure.Z3`.
- `Algebra/F2/Linear/` (2): SpectralCrossCoherent, SpectralTower — `PhiMultiplicity.mult2/nullity2`.
- **The Perm/LehmerPath/SnGroup/IsPerm/decode core is imported by ZERO external modules** — consumed ONLY internally within the tower. The tower's outward-facing API is a thin **simplicial/face-complex + Hodge-dual + Phi** surface (`delAt`, `Face`, `mult2`, `dual-grade₃`).

**(B) Upstream deps (712 external import lines):** Foundation 586 (Eq 109, Nat 93, Fin 73, Vec 47, Product 42 — overwhelmingly a Fin/Vec/Nat/Eq client), Algebra 79 (Wedge/Graded, Nat.GCD.*, Monoid/Group), Groups 26 (Actions.S3 14, V4.Axioms 7), Category 20.

## 3. Rig-tree IMPORT NEIGHBORHOOD (Wedge/Orientation* — 55 modules)

- **No external consumers** — self-contained closed DAG; only downstream is internal + the PyAstRig chain.
- **Spine:** `OrientationSum` (`_⊕_`) + `OrientationProduct` (`_⊗_`) → `OrientationBimonoidal` (`GradedProductOver`, top in-deg 12) → `OrientationRigCat` (`GradedRigCat`, in-deg 7) → the RigCat*/Rig*Universal/RigInstance roots. `OrientationDistributor` (`δ`), `OrientationSumComm`/`ProductComm` (`blockSwap`/`factorSwap`), `OrientationFixedPoint` (`decode-injective`).
- **Sits ON the witness-tower core: 93 edges** — `Enumerate.Perm` 29, `LehmerPath.decode` 23, `IsPermutation.IsPerm` 14, `FirstAppearance` 11, `SnGroup` 6. + Foundation ~352 (Fin arithmetic). **Only 13 edges to Algebra.*, and the Orientation core does NOT depend on `Algebra.Semiring` at all** — it builds its rig natively from Wedge + Perm.

## 4. ⟡ LOAD-BEARING FINDING FOR OUR ARC — the PyAstRig chain is a LEAN NEW BRIDGE

`PyAstRig` → `PyAstRigNormalize` → `PyAstRigCospan` is a thin new layer that:
- rides mostly on the **witness-tower CORE directly** (Enumerate `Perm`/`insert-at`, SnGroup `apply`/`apply-id/compose/injective`, FirstAppearance `id-perm`/`compose`, LehmerPath `decode`, IsPermutation `IsPerm`),
- uses **`Algebra.Semiring.SPPF` as its carrier** — and IS THE FIRST module in this whole neighborhood to bring `Algebra.Semiring` in as a carrier (the Orientation rig tree never touches Semiring),
- reaches into the entire heavy **Orientation rig tree for EXACTLY ONE lemma: `decode-injective`** (OrientationFixedPoint).

**Implication (two readings, both true):**
- (a) MINIMAL COUPLING / reuse-maximal: PyAstRig is lean, not entangled with the 55-module Orientation machinery — good.
- (b) UNTAPPED: the rich rig-category structure (`GradedRigCat`, `RigFunctor`, `RigAlgebra` initiality, `FreeRigAlgebra` foldF, the Perm/Sym categorification) is NOT yet leveraged by PyAstRig. `⟡pyrig-action-bridge` (register `act`/torsor as a `GradedRigCat`/`Actionᴳ`/`GTorsor` instance) is the connection that would tie PyAstRig INTO the rig category proper — currently it only borrows `decode-injective`.

Also note: the tower's OWN outward API is simplicial/Hodge (delAt/Face/dual-grade), NOT the Perm/Sₙ machinery — so PyAstRig is a NEW KIND of consumer of the tower core (the first outside-the-tower user of Perm/apply/decode as a group ACTION on a carrier).

## 5. Rig-tree INTERNAL (Wedge/Orientation* — 52 modules, closed DAG, all --safe, 0 postulates)

**Spine:** `OrientationSum` (`_⊕_ : Lehmer m→Lehmer n→Lehmer(m+n)`, `0#`) + `OrientationProduct`
(`_⊗_ : Perm m→Perm n→Perm(m*n)`) → `OrientationBimonoidal` (`GradedProductOver op ε C` = {u, _∧_};
+ GradedBraid/Bifunctor/SymMonoidal) → `OrientationRigCat` (`GradedRigCat Obj Hom` — the Set₀
categorification, Obj/Hom PARAMETERIZED) → the roots.

**The 6 KEYSTONES (the central theorems):**
1. `OrientationFixedPoint.decode-injective` — LehmerPath ≅ Sₙ as μΦ≅νΦ fixed point (the pairing
   witness every UP reuses; the ONE lemma PyAstRig borrows).
2. `OrientationRigInitial.foldR-initial` (over `OrientationUniversal.fold-unique`) — **LehmerPath is
   the INITIAL rig-algebra**: `fold`/`foldR` the unique base/step-respecting map, carrying ⊕ AND ⊗
   (the single wreath catamorphism). `OrientationRigInstance.LehmerRig` = the canonical identity-fold
   model (`RigAlgebra LehmerPath`, base=start step=◂ ⊕ᶜ=⊕ ⊗ᶜ=⊗ˢ).
3. `OrientationRigFreeUP.foldF-free-unique` — generic FREE-rig UP: a hom respecting only
   zeroᶜ/oneᶜ/⊕ᶜ/rotᶜ is forced to `foldF` (◂ is DERIVED: `◂ = rotᴸ∘(X⊕·)`, OrientationRigFree).
4. `OrientationRigCat.GradedRigCat` + `.Properties.orientationRigCatₛ` + `OrientationRigCatUP`
   (`RigFunctor`, `freeObj`, `freeFunctorₛ-unique`) — the Set₀ rig category + its functor UP.
5. `OrientationRigCatSymUP.sym-hom-unique-record` (over `…CoxeterGeneral/Properties.coxeter-complete`:
   every perm is an adjacent-transposition word) — the genuine Sₙ categorification: a RigFunctor is
   determined by its value on the single generator s₁. `…PermGap` (¬ generated, NEGATIVE) +
   `…PermAdjClosure`/`…PermBifunctor` (POSITIVE) pin why Tₙ fails freeness but Sₙ succeeds.
   `OrientationRigCatPerm` (Tₙ, Hom=Vec) / `…Sym` (Sₙ, Hom=perms) are the two instances.
6. `OrientationDistributor.δ`/`dist-nat` + `OrientationHexagon` + `OrientationDistributorCoherence.
   δ-⊕braid` — the Laplaza coherence (distributor δ, ⊕-braiding hexagon, distrib–braid hexagon),
   upgrading `OrientationSymMonoidal.⊕/⊗-symmon` to a full symmetric rig category.

**Braidings:** `OrientationSumComm.blockSwap`(+invol) / `OrientationProductComm.factorSwap`(+invol);
naturality in Sum/ProductNaturality. **Structural ⊗:** `OrientationProductStructural._⊗ˢ_` +
`…Decode.decode-⊗ˢ`. **Residue:** `OrientationRigResidue.divᴸ` (flat DivStr) + `OrientationTowerDiv.
towerDiv` (**graded DivStr, `recon n l d = l ◂ d` — RESIDUE = THE LEHMER DIGIT**) + FlatGradedBridge.

## 6. ⟡ REUSE CONNECTIONS — what PyAstRig should draw from these trees (the payoff)

The PyAstRig chain currently borrows ONLY `decode-injective` from the 52-module rig tree. The map
exposes deep, unused overlaps — each a candidate ⟡:
- **RESIDUE = LEHMER DIGIT is ALREADY MODELLED.** `OrientationTowerDiv.towerDiv` is a graded
  `DivStr LehmerPath (λ n → Fin(suc n))` with `recon n l d = l ◂ d` — i.e. the substrate already
  proves "a point = an orbit rep reconstructed with a residue, residue = the Lehmer digit". My
  `pyRecon`(residue:LehmerPath) + `PyAstRigNormalize` are a RE-DERIVATION of this. ⟡pyrig-residue-bridge:
  connect pyRecon/normalize to `towerDiv` / `OrientationRigResidue` (the wedge the whole arc named).
- **INITIALITY UNUSED.** `LehmerRig` (LehmerPath = initial rig algebra, `foldR` unique) is the exact
  "everything is a fold determined by generators" my `cata`/`pyEval` re-implement ad hoc. My orbit
  `normalize` (positions→first-appearance-rank) is morally `encode` (the factoradic canonical) — worth
  relating.
- **act SHOULD BE a GradedRigCat MORPHISM.** `orientationRigCatPerm`/`Sym` already give the Sₙ-morphism
  rig category (laws proven, object-independent). ⟡pyrig-action-bridge: register `act`/torsor as a
  `RigFunctor`/`GTorsor` instance — ties PyAstRig INTO the rig category instead of borrowing 1 lemma.
- **COSPAN/cross-term:** `Algebra.Wedge.CrossMul` (algebraic, graded-deferred) vs my `PyAstRigCospan`
  (structural, equivariance proven) — two faces of the same cospan; the substrate's is the CRT/
  nilpotency reading, mine the shared-support reading.

## 7. Neighborhood shape (both trees nearly self-contained)
- Witness tower: only 10 external consumers, ALL via the simplicial/Hodge surface (`delAt`, `Face`,
  `mult2`, `dual-grade₃`) — NOT the Perm/Sₙ core. **PyAstRig is the FIRST outside-the-tower consumer of
  the Perm/apply/decode core as a group ACTION on a carrier.**
- Rig tree: ZERO external consumers; a closed DAG on the tower core (93 edges: Enumerate.Perm 29 +
  LehmerPath.decode 23). Both trees are Foundation-Fin/Nat-heavy, Algebra/Category-light.
