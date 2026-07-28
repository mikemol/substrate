------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3
--
-- Slice 17: the OrbitKey ↔ SFin.Permutation 3 chirality choice for
-- the CY-5 cocycle. File-per-lemma:
--
--   OrbitKey-S3.Transposition       — parametric (i j) transposition + fixes-third
--   OrbitKey-S3.Cycle3              — parametric 3-cycle
--   OrbitKey-S3.S3Elements          — the 6 named s3-* elements
--   OrbitKey-S3.OrbitKeyToS3        — the chirality choice function
--   OrbitKey-S3.S3ToOrbitKey        — inverse direction + cong
--   OrbitKey-S3.OrbitKeyRoundTrip   — s3∘key ≡ id on OrbitKey
--   OrbitKey-S3.SFinApplyInj        — SFin.apply injectivity
--   OrbitKey-S3.SFinRoundTrip       — key∘s3 ≡ id on SFin.Permutation 3
--
-- The OrbitKey ↔ s3-* labeling is the cocycle's chirality choice —
-- one of 6! = 720 valid labelings; per
-- [[feedback-ordering-is-chirality-choice]] downstream code MUST
-- consume the labeling abstractly via orbit-key-to-s3 / s3-to-orbit-key,
-- not by pattern-matching on specific (Pairing, Chirality) ↔ Fin 3
-- indices.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3 where

open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Cycle3
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3Elements
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyRoundTrip
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip