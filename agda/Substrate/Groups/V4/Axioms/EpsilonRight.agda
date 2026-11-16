------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.EpsilonRight
--
-- ε is a right identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.EpsilonRight where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·₄_; ε; v4-cover)
open import Substrate.Foundation.Eq

ε-right : (x : V₄) → (x ·₄ ε) ≡ x
ε-right = v4-cover _ (refl , refl , refl , refl)
