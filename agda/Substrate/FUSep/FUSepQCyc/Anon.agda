------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Anon
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Anon where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Cyc
open import Substrate.FUSep.FUSepQCyc.Const
open import Substrate.FUSep.FUSepQCyc.Op
open import Substrate.FUSep.FUSepQCyc.AllHeads
open import Substrate.FUSep.FUSepQCyc.SelfSimilarcyc



------------------------------------------------------------------------
-- THE BRIDGE to ADD-110's Diverges: a divergent term's observation is a Stream;
-- a SELF-LOOPING divergent term (Ω → Ω, obs constant along the loop) is AllHeads,
-- hence ~ cyc — its observation IS the periodic real. This wires Diverges (the
-- greatest fixed point, ADD 110) to the periodic RealTrace (≋/CycleWire).
------------------------------------------------------------------------

module _ (⇒ : Reduce) (A : Set) (obs : Tm-QReduce → A) where
  -- the observation stream of a divergent path (unfold via Diverges.onward).
  divStream : (t : Tm-QReduce) → FUSepQReduce.Diverges ⇒ t → Stream A
  hd (divStream t d) = obs t
  tl (divStream t d) = divStream (FUSepQReduce.Diverges.next d) (FUSepQReduce.Diverges.onward d)

  -- if the divergent path stays observationally constant (a self-loop at obs x),
  -- its observation is AllHeads x — hence ~ cyc x [], the periodic real. The
  -- Diverges residue, observed, IS the greatest-fixed-point periodic stream.
  divStream-const→cyc :
    (t : Tm-QReduce) (d : FUSepQReduce.Diverges ⇒ t) (x : A)
    → AllHeads x (divStream t d) → divStream t d ~ₛ cyc x []
  divStream-const→cyc t d x ah = selfSimilar~cyc x (divStream t d) ah
