------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.Surreal.SurrealQuotient
--
-- Defines: Surreal-Quotient
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient.Surreal; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.Surreal.SurrealQuotient where

open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.Surreal.Approx
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Conway.SurrealFinite
open import Substrate.Conway.Equivalence



------------------------------------------------------------------------
-- 2. Quotient instance at each birthday `suc n`.
------------------------------------------------------------------------

Surreal-Quotient :
  (n : ℕ) → Quotient (SurrealFinite (suc n)) (_≈_ {n})
Surreal-Quotient n = record
  { ≈-refl  = λ x → ≤ⁿ-refl x , ≤ⁿ-refl x
  ; ≈-sym   = λ {x} {y} → sym-≈ⁿ x y
  ; ≈-trans = λ {x} {y} {z} (x≤y , y≤x) (y≤z , z≤y) →
                 ≤ⁿ-trans x y z x≤y y≤z ,
                 ≤ⁿ-trans z y x z≤y y≤x
  }

------------------------------------------------------------------------
-- 3. Capstone for QU8.
--
-- Surreals attach as a base Quotient — closing the loop with the
-- term-algebra (Coxeter Word) carrier per
-- [[project-surreals-term-algebra-alignment]]. The Conway-induction
-- gap is captured as module parameters; downstream attachment
-- becomes a one-line instantiation once Conway.OrderTrans /
-- Conway.OrderLaws complete.
------------------------------------------------------------------------
