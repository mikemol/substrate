------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.EpsilonRight
--
-- ε is a right identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.EpsilonRight where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·_; ε; v4-cover)

ε-right : (x : V₄) → (x · ε) ≡ x
ε-right = v4-cover _ (refl , refl , refl , refl)
