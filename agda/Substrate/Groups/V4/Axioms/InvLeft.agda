------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.InvLeft
--
-- Every element is a left inverse of itself (V₄ is 2-torsion).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.InvLeft where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·₄_; ε; inv; v4-cover)
open import Substrate.Foundation.Eq

inv-left : (x : V₄) → ((inv x) ·₄ x) ≡ ε
inv-left = v4-cover _ (refl , refl , refl , refl)
