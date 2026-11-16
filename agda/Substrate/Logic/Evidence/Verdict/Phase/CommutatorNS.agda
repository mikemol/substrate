------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.CommutatorNS
--
-- Defines: commutator-N₊-S
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.CommutatorNS where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Logic.Evidence.Verdict.Phase.NegPosCompnegNeg



------------------------------------------------------------------------
-- The cocycle (el-atlas §5.10c): the commutator [N₊, S] = −id, with
-- N₊ = negPos and S = swapE (both involutions, so the commutator is the
-- alternating fourfold product).
------------------------------------------------------------------------

commutator-N₊-S : (x : Evidence) → negPos (swapE (negPos (swapE x))) ≡ negBoth x
commutator-N₊-S ⟨ p , n ⟩ = refl
