------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceunique
--
-- Defines: coemit-trace-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceunique where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Coalg
  renaming (coalg to coemit-coalg)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Final.Ana
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitisana
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


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
