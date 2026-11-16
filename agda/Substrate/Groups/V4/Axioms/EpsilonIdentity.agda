------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.EpsilonIdentity
--
-- ε is a two-sided identity (the pair).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.EpsilonIdentity where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.V4.Operations using (_·₄_; ε)
open import Substrate.Groups.V4.Axioms.EpsilonLeft using (ε-left)
open import Substrate.Groups.V4.Axioms.EpsilonRight using (ε-right)
open import Substrate.Foundation.Eq

ε-identity : ((x : V₄) → (ε ·₄ x) ≡ x) × ((x : V₄) → (x ·₄ ε) ≡ x)
ε-identity = ε-left , ε-right
