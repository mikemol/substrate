------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.Len
--
-- Defines: len
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.Len where

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



-- a k-simplex (k+1 vertices) has exactly k+1 codim-1 faces — the f-vector edge
-- of WitnessTower.FaceCount (the faces of a face = its vertices).
len : {B : Set} → List B → ℕ
len []       = zero
len (_ ∷ xs) = suc (len xs)
