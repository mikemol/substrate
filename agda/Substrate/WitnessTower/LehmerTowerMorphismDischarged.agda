------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerTowerMorphismDischarged
--
-- THE DISCHARGE AS A CHECKABLE TERM (not a prose pointer). LehmerTowerMorphism
-- STATES its ◆AI-3-pkg-twisted-lehmer obligation as a module parameter, and its
-- docstring can only POINT (in prose) to the discharge — a cycle forbids it
-- importing InsertionParity (which imports LehmerTowerMorphism). This module
-- sits BELOW both, imports BOTH, and reifies the reverse-direction tie:
--
--   · obligation-discharged has EXACTLY LehmerTowerMorphism's `insertion-parity`
--     parameter type, with body InsertionParity's Route-B proof. If either the
--     stated obligation or the proof drifts, THIS breaks — a machine-checked
--     comparison, not a comment.
--   · twisted-lehmer-sign-morphism re-homes the packaged UNCONDITIONAL morphism.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerTowerMorphismDischarged where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.Algebra.Wedge.Graded.Morphism using (GradedDivStrMorphism)
open import Substrate.WitnessTower.LehmerTowerMorphism.F2Target
open import Substrate.WitnessTower.LehmerTowerMorphism.FinParity
open import Substrate.WitnessTower.LehmerTowerMorphism.LehmerGraded
open import Substrate.WitnessTower.InsertionParity
  using (insertion-parity-B; sign-lehmer-morphism-unconditional)
open import Substrate.Foundation.Eq

-- the fact LehmerTowerMorphism states as its `insertion-parity` parameter,
-- proved unconditionally (InsertionParity, Route B). The type is written to
-- match the parameter; the body is the proof — the tie is checked here.
obligation-discharged :
  {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) →
  signF (decode (l ◂ p)) ≡ (finParity p +F signF (decode l))
obligation-discharged = insertion-parity-B

-- the packaged UNCONDITIONAL twisted-Lehmer sign-morphism, discoverable here.
twisted-lehmer-sign-morphism : GradedDivStrMorphism lehmer-graded F₂-target
twisted-lehmer-sign-morphism = sign-lehmer-morphism-unconditional
