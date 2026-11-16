------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.AllHeads
--
-- Defines: AllHeads, ah-hd, field
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.AllHeads where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Cyc



------------------------------------------------------------------------
-- THE GENERAL COUNIT: a SELF-SIMILAR stream (all heads x — a divergent process
-- with constant observation, the residue that refuses to vanish, ADD 110/
-- ResidueAtom) IS bisimilar to cyc x []. `AllHeads` is the periodicity witness;
-- the greatest-fixed-point universal property (uniqueness up to ~).
------------------------------------------------------------------------
record AllHeads {A : Set} (x : A) (s : Stream A) : Set where
  coinductive
  field ah-hd : hd s ≡ x ; ah-tl : AllHeads x (tl s)
open AllHeads public
