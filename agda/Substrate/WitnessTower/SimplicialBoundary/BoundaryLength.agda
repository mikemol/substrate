------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.BoundaryLength
--
-- Defines: boundary-length
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.BoundaryLength where

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
open import Substrate.WitnessTower.SimplicialBoundary.Boundary
open import Substrate.WitnessTower.SimplicialBoundary.Len
open import Substrate.WitnessTower.SimplicialBoundary.ConsAllLen



boundary-length : (xs : List A) → len (boundary xs) ≡ len xs
boundary-length []       = refl
boundary-length (x ∷ xs) =
  cong suc (trans (consAll-len x (boundary xs)) (boundary-length xs))
