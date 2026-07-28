------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3
--
-- Defines: Anon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3 where

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
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.WitnessTower.SimplicialBoundary
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis

open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar


------------------------------------------------------------------------
-- OPERATOR (house style): "When you want to reach for a postulate, it's better to take the 'postulate' as a
-- MODULE PARAMETER. This promotes decomposition and composability."
-- The substrate does exactly this: Lawvere's `module _ {I V : Set} (fpf : FixedPointFree V) where`,
-- SemidirectProduct's `module Build (G_N : Group N)(G_H : Group H)(φ : Actionᴳ G_H N)`. Nothing is postulated;
-- the needed structure is DEMANDED at the module boundary, so instances compose.
--
-- Two things I was tempted to postulate / honest-partial away, now PARAMETERS:
--   (a) the EQUALITY. Lawvere's four atoms are ≡-valued (carrier-generic, in Set). RealTrace's constructed ≡ is ~
--       (351). Rather than postulate ≡ (funext) or abandon the atom, parameterize by _≈_ : V → V → Set. The record
--       stays in Set (no Set₁ bump — the equality is a PARAMETER, not a field of type `Set`).
--   (b) the SECOND INVOLUTION on the trace carrier. I have bar (352). StarV4's † lives on the groupoid's ARROWS
--       (~-sym), not the carrier. Rather than invent a carrier-level partner, DEMAND it: any δ₂ the caller supplies,
--       with its involutivity and commutation, completes the V₄. Composable: supply δ₂, get the Klein four-group.
------------------------------------------------------------------------
-- the ≈-parameterized Klein atom (mirrors Lawvere.CommutingInvolutions; the equality is a PARAMETER, so : Set).
module _ (V : Set) (_≈_ : V → V → Set) where
  record CommutingInvolutionsUpTo : Set where
    field
      δ₁ δ₂   : V → V
      δ₁-inv  : (v : V) → δ₁ (δ₁ v) ≈ v
      δ₂-inv  : (v : V) → δ₂ (δ₂ v) ≈ v
      commute : (v : V) → δ₂ (δ₁ v) ≈ δ₁ (δ₂ v)
