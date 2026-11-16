------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.Single
--
-- Defines: single
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.Single where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.KelenWord



single : Relational → KelenWord
single r = r ∷ []
