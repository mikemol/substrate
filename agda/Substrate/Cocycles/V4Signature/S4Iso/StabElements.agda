------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso.StabElements
--
-- The 6 canonical Stab(D) elements (stab-id, stab-sw, stab-cs, stab-cw,
-- stab-csw, stab-cws) and their fixes-* verifications. Each is built
-- parametrically via `extend D <SFin element>`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso.StabElements where

open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.SemidirectProduct.Stab
open import Substrate.Groups.SemidirectProduct.V
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Groups.SemidirectProduct.Factorisation
open import Substrate.Groups.V4-Embedding
  using (Stab)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Groups.Stab-S3 using (fin3-to-non-anchor)
open import Substrate.Groups.Stab-S3-Extend using (extend)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3Elements
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Cycle3
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyToS3
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3ToOrbitKey
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.OrbitKeyRoundTrip
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinApplyInj
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip
  using (transposition; transposition-fixes-third; s3-id; s3-csw; s3-cws)

------------------------------------------------------------------------
-- Identity in Stab(D).
------------------------------------------------------------------------

stab-id : Permutation
stab-id = proj₁ (extend D s3-id)

------------------------------------------------------------------------
-- Three transpositions.
------------------------------------------------------------------------

-- (SW): D↔D, C↔C, S↔W.
stab-sw : Permutation
stab-sw = proj₁ (extend D (transposition ₁ ₂))

-- (CS): D↔D, W↔W, C↔S.
stab-cs : Permutation
stab-cs = proj₁ (extend D (transposition zero ₁))

-- (CW): D↔D, S↔S, C↔W.
stab-cw : Permutation
stab-cw = proj₁ (extend D (transposition zero ₂))

------------------------------------------------------------------------
-- Two 3-cycles.
------------------------------------------------------------------------

-- (CSW): C→S→W→C, D fixed.
stab-csw : Permutation
stab-csw = proj₁ (extend D s3-csw)

-- (CWS): C→W→S→C, D fixed. Inverse of (CSW).
stab-cws : Permutation
stab-cws = proj₁ (extend D s3-cws)

------------------------------------------------------------------------
-- Verification that each constructed element is in Stab(D).
------------------------------------------------------------------------

stab-id-fixes-D : Stab D stab-id
stab-id-fixes-D = refl

stab-id-fixes-C : Stab C stab-id
stab-id-fixes-C = refl

stab-id-fixes-S : Stab S stab-id
stab-id-fixes-S = refl

stab-id-fixes-W : Stab W stab-id
stab-id-fixes-W = refl

stab-sw-fixes-D : Stab D stab-sw
stab-sw-fixes-D = refl

stab-sw-fixes-C : Stab C stab-sw
stab-sw-fixes-C = cong (fin3-to-non-anchor D) (transposition-fixes-third ₁ ₂ zero (λ ()) (λ ()))

stab-cs-fixes-D : Stab D stab-cs
stab-cs-fixes-D = refl

stab-cs-fixes-W : Stab W stab-cs
stab-cs-fixes-W = cong (fin3-to-non-anchor D) (transposition-fixes-third zero ₁ ₂ (λ ()) (λ ()))

stab-cw-fixes-D : Stab D stab-cw
stab-cw-fixes-D = refl

stab-cw-fixes-S : Stab S stab-cw
stab-cw-fixes-S = cong (fin3-to-non-anchor D) (transposition-fixes-third zero ₂ ₁ (λ ()) (λ ()))

stab-csw-fixes-D : Stab D stab-csw
stab-csw-fixes-D = refl

stab-cws-fixes-D : Stab D stab-cws
stab-cws-fixes-D = refl
