------------------------------------------------------------------------
-- Substrate.Foundation.Bool.And
--
-- Defines: _∧_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.And where

open import Substrate.Foundation.Bool.Bool

infixr 6 _∧_


_∧_ : Bool → Bool → Bool
true  ∧ b = b
false ∧ _ = false
