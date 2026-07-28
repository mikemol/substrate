------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits3compassoc
--
-- Defines: coemit-s3-comp-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits3compassoc where

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
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
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
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3actcomp
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemits4mul


------------------------------------------------------------------------
-- coemit-s4-group-laws + coemit-braid-trace-mul + coemit-rung4-action: the S₄ obligations. VERIFIED (KleinCensus):
-- a Klein-four is {id, a, b, ab} = 4 elts; GradingAxis is the 3 NON-IDENTITY involutions — NOT the full V₄ group
-- (lacks id). So the S₃-COMPONENT laws (Fin 3 under ∘: assoc + id) are GENUINE; the full V₄ ·N is HONEST-PARTIAL
-- (needs the 4-element group, e.g. Abelian/V4-as-PFG). The semidirect twist compat is s3-act-comp (333).
------------------------------------------------------------------------
-- (1) coemit-s4-group-laws: the S₃-component of coemit-s4-mul (the perm ∘) satisfies the group laws. ∘-assoc and
--     ∘-id are the monoid structure; s3-act-comp is the semidirect twist-compatibility. (Full V₄ ·N: honest-partial.)
coemit-s3-comp-assoc : (σ τ ρ : Fin 3 → Fin 3) (x : Fin 3)
                     → (λ y → σ (τ y)) (ρ x) ≡ σ ((λ y → τ (ρ y)) x)
coemit-s3-comp-assoc σ τ ρ x = refl
