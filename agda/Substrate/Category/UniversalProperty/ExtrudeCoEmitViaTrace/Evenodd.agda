------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Evenodd
--
-- Defines: even≠odd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Evenodd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Nat.SucInjective
open import Substrate.Foundation.Empty.Bot
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Double



even≠odd : (a o : ℕ) → double a ≡ suc (double o) → ⊥
even≠odd zero    o       ()        -- zero ≡ suc _ : impossible
even≠odd (suc a) zero    eq with suc-injective eq   -- suc (double a) ≡ zero : impossible
... | ()
even≠odd (suc a) (suc o) eq = even≠odd a o (suc-injective (suc-injective eq))
