------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.Assoc
--
-- _·₄_ is associative (64 cases via the triple cover).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.Assoc where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·₄_; v4×v4×v4-cover)
open import Substrate.Foundation.Eq

·-assoc : (x y z : V₄) → ((x ·₄ y) ·₄ z) ≡ (x ·₄ (y ·₄ z))
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
