------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.InvRight
--
-- Every element is a right inverse of itself.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.InvRight where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·_; ε; inv; v4-cover)

inv-right : (x : V₄) → (x · (inv x)) ≡ ε
inv-right = v4-cover _ (refl , refl , refl , refl)
