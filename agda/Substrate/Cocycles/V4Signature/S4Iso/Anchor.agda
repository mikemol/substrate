------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso.Anchor
--
-- Parametric anchor dispatcher and its anchor-specialisations
-- (D, C, S, W) plus the stop-anchoring decomposition theorems.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso.Anchor where

open import Substrate.Foundation.Product using (_,_; proj₁; proj₂; Σ; Σ-syntax)
open import Substrate.Foundation.Eq using (_≡_; trans)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4 using (Permutation)
  renaming (apply to applyₛ)
open import Substrate.Groups.SemidirectProduct
  using (Stab)
open import Substrate.Groups.Stab-S3-Extend
  using (extend; extend-apply-pointwise-cong)
open import Substrate.Groups.Stab-S3-Restrict using (restrict)
open import Substrate.Groups.Stab-S3-Iso using (extend-restrict)
import Substrate.Groups.SFin as SFin
open import Substrate.Cocycles.V4Signature
  using (OrbitKey)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3
  using (orbit-key-to-s3; s3-to-orbit-key; orbit-key-to-s3-of-s3-to-orbit-key)

------------------------------------------------------------------------
-- Parametric anchor dispatcher.
------------------------------------------------------------------------

orbit-key-to-stab-anchor : (X : Axis) → OrbitKey → Permutation
orbit-key-to-stab-anchor X ok = proj₁ (extend X (orbit-key-to-s3 ok))

orbit-key-to-stab-anchor-fixes :
  (X : Axis) (ok : OrbitKey) → Stab X (orbit-key-to-stab-anchor X ok)
orbit-key-to-stab-anchor-fixes X ok = proj₂ (extend X (orbit-key-to-s3 ok))

------------------------------------------------------------------------
-- D-anchor specialisation (the cocycle's chirality choice anchor).
------------------------------------------------------------------------

orbit-key-to-stab-d : OrbitKey → Permutation
orbit-key-to-stab-d = orbit-key-to-stab-anchor D

orbit-key-to-stab-d-fixes-D :
  (ok : OrbitKey) → Stab D (orbit-key-to-stab-d ok)
orbit-key-to-stab-d-fixes-D = orbit-key-to-stab-anchor-fixes D

------------------------------------------------------------------------
-- C/S/W anchor specialisations.
------------------------------------------------------------------------

orbit-key-to-stab-C : OrbitKey → Permutation
orbit-key-to-stab-C = orbit-key-to-stab-anchor C

orbit-key-to-stab-C-fixes-C :
  (ok : OrbitKey) → Stab C (orbit-key-to-stab-C ok)
orbit-key-to-stab-C-fixes-C = orbit-key-to-stab-anchor-fixes C

orbit-key-to-stab-S : OrbitKey → Permutation
orbit-key-to-stab-S = orbit-key-to-stab-anchor S

orbit-key-to-stab-S-fixes-S :
  (ok : OrbitKey) → Stab S (orbit-key-to-stab-S ok)
orbit-key-to-stab-S-fixes-S = orbit-key-to-stab-anchor-fixes S

orbit-key-to-stab-W : OrbitKey → Permutation
orbit-key-to-stab-W = orbit-key-to-stab-anchor W

orbit-key-to-stab-W-fixes-W :
  (ok : OrbitKey) → Stab W (orbit-key-to-stab-W ok)
orbit-key-to-stab-W-fixes-W = orbit-key-to-stab-anchor-fixes W

------------------------------------------------------------------------
-- Parametric-over-anchor decomposition theorems.
------------------------------------------------------------------------

stab-anchor-decomposes :
  (X : Axis) (σ : Permutation) (σ-stab : Stab X σ) →
  Σ[ s ∈ SFin.Permutation 3 ]
    ((x : Axis) → applyₛ (proj₁ (extend X s)) x ≡ applyₛ σ x)
stab-anchor-decomposes X σ σ-stab =
  restrict X (σ , σ-stab) , extend-restrict X σ σ-stab

stab-anchor-decomposes-orbitkey :
  (X : Axis) (σ : Permutation) (σ-stab : Stab X σ) →
  Σ[ ok ∈ OrbitKey ]
    ((x : Axis) → applyₛ (proj₁ (extend X (orbit-key-to-s3 ok))) x
                ≡ applyₛ σ x)
stab-anchor-decomposes-orbitkey X σ σ-stab =
  s3-to-orbit-key s , λ x →
    trans
      (extend-apply-pointwise-cong X
         (orbit-key-to-s3 (s3-to-orbit-key s)) s
         (orbit-key-to-s3-of-s3-to-orbit-key s) x)
      (extend-restrict X σ σ-stab x)
  where
    s : SFin.Permutation 3
    s = restrict X (σ , σ-stab)
