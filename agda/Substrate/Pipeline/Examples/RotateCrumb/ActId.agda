------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb.ActId
--
-- Defines: act-idᶜ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Pipeline.Examples.RotateCrumb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb.ActId where

open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Eq
open import Substrate.Pipeline.Examples.RotateCrumb.Crumb
open import Substrate.Pipeline.Examples.RotateCrumb.V4Xor



-- v4-xor IS a genuine V₄ group action — the real content the old vacuous
-- `Preserves-V4` tag stood in for. Both laws hold by computation (ε reduces to
-- e; V₄'s Coxeter-routed op reduces to a concrete element, so every case is refl).
act-idᶜ : (c : Crumb) → v4-xor c e ≡ c
act-idᶜ c₀ = refl ; act-idᶜ c₁ = refl ; act-idᶜ c₂ = refl ; act-idᶜ c₃ = refl
