------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.InvInverse
--
-- inv is a two-sided inverse (the pair).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.InvInverse where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.V4.Operations using (_·₄_; ε; inv)
open import Substrate.Groups.V4.Axioms.InvLeft using (inv-left)
open import Substrate.Groups.V4.Axioms.InvRight using (inv-right)
open import Substrate.Foundation.Eq

inv-inverse :
  ((x : V₄) → ((inv x) ·₄ x) ≡ ε) × ((x : V₄) → (x ·₄ (inv x)) ≡ ε)
inv-inverse = inv-left , inv-right
