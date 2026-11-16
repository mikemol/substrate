------------------------------------------------------------------------
-- Substrate.Foundation.Eq.Sym
--
-- Defines: sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.Sym where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq



sym : {A : Set a} {x y : A} → x ≡ y → y ≡ x
sym refl = refl
