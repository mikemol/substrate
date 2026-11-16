------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.NewmanSKI.Op
--
-- Defines: _⇒_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.NewmanSKI; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.NewmanSKI.Op where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



-- 2. The I-reduction relation: β-I at the root ℕ+ application congruence.
data _⇒_ : Tm → Tm → Set where      -- ⟦shape:f6ded35b β-I,cong-l,cong-r⟧
  β-I    : (x : Tm)             → (I ∙ x) ⇒ x
  cong-l : {f f' : Tm} (g : Tm) → f ⇒ f' → (f ∙ g) ⇒ (f' ∙ g)
  cong-r : (f : Tm) {g g' : Tm} → g ⇒ g' → (f ∙ g) ⇒ (f ∙ g')
