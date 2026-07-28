------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3
--
-- orbit-key-to-s3 : OrbitKey → SFinP.Permutation 3.
-- The cocycle's chirality choice (one of 6! = 720 valid labelings).
-- Downstream code MUST consume this abstractly per
-- [[feedback-ordering-is-chirality-choice]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3 where

open import Substrate.Foundation.Product using (_,_)
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Cocycles.V4Signature.Chirality.Type using (Chirality; even; odd)
open import Substrate.Cocycles.V4Signature.OrbitKey.Type using (OrbitKey)
open import Substrate.Cocycles.V4Signature.Pairing.Type using (Pairing; α-pair; β-pair; γ-pair)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3Elements
  using (s3-id; s3-sw; s3-cs; s3-cw; s3-csw; s3-cws)

orbit-key-to-s3 : OrbitKey → SFinP.Permutation 3
orbit-key-to-s3 (α-pair , even) = s3-id
orbit-key-to-s3 (α-pair , odd)  = s3-sw
orbit-key-to-s3 (β-pair , even) = s3-csw
orbit-key-to-s3 (β-pair , odd)  = s3-cs
orbit-key-to-s3 (γ-pair , even) = s3-cws
orbit-key-to-s3 (γ-pair , odd)  = s3-cw
