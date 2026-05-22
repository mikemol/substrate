------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedSignedMaps
--
-- reserved-to-signed / signed-to-reserved : the bidirectional maps
-- between Reserved and Axis × Bool (signed singletons / Hodge 1-form
-- basis × sign at dim 4).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedSignedMaps where

open import Substrate.Foundation.Bool using (Bool; false)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Axes using (Axis)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.AxisBits
  using (axis-from-bits; axis-to-bits)

reserved-to-signed : Reserved → Axis × Bool
reserved-to-signed ((b₀v , b₁v , b₂v , _ , _) , _) =
  axis-from-bits b₀v b₁v , b₂v

signed-to-reserved : Axis × Bool → Reserved
signed-to-reserved (a , sign) =
  (proj₁ (axis-to-bits a) , proj₂ (axis-to-bits a) , sign , false , false)
  , (refl , refl)
