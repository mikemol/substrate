------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Stream
--
-- Defines: Stream, field, hd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Stream where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)



-- the observation stream (RealTrace analog): head + coinductive tail.
record Stream (A : Set) : Set where
  coinductive
  field hd : A ; tl : Stream A
open Stream public
