------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.SelfSimilarcyc
--
-- Defines: selfSimilar~cyc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.SelfSimilarcyc where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Cyc
open import Substrate.FUSep.FUSepQCyc.Const
open import Substrate.FUSep.FUSepQCyc.Op
open import Substrate.FUSep.FUSepQCyc.Sym
open import Substrate.FUSep.FUSepQCyc.Trans
open import Substrate.FUSep.FUSepQCyc.Cycconst
open import Substrate.FUSep.FUSepQCyc.AllHeads
open import Substrate.FUSep.FUSepQCyc.AllHeadsconst



-- so any self-similar (constant-observation) divergent stream ~ cyc x [] — the
-- Diverges residue IS the periodic real, up to bisimilarity.
selfSimilar~cyc : {A : Set} (x : A) (s : Stream A) → AllHeads x s → s ~ₛ cyc x []
selfSimilar~cyc x s ah = ~-trans (allHeads~const x s ah) (~-sym (cyc~const x))
