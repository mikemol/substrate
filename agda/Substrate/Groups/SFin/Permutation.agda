------------------------------------------------------------------------
-- Substrate.Groups.SFin.Permutation
--
-- Permutation n = a bijection Fin n → Fin n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin.Permutation where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.Symmetric.Permutation as SymP

Permutation : ℕ → Set
Permutation n = SymP.Permutation (Fin n)
