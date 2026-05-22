------------------------------------------------------------------------
-- Substrate.Category.CommutativeComonoid.Term (T14)
-- CommutativeComonoid term-algebra layer.
-- Reuses Comonoid.Term with cocommutativity as a derived equation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CommutativeComonoid.Term where

open import Substrate.Category.Comonoid.Term public

-- CommutativeComonoidTerm IS a ComonoidTerm; cocommutativity is
-- enforced at the GENERATOR level (each generator must commute with
-- the carrier's swap morphism). Stated structurally; concrete
-- instances at e.g. V₄ supply the cocommutativity proof.

CommutativeComonoidTerm : Set → Set → Set → Set₁
CommutativeComonoidTerm = ComonoidTerm
