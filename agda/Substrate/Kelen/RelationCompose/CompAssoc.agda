------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.CompAssoc
--
-- Defines: ∘ᴿ-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.CompAssoc where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Foundation.Eq
open import Substrate.Kelen.RelationCompose.Preamble
open import Substrate.Kelen.RelationCompose.Comp



------------------------------------------------------------------------
-- 3. Associativity.
--
-- (w₁ ∘ᴿ w₂) ∘ᴿ w₃ ≡ w₁ ∘ᴿ (w₂ ∘ᴿ w₃). Inherited from Coxeter.Word's
-- ++-assoc. Together with the identity laws, this makes
-- (KelenWord, _∘ᴿ_, ε) a monoid — the FREE relation monoid at the
-- linguistic site.
------------------------------------------------------------------------

∘ᴿ-assoc :
  (w₁ w₂ w₃ : KelenWord) →
  (w₁ ∘ᴿ w₂) ∘ᴿ w₃ ≡ w₁ ∘ᴿ (w₂ ∘ᴿ w₃)
∘ᴿ-assoc = ++-assoc
