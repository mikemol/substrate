------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.SymEq
--
-- Defines: symEq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.SymEq where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)



symEq : {X : Set}{a b : X} → a ≡ b → b ≡ a
symEq refl = refl
-- ⟡def-eq: this private helper IS Foundation.Eq.sym (pointwise, definitionally).
