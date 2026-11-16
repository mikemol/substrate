------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQ.Eqtrans
--
-- Defines: ≡trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQ; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQ.Eqtrans where

open import Substrate.Foundation.Eq


≡trans : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
≡trans refl q = q
