------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.Assoc
--
-- _·_ is associative (64 cases via the triple cover).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.Assoc where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·_; v4×v4×v4-cover)

·-assoc : (x y z : V₄) → ((x · y) · z) ≡ (x · (y · z))
·-assoc = v4×v4×v4-cover _
  ( ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  , ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  , ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  , ( (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl)
    , (refl , refl , refl , refl) )
  )
