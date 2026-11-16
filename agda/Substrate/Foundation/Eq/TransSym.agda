------------------------------------------------------------------------
-- Substrate.Foundation.Eq.TransSym
--
-- Defines: trans-sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.TransSym where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



trans-sym : {A : Set a} {x y z : A} → x ≡ y → z ≡ y → x ≡ z
trans-sym p q = trans p (sym q)
