------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.Comm
--
-- _·₄_ is commutative.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.Comm where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·₄_; v4×v4-cover)
open import Substrate.Foundation.Eq

·-comm : (x y : V₄) → (x ·₄ y) ≡ (y ·₄ x)
·-comm = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
