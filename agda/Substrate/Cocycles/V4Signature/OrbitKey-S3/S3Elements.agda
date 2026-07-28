------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.S3Elements
--
-- The 6 named elements of SFinP.Permutation 3 used by the cocycle's
-- chirality-choice labeling.
--
--   s3-id   = identity
--   s3-sw   = swap (1 2)
--   s3-cs   = swap (0 1)
--   s3-cw   = swap (0 2)
--   s3-csw  = 3-cycle 0→1→2→0
--   s3-cws  = 3-cycle 0→2→1→0 (= s3-csw⁻¹)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.S3Elements where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
import Substrate.Groups.SFin.Identity as SFinI
import Substrate.Groups.Symmetric.Permutation.SFinInverse as SFinV
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
  using (transposition)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Cycle3
  using (cycle3)

s3-id : SFinP.Permutation 3
s3-id = SFinI.ε

s3-sw : SFinP.Permutation 3
s3-sw = transposition ₁ ₂

s3-cs : SFinP.Permutation 3
s3-cs = transposition zero ₁

s3-cw : SFinP.Permutation 3
s3-cw = transposition zero ₂

s3-csw : SFinP.Permutation 3
s3-csw = cycle3 zero ₁ ₂

-- Inverse of s3-csw via SFinV._⁻¹.
s3-cws : SFinP.Permutation 3
s3-cws = s3-csw SFinV.⁻¹
