------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.NewmanKI.Op
--
-- Defines: _⇒_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.NewmanKI; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.NewmanKI.Op where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- 2. KI-reduction: β-I, β-K, and application congruence.
data _⇒_ : Tm → Tm → Set where      -- ⟦shape:03d50a66 β-I,β-K,cong-l⟧
  β-I    : (x : Tm)             → (I ∙ x) ⇒ x
  β-K    : (x y : Tm)          → ((K ∙ x) ∙ y) ⇒ x
  cong-l : {f f' : Tm} (g : Tm) → f ⇒ f' → (f ∙ g) ⇒ (f' ∙ g)
  cong-r : (f : Tm) {g g' : Tm} → g ⇒ g' → (f ∙ g) ⇒ (f ∙ g')
