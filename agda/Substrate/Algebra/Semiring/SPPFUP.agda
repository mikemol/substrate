------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.SPPFUP
--
-- The FREE-SEMIRING UNIVERSAL PROPERTY of the packed parse forest — the claim
-- SPPF.agda's header makes ("the free-semiring term on its generators; a single
-- fold `inside` evaluates it in ANY semiring") now PROVEN, not asserted.
--
--   inside-unique : `inside S v` is the UNIQUE semiring homomorphism SPPF G → A
--                   extending the valuation v : G → A. Any h respecting the four
--                   constructors (gen ↦ v, one ↦ ×-unit, ⊗ ↦ ×, ⊕ ↦ +) equals
--                   `inside S v` on every term.
--
-- This grounds every "the universal fold" claim over SPPF (PyAstRig.pyEval =
-- inside; ElAtlas / SWP) in an actual theorem. The proof is one structural
-- induction, mirroring the four `inside` clauses.
--
-- SCOPE NOTE (⟡pyrig-ground-initiality): this is SPPF's SEMIRING initiality — a
-- DIFFERENT initial object from the witness tower's LehmerPath (the graded
-- initial RIG algebra, OrientationRigInitial.foldR). Same PATTERN (initial object
-- ⇒ unique fold), different INSTANCE. So `inside` is NOT `foldR`; the pyast fold
-- is grounded here, in SPPF's own UP.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring.SPPFUP where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong₂)
open import Substrate.Algebra.Magma     using (Magma)
open import Substrate.Algebra.Semigroup using (magma)
open import Substrate.Algebra.Monoid    using (semigroup; ε)
open import Substrate.Algebra.Semiring  using (Semiring; +-monoid; *-monoid)
open import Substrate.Algebra.Semiring.SPPF using (SPPF; gen; one; _⊗_; _⊕_; inside)

module _ {A G : Set} (S : Semiring A) (v : G → A) where
  private
    _×_ = Magma._·_ (magma (semigroup (*-monoid S)))
    _+_ = Magma._·_ (magma (semigroup (+-monoid S)))
    1×  = ε (*-monoid S)

  -- THE UNIVERSAL PROPERTY: inside is the unique semiring hom extending v.
  inside-unique :
    (h : SPPF G → A) →
    (∀ g → h (gen g) ≡ v g) →
    (h one ≡ 1×) →
    (∀ a b → h (a ⊗ b) ≡ (h a × h b)) →
    (∀ a b → h (a ⊕ b) ≡ (h a + h b)) →
    (t : SPPF G) → h t ≡ inside S v t
  inside-unique h hg h1 h⊗ h⊕ (gen g) = hg g
  inside-unique h hg h1 h⊗ h⊕ one     = h1
  inside-unique h hg h1 h⊗ h⊕ (a ⊗ b) =
    trans (h⊗ a b) (cong₂ _×_ (inside-unique h hg h1 h⊗ h⊕ a)
                              (inside-unique h hg h1 h⊗ h⊕ b))
  inside-unique h hg h1 h⊗ h⊕ (a ⊕ b) =
    trans (h⊕ a b) (cong₂ _+_ (inside-unique h hg h1 h⊗ h⊕ a)
                              (inside-unique h hg h1 h⊗ h⊕ b))
