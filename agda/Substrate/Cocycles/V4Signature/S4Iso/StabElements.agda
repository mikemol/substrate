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

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.SemidirectProduct.Stab
open import Substrate.Groups.SemidirectProduct.V.NonDSends
open import Substrate.Groups.SemidirectProduct.V.Private
open import Substrate.Groups.SemidirectProduct.V.SelfToD
open import Substrate.Groups.SemidirectProduct.V.VFor
open import Substrate.Groups.SemidirectProduct.V.VForAnchor
open import Substrate.Groups.SemidirectProduct.V.VForAnchorSends
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchor
open import Substrate.Groups.SemidirectProduct.V.VOfAxisAnchorSends
open import Substrate.Groups.SemidirectProduct.V.VOfAxisUnique
open import Substrate.Groups.SemidirectProduct.V.VSendsD
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
-- ⚑ THE CLAUSE NAMED THE WRONG PARENT, not merely a dissolved one. `SFinRoundTrip`
-- is gone, but these five names were never its: `transposition` and
-- `transposition-fixes-third` are `.Transposition`'s, and `s3-id`/`s3-csw`/`s3-cws`
-- are `.S3Elements`' — SIBLING leaves. So `rewire_to_leaves` was right to refuse:
-- it maps a parent onto ITS OWN leaves, and no leaf of `SFinRoundTrip` provides
-- these. `agda_defs <name>` places each one directly.
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.S3Elements
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

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
