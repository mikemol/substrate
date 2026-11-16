------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Conn4
--
-- Defines: conn4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Conn4 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.OccKTo0
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0



------------------------------------------------------------------------
-- conn4 (orbit-hits-once) and conn5 (close): Φ_p(σ_p) = A ⟹ dim ker = p−1.
------------------------------------------------------------------------

conn4 : ∀ {n} (k j : Fin (suc n)) → occ (suc n) k j ≡ 𝟙
conn4 k j = trans (occ-k-to-0 k j) (occ-0 j)
