------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyRoundTrip
--
-- s3-to-orbit-key-of-orbit-key-to-s3 :
--   (ok : OrbitKey) → s3-to-orbit-key (orbit-key-to-s3 ok) ≡ ok.
-- The OrbitKey-side round-trip; each of the 6 cases reduces by
-- computation on the named s3-X elements.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyRoundTrip where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Cocycles.V4Signature
  using (α-pair; β-pair; γ-pair; even; odd; OrbitKey)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3
  using (orbit-key-to-s3)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
  using (s3-to-orbit-key)

s3-to-orbit-key-of-orbit-key-to-s3 :
  (ok : OrbitKey) → s3-to-orbit-key (orbit-key-to-s3 ok) ≡ ok
s3-to-orbit-key-of-orbit-key-to-s3 (α-pair , even) = refl
s3-to-orbit-key-of-orbit-key-to-s3 (α-pair , odd)  = refl
s3-to-orbit-key-of-orbit-key-to-s3 (β-pair , even) = refl
s3-to-orbit-key-of-orbit-key-to-s3 (β-pair , odd)  = refl
s3-to-orbit-key-of-orbit-key-to-s3 (γ-pair , even) = refl
s3-to-orbit-key-of-orbit-key-to-s3 (γ-pair , odd)  = refl
