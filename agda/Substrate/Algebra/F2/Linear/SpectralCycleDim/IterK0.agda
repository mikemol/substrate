------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.IterK0
--
-- Defines: σ-iter-k0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.IterK0 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans



-- every k is reachable from 0 by the orbit: σ-iterate(toℕ k) cyc 0 ≡ k.
σ-iter-k0 : ∀ {n} (k : Fin (suc n)) → σ-iterate (toℕ k) (cyclic-suc {n}) (zero {n}) ≡ k
σ-iter-k0 {n} k =
  toℕ-injective (trans (σ-iterate-toℕ (toℕ k) zero) (mod-suc-id (toℕ k) n (toℕ-bound k)))
