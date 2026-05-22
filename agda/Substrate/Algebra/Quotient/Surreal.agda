------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.Surreal
--
-- QU8 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- Surreal numbers (Conway games modulo ≈ⁿ) → base Quotient instance,
-- closing the loop with the substrate's term-algebra spine per
-- [[project-surreals-term-algebra-alignment]].
--
-- Surreals' `_≈ⁿ_` is defined as `x ≈ⁿ y = x ≤ⁿ y × y ≤ⁿ x` in
-- Substrate.Conway.Equivalence. The relation is heterogeneous across
-- birthdays; here we fix a single birthday `suc n` to give a
-- homogeneous `_≈_ : A → A → Set` matching the Quotient record's
-- shape.
--
-- ≤ⁿ-refl and ≤ⁿ-trans are Conway-induction-deep and partially
-- deferred in the substrate (see Conway.OrderLaws header). This
-- module parameterises on the missing witnesses so the
-- Quotient-instance attaches as soon as they're discharged.
--
-- NO Canonical extension: surreals don't have a privileged
-- representative per equivalence class (multiple ⟨L|R⟩ with the
-- same equivalence-class membership exist; the canonical form
-- would require a choice that isn't a function of a single
-- surreal). Same shape as V4-Cosets (QU7).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.Order using (_≤ⁿ_)
open import Substrate.Conway.Equivalence using (_≈ⁿ_; sym-≈ⁿ)

module Substrate.Algebra.Quotient.Surreal
  -- The two Conway-induction-deep witnesses parameterising this
  -- module. Both have witnesses on the simple cases (Conway.OrderLaws,
  -- Conway.OrderTrans), with full versions deferred to the substrate's
  -- Conway-induction arc.
  (≤ⁿ-refl :
    {n : ℕ} (x : SurrealFinite (suc n)) → x ≤ⁿ x)
  (≤ⁿ-trans :
    {m n p : ℕ}
    (x : SurrealFinite (suc m)) (y : SurrealFinite (suc n))
    (z : SurrealFinite (suc p)) →
    x ≤ⁿ y → y ≤ⁿ z → x ≤ⁿ z)
  where

open import Substrate.Algebra.Quotient using (Quotient)

------------------------------------------------------------------------
-- 1. Homogeneous fixed-birthday ≈ⁿ.
------------------------------------------------------------------------

private
  _≈_ : {n : ℕ} → SurrealFinite (suc n) → SurrealFinite (suc n) → Set
  x ≈ y = x ≈ⁿ y

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
