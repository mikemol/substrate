------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedSignedRoundTrip
--
-- The two round-trip proofs for Reserved ↔ Axis × Bool. Each closes
-- by case-splits on the Axis (forward) or bit pattern (reverse).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedSignedRoundTrip where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedSignedMaps
  using (reserved-to-signed; signed-to-reserved)

signed-reserved-leftinv :
  (xy : Axis × Bool) →
  reserved-to-signed (signed-to-reserved xy) ≡ xy
signed-reserved-leftinv (D , _) = refl
signed-reserved-leftinv (C , _) = refl
signed-reserved-leftinv (S , _) = refl
signed-reserved-leftinv (W , _) = refl

reserved-signed-rightinv :
  (r : Reserved) →
  signed-to-reserved (reserved-to-signed r) ≡ r
reserved-signed-rightinv
  ((false , false , _ , .false , .false) , (refl , refl)) = refl
reserved-signed-rightinv
  ((true  , false , _ , .false , .false) , (refl , refl)) = refl
reserved-signed-rightinv
  ((false , true  , _ , .false , .false) , (refl , refl)) = refl
reserved-signed-rightinv
  ((true  , true  , _ , .false , .false) , (refl , refl)) = refl
