------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.EqBackedGraded — ⟡C2g-m-eq (graded): the equality UP as a
-- Set₀ graded backing.
--
-- THE SMOKE-TEST MIGRATION of the flat `eq-backed : BackedUP` (Backed.agda:62). The flat equality UP
-- had Source = Target = ℕ, Witness = _≡_, solve = id, content = (0 , 1 , λ ()). The graded backing
-- absorbs the Witness into `Contentfulᴳ` (which hard-wires `t ≡ solve s`) and DELETES the `solves`
-- field (it was `refl`). Constant grade (Spec = Sol = λ _ → ℕ); the identity solve; content = the
-- discriminating pair 0 ≢ 1 at grade 0. Class A (flat Witness = functional _≡_), CLEAN.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.EqBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- the constructive universal arrow: solve = id (s solved by s).
eq-arrowᴳ : UPArrowᴳ (λ _ → ℕ) (λ _ → ℕ)
eq-arrowᴳ = mkUP (λ x → x)

-- the equality UP as a Set₀ graded backing; content = the discriminating pair (1 ≢ solve 0 = 1 ≢ 0).
eq-backedᴳ : BackedUPᴳ (λ _ → ℕ) (λ _ → ℕ)
eq-backedᴳ = record
  { arrowᴳ  = eq-arrowᴳ
  ; content = 0 , 0 , 1 , λ ()
  }
