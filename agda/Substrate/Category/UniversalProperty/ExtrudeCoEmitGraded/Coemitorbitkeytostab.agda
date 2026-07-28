------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkeytostab
--
-- Defines: coemit-orbitkey-to-stab
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkeytostab where

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
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Algebra.F2
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor
open import Substrate.Cocycles.V4Signature.S4Iso.Roundtrips
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Cocycles.V4Signature.S4Iso.Classify
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkey


------------------------------------------------------------------------
-- coemit-orbitkey-to-stab + coemit-s4-roundtrip: the canonical OrbitKey ↔ Stab(D) maps, REUSED (not re-derived).
-- S4Iso/Anchor: orbit-key-to-stab-d : OrbitKey → Permutation (= orbit-key-to-stab-anchor D); orbit-key-to-stab-d-fixes-D
-- (the anchor IS fixed — confirming D-fixed-point-is-anchor from the canonical side).
-- S4Iso/Roundtrips: stab-round-trip : orbit-key-to-stab-d (stab-d-to-orbit-key σ σ-stab) ≈ σ.
------------------------------------------------------------------------

-- (2) coemit-orbitkey-to-stab: coemit's orbit-key (Pairing × Chirality = OrbitKey) maps to its canonical
--     Stab(D)-REPRESENTATIVE permutation. Reuse orbit-key-to-stab-d (= orbit-key-to-stab-anchor D) directly.
coemit-orbitkey-to-stab : coemit-orbitkey → Permutation
coemit-orbitkey-to-stab = orbit-key-to-stab-d
