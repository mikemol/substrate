------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.PlusSwap
--
-- Defines: +-swap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.PlusSwap where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



------------------------------------------------------------------------
-- ◆ip-invcount-recurrence — the ℕ-EXACT single-insertion inversion count.
-- Route A re-run at ℕ (sum, not xor): the count of tail entries below p is
-- permutation-invariant, hence = its value on id-perm = toℕ p.
------------------------------------------------------------------------

-- a ℕ+ (b ℕ+ c) ≡ b ℕ+ (a ℕ+ c) — the summand swap that adjacent transposition uses
-- (private: a local ℕ helper; NOT the F₂ `+-swap` of Algebra/F2/Linear/Cycle3).
+-swap : (a b c : ℕ) → a ℕ+ (b ℕ+ c) ≡ b ℕ+ (a ℕ+ c)
+-swap a b c =
  trans (sym (+ℕ-assoc a b c)) (trans (cong (_ℕ+ c) (+ℕ-comm a b)) (+ℕ-assoc b a c))
