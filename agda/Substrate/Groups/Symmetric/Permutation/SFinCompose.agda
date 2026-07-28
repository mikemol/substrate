------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Permutation.SFinCompose
--
-- Composition, ℕ-indexed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Permutation.SFinCompose where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.Symmetric.Permutation.Compose as SymComp
open import Substrate.Groups.SFin.Permutation using (Permutation)

_·_ : {n : ℕ} → Permutation n → Permutation n → Permutation n
_·_ {n} = SymComp._·_ (Fin n)
