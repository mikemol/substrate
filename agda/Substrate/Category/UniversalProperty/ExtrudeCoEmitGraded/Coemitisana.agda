------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitisana
--
-- Defines: coemit-is-ana
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitisana where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Coalg
  renaming (coalg to coemit-coalg)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obs
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-nu-realtrace: coemit-trace lands in νΦ_T = RealTrace (the terminal coalgebra of Φ_T S = ℕ × S,
-- Trace.Final; distinct from the fiber-level Φ-obs refinement above). coemit-trace = ana coalg (302, unfold),
-- so it IS the terminal-coalgebra (νΦ_T) map by construction; ana-unique gives terminal uniqueness — any
-- coalgebra morphism from CoEmit's parity coalgebra into RealTrace is ~ coemit-trace. RealTrace = νΦ_T; _~_ = equality there.
------------------------------------------------------------------------

-- coemit-trace IS ana of its coalgebra (the νΦ_T map) — definitional (coemit-trace = unfold coalg = ana coalg).
coemit-is-ana : (c : CoEmit ℕ) → coemit-trace c ≡ ana coemit-coalg c
coemit-is-ana c = refl
