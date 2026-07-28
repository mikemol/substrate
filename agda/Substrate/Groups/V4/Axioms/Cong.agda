------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.Cong
--
-- ·-cong: _·_ respects propositional equality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.Cong where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.V4.Operations using (_·_)

·-cong : {x y u v : V₄} → x ≡ y → u ≡ v → (x · u) ≡ (y · v)
·-cong refl refl = refl
