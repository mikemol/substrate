------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.MuBackedGraded — ⟡C2g-m-mu (graded): the μ initial-algebra
-- (trace-fold) UP as a Set₀ graded backing.
--
-- Migrates the flat `mu-backed : BackedUP` (MuBacked.agda:96, over ℕ-div). solve = collapse-fold (the
-- trace-fold reading a trace to its gcd index); `solves` (= refl) vanishes into `Contentfulᴳ`.
-- Constant grade @ℕ-div (Spec = λ _ → SomeTraceℕ, Sol = λ _ → ℕ); content = the trace `done 0` folds
-- to 0, candidate 1 ≠ 0. Class A, CLEAN. (`mu-fold-unique` — the initial-algebra ≡-uniqueness — stays
-- a separate layer, matching UPArrowGraded.Determines; it is not a backing field.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.MuBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr; Trace; done; collapse-fold; ℕ-div)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

SomeTraceℕ : Set
SomeTraceℕ = Σ ℕ (λ a → Σ ℕ (λ b → Σ ℕ (λ g → Trace ℕ-div a b g)))

mu-solve : SomeTraceℕ → ℕ
mu-solve (a , b , g , t) = collapse-fold t

mu-arrowᴳ : UPArrowᴳ (λ _ → SomeTraceℕ) (λ _ → ℕ)
mu-arrowᴳ = mkUP mu-solve

mu-backedᴳ : BackedUPᴳ (λ _ → SomeTraceℕ) (λ _ → ℕ)
mu-backedᴳ = record
  { arrowᴳ  = mu-arrowᴳ
  ; content = 0 , (0 , 0 , 0 , done 0) , 1 , λ ()
  }
