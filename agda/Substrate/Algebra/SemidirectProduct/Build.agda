------------------------------------------------------------------------
-- Substrate.Algebra.SemidirectProduct.Build
--
-- Defines: Build
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.SemidirectProduct; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.SemidirectProduct.Build where

open import Substrate.Foundation.Product
open import Substrate.Algebra.Magma
open import Substrate.Algebra.Semigroup
open import Substrate.Algebra.Monoid
open import Substrate.Algebra.Group
open import Substrate.Algebra.GroupAction



------------------------------------------------------------------------
-- The semidirect-product carrier + operations.
------------------------------------------------------------------------

module Build
  {N H : Set}
  (G_N : Group N) (G_H : Group H)
  (φ : Actionᴳ G_H N)
  where

  Carrier⋊ : Set
  Carrier⋊ = Σ N (λ _ → H)

  ε⋊ : Carrier⋊
  ε⋊ = ε (monoid G_N) , ε (monoid G_H)

  _·⋊_ : Carrier⋊ → Carrier⋊ → Carrier⋊
  (n₁ , h₁) ·⋊ (n₂ , h₂) =
    let _·N_ = Magma._·_ (magma (semigroup (monoid G_N)))
        _·H_ = Magma._·_ (magma (semigroup (monoid G_H)))
    in (n₁ ·N (act φ h₁ n₂)) , (h₁ ·H h₂)

  inv⋊ : Carrier⋊ → Carrier⋊
  inv⋊ (n , h) = act φ (inv G_H h) (inv G_N n) , inv G_H h
