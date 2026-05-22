------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical
--
-- Dispatches act-hom-on-canonical across the 6 canonical S₃-pair cases,
-- routing each to its rotation/swap homomorphism witness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.HomRotations.HomId    using (hom-id)
open import Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot   using (hom-rot)
open import Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot2  using (hom-rot²)
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapAB    using (hom-swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapAG    using (hom-swap-αγ)
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapBG    using (hom-swap-βγ)

act-hom-on-canonical :
  ∀ {n h} (c-n : Z₃.Canonical n) (c-h : Z₂.Canonical h) →
  ∀ v₁ v₂ →
  act-on-canonical n h (v₁ V4.· v₂) ≡
  act-on-canonical n h v₁ V4.· act-on-canonical n h v₂
act-hom-on-canonical Z₃.c-ε  Z₂.c-ε = hom-id
act-hom-on-canonical Z₃.c-a  Z₂.c-ε = hom-rot
act-hom-on-canonical Z₃.c-aa Z₂.c-ε = hom-rot²
act-hom-on-canonical Z₃.c-ε  Z₂.c-a = hom-swap-αβ
act-hom-on-canonical Z₃.c-a  Z₂.c-a = hom-swap-αγ
act-hom-on-canonical Z₃.c-aa Z₂.c-a = hom-swap-βγ
