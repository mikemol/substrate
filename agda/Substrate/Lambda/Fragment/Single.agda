------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.Single
--
-- Defines: single
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.Single where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Lambda.Fragment.Combinator
open import Substrate.Lambda.Fragment.SKIWord



single : Combinator → SKIWord
single c = c ∷ []
