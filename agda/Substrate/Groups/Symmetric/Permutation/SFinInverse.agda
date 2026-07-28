------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Permutation.SFinInverse
--
-- The inverse permutation, ℕ-indexed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Permutation.SFinInverse where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.Symmetric.Permutation.Inverse as SymInv
open import Substrate.Groups.SFin.Permutation using (Permutation)

_⁻¹ : {n : ℕ} → Permutation n → Permutation n
_⁻¹ {n} = SymInv._⁻¹ (Fin n)
