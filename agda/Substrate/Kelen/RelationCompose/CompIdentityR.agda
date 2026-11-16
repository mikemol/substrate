------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.CompIdentityR
--
-- Defines: ∘ᴿ-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.CompIdentityR where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Op
open import Substrate.Foundation.Eq
open import Substrate.Kelen.RelationCompose.Preamble
open import Substrate.Kelen.RelationCompose.Comp



∘ᴿ-identityʳ : (w : KelenWord) → w ∘ᴿ ε ≡ w
∘ᴿ-identityʳ = ++-identity-right
