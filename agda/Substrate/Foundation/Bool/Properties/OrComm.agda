------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.OrComm
--
-- Defines: ∨-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.OrComm where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or



∨-comm : (a b : Bool) → a ∨ b ≡ b ∨ a
∨-comm true  true  = refl
∨-comm true  false = refl
∨-comm false true  = refl
∨-comm false false = refl
