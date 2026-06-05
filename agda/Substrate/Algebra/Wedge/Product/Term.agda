------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.Term
--
-- SLICE 3: the WEDGE TERM — the free graded monoid term over a GradedProduct,
-- i.e. the QUOTE side made first-class (quote = quotient = grade, Product.agda).
-- A term is a leaf (a kept grade-i factor), the empty term, or a ∧-node; its
-- grade is the sum of its leaves' grades. The term KEEPS EVERY FACTOR — NEVER
-- DROPS A RESIDUE (user): the whole bracketed structure is retained, and `eval`
-- is the ONLY forgetful step (it collapses the bracketing to the carrier value,
-- still keeping every value).
--
--   eval — the forgetful evaluation WedgeTerm P n → C P n (the term's value).
--   pow-term / eval-pow — power/gpower FACTOR THROUGH the term: the q-deep
--     ∧-term of b evaluates to gpower b q. So "q copies" (quotient) = a q-deep
--     quote (term) = grade q, now literally as a term that evaluates correctly.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Product.Term where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.Wedge.Product using (GradedProduct; C; u; _∧_; gpower)

------------------------------------------------------------------------
-- 1. The free graded monoid term: leaves (kept factors), the empty term,
--    and ∧-nodes. The grade is the sum of the leaf grades.
------------------------------------------------------------------------

data WedgeTerm (P : GradedProduct) : ℕ → Set where
  leaf : {i : ℕ} → C P i → WedgeTerm P i
  nil  : WedgeTerm P 0
  _⊗_  : {i j : ℕ} → WedgeTerm P i → WedgeTerm P j → WedgeTerm P (i + j)

------------------------------------------------------------------------
-- 2. eval — the only forgetful step: collapse the bracketing to the value.
--    (Every value is kept; only the bracket structure is forgotten.)
------------------------------------------------------------------------

eval : {P : GradedProduct} {n : ℕ} → WedgeTerm P n → C P n
eval {P} (leaf x) = x
eval {P} nil      = u P
eval {P} (s ⊗ t)  = _∧_ P (eval s) (eval t)

------------------------------------------------------------------------
-- 3. power factors through the term: the q-deep ∧-term of b evaluates to
--    gpower b q. "q copies" (quotient) = a q-deep quote (term) = grade q.
------------------------------------------------------------------------

pow-term : {P : GradedProduct} {i : ℕ} (b : C P i) (q : ℕ) → WedgeTerm P (q * i)
pow-term b zero    = nil
pow-term b (suc n) = leaf b ⊗ pow-term b n

eval-pow : {P : GradedProduct} {i : ℕ} (b : C P i) (q : ℕ) →
           eval (pow-term {P} b q) ≡ gpower P b q
eval-pow b zero    = refl
eval-pow {P} b (suc n) = cong (_∧_ P b) (eval-pow b n)
