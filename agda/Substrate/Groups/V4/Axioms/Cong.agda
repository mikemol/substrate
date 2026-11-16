------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.Cong
--
-- ·-cong: _·₄_ respects propositional equality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.Cong where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations using (_·₄_)
open import Substrate.Foundation.Eq

·-cong : {x y u v : V₄} → x ≡ y → u ≡ v → (x ·₄ u) ≡ (y ·₄ v)
·-cong refl refl = refl
