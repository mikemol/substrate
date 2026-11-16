------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQ.Cong2
--
-- Defines: cong₂
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQ; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQ.Cong2 where

open import Substrate.Foundation.Eq


cong₂ : {A B C : Set} (f : A → B → C) {x x' : A} {y y' : B}
      → x ≡ x' → y ≡ y' → f x y ≡ f x' y'
cong₂ f refl refl = refl
