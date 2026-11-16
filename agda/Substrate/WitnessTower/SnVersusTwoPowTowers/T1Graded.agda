------------------------------------------------------------------------
-- Ⓣ₁ — the PERMUTATION witnessing tower as a GradedDivStr; the increment is an
-- insertion choice Fin (suc n). Cited from its home, not rebuilt.
-- Context: Substrate/WitnessTower/SnVersusTwoPowTowers/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnVersusTwoPowTowers.T1Graded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.Wedge.Graded
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.Graded

Ⓣ₁-graded : GradedDivStr Perm (λ n → Fin (suc n))
Ⓣ₁-graded = tower-graded
