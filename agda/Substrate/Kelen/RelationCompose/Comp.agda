------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.Comp
--
-- Defines: _∘ᴿ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.Comp where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.RelationCompose.Preamble

infixr 5 _∘ᴿ_


_∘ᴿ_ : KelenWord → KelenWord → KelenWord
_∘ᴿ_ = _++_
