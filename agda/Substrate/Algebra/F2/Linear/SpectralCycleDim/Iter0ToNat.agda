------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Iter0ToNat
--
-- Defines: σ-iter0-toℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Iter0ToNat where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
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
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ



------------------------------------------------------------------------
-- The Kronecker base: at k=0 the orbit is the identity enumeration (step i
-- lands on toℕ⁻¹ i), so j is visited exactly at step toℕ j ⟹ occ(p) 0 j ≡ 𝟙.
------------------------------------------------------------------------

-- step i (i < p) of the orbit from 0 has toℕ = i.
σ-iter0-toℕ : ∀ {n} (i : ℕ) → i < suc n →
              toℕ (σ-iterate i (cyclic-suc {n}) (zero {n})) ≡ i
σ-iter0-toℕ {n} i i<sn = trans (σ-iterate-toℕ i (zero {n})) (mod-suc-id i n i<sn)
