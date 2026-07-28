------------------------------------------------------------------------
-- Substrate.Category.CommutativeComonoid.Term (T14)
-- CommutativeComonoid term-algebra layer.
-- Reuses Comonoid.Term (the tower's free graded tower of combined generators)
-- with cocommutativity as a derived equation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CommutativeComonoid.Term where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Category.Comonoid.Term
-- CommutativeComonoidTerm IS a ComonoidTerm; cocommutativity is enforced at
-- the GENERATOR level (each generator must commute with the carrier's swap
-- morphism). Now that terms ARE the tower's LehmerPath (combinations of
-- generators UP TO PERMUTATION), cocommutativity is the permutation-invariance
-- the tower already carries. Concrete instances at e.g. V₄ supply the proof.
CommutativeComonoidTerm : ℕ → Set
CommutativeComonoidTerm = ComonoidTerm
