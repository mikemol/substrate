------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.InvLeft
--
-- Every element is a left inverse of itself (V₄ is 2-torsion).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.InvLeft where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·_; ε; inv; v4-cover)

inv-left : (x : V₄) → ((inv x) · x) ≡ ε
inv-left = v4-cover _ (refl , refl , refl , refl)
