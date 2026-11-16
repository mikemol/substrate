------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.IsSingleton
--
-- Defines: isSingleton
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.IsSingleton where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble



-- the singleton READOUT (map ⟷ relation): a fiber family is map-like when each
-- fiber is a subsingleton.  μΦ a singleton ⟺ the limit is a map (ALG-5).
isSingleton : {A : Set} → (A → Set) → Set
isSingleton {A} P = (a : A) (x y : P a) → x ≡ y
