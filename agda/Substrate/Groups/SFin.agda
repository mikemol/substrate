------------------------------------------------------------------------
-- Substrate.Groups.SFin
--
-- The parameterised symmetric group S_n on Fin n. Thin adapter over
-- Substrate.Groups.Symmetric instantiated at Fin n. Substrate-native.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin where

open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)

import Substrate.Groups.Symmetric as Sym

------------------------------------------------------------------------
-- Permutation n = bijection Fin n → Fin n.
------------------------------------------------------------------------

Permutation : ℕ → Set
Permutation n = Sym.Permutation (Fin n)

------------------------------------------------------------------------
-- All operations + bundle, parametric in n.
------------------------------------------------------------------------

module _ {n : ℕ} where

  open Sym (Fin n) public hiding (Permutation)

  S-Group : SetoidGroup (Permutation n) _≈_
  S-Group = Symmetric-Group
