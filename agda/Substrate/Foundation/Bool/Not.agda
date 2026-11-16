------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Not
--
-- Defines: not
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Not where

open import Substrate.Foundation.Bool.Bool



not : Bool → Bool
not true  = false
not false = true
