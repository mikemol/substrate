------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.AndIdentityL
--
-- Defines: ∧-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.AndIdentityL where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Eq
-- from Algebra.Semiring.Instances (where they were proven "for lack of a prior
-- home"). Their carrier home is Bool's properties. The identityˡ pair also
-- completes the chirality with the identityʳ above.
∧-identityˡ : (a : Bool) → true ∧ a ≡ a
∧-identityˡ _ = refl
