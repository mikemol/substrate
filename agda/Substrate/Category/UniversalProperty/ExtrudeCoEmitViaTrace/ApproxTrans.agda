------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxTrans
--
-- Defines: ≈ᵉ-trans′
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxTrans where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Nat.SucInjective
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.ApproxTo
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Approx



≈ᵉ-trans′ : {c d e : CoEmit ℕ} → c ≈ᵉ d → d ≈ᵉ e → c ≈ᵉ e
≈ᵉ-trans′ p q = ≈ᵉ←~ (~-trans (≈ᵉ→~ p) (≈ᵉ→~ q))
