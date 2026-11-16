------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.ModN
--
-- QU12 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- ℕ / ≡[m] as a Quotient + Canonical instance. The canonical form
-- is the modular remainder `_mod-suc m`, the substrate-native
-- divisor-as-suc-of-something flavour of mod m+1.
--
-- This is the substrate's first concrete arithmetic quotient with a
-- well-defined canonical representative — the bridge between the
-- algebraic Quotient interface and the modular arithmetic that CRT
-- (QU13) sits on top of.
--
-- Per [[project-composite-torsion-euler-substrate]]: ℕ-mod-m is
-- the base case of the substrate's number-theoretic tower; with
-- coprime (m, n), QU13 will provide the CRT splitter.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.ModN where

open import Substrate.Foundation.Nat.Nat

-- ⚑ `_mod-suc_` WAS REACHED THROUGH `ModEquiv`'s `public` RE-EXPORT (Ⓑ2c),
-- which this one `using` list mixed with ModEquiv's OWN four `≡[m]` names —
-- one clause, two providers, and no way to see from here that the canonical
-- form comes from `Nat.Mod`.  Binding it at its real home is the PRECONDITION
-- for retiring that re-export, not a separate cleanup.
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.ModEquiv
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. Per-modulus Quotient instance.
--
-- For each `m : ℕ` the modulus is `suc m`. The equivalence relation
-- is `_≡[ m ]_` over ℕ.
------------------------------------------------------------------------

ModN-Quotient : (m : ℕ) → Quotient ℕ (λ a b → a ≡[ m ] b)
ModN-Quotient m = record
  { ≈-refl  = ≡[m]-refl m
  ; ≈-sym   = λ {a} {b}   → ≡[m]-sym   {m} {a} {b}
  ; ≈-trans = λ {a} {b} {c} → ≡[m]-trans {m} {a} {b} {c}
  }

------------------------------------------------------------------------
-- 2. No Canonical extension yet.
--
-- The natural canonical-form function is `_mod-suc m` itself. The
-- three required laws break down as:
--
--   1. respect:     a ≡[ m ] b ⟹ a mod-suc m ≡ b mod-suc m
--                   ← immediate (this IS the definition).
--   2. soundness:   a ≡[ m ] (a mod-suc m)
--                   ← needs idempotence (below).
--   3. idempotence: (a mod-suc m) mod-suc m ≡ a mod-suc m
--                   ← the load-bearing fact; requires unfolding
--                     the Wedge for r < suc m showing the
--                     re-wedge collapses to (0, r). Its own slice
--                     (deferred to Phase D, paired with EEA-as-
--                     morphism).
--
-- ModN therefore attaches as a base Quotient instance only at this
-- slice. Once the idempotence lemma lands as a substrate-native
-- proof (not a postulate), the Canonical extension follows
-- mechanically — same shape as the Coxeter / F₂Parity attachments.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 3. Capstone for QU12.
--
-- ℕ-mod-(suc m) attached as base Quotient. The Canonical extension
-- is a one-shot mechanical lift once `mod-suc-idempotent` is
-- discharged. QU13 builds CRT on top of this base form.
------------------------------------------------------------------------
