------------------------------------------------------------------------
-- Substrate.Algebra.F2.InvOfOne
--
-- Defines: inv-of-𝟙
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.InvOfOne where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op



------------------------------------------------------------------------
-- Multiplicative inverse on the invertible element only.
--
-- The total form `_⁻¹ : F₂ → F₂` is intentionally absent — there is
-- no inverse for 𝟘 in any field, and giving 𝟘⁻¹ a junk value (e.g.
-- 𝟘 or 𝟙) creates a leaky abstraction. Consumers that need an
-- inverse work with the partial form `inv-of-𝟙` directly, and the
-- (rare) generic inverse pattern is mediated by the universal
-- property in M-1.5.
------------------------------------------------------------------------

inv-of-𝟙 : (𝟙 · 𝟙) ≡ 𝟙
inv-of-𝟙 = refl
