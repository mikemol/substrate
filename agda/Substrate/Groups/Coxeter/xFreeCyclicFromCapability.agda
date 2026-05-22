------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.xFreeCyclicFromCapability
--
-- Takes an xFreeCyclicCapability record and produces the Zₙ × FreeCyclic
-- DirectProduct by feeding its fields into Zn-x-FreeCyclic.
--
-- Per [[expose-generator-not-orbit]]: the 5-file Zₙ-x-FreeCyclic orbit
-- was 100% structurally identical after Zₙ-name anonymization. Each
-- per-Zₙ adapter becomes a one-line `open` of this module with cap-Zₙ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Groups.Capabilities.xFreeCyclic
  using (xFreeCyclicCapability)

module Substrate.Groups.Coxeter.xFreeCyclicFromCapability
  (cap : xFreeCyclicCapability)
  where

open xFreeCyclicCapability cap

open import Substrate.Groups.Zn-x-FreeCyclic
  Zn-Word _Zn-++_ Zn-ε Zn-++-assoc
  Zn-Canonical Zn-normalize Zn-normalize-canonical
  Zn-canonical-is-fixed Zn-normalize-distrib
  public
