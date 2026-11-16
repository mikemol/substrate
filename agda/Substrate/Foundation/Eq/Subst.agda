------------------------------------------------------------------------
-- Substrate.Foundation.Eq.Subst
--
-- Defines: subst
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.Subst where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq



subst : {A : Set a} (P : A → Set b) {x y : A} → x ≡ y → P x → P y
subst _ refl p = p
