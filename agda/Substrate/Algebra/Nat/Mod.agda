------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod
--
-- Substrate-native modular reduction `_mod-suc_ : ℕ → ℕ → ℕ`.
--
-- The cleanest read: `a mod-suc b` is the canonical-form
-- representative of `a` in the equivalence class of `_≡[ b ]_` on ℕ
-- (the Quotient instance ℕ / ≡[b], where the divisor is `suc b`).
--
-- The substrate's [[homology-cohomology-recursion]] reading:
-- Substrate.Algebra.Quotient gives the universal property; this
-- file gives the canonical-form function for the modular instance.
-- The earlier GCD module's `construct-wedge` was a bridge to
-- stdlib's `Data.Nat.DivMod`; this module replaces it for the
-- mod-reduction-only use case.
--
-- Recursion: STRUCTURAL on `a` alone, no well-founding needed. The
-- step `(suc a) mod-suc b` uses the IH `(a mod-suc b)`:
--   - if suc (a mod-suc b) < suc b, advance the remainder by one;
--   - else (it was = b, the max), wrap to zero.
--
-- This is the substrate's first piece of "modular arithmetic from
-- scratch", with no Data.Nat.DivMod / Data.Nat.Divisibility /
-- Induction.WellFounded touchpoints.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _<_; _<?_; s≤s; z≤n)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (Dec; yes; no)

------------------------------------------------------------------------
-- 1. Modular reduction.
--
-- `a mod-suc b` returns the canonical-form representative of `a`
-- modulo `suc b`. The divisor is stored as `suc b` rather than as
-- an arbitrary positive ℕ so non-zero-ness is structural.
------------------------------------------------------------------------

_mod-suc_ : ℕ → ℕ → ℕ
zero   mod-suc _ = zero
suc a  mod-suc b with suc (a mod-suc b) <? suc b
... | yes _ = suc (a mod-suc b)
... | no  _ = zero

------------------------------------------------------------------------
-- 2. The remainder-bound.
--
-- `a mod-suc b < suc b` always: the result lives in {0, 1, …, b}.
-- Proof by induction on `a`, dispatching on the same with-clause
-- that defines `_mod-suc_`.
------------------------------------------------------------------------

mod-suc-bound : (a b : ℕ) → (a mod-suc b) < suc b
mod-suc-bound zero    b = s≤s z≤n
mod-suc-bound (suc a) b with suc (a mod-suc b) <? suc b
... | yes sr<sb = sr<sb
... | no  _     = s≤s z≤n

------------------------------------------------------------------------
-- 3. Capstone.
--
-- Substrate-native `_mod-suc_` + its remainder bound. Downstream:
-- `Substrate.Algebra.Nat.ModEquiv` (QU11) routes here instead of
-- through `Substrate.Algebra.Nat.GCD`, breaking the stdlib chain
-- that blocks QU11-QU13. The full Wedge-equation (`a ≡ q * suc b +
-- r`) stays in GCD where the broader GCD/Bezout machinery uses it.
------------------------------------------------------------------------
