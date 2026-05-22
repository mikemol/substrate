------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.GroupFromCapability
--
-- Takes a CoxeterGroupCapability record and produces the Coxeter
-- Group bundle by feeding its fields into Coxeter.GroupAdapter.
--
-- Per [[expose-generator-not-orbit]]: the 5-file Zₙ-Coxeter-Group
-- orbit scored ~98% structurally identical after Zₙ-name
-- anonymization. Each per-Zₙ adapter collapses to a one-line `open`
-- of this module with cap-Zₙ + the per-Zₙ canonical-constructor
-- re-export (which can't be parameterized; constructor lists differ
-- per n).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Groups.Capabilities.CoxeterGroup
  using (CoxeterGroupCapability)

module Substrate.Groups.Coxeter.GroupFromCapability
  (cap : CoxeterGroupCapability)
  where

open CoxeterGroupCapability cap
open import Substrate.Groups.Coxeter.Word
  using (Word; _++_; []; ++-identity-left; ++-identity-right)

open import Substrate.Groups.Coxeter.GroupAdapter
  (Word Gen)
  _++_
  []
  ++-assoc
  Canonical
  c-ε
  normalize
  normalize-canonical
  canonical-is-fixed
  normalize-distrib
  ++-identity-left
  ++-identity-right
  inv
  inv-canonical
  inv-left-canonical
  inv-right-canonical
  public
