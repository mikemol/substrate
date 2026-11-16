------------------------------------------------------------------------
-- Substrate.Algebra.SemidirectProduct.SemidirectGroupObligation
--
-- Defines: SemidirectGroupObligation, assoc⋊, inv⋊-left, inv⋊-right
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.SemidirectProduct; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.SemidirectProduct.SemidirectGroupObligation where

open import Substrate.Foundation.Product
open import Substrate.Algebra.Semigroup
open import Substrate.Algebra.Monoid
open import Substrate.Algebra.Group
open import Substrate.Algebra.GroupAction
open import Substrate.Foundation.Eq
open import Substrate.Algebra.SemidirectProduct.Build


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
  (φ : Actionᴳ G_H N)
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
