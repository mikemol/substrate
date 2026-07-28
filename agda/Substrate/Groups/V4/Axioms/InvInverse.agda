------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.InvInverse
--
-- inv is a two-sided inverse (the pair).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.InvInverse where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.V4.Operations using (_·_; ε; inv)
open import Substrate.Groups.V4.Axioms.InvLeft using (inv-left)
open import Substrate.Groups.V4.Axioms.InvRight using (inv-right)

inv-inverse :
  ((x : V₄) → ((inv x) · x) ≡ ε) × ((x : V₄) → (x · (inv x)) ≡ ε)
inv-inverse = inv-left , inv-right
