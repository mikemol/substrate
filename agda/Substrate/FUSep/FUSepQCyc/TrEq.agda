------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.TrEq
--
-- Defines: trEq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.TrEq where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)


trEq : {X : Set}{a b c : X} → a ≡ b → b ≡ c → a ≡ c
trEq refl r = r
