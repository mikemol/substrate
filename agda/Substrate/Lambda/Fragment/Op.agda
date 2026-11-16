------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.Op
--
-- Defines: ε
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.Op where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Lambda.Fragment.SKIWord



ε : SKIWord
ε = []
