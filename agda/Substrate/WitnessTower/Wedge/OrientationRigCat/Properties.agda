------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCat.Properties
--
-- ⟡rig-UP-cat-graded (instance) — A CONCRETE Set₀ RIG CATEGORY (the
-- record is inhabited: the dissolution is not vacuous). The proof-dependent
-- face of OrientationRigCat: imports +-comm / *-comm and the Hedberg UIP
-- (from decidable _≟_), so it is kept out of the proof-free record home
-- (def/proof separation).
--
-- The SKELETAL orientation-grade groupoid: objects are the grades
-- (one object ⋆ per grade n — the n-element ordered-set spine, a
-- grade-INDEXED singleton so the grade is recoverable from the type),
-- and a morphism from grade i to grade j is a proof i ≡ j (the thin
-- groupoid on grades). The two products decategorify onto ℕ: ⊕ = (ℕ,+,0),
-- ⊗ = (ℕ,*,1); the braidings are the grade commutativities +-comm /
-- *-comm, and the symmetry (involution) laws hold by UIP on ℕ (Hedberg,
-- from decidable equality _≟_). Fully proven — zero postulates/holes.
--
-- HONEST SCOPE: this is the terminal/skeletal instance (one object per
-- grade). The richer instance — objects = orderings (Perm n), tensor =
-- the committed OrientationProduct _⊗_, braidings = the Fin-level
-- GradedBraid readouts — is the natural S2+ and is NOT built here (it
-- needs the Perm category laws id/∘/assoc, out of scope for this bar).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCat.Properties where

open import Substrate.Foundation.Nat using (ℕ; _≟_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; trans)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; _∧_; u)
open import Substrate.WitnessTower.Wedge.OrientationRigCat using (GradedRigCat; Objₛ; ⋆)

private
  Homₛ : {i j : ℕ} → Objₛ i → Objₛ j → Set
  Homₛ {i} {j} _ _ = i ≡ j

  -- UIP on ℕ specialised: any two grade-equalities coincide.
  uipℕ : {i j : ℕ} (p q : i ≡ j) → p ≡ q
  uipℕ = Decidable⇒UIP _≟_

orientationRigCatₛ : GradedRigCat Objₛ Homₛ
orientationRigCatₛ = record
  { idHom        = λ _ → refl
  ; _∘_          = λ g f → trans f g
  ; left-id      = λ { refl → refl }
  ; right-id     = λ _ → refl
  ; assoc        = λ { refl _ _ → refl }
  ; ⊕obj         = record { u = ⋆ ; _∧_ = λ _ _ → ⋆ }
  ; ⊗obj         = record { u = ⋆ ; _∧_ = λ _ _ → ⋆ }
  ; braid⊕       = λ {i} {j} _ _ → +-comm i j
  ; braid⊗       = λ {i} {j} _ _ → *-comm i j
  ; braid⊕-invol = λ {i} {j} _ _ → uipℕ (trans (+-comm i j) (+-comm j i)) refl
  ; braid⊗-invol = λ {i} {j} _ _ → uipℕ (trans (*-comm i j) (*-comm j i)) refl
  }
