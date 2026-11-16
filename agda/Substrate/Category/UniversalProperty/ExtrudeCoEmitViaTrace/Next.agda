------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Next
--
-- Defines: next
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Next where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈) renaming (Step to Step⟦f8c709b4⟧)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst



next : CoEmit ℕ → Step⟦f8c709b4⟧ ℕ (CoEmit ℕ) → CoEmit ℕ
next c (ret a)     = c
next c (emitᶜ o k) = k
