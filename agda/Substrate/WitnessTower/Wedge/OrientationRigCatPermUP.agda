------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermUP
--
-- ⟡rig-UP-cat-perm-UP — THE HONEST FUNCTOR UNIVERSAL PROPERTY of
-- orientationRigCatPerm, the TRANSFORMATION-MONOID (Tₙ) rig category
-- (OrientationRigCatPerm — its morphisms are unrestricted vectors, NOT Sₙ; see
-- that header's CORRECTION). Companion to ⟡rig-UP-cat-UP
-- (OrientationRigCatUP.Properties), which settled the SKELETAL (thin) source;
-- this one settles the Tₙ source and — crucially — exposes exactly WHERE its
-- universal property STOPS, without faking the missing part. (The genuine
-- SYMMETRIC Sₙ source, where the UP is actually FREE, is OrientationRigCatSym
-- .UP: sym-hom-unique — F determined by F(s₁) on every permutation morphism.)
--
-- WHAT IT SETTLES (both solid, ∀ target, NO Σ / ∃):
--
--   (1) OBJECT-UP — FORCED. orientationRigCatPerm's objects are Objₚ = Objₛ
--       (the SAME grade-indexed singleton as the skeletal source) with the
--       SAME trivial ⊕obj/⊗obj on objects (u = ⋆, _∧_ = λ _ _ → ⋆). So the
--       object-map of ANY RigFunctor orientationRigCatPerm → T is forced to
--       the grade-fold freeObj T by the ⊕/⊗-unit + ⊕-product preservation
--       fields — the SAME induction that freeFunctor-obj-unique runs for the
--       skeletal source (freeObj / the proof are reused, only the source
--       swapped). `freeFunctorₚ-obj-unique`.
--
--   (2) BRAIDING-WORD DETERMINATION — FORCED. On a braiding, F-hom is pinned
--       by the functor's own F-braid⊕/F-braid⊗ coherence fields; on a ∘-com-
--       posite of braidings it is pinned by F-∘. So any morphism EXPRESSIBLE
--       AS A BRAIDING-WORD has its image determined. `F-braid⊕-forced`,
--       `F-braid⊗-forced`, `F-hom-∘-forced` (each is the corresponding field,
--       named for this concrete source — definitional/direct, no new machinery).
--
-- THE HONEST SCOPE — THE PRIMALITY GAP (numpy-verified; this is the real
-- theorem, and it is NEGATIVE). The braiding morphisms of orientationRigCatPerm
-- at grade n are:
--   * the block-swaps braid⊕{i}{j} (i+j=n) = blockSwap i (n−i) = the cyclic
--     shift by n−i — together the ROTATIONS, which generate Cₙ; and
--   * the factor-swaps braid⊗{i}{j} (i·j=n) = the i×j grid transposes.
-- The subgroup they generate under ∘:
--
--     ⟨block-swaps ∪ factor-swaps⟩ = Sₙ   ⟺   n composite (or n ∈ {1,2});
--     for PRIME n ≥ 3, i·j=n has no nontrivial split so the factor-swaps are
--     trivial and only the rotations survive → the subgroup is Cₙ ⊊ Sₙ.
--
-- Measured (numpy, verified): n = 1,2,4,6,8 → full Sₙ (orders 1,2,24,720,40320);
-- n = 3,5,7 → only Cₙ (orders 3,5,7).
--
-- CONSEQUENCE: a RigFunctor orientationRigCatPerm → T has its F-hom FORCED (by
-- F-∘ + F-braid⊕/⊗) ONLY on the braiding-generated subgroup — all of Sₙ at
-- COMPOSITE grades, but only the rotation subgroup Cₙ at PRIME grades. So
-- orientationRigCatPerm is NOT free/initial via its braidings: at prime grades
-- ≥ 3 the full Sₙ homs are NOT pinned by the GradedRigCat structure. The
-- obstruction is precisely PRIMALITY (⊗ contributes nothing) TOGETHER WITH the
-- ABSENCE of a monoidal-product-ON-MORPHISMS (a bifunctor `gmap`) that would
-- make the adjacent transpositions sᵢ = id ⊕ s₁ ⊕ id reachable — and adjacent
-- transpositions DO generate Sₙ (Coxeter; Substrate.Category.CoxeterPermutation
-- Group). Full freeness would need that bifunctor; the current GradedRigCat does
-- not field it. Ⓐ NOW CLOSED — the concrete Agda non-membership witness at grade
-- 3 (the transposition (0 1) ∈ Perm 3 is not any ∘-composite of the three grade-3
-- braidings = C₃) is PROVEN in `OrientationRigCatPermGap` (`transposition-∉-
-- braidings : ¬ BraidGen t01`), by the FINITE CLOSURE of the two rotation
-- generators (C₃ = { id, [2,0,1], [1,2,0] }, closed under compose — each of the 9
-- products `refl`) plus the constructor-distinct disequality of the transposition
-- vector — no general sign theorem was needed after all. (The earlier note that
-- this "needed a sign map that doesn't exist" was an ABSENCE claim I had not
-- searched: the alternating sign DOES already walk the tower —
-- `WitnessTower.CycleType.cycle-type : {n} → Perm n → Vec ℕ n` is general and
-- separates them [transposition ↦ [1,1,0] vs id/3-cycle ↦ [3,0,0]/[0,0,1]], and
-- the sign-as-xor-hom PATTERN is proven for the position sign
-- [`SimplicialBoundary.osign`+`∂∂-opp-sign`] and chirality [`M40Action.sgn-hom`];
-- the finite-closure route sidesteps needing a Perm-n sign homomorphism at all.)
--
-- This module declares NO data/record (proof-side): all content is lemmas over
-- the existing RigFunctor / GradedRigCat types, so it may import the proof-
-- carrying orientationRigCatPerm and freeObj (def/proof separation).
--
-- Zero postulates, zero holes, --safe --without-K. NO Σ / ∃ to PACKAGE any
-- existence/uniqueness claim.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermUP where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; trans; cong₂)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (_∧_)
open import Substrate.WitnessTower.Wedge.OrientationRigCat
  using (GradedRigCat; _∘_; ⊕obj; braid⊕; braid⊗; Objₛ; ⋆)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm
  using (orientationRigCatPerm; Objₚ; Homₚ)
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP
  using ( RigFunctor; F-obj; F-hom; F-∘; F-braid⊕; F-braid⊗
        ; F-⊕obj-u; F-⊕obj-∧; F-⊗obj-u; F-⊗obj-∧; trⱽ )
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties
  using (freeObj)

