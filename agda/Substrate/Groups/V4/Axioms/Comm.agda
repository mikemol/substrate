------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.Comm
--
-- _·_ is commutative.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.Comm where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·_; v4×v4-cover)

·-comm : (x y : V₄) → (x · y) ≡ (y · x)
·-comm = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )
