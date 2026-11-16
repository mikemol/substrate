------------------------------------------------------------------------
-- Substrate.Foundation.Eq.Trans
--
-- Defines: trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.Trans where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq



trans : {A : Set a} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl q = q
