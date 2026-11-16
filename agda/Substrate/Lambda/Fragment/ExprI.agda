------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.ExprI
--
-- Defines: expr-I
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.ExprI where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Lambda.Fragment.SKIWord
open import Substrate.Lambda.Fragment.Single



------------------------------------------------------------------------
-- 3. Worked examples.
--
-- I = SKK (the classic SKI-encoding of identity using only S and K)
-- — the fragment can express it as a Word.
------------------------------------------------------------------------

-- The pure identity (single combinator I).
expr-I : SKIWord
expr-I = I ∷ []
