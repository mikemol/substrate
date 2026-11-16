------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.ExprSKK
--
-- Defines: expr-SKK
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.ExprSKK where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Lambda.Fragment.SKIWord



-- The SKK form of identity: a 3-combinator word.
expr-SKK : SKIWord
expr-SKK = S ∷ K ∷ K ∷ []
