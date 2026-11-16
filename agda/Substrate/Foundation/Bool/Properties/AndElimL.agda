------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndElimL
--
-- Defines: ∧-elimˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndElimL where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Eq
-- here from Realizability.Charter and …Wedge.GUnit (both re-proved them; the
-- carrier home is Bool's properties).
∧-elimˡ : {a b : Bool} → (a ∧ b) ≡ true → a ≡ true
∧-elimˡ {true}  _ = refl
∧-elimˡ {false} ()
