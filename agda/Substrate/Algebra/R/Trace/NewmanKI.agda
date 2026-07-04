{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.NewmanKI — ⟡newman-ki-instance (DEFINITIONS): the KI
-- combinator terms + KI-reduction relation. The SN / WCR / CR PROOFS live in the
-- .Properties sibling, so this definition module's import closure stays proof-free
-- (def/proof separation policy). β-K (K∙x∙y ⇒ x) and β-I (I∙x ⇒ x) both strictly
-- SHRINK the term ⟹ strongly normalizing; full SKI is out of reach (S∙x∙y∙z is not
-- size-decreasing — SII(SII) loops). CR (via Newman) is in .Properties.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.NewmanKI where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)

-- 1. Combinator terms + size.
data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm

infixl 7 _∙_

size : Tm → ℕ
size S = 1
size K = 1
size I = 1
size (f ∙ g) = suc (size f + size g)

-- 2. KI-reduction: β-I, β-K, and application congruence.
data _⇒_ : Tm → Tm → Set where      -- ⟦shape:03d50a66 β-I,β-K,cong-l⟧
  β-I    : (x : Tm)             → (I ∙ x) ⇒ x
  β-K    : (x y : Tm)          → ((K ∙ x) ∙ y) ⇒ x
  cong-l : {f f' : Tm} (g : Tm) → f ⇒ f' → (f ∙ g) ⇒ (f' ∙ g)
  cong-r : (f : Tm) {g g' : Tm} → g ⇒ g' → (f ∙ g) ⇒ (f ∙ g')
