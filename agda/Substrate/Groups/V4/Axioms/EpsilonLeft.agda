------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.EpsilonLeft
--
-- ε is a left identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.EpsilonLeft where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·₄_; ε; v4-cover)
open import Substrate.Foundation.Eq

ε-left : (x : V₄) → (ε ·₄ x) ≡ x
ε-left = v4-cover _ (refl , refl , refl , refl)
