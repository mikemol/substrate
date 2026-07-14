------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aBackedGraded — ⟡C2g-m-x8a (graded): the EXTRUDER
-- (reduction-to-fixpoint) solver as a Set₀ graded backing — the NATIVE-GRADE flagship.
--
-- Migrates the flat `x8a-backed : BackedUP` (X8aBacked.agda:91). The flat Fuelled Source was
-- `Σ ℕ (λ _ → ℕ)` = (fuel , start); the graded backing makes the FUEL the ℕ grade — Spec n =
-- start-at-fuel-n, Sol = ℕ, solve {n} = run n (the machine run at fuel n). `solves` (= refl)
-- vanishes into `Contentfulᴳ`'s hard-wired `t ≡ solve s`. Content at grade 1: run 1 1 = 0 (one
-- step to the fixpoint), candidate 1 ≢ 0. Class A (flat Witness = `v ≡ run …`), CLEAN.
--
-- Self-contained: re-derives the concrete machine (next/fix?/run) rather than importing the flat
-- X8aBacked (which retires). Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.X8aBackedGraded where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)
open import Substrate.S5.S5Fixpoint using (module Machine)

-- the concrete extruder machine over ℕ: `next` = predecessor (its fixpoint is 0).
next : ℕ → ℕ
next zero    = zero
next (suc n) = n

fix? : (s : ℕ) → Dec (next s ≡ s)
fix? zero    = yes refl
fix? (suc n) = no λ ()

open Machine ℕ next fix? using (run)

-- FUEL IS THE GRADE: solve {n} = run n (run the reduction n steps to the fixpoint).
x8a-arrowᴳ : UPArrowᴳ (λ _ → ℕ) (λ _ → ℕ)
x8a-arrowᴳ = mkUP (λ {n} start → run n start)

-- the extruder as a Set₀ graded backing; content: at grade 1, run 1 1 = 0, so 1 ≢ solve 1.
x8a-backedᴳ : BackedUPᴳ (λ _ → ℕ) (λ _ → ℕ)
x8a-backedᴳ = record
  { arrowᴳ  = x8a-arrowᴳ
  ; content = 1 , 1 , 1 , λ ()
  }
