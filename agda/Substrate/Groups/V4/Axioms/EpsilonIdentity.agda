------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.EpsilonIdentity
--
-- ε is a two-sided identity (the pair).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.EpsilonIdentity where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.V4.Operations using (_·_; ε)
open import Substrate.Groups.V4.Axioms.EpsilonLeft using (ε-left)
open import Substrate.Groups.V4.Axioms.EpsilonRight using (ε-right)

ε-identity : ((x : V₄) → (ε · x) ≡ x) × ((x : V₄) → (x · ε) ≡ x)
ε-identity = ε-left , ε-right
