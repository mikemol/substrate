------------------------------------------------------------------------
-- Substrate.Groups.SFin.Group
--
-- The symmetric group on Fin n as a SetoidGroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin.Group where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
import Substrate.Groups.Symmetric.Group as SymGrp
open import Substrate.Groups.SFin.Permutation using (Permutation)
open import Substrate.Groups.SFin.Eq using (_≈_)

S-Group : {n : ℕ} → SetoidGroup (Permutation n) _≈_
S-Group {n} = SymGrp.Symmetric-Group (Fin n)
