------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.BilinForm
--
-- BilinForm n : a general (not necessarily symmetric) bilinear form
-- over F₂ⁿ as the data of a matrix Fin n → Fin n → F₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.BilinForm where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.F2 using (F₂)

BilinForm : ℕ → Set
BilinForm n = Fin n → Fin n → F₂
