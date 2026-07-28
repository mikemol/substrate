------------------------------------------------------------------------
-- Substrate.Groups.SFin.Eq
--
-- Pointwise equality, ℕ-indexed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin.Eq where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.Symmetric.Eq as SymEq
open import Substrate.Groups.SFin.Permutation using (Permutation)

infix 4 _≈_

_≈_ : {n : ℕ} → Permutation n → Permutation n → Set
_≈_ {n} = SymEq._≈_ (Fin n)
