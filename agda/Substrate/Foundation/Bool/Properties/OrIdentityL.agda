------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.OrIdentityL
--
-- Defines: ∨-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.OrIdentityL where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or



∨-identityˡ : (a : Bool) → false ∨ a ≡ a
∨-identityˡ _ = refl
