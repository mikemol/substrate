------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.ConsAllLen
--
-- Defines: consAll-len
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.ConsAllLen where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.XorComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.WitnessTower.SimplicialBoundary.ConsAll
open import Substrate.WitnessTower.SimplicialBoundary.Len


consAll-len : (x : A) (fs : List (List A)) → len (consAll x fs) ≡ len fs
consAll-len x []       = refl
consAll-len x (f ∷ fs) = cong suc (consAll-len x fs)
