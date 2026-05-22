------------------------------------------------------------------------
-- Substrate.Category.PhaseLockedLoop.Bank
--
-- Polyphonic PLL Bank + Independence law (file-per-lemma):
--
--   Bank.PLLBank           — primes list + per-prime lookups
--   Bank.BankIndependence  — structural independence marker
--
-- Stdlib audit: Data.List → Substrate.Groups.Coxeter.Word (Word ℕ
-- replaces List ℕ for the primes field).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PhaseLockedLoop.Bank where

open import Substrate.Category.PhaseLockedLoop.Bank.PLLBank          public
open import Substrate.Category.PhaseLockedLoop.Bank.BankIndependence public
