------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Strict2MonoidFromCapability
--
-- Takes a Strict2MonoidCapability record and produces the Coxeter
-- Strict2Monoid by feeding its fields into Zn-Coxeter-Strict2Monoid.
--
-- Per [[expose-generator-not-orbit]]: the 5-file Zₙ-Coxeter-Strict2Monoid
-- orbit (100% structurally shared after Zₙ-name anonymization) was a
-- pure rename-orbit. This adapter consumes the substrate's named
-- capability record once; each per-Zₙ adapter becomes a one-line
-- `open` of this module with cap-Zₙ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Groups.Capabilities.Strict2Monoid
  using (Strict2MonoidCapability)

-- ⟡set1-paydown: parameterize Word — Strict2MonoidCapability now takes its
-- carrier as a parameter; `W` is implicit here so per-Zₙ instances still
-- open this adapter with a bare `cap-Zₙ` (W inferred from the record's type).
module Substrate.Groups.Coxeter.Strict2MonoidFromCapability
  {W : Set}
  (cap : Strict2MonoidCapability W)
  where

open Strict2MonoidCapability cap

open import Substrate.Groups.Zn-Coxeter-Strict2Monoid
  W _++_ ε ++-assoc ++-identityˡ ++-identityʳ normalize normalize-distrib
  public
