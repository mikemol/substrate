------------------------------------------------------------------------
-- Substrate.Groups.SFin.Injective
--
-- apply is injective, ℕ-indexed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin.Injective where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)
import Substrate.Groups.Symmetric.Injective as SymInj
open import Substrate.Groups.SFin.Permutation using (Permutation)
open import Substrate.Groups.SFin.Apply using (apply)

σ-injective :
  {n : ℕ} (σ : Permutation n) (x y : Fin n) → apply σ x ≡ apply σ y → x ≡ y
σ-injective {n} = SymInj.σ-injective (Fin n)