------------------------------------------------------------------------
-- (1) OBJECT-UP — FORCED, ∀ target. The object map of ANY RigFunctor out of
-- orientationRigCatPerm equals the grade-fold freeObj. Objₚ = Objₛ and the two
-- object products are the trivial ones (u = ⋆, _∧_ = λ _ _ → ⋆), IDENTICAL to
-- the skeletal source — so this is freeFunctor-obj-unique's induction verbatim
-- with the source swapped:
--   n = 0     : F-obj ⋆₀ ≡ ⊕-unit T                       (F-⊕obj-u)
--   n = suc m : F-obj ⋆_{suc m} = F-obj (⋆₁ ⊕ₚ ⋆ₘ)
--             ≡ (F-obj ⋆₁) ⊕_T (F-obj ⋆ₘ)                  (F-⊕obj-∧)
--             ≡ (⊗-unit T) ⊕_T freeObj m                  (F-⊗obj-u, IH)
-- NO Σ.
------------------------------------------------------------------------

freeFunctorₚ-obj-unique :
  {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
  (T : GradedRigCat Obj Hom)
  (F : RigFunctor orientationRigCatPerm T) →
  (n : ℕ) → F-obj F (⋆ {n}) ≡ freeObj T n
freeFunctorₚ-obj-unique T F zero    = F-⊕obj-u F
freeFunctorₚ-obj-unique T F (suc n) =
  trans (F-⊕obj-∧ F (⋆ {1}) (⋆ {n}))
        (cong₂ (_∧_ (⊕obj T)) (F-⊗obj-u F) (freeFunctorₚ-obj-unique T F n))

------------------------------------------------------------------------
-- (2) BRAIDING-WORD DETERMINATION — FORCED, ∀ target. Each lemma below IS the
-- corresponding RigFunctor coherence/functoriality field, specialised to the
-- concrete source orientationRigCatPerm, so it reads as "the image of THIS
-- braiding / composite is forced". Together they pin F-hom on any braiding-
-- WORD (a ∘-composite of braidings). Definitional (each body is one field).
------------------------------------------------------------------------

-- The image of an ADDITIVE braiding is pinned: transported along the ⊕-product
-- preservation, F-hom (braid⊕) IS the target's braid⊕.
F-braid⊕-forced :
  {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
  (T : GradedRigCat Obj Hom) (F : RigFunctor orientationRigCatPerm T)
  {i j : ℕ} (a : Objₚ i) (b : Objₚ j) →
  trⱽ {Obj = Obj} {Hom = Hom}
      (F-⊕obj-∧ F a b) (F-⊕obj-∧ F b a)
      (F-hom F (braid⊕ orientationRigCatPerm a b))
  ≡ braid⊕ T (F-obj F a) (F-obj F b)
F-braid⊕-forced T F a b = F-braid⊕ F a b

-- The image of a MULTIPLICATIVE braiding is pinned likewise.
F-braid⊗-forced :
  {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
  (T : GradedRigCat Obj Hom) (F : RigFunctor orientationRigCatPerm T)
  {i j : ℕ} (a : Objₚ i) (b : Objₚ j) →
  trⱽ {Obj = Obj} {Hom = Hom}
      (F-⊗obj-∧ F a b) (F-⊗obj-∧ F b a)
      (F-hom F (braid⊗ orientationRigCatPerm a b))
  ≡ braid⊗ T (F-obj F a) (F-obj F b)
F-braid⊗-forced T F a b = F-braid⊗ F a b

-- The image of a ∘-COMPOSITE is the composite of the images: so a braiding-WORD
-- (any ∘-composite of braidings) has its image fully determined by the two
-- forcings above together with this. (This is F-∘, named for the source.)
-- Objects are EXPLICIT and passed explicitly everywhere: Homₚ discards its
-- object arguments (Objₚ = Objₛ is a grade-indexed singleton), so g/f cannot
-- recover a/b/c — they would be unsolved metas. Pinning them is the mechanically-
-- forced honest reading (the same Objₚ-erasure discipline the source header names).
F-hom-∘-forced :
  {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
  (T : GradedRigCat Obj Hom) (F : RigFunctor orientationRigCatPerm T)
  {i j k : ℕ} (a : Objₚ i) (b : Objₚ j) (c : Objₚ k)
  (g : Homₚ b c) (f : Homₚ a b) →
  F-hom F (_∘_ orientationRigCatPerm {a = a} {b = b} {c = c} g f)
  ≡ _∘_ T (F-hom F {a = b} {b = c} g) (F-hom F {a = a} {b = b} f)
F-hom-∘-forced T F a b c g f = F-∘ F {a = a} {b = b} {c = c} g f
