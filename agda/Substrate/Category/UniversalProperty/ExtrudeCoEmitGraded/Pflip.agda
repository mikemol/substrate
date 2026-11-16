------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
--
-- Defines: pflip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-conj-conj-totality + coemit-faceset-star + coemit-stardivstr.
-- NOTE (self-audit): 350 identified the conjugation as "the stepwise chirality flip" but never defined
-- bar : RealTrace → RealTrace — my ad-hoc `step-flip : ℕ → ℕ` was DISCARDED (not an involution). A genuine
-- conjugation needs a genuine involution on the payload that FLIPS PARITY (so it flips the step's chirality bit).
-- That map is `pflip` : swap 0↔1, 2↔3, 4↔5, … — an involution on ℕ whose parity is always flipped.
------------------------------------------------------------------------
-- pflip: the payload involution that flips parity (0↔1, 2↔3, …). THE per-step chirality flip, on the digit.
pflip : ℕ → ℕ
pflip zero                = suc zero
pflip (suc zero)          = zero
pflip (suc (suc n))       = suc (suc (pflip n))
