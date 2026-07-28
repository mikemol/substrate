------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfixunit
--
-- Defines: axis-fix→unit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfixunit where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
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
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Axes.AxisOfV
open import Substrate.Axes.ActAxis
open import Substrate.Axes.Axis.Compose
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3


------------------------------------------------------------------------
-- PREFLIGHT: Substrate.Groups.V4.Bijection: `data V₄ : Set where e α β γ : V₄` (a 4-element enum);
-- Substrate.Groups.V4.Operations supplies _·_, ε, inv; Substrate.Axes re-exports them and defines
-- `act-axis v x = axis-of-v (v V4.· v-of-axis x)` with the bijection v-of-axis / axis-of-v (D ↔ e).
--
-- (2) coemit-axis-torsor: 347 quoted "Axis is a V₄-torsor anchored at D". TorsorAtom's `fix→unit` is exactly the
--     torsor law ("only the unit fixes a point"). Transport the group structure along the bijection: the anchor D
--     is the unit, and g ∙ x ≡ x forces g ≡ D. Proven by the 4×4 case split (V₄ is a finite enum).
------------------------------------------------------------------------
-- import the Axis constructors (C, S, W) and the Axis product _∙ᴬ_ from its carrier-local
-- home (⟡carrier-locality): Substrate.Axes now hosts _∙ᴬ_ = act-axis ∘ v-of-axis, so the
-- transport-of-V₄'s-product lives with the Axis carrier, not here.

-- ONLY THE ANCHOR FIXES A POINT: if x ∙ᴬ y ≡ y then x ≡ D. (The torsor law, by exhaustive case analysis on Axis.)
axis-fix→unit : (g x : Axis) → (g ∙ᴬ x) ≡ x → g ≡ D
axis-fix→unit D _ _ = refl
axis-fix→unit C D ()
axis-fix→unit C C ()
axis-fix→unit C S ()
axis-fix→unit C W ()
axis-fix→unit S D ()
axis-fix→unit S C ()
axis-fix→unit S S ()
axis-fix→unit S W ()
axis-fix→unit W D ()
axis-fix→unit W C ()
axis-fix→unit W S ()
axis-fix→unit W W ()
