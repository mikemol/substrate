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

-- ⟡set1-paydown: xFreeCyclicCapability now takes (Zn-Word : Set) and the
-- family (Zn-Canonical : Zn-Word → Set) as parameters; take them as implicit
-- module params (inferred from `cap`'s type) so the per-Zₙ adapters still
-- write `xFreeCyclicFromCapability cap-Zₙ`.
module Substrate.Groups.Coxeter.xFreeCyclicFromCapability
  {Zn-Word : Set} {Zn-Canonical : Zn-Word → Set}
  (cap : xFreeCyclicCapability Zn-Word Zn-Canonical)
  where

open xFreeCyclicCapability cap

open import Substrate.Groups.Zn-x-FreeCyclic
  Zn-Word _Zn-++_ Zn-ε Zn-++-assoc
  Zn-Canonical Zn-normalize Zn-normalize-canonical
  Zn-canonical-is-fixed Zn-normalize-distrib
  public
