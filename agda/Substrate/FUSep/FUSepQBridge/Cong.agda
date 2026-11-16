------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQBridge.Cong
--
-- Defines: cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQBridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQBridge.Cong where

open import Substrate.Foundation.Eq


cong : {A B : Set} (f : A → B) {x y : A} → x ≡ y → f x ≡ f y
cong f refl = refl
