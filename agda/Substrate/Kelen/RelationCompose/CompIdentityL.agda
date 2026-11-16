------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.CompIdentityL
--
-- Defines: ∘ᴿ-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.CompIdentityL where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Op
open import Substrate.Foundation.Eq
open import Substrate.Kelen.RelationCompose.Preamble
open import Substrate.Kelen.RelationCompose.Comp



------------------------------------------------------------------------
-- 2. Identity laws.
--
-- The empty word ε is the two-sided identity for ∘ᴿ. Inherited
-- from Coxeter.Word's ++-identity-left / ++-identity-right.
------------------------------------------------------------------------

∘ᴿ-identityˡ : (w : KelenWord) → ε ∘ᴿ w ≡ w
∘ᴿ-identityˡ = ++-identity-left
