------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Natuip
--
-- Defines: nat-uip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Natuip where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Fin.Op
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Algebra.Wedge.Iso
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar


------------------------------------------------------------------------
-- PREFLIGHT (operator: "the catalog serves to re-sync, dedupe and dedrift AFTER a sprint; we use it as a preflight
-- check because at that moment we know the most about what we need next and about what we just built"):
--   • reuse-index: `DivStr` is multiply-homed (Algebra.Wedge, S5.S5EEA); `GradedDivStr` is its indexed lift;
--     **no setoid-valued StarDivStr exists** ⇒ building one is a CONTRIBUTION, not a duplicate.
--   • reuse-index: the canonical iso record is `WedgeIso`@Substrate.Algebra.Wedge.Iso {fwd,bwd,fwd∘bwd,bwd∘fwd};
--     IsoGroupoid REFINES it (iso-id/iso-sym/iso-∘ + the pointwise _≈ʷ_). StarV4: **iso-sym IS the dagger †**.
--   • Foundation.Hedberg: `Decidable⇒UIP : DecidableEquality A → (p q : x ≡ y) → p ≡ q`, HOLDS UNDER --without-K.
--     With Nat._≟_ this gives UIP on ℕ — the engine for identifying two ~-proofs' head~ components.
--   • No ~-proof-irrelevance exists in-tree ⇒ also a contribution.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- (1) coemit-v4-square: the V₄ square at PROOF level. 353 downgraded "† and bar commute" to endpoint-commutation
--     because †∘bar and bar∘† are two CONSTRUCTIONS of the same TYPE. Now we identify them where it counts:
--     a ~-proof's observable content at each step is its head~ : ℕ-equality — and ℕ has UIP (Hedberg, via _≟_).
--     So the two routes agree on every head~, at every depth: the square COMMUTES stepwise, hence (351: ≡ is the
--     totality of the orbit's actions) it commutes. This is the totality-construction, not proof-irrelevance-by-fiat.
------------------------------------------------------------------------
-- ℕ's UIP (Hedberg + decidable equality) — any two proofs of a head-equality coincide.
nat-uip : {m n : ℕ} (p q : m ≡ n) → p ≡ q
nat-uip = Decidable⇒UIP Substrate.Foundation.Nat._≟_
