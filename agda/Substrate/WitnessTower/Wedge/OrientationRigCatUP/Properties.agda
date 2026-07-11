------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties
--
-- ⟡rig-UP-cat-UP (S2'/S3' — THE PROVEN, NO-Σ UNIVERSAL PROPERTY). The
-- decategorified functor-UP EXPOSED as a construction + a uniqueness lemma,
-- exactly mirroring foldF-free-unique (OrientationRigFreeUP) — NO Σ, NO ∃.
--
--   freeObj T                — THE CONSTRUCTION on objects: the canonical
--                              grade-fold of the target's own units/product
--                              (freeObj 0 = the ⊕-unit; freeObj (suc n) =
--                              the ⊗-unit ⊕ freeObj n). This is the "foldF"
--                              of the functor-UP: the object family a
--                              RigFunctor out of the skeletal source MUST
--                              carry.
--   freeFunctor-obj-unique   — THE UNIQUENESS LEMMA (general T): the object
--                              map of ANY RigFunctor orientationRigCatₛ → T
--                              equals freeObj T, forced by the ⊕/⊗-unit and
--                              ⊕-product preservation. Faithful analogue of
--                              `g l ≡ foldF F l`. No Σ; general (∀ target).
--
--   freeFunctorₛ             — THE CONSTRUCTION as an actual RigFunctor, for
--                              the concrete skeletal free object (= the
--                              identity endofunctor of orientationRigCatₛ).
--   freeFunctorₛ-unique      — full RigFunctor≈ uniqueness: every endofunctor
--                              of orientationRigCatₛ is ≈ freeFunctorₛ, by the
--                              object-singleton (Objₛ) on objects and UIP on
--                              ℕ (Hedberg) on the thin morphisms.
--
-- HONEST STOP POINT: the GENERAL freeFunctor (a RigFunctor to an ARBITRARY T)
-- is NOT built. Its F-⊕obj-∧ field would demand a ⊕-unit/associativity law on
-- the target's object product that GradedRigCat deliberately does not field
-- (the products are bare GradedProductOver — u, _∧_, no unit/assoc). The
-- F-⊕obj-∧ law already at i=j=0 demands  u⊕T ≡ (u⊕T ∧⊕T u⊕T)  — unavailable
-- law-free. The UNIQUENESS (freeFunctor-obj-unique) needs no such law — it
-- only USES the preservation fields — so it lands for arbitrary T; the
-- CONSTRUCTION lands concretely for the skeletal free object.
--
-- This module declares NO data/record (proof-side), so it may import the
-- proof-carrying orientationRigCatₛ / Hedberg (def/proof separation).
--
-- Zero postulates, zero holes, --safe --without-K. NO Σ / ∃ anywhere.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong₂)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; _∧_; u)
open import Substrate.WitnessTower.Wedge.OrientationRigCat
  using (GradedRigCat; ⊕obj; ⊗obj; Objₛ; ⋆)
open import Substrate.WitnessTower.Wedge.OrientationRigCat.Properties
  using (orientationRigCatₛ)
open import Substrate.WitnessTower.Wedge.OrientationRigCatUP
  using ( RigFunctor; F-obj
        ; F-⊕obj-u; F-⊕obj-∧; F-⊗obj-u
        ; RigFunctor≈; id-RigFunctor )

------------------------------------------------------------------------
-- THE CONSTRUCTION on objects — freeObj: the grade-fold of the target's own
-- units and additive product. This is the object family determined by the
-- generator's image (the ⊗-unit at grade 1), n-fold ⊕-composed.
------------------------------------------------------------------------

freeObj : {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
          (T : GradedRigCat Obj Hom) → (n : ℕ) → Obj n
freeObj T zero    = u (⊕obj T)
freeObj T (suc n) = _∧_ (⊕obj T) (u (⊗obj T)) (freeObj T n)

------------------------------------------------------------------------
-- THE UNIQUENESS LEMMA (general target). Any RigFunctor out of the skeletal
-- orientationRigCatₛ has its object map FORCED to freeObj by preservation:
--   n = 0     : F-obj ⋆₀ ≡ ⊕-unit T                          (F-⊕obj-u)
--   n = suc m : F-obj ⋆_{suc m} = F-obj (⋆₁ ⊕ₛ ⋆ₘ)
--             ≡ (F-obj ⋆₁) ⊕_T (F-obj ⋆ₘ)                    (F-⊕obj-∧)
--             ≡ (⊗-unit T) ⊕_T freeObj m                    (F-⊗obj-u, IH)
-- (⋆₁ = the ⊗-unit object of the skeletal source; 1 + m ≡ suc m.) NO Σ.
------------------------------------------------------------------------

freeFunctor-obj-unique :
  {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
  (T : GradedRigCat Obj Hom)
  (F : RigFunctor orientationRigCatₛ T) →
  (n : ℕ) → F-obj F (⋆ {n}) ≡ freeObj T n
freeFunctor-obj-unique T F zero    = F-⊕obj-u F
freeFunctor-obj-unique T F (suc n) =
  trans (F-⊕obj-∧ F (⋆ {1}) (⋆ {n}))
        (cong₂ (_∧_ (⊕obj T)) (F-⊗obj-u F) (freeFunctor-obj-unique T F n))

------------------------------------------------------------------------
-- THE CONSTRUCTION as a RigFunctor, for the concrete skeletal free object.
-- The skeletal rig-category orientationRigCatₛ is its own free object; the
-- free functor onto it is the identity endofunctor (freeObj orientationRig
-- Catₛ n = ⋆, and the identity realises it).
------------------------------------------------------------------------

freeFunctorₛ : RigFunctor orientationRigCatₛ orientationRigCatₛ
freeFunctorₛ = id-RigFunctor orientationRigCatₛ

------------------------------------------------------------------------
-- FULL uniqueness for the concrete free object (RigFunctor≈, NO Σ). Every
-- endofunctor of orientationRigCatₛ agrees with freeFunctorₛ:
--   * objects — Objₛ n is a singleton (⋆), so any object map is ⋆ ↦ ⋆;
--   * morphisms — Homₛ i j = (i ≡ j) is a mere proposition (UIP on ℕ,
--     Hedberg from decidable _≟_), so any two thin morphisms are equal.
------------------------------------------------------------------------

private
  -- every object of grade n is ⋆ (Objₛ is the grade-indexed singleton).
  objₛ-canon : {n : ℕ} (x : Objₛ n) → x ≡ ⋆
  objₛ-canon ⋆ = refl

  -- UIP on ℕ specialised: any two grade-equalities coincide (thin homs).
  uipℕ : {i j : ℕ} (p q : i ≡ j) → p ≡ q
  uipℕ = Decidable⇒UIP _≟_

freeFunctorₛ-unique :
  (F : RigFunctor orientationRigCatₛ orientationRigCatₛ) →
  RigFunctor≈ F freeFunctorₛ
freeFunctorₛ-unique F = record
  { obj≈ = λ a → trans (objₛ-canon (F-obj F a)) (sym (objₛ-canon a))
  ; hom≈ = λ h → uipℕ _ h
  }
