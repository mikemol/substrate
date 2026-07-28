------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconj
--
-- Defines: coemit-stardivstr-conj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconj where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
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
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.WitnessTower.FaceSet
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar


------------------------------------------------------------------------
-- (3) coemit-stardivstr: HONEST-PARTIAL, with a precise reason. StarDivStr.conj-conj demands Agda's INTENSIONAL
--     _≡_ : conj (conj x) ≡ x. On RealTrace the constructed ≡ IS ~ (351: the totality of the orbit's actions);
--     intensional ≡ on a coinductive carrier is not that construction (it would need funext/quotients — and
--     D-safe-no-postulate forbids postulating it). So the record as written does NOT admit RealTrace directly:
--     it wants a carrier whose Agda-≡ already IS the totality (a finite Vector, as Face is; or a quotient/setoid).
--     What coemit HAS is every component, with ~ in place of ≡ — i.e. the StarDivStr over the ~-setoid.
------------------------------------------------------------------------
-- the conjugation exists (bar) and is involutive in the CONSTRUCTED equality (~) — the StarDivStr data, ~-valued.
coemit-stardivstr-conj : RealTrace → RealTrace
coemit-stardivstr-conj = bar
