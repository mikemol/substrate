------------------------------------------------------------------------
-- Substrate.Groups.SFin.Injective
--
-- apply is injective, ℕ-indexed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin.Injective where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.Symmetric.Injective as SymInj
open import Substrate.Groups.SFin.Permutation using (Permutation)
open import Substrate.Groups.SFin.Apply using (apply)
open import Substrate.Foundation.Eq

σ-injective :
  {n : ℕ} (σ : Permutation n) (x y : Fin n) → apply σ x ≡ apply σ y → x ≡ y
σ-injective {n} = SymInj.σ-injective (Fin n)
