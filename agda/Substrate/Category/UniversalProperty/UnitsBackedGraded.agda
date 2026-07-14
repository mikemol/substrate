------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.UnitsBackedGraded — ⟡C2g-m-units (graded): the units (ℤ/2)*
-- universal property as a Set₀ graded backing.
--
-- Migrates the flat `units-backed : BackedUP` (DeferredBacked.agda:96). Class B CARE: the flat Witness
-- was the product-mod relation `(a * b) mod-suc 1 ≡ 1` ("b is a's right inverse"); the graded
-- Contentfulᴳ collapses it to functional `t ≡ solve s`, where solve extracts the inverse component
-- from the unit-proof (the Source carries invertibility, so the solver is total). `solves` (the
-- inverse-witness) is dropped. Content at grade 0: 1's inverse is 1, candidate 0 ≠ 1.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.UnitsBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Nat.Units using (IsUnit; one-is-unit)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- solve extracts the inverse component from the unit-proof (the inverse IS the witness).
units-solve : Σ ℕ (IsUnit 1) → ℕ
units-solve (a , b , _) = b

units-arrowᴳ : UPArrowᴳ (λ _ → Σ ℕ (IsUnit 1)) (λ _ → ℕ)
units-arrowᴳ = mkUP units-solve

units-backedᴳ : BackedUPᴳ (λ _ → Σ ℕ (IsUnit 1)) (λ _ → ℕ)
units-backedᴳ = record
  { arrowᴳ  = units-arrowᴳ
  ; content = 0 , (1 , one-is-unit 1) , 0 , λ ()
  }
