------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerConcatEq
--
-- Defines: power-concat-eq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.NthPower.Concat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.Word
module Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerConcatEq (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Core n



------------------------------------------------------------------------
-- 1. power-concat-eq: concatenating powers adds exponents.
------------------------------------------------------------------------

-- ⚑ `k₁ + k₂` → `k₁ ℕ+ k₂` (Ⓑ2c-BRIDGE10‴).  The pre-split parent wrote `_+_`,
-- and the tree-wide ℕ rename made ℕ-addition `_ℕ+_` at source; bare `+` now
-- resolves only to `Algebra.Z.Int` / `Groups.F2Cubed`, neither of them ℕ.  The
-- dissolved conduit had been supplying the old spelling.
power-concat-eq : (k₁ k₂ : ℕ) → power k₁ ++ power k₂ ≡ power (k₁ ℕ+ k₂)
power-concat-eq zero     k₂ = refl
power-concat-eq (suc k₁) k₂ = cong (a ∷_) (power-concat-eq k₁ k₂)
