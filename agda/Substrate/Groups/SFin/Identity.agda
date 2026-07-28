------------------------------------------------------------------------
-- Substrate.Groups.SFin.Identity
--
-- The identity permutation, ℕ-indexed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin.Identity where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.Symmetric.Identity as SymId
open import Substrate.Groups.SFin.Permutation using (Permutation)

ε : {n : ℕ} → Permutation n
ε {n} = SymId.ε (Fin n)
