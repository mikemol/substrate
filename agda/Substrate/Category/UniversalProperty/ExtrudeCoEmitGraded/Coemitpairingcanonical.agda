------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitpairingcanonical
--
-- Defines: coemit-pairing-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitpairingcanonical where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Algebra.F2
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4pairings
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4ontopairings


------------------------------------------------------------------------
-- coemit-orientation-rederive + coemit-pairing-canonical + coemit-orbitkey-bridge.
-- CATALOG (per item): OrbitKey = Pairing × Chirality (3×2 = 6 = |S₃|) — the Stab(D)-representatives ARE (V₄-partition,
-- chirality) pairs; S4Iso/Anchor: orbit-key-to-stab-d : OrbitKey → Permutation. Pairing/Structural documents the
-- CANONICAL correspondence by COORDINATES: α-pair ↔ v4nz-α (𝟙,𝟘) ; β-pair ↔ v4nz-β (𝟘,𝟙) ; γ-pair ↔ v4nz-γ (𝟙,𝟙).
------------------------------------------------------------------------
-- (2) coemit-pairing-canonical: VERIFIED — my 344 assignment (rowSwap=(𝟙,𝟘)↦α, recip=(𝟘,𝟙)↦β, klein=(𝟙,𝟙)↦γ) matches
--     the canonical Pairing↔V4-Nonzero coordinates EXACTLY. The V4Full generators carry the canonical coords.
coemit-pairing-canonical : (coemit-v4-pairings 𝟙 𝟘 ≡ α-pair)      -- rowSwap coords (𝟙,𝟘) — canonical α
                         × ((coemit-v4-pairings 𝟘 𝟙 ≡ β-pair)      -- recip   coords (𝟘,𝟙) — canonical β
                         × (coemit-v4-pairings 𝟙 𝟙 ≡ γ-pair))      -- klein   coords (𝟙,𝟙) — canonical γ
coemit-pairing-canonical = coemit-v4-onto-pairings
