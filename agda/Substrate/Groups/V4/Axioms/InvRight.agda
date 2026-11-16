------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.InvRight
--
-- Every element is a right inverse of itself.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.InvRight where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·₄_; ε; inv; v4-cover)
open import Substrate.Foundation.Eq

inv-right : (x : V₄) → (x ·₄ (inv x)) ≡ ε
inv-right = v4-cover _ (refl , refl , refl , refl)
