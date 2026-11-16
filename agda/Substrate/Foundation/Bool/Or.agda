------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Or
--
-- Defines: _∨_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Or where

open import Substrate.Foundation.Bool.Bool

infixr 5 _∨_


_∨_ : Bool → Bool → Bool
true  ∨ _ = true
false ∨ b = b
