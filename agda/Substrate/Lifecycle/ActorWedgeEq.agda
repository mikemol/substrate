------------------------------------------------------------------------
-- Substrate.Lifecycle.ActorWedgeEq
--
-- Defines: actor-wedge-eq
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.ActorWedgeEq where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong


------------------------------------------------------------------------
-- THE WEDGE EQUATION: a base plus its residue reconstructs the whole.
--
--     b ≤ a   ⟹   b ℕ+ (a ∸ b) ≡ a
--
-- This is `GradedWedge`'s `wedge-eq : a ≡ recon n b rem` at the constant
-- grading (recon _ b r = b ℕ+ r) — the witness that makes a pair of
-- watermarks an exact DECOMPOSITION rather than two numbers that happen to
-- be ordered. Without it, `feed-lwm` and `draw-hwm` are merely comparable;
-- with it, the residue is forced to be the unique thing bridging them.
--
-- ⚑ PROVED BY INDUCTION ON THE `≤` PROOF, NOT IMPORTED. Three name-probes
-- (`m+n∸m≡n`, `+-∸-assoc`, `∸-suc`) each returned "no definer" — which is a
-- fact about the SPELLING I guessed, never about the substrate. Rather than
-- guess a fourth, this derives it from `Foundation.Nat.Le`'s own
-- constructors (`z≤n` / `s≤s`), which `agda_defs --provides` confirms are
-- the whole interface. Two cases, no dependency.
------------------------------------------------------------------------

actor-wedge-eq : ∀ {b a} → b ≤ a → b ℕ+ (a ∸ b) ≡ a
actor-wedge-eq {zero}  {a}     z≤n       = refl
actor-wedge-eq {suc b} {suc a} (s≤s b≤a) = cong suc (actor-wedge-eq b≤a)
