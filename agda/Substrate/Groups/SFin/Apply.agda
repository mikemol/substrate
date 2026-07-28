------------------------------------------------------------------------
-- Substrate.Groups.SFin.Apply
--
-- The underlying map and its inverse, ℕ-indexed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin.Apply where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)
import Substrate.Groups.Symmetric.Permutation as SymP
open import Substrate.Groups.SFin.Permutation using (Permutation)

apply : {n : ℕ} → Permutation n → Fin n → Fin n
apply {n} = SymP.Permutation.apply

invₐ : {n : ℕ} → Permutation n → Fin n → Fin n
invₐ {n} = SymP.Permutation.invₐ

inv-l : {n : ℕ} (σ : Permutation n) (x : Fin n) → invₐ σ (apply σ x) ≡ x
inv-l {n} = SymP.Permutation.inv-l

inv-r : {n : ℕ} (σ : Permutation n) (x : Fin n) → apply σ (invₐ σ x) ≡ x
inv-r {n} = SymP.Permutation.inv-r
