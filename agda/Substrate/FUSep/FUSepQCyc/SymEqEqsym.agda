------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.SymEqEqsym
--
-- Defines: symEq≡sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.SymEqEqsym where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.SymEq


symEq≡sym : {X : Set}{a b : X} (p : a ≡ b) → symEq p ≡ sym p
symEq≡sym refl = refl
