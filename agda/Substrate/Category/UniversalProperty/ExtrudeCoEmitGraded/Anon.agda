------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
--
-- Defines: Anon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Coalg
  renaming (coalg to coemit-coalg)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceunique
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-nu-uniqueness: the ~-CONDITIONED uniqueness (tail up to ~, not ≡ — letting Lambek/reassociation
-- morphisms through, unlike the rigid ≡-conditioned coemit-trace-unique). The naive proof wraps the corecursive
-- call in ~-trans (breaks guardedness); the MIX trick threads the accumulated ~ as a DATA argument, keeping the
-- corecursive call guarded (D-guarded-not-mutual). So any h matching head (≡) and tail-UP-TO-~ is ~ coemit-trace.
------------------------------------------------------------------------

module _ (h : CoEmit ℕ → RealTrace)
         (hh : (c : CoEmit ℕ) → RealTrace.head (h c) ≡ proj₁ (coemit-coalg c))
         (ht : (c : CoEmit ℕ) → RealTrace.tail (h c) ~ h (proj₂ (coemit-coalg c))) where

  -- mix threads x ~ h c through; the corecursive call sits directly under tail~ (guarded), the ~-trans is in its ARGUMENT.
  mix : (c : CoEmit ℕ) (x : RealTrace) → x ~ h c → x ~ coemit-trace c
  head~ (mix c x pf) = trans (head~ pf) (hh c)
  tail~ (mix c x pf) = mix (proj₂ (coemit-coalg c)) (RealTrace.tail x) (~-trans (tail~ pf) (ht c))

  coemit-trace-unique-~ : (c : CoEmit ℕ) → h c ~ coemit-trace c
  coemit-trace-unique-~ c = mix c (h c) (~-refl (h c))
