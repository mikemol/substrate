------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Code
--
-- Defines: code
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Code where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈) renaming (Step to Step⟦f8c709b4⟧)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Double



-- coalg via step-level functions (so head/tail of coemit-trace reduce definitionally on the Step):
code : Step⟦f8c709b4⟧ ℕ (CoEmit ℕ) → ℕ
code (ret a)     = double a
code (emitᶜ o k) = suc (double o)
