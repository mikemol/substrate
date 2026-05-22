------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.NonDegenerate
--
-- NonDegenerate M : the radical contains only 𝟎ⱽ. The kernel-free
-- predicate expressed via categorical primitives (Wide-Meet of
-- IsEqualised); same structure at any n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.NonDegenerate where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)
open import Substrate.Algebra.F2.SymBilinForm.Radical using (Radical)

NonDegenerate : ∀ {n} → BilinForm n → Set
NonDegenerate {n} M = (v : Vector n) → Radical M v → v ≡ 𝟎ⱽ
