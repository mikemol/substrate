------------------------------------------------------------------------
-- Substrate.Foundation.Eq.Cong
--
-- Defines: cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.Cong where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq



cong : {A : Set a} {B : Set b} (f : A → B) {x y : A} → x ≡ y → f x ≡ f y
cong f refl = refl
