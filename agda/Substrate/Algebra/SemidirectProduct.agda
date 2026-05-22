------------------------------------------------------------------------
-- Substrate.Algebra.SemidirectProduct
--
-- The semidirect product G_N ⋊ G_H of two substrate-native groups
-- via an action of G_H on G_N. Substrate-native replacement for
-- stdlib's `Algebra.Bundles.Group` semidirect-product construction.
--
-- The carrier is the Σ-pair (n : ∣N∣, h : ∣H∣); composition is
--   (n₁, h₁) · (n₂, h₂) = (n₁ · (act h₁ n₂), h₁ · h₂)
-- with the identity (ε_N, ε_H) and inverse
--   (n, h)⁻¹ = (act (h⁻¹) (n⁻¹), h⁻¹).
--
-- Substrate-honest scope: the laws are SIGNATURE-bearing here. The
-- per-instance discharge (V₄ ⋊ S₃ → S₄ at S4-Composed) is supplied
-- where the construction is consumed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.SemidirectProduct where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε)
open import Substrate.Algebra.Group using (Group; monoid; inv)
open import Substrate.Algebra.GroupAction using (Action; act)

------------------------------------------------------------------------
-- The semidirect-product carrier + operations.
------------------------------------------------------------------------

module Build
  {N H : Set}
  (G_N : Group N) (G_H : Group H)
  (φ : Action G_H N)
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

------------------------------------------------------------------------
-- The full Group structure on Carrier⋊ requires propositional
-- equality of pairs + congruence proofs for ·⋊ + assoc + identity +
-- inverse witnesses. These are signature-bearing here as the
-- `SemidirectGroupObligation` record; concrete instances discharge
-- the fields at the consumer site.
------------------------------------------------------------------------

record SemidirectGroupObligation
  {N H : Set}
  (G_N : Group N) (G_H : Group H)
  (φ : Action G_H N)
  : Set where
  open Build G_N G_H φ public
  field
    assoc⋊ :
      (x y z : Carrier⋊) → ((x ·⋊ y) ·⋊ z) ≡ (x ·⋊ (y ·⋊ z))
    ε⋊-left  : (x : Carrier⋊) → (ε⋊ ·⋊ x) ≡ x
    ε⋊-right : (x : Carrier⋊) → (x ·⋊ ε⋊) ≡ x
    inv⋊-left  : (x : Carrier⋊) → (inv⋊ x ·⋊ x) ≡ ε⋊
    inv⋊-right : (x : Carrier⋊) → (x ·⋊ inv⋊ x) ≡ ε⋊

open SemidirectGroupObligation public
