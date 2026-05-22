------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.Iso
--
-- Reserved↔SignedAxis : packaged Reserved ↔ Axis × Bool bijection.
-- The first reading of the 32+8 ambient: the 8 reserved codewords
-- correspond to (axis, sign) pairs — the Hodge 1-form layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.Iso where

open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Product using (_×_)
open import Substrate.Algebra.Bijection using (_↔_; mk↔ₛ′)
open import Substrate.Axes using (Axis)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedSignedMaps
  using (reserved-to-signed; signed-to-reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedSignedRoundTrip
  using (signed-reserved-leftinv; reserved-signed-rightinv)

Reserved↔SignedAxis : Reserved ↔ (Axis × Bool)
Reserved↔SignedAxis = mk↔ₛ′
  reserved-to-signed
  signed-to-reserved
  signed-reserved-leftinv
  reserved-signed-rightinv
