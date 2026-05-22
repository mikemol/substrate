------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso.Classify
--
-- TotalSpace, total-to-s4 (forward map), classify-CS,
-- stab-d-to-orbit-key (reverse map), s4-to-total, and the OrbitKey
-- round-trip ok-round-trip.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso.Classify where

open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4
  using (Permutation; _·_)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.SemidirectProduct
  using (Stab; v-for; s-for; s-for-fixes-anchor)
open import Substrate.Cocycles.V4Signature
  using (OrbitKey; α-pair; β-pair; γ-pair; even; odd; CY5-V4Signature)
open import Substrate.Cocycle using (IsomorphicCocycleStructure)

open import Substrate.Cocycles.V4Signature.S4Iso.Anchor public

------------------------------------------------------------------------
-- TotalSpace of the CY-5 cocycle.
------------------------------------------------------------------------

TotalSpace : Set
TotalSpace = IsomorphicCocycleStructure.TotalSpace CY5-V4Signature

------------------------------------------------------------------------
-- Forward map: TotalSpace → S₄.
------------------------------------------------------------------------

total-to-s4 : TotalSpace → Permutation
total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok

------------------------------------------------------------------------
-- Reverse map: classify-CS + stab-d-to-orbit-key + s4-to-total.
------------------------------------------------------------------------

classify-CS : Axis → Axis → OrbitKey
classify-CS C S = α-pair , even
classify-CS C W = α-pair , odd
classify-CS S W = β-pair , even
classify-CS S C = β-pair , odd
classify-CS W C = γ-pair , even
classify-CS W S = γ-pair , odd
classify-CS _ _ = α-pair , even   -- impossible for σ ∈ Stab(D)

stab-d-to-orbit-key : (σ : Permutation) → Stab D σ → OrbitKey
stab-d-to-orbit-key σ _ = classify-CS (applyₛ σ C) (applyₛ σ S)

s4-to-total : Permutation → IsomorphicCocycleStructure.TotalSpace CY5-V4Signature
s4-to-total σ =
  stab-d-to-orbit-key (s-for σ) (s-for-fixes-anchor D σ) , v-for σ

------------------------------------------------------------------------
-- Round-trip on the OrbitKey side.
------------------------------------------------------------------------

ok-round-trip :
  (ok : OrbitKey) →
  stab-d-to-orbit-key (orbit-key-to-stab-d ok)
                      (orbit-key-to-stab-d-fixes-D ok) ≡ ok
ok-round-trip (α-pair , even) = refl
ok-round-trip (α-pair , odd)  = refl
ok-round-trip (β-pair , even) = refl
ok-round-trip (β-pair , odd)  = refl
ok-round-trip (γ-pair , even) = refl
ok-round-trip (γ-pair , odd)  = refl
