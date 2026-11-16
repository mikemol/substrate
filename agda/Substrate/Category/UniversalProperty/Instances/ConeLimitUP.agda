------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.ConeLimitUP
--
-- Defines: ConeLimit-UP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.ConeLimitUP where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Unit
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.LimitUniversalProperty
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 3. Cone / Limit — the product is the limit of a discrete diagram.
------------------------------------------------------------------------

ConeLimit-UP = LimitUP-UPArrow (product-leg 1 (λ _ → ℕ)) ⊤
