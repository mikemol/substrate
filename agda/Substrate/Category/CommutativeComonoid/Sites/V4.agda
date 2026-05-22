------------------------------------------------------------------------
-- Substrate.Category.CommutativeComonoid.Sites.V4
--
-- Concrete site: V₄ as a commutative comonoid.
--
-- The diagonal x ↦ (x, x) is trivially cocommutative under the
-- standard swap on V₄ × V₄: swap (x, x) = (x, x).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CommutativeComonoid.Sites.V4 where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.Comonoid
open import Substrate.Category.CommutativeComonoid
open import Substrate.Category.Comonoid.Sites.V4 using (V4; e; α; β; γ; V4-Comonoid)

------------------------------------------------------------------------
-- Swap on V₄ × V₄.

swap-V4 : V4 × V4 → V4 × V4
swap-V4 (x , y) = (y , x)

------------------------------------------------------------------------
-- Cocommutativity: swap-V4 (comult x) = swap (x, x) = (x, x) = comult x.

cocomm-V4 : (x : V4) → swap-V4 (comult V4-Comonoid x) ≡ comult V4-Comonoid x
cocomm-V4 _ = refl

------------------------------------------------------------------------
-- V₄ as a commutative comonoid.

V4-CommutativeComonoid : CommutativeComonoid V4 _×_ ⊤
V4-CommutativeComonoid = record
  { comonoid = V4-Comonoid
  ; swap    = swap-V4
  ; cocomm  = cocomm-V4
  }
