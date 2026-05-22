------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.S3Elements
--
-- The 6 named elements of SFin.Permutation 3 used by the cocycle's
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

open import Substrate.Foundation.Fin using (zero; suc)
import Substrate.Groups.SFin as SFin
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
  using (transposition)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Cycle3
  using (cycle3)

s3-id : SFin.Permutation 3
s3-id = SFin.ε

s3-sw : SFin.Permutation 3
s3-sw = transposition (suc zero) (suc (suc zero))

s3-cs : SFin.Permutation 3
s3-cs = transposition zero (suc zero)

s3-cw : SFin.Permutation 3
s3-cw = transposition zero (suc (suc zero))

s3-csw : SFin.Permutation 3
s3-csw = cycle3 zero (suc zero) (suc (suc zero))

-- Inverse of s3-csw via SFin._⁻¹.
s3-cws : SFin.Permutation 3
s3-cws = s3-csw SFin.⁻¹
