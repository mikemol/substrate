------------------------------------------------------------------------
-- Substrate.Lojban.PlaceStructure.SelbriPostcomposeId
--
-- Defines: selbri-postcompose-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.PlaceStructure; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.PlaceStructure.SelbriPostcomposeId where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Lojban.PlaceStructure.Private
open import Substrate.Lojban.PlaceStructure.Selbri
open import Substrate.Lojban.PlaceStructure.SelbriPostcompose
open import Substrate.Lojban.Fragment.Carriers
open import Substrate.Lojban.Bridi



------------------------------------------------------------------------
-- 3. Identity preservation (pointwise).
--
-- Post-composing with the identity on Sem reproduces the original
-- apply on every argument vector.
------------------------------------------------------------------------

selbri-postcompose-id :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (S : Selbri n Sumti Sem) →
  (args : Vec Sumti n) →
  apply (selbri-postcompose (λ x → x) S) args ≡ apply S args
selbri-postcompose-id _ _ = refl
