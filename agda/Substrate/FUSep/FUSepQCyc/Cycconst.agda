------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Cycconst
--
-- Defines: cyc~const
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Cycconst where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Cyc
open import Substrate.FUSep.FUSepQCyc.Const
open import Substrate.FUSep.FUSepQCyc.Op
open import Substrate.FUSep.FUSepQCyc.CycLoopconst



cyc~const : {A : Set} (x : A) → cyc x [] ~ₛ const x
hd~ (cyc~const x) = refl
tl~ (cyc~const x) = cyc-loop~const x
