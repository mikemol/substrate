------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.NatTarget
--
-- Defines: ℕ⁺-target
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.NatTarget where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



------------------------------------------------------------------------
-- THE Fₙ PICTURE — the sign (F₂) is the mod-2 shadow of a UNIVERSAL ℕ (= F_∞)
-- cocycle, and Route A (inversion count) is that universal object while Route B
-- (the sign homomorphism) is F₂-terminal. This dissolves the "no tower→F₂
-- composition": it composes — through ℕ, not through the bare tower.
------------------------------------------------------------------------

-- the additive-ℕ graded target (F_∞: mirror F₂-target at ℕ; reduces to every Fₙ).
ℕ⁺-target : GradedDivStr (λ _ → ℕ) (λ _ → ℕ)
ℕ⁺-target = record { recon = λ n b r → r ℕ+ b }
