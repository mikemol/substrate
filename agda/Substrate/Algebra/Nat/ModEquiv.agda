------------------------------------------------------------------------
-- Substrate.Algebra.Nat.ModEquiv
--
-- QU11 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- Modular equivalence on ℕ: a ≡[m] b iff a mod (suc m) ≡ b mod
-- (suc m). Encoded via the substrate's Wedge primitive from
-- Substrate.Algebra.Nat.GCD — the wedge gives the (quotient,
-- remainder) decomposition, and the remainder IS the canonical
-- modular representative.
--
-- The modulus is stored as `m` with actual divisor `suc m`, mirroring
-- the substrate's denominator-minus-1 convention (Substrate.Algebra.Q,
-- Substrate.Foundation.Nat). This guarantees non-zero modulus at the
-- type level.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: builds on the
-- substrate's existing Wedge / EEATrace machinery rather than
-- pulling stdlib's modular-arithmetic ecosystem.
--
-- QU12 attaches this as a Quotient + Canonical instance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.ModEquiv where

open import Substrate.Foundation.Nat.Nat

-- ⚑ `public` RETIRED (Ⓑ2c).  Both consumers (`Quotient.CRT`, `Quotient.ModN`)
-- reached `_mod-suc_` through this forward and now bind `Nat.Mod` themselves —
-- that binding is the precondition for the removal, not a separate cleanup.
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
-- `_mod-suc_` now comes from the substrate-native module; no
-- dependency on stdlib's Data.Nat.DivMod chain. The earlier
-- Wedge-eq-based formulation lives in Substrate.Algebra.Nat.GCD
-- and is only consulted when the full quotient/remainder
-- reconstruction equation is needed.

------------------------------------------------------------------------
-- 2. Modular equivalence.
--
-- a ≡[m] b iff their remainders modulo (suc m) coincide. This is
-- the standard "congruence modulo m" relation, lifted to the
-- substrate's m-as-suc-of-something encoding.
------------------------------------------------------------------------

_≡[_]_ : ℕ → ℕ → ℕ → Set
a ≡[ m ] b = a mod-suc m ≡ b mod-suc m

------------------------------------------------------------------------
-- 3. Equivalence-relation witnesses.
------------------------------------------------------------------------

≡[m]-refl : (m a : ℕ) → a ≡[ m ] a
≡[m]-refl _ _ = refl

≡[m]-sym : {m a b : ℕ} → a ≡[ m ] b → b ≡[ m ] a
≡[m]-sym = sym

≡[m]-trans :
  {m a b c : ℕ} → a ≡[ m ] b → b ≡[ m ] c → a ≡[ m ] c
≡[m]-trans = trans

------------------------------------------------------------------------
-- 4. Capstone for QU11.
--
-- Modular equivalence _≡[ m ]_ defined via Wedge; the three
-- equivalence witnesses are immediate by `_mod-suc_` factoring
-- through propositional equality. QU12 attaches the Quotient
-- + Canonical instance.
------------------------------------------------------------------------
