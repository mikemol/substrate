------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.AxisBits
--
-- axis-from-bits / axis-to-bits : the Bool² ↔ Axis correspondence,
-- with round-trip witnesses. Pure-bit encoding convention; the
-- pairing on Reserved uses these.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.AxisBits where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Axes using (Axis; D; C; S; W)

axis-from-bits : Bool → Bool → Axis
axis-from-bits false false = D
axis-from-bits true  false = C
axis-from-bits false true  = S
axis-from-bits true  true  = W

axis-to-bits : Axis → Bool × Bool
axis-to-bits D = false , false
axis-to-bits C = true  , false
axis-to-bits S = false , true
axis-to-bits W = true  , true

axis-bits-id :
  (a : Axis) →
  axis-from-bits (proj₁ (axis-to-bits a)) (proj₂ (axis-to-bits a)) ≡ a
axis-bits-id D = refl
axis-bits-id C = refl
axis-bits-id S = refl
axis-bits-id W = refl

bits-axis-id :
  (b₀v b₁v : Bool) →
  axis-to-bits (axis-from-bits b₀v b₁v) ≡ (b₀v , b₁v)
bits-axis-id false false = refl
bits-axis-id true  false = refl
bits-axis-id false true  = refl
bits-axis-id true  true  = refl
