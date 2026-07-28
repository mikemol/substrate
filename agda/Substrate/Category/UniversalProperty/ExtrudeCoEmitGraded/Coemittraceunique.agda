------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceunique
--
-- Defines: coemit-trace-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceunique where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Final
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitisana


------------------------------------------------------------------------
-- coemit-ana-unique-apply: ana-unique applied — the TERMINAL CHARACTERIZATION. Any coalgebra morphism h from
-- CoEmit's parity coalgebra into RealTrace (agreeing with coemit-coalg on head + tail) is ~ coemit-trace. Since
-- coemit-trace = ana coemit-coalg definitionally (coemit-is-ana = refl), ana-unique gives it directly. This is the
-- USABLE uniqueness: coemit-trace is THE map, up to ~, characterized by its one-step behavior.
------------------------------------------------------------------------

coemit-trace-unique : (h : CoEmit ℕ → RealTrace)
                    → ((c : CoEmit ℕ) → RealTrace.head (h c) ≡ proj₁ (coemit-coalg c))
                    → ((c : CoEmit ℕ) → RealTrace.tail (h c) ≡ h (proj₂ (coemit-coalg c)))
                    → (c : CoEmit ℕ) → h c ~ coemit-trace c
coemit-trace-unique h hh ht c = ana-unique coemit-coalg h hh ht c
