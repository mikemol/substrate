------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedSignedMaps
--
-- reserved-to-signed / signed-to-reserved : the bidirectional maps
-- between Reserved and Axis × Bool (signed singletons / Hodge 1-form
-- basis × sign at dim 4).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedSignedMaps where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.AxisBits
  using (axis-from-bits; axis-to-bits)
open import Substrate.Foundation.Eq

reserved-to-signed : Reserved → Axis × Bool
reserved-to-signed ((b₀v , b₁v , b₂v , _ , _) , _) =
  axis-from-bits b₀v b₁v , b₂v

signed-to-reserved : Axis × Bool → Reserved
signed-to-reserved (a , sign) =
  (proj₁ (axis-to-bits a) , proj₂ (axis-to-bits a) , sign , false , false)
  , (refl , refl)
