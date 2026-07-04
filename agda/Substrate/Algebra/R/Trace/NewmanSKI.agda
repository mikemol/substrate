{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.NewmanSKI — ⟡newman-ski-instance (DEFINITIONS): the
-- combinator terms + I-reduction relation. The SN / WCR / CR proofs — instantiating
-- the substrate's own Newman's lemma (Foundation.RewriteConfluence, ADD 128) — live
-- in the .Properties sibling (def/proof separation). Full untyped SKI is NOT SN
-- (SII(SII) loops); this is the I-reduction fragment, which IS SN. CR in .Properties.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.NewmanSKI where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)

-- 1. Combinator terms (S/K/I atoms + application) + size measure.
data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm

infixl 7 _∙_

size : Tm → ℕ
size S = 1
size K = 1
size I = 1
size (f ∙ g) = suc (size f + size g)

-- 2. The I-reduction relation: β-I at the root + application congruence.
data _⇒_ : Tm → Tm → Set where      -- ⟦shape:f6ded35b β-I,cong-l,cong-r⟧
  β-I    : (x : Tm)             → (I ∙ x) ⇒ x
  cong-l : {f f' : Tm} (g : Tm) → f ⇒ f' → (f ∙ g) ⇒ (f' ∙ g)
  cong-r : (f : Tm) {g g' : Tm} → g ⇒ g' → (f ∙ g) ⇒ (f ∙ g')
