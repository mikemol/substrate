------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitunfoldlaw
--
-- Defines: coemit-unfold-law
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitunfoldlaw where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Coalg
  renaming (coalg to coemit-coalg)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceunique
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-second-morphism: the UNFOLDING LAW — coemit-trace satisfies its own coalgebra unfolding up to ~ (both
-- sides share head + tail). This is the ONE-STEP behavior coemit-trace-unique characterizes. HONEST finding
-- (D-verify-dont-assume-substance): ana-unique's ≡-conditions are RIGID — the natural reconstruction (Lambek
-- into∘out) satisfies them only up to ~ (lambek-into-out : into(out x) ~ x, NOT ≡), so genuine second morphisms
-- live at the ~-level; the unfolding law is that ~-behavior made explicit (head~ refl, tail~ ~-refl).
------------------------------------------------------------------------

coemit-unfold-law : (c : CoEmit ℕ)
                  → coemit-trace c ~ cons (proj₁ (coemit-coalg c)) (coemit-trace (proj₂ (coemit-coalg c)))
head~ (coemit-unfold-law c) = refl
tail~ (coemit-unfold-law c) = ~-refl (coemit-trace (proj₂ (coemit-coalg c)))
