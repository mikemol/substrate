------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.EpsilonLeft
--
-- ε is a left identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.EpsilonLeft where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·_; ε; v4-cover)

ε-left : (x : V₄) → (ε · x) ≡ x
ε-left = v4-cover _ (refl , refl , refl , refl)
