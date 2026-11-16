------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.AllHeadsconst
--
-- Defines: allHeads~const
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.AllHeadsconst where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Const
open import Substrate.FUSep.FUSepQCyc.Op
open import Substrate.FUSep.FUSepQCyc.AllHeads



allHeads~const : {A : Set} (x : A) (s : Stream A) → AllHeads x s → s ~ₛ const x
hd~ (allHeads~const x s ah) = ah-hd ah
tl~ (allHeads~const x s ah) = allHeads~const x (tl s) (ah-tl ah)
