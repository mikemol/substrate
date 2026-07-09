------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.PhaseProjectionFromCapability
--
-- Takes a PhaseProjectionCapability record and produces the
-- phase-projection chain by feeding its fields into
-- Zn-x-FreeCyclic-PhaseProjection.
--
-- Per [[expose-generator-not-orbit]]: the 5-file
-- Zₙ-x-FreeCyclic-PhaseProjection orbit was 100% structurally identical
-- after Zₙ-name anonymization. Each per-Zₙ adapter becomes a one-line
-- `open` of this module with cap-Zₙ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Groups.Capabilities.PhaseProjection
  using (PhaseProjectionCapability)

-- ⟡set1-paydown: PhaseProjectionCapability now takes (Zn-Word F-Word : Set)
-- as parameters; take them as implicit module params (inferred from `cap`'s
-- type) so the per-Zₙ adapters still write `PhaseProjectionFromCapability cap-Zₙ`.
module Substrate.Groups.Coxeter.PhaseProjectionFromCapability
  {Zn-Word F-Word : Set}
  (cap : PhaseProjectionCapability Zn-Word F-Word)
  where

open PhaseProjectionCapability cap

open import Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
  Zn-Word Zn-ε _Zn-++_ Zn-normalize
  F-Word F-ε _F-++_ F-normalize
  public
