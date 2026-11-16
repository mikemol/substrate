------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Approx
--
-- Defines: ≈ᵉ←~
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Approx where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Unfold
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Nat.SucInjective
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.DoubleInj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Evenodd



≈ᵉ←~ : {c d : CoEmit ℕ} → coemit-trace c ~ coemit-trace d → c ≈ᵉ d
step≈ (≈ᵉ←~ {c} {d} p) with step c | step d | head~ p | tail~ p
... | ret a     | ret b       | h | _ rewrite double-inj h                = ret≈ b
... | ret a     | emitᶜ o k'  | h | _ = ⊥-elim (even≠odd a o h)
... | emitᶜ o k  | ret b       | h | _ = ⊥-elim (even≠odd b o (sym h))
... | emitᶜ o k  | emitᶜ o' k' | h | t rewrite double-inj (suc-injective h) = emit≈ o' (≈ᵉ←~ t)
