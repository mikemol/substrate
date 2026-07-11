------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.CellReconstruct
--
-- SYNTHESIZED by jea/metalanguage/synth_agda_prototype.py (⟡pipeline-driver,
-- `reconstruct` class, M1 carrier-parameterization) — the Set₀ reconstruction of
-- `Cell` (Set₁). Located mechanically: the Set₁ cause is the bare-`Set`
--   carrier field(s) ['evidence'] — a HELD carrier. Hoisting it to a MODULE PARAMETER
--   (set1-carrier-always-parameterize) lands the record at `: Set`. That green `: Set`
--   compile IS the Set₁ paydown. The original `Cell` = this at a re-fielded
--   carrier (Σ Set Cellₚ); the RESIDUE is exactly the held carrier ['evidence'].
-- Substrate-only imports (carried from the target). Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.CellReconstruct where

open import Substrate.Foundation.Unit using (⊤; tt) public
open import Substrate.Foundation.Product using (_,_; _×_)

-- carrier(s) ['evidence'] hoisted to a module PARAMETER ⇒ the record lands at `: Set`.
module _ (evidence : Set) where
  record Cellₚ : Set where
    constructor cellₚ
    field
      witness : evidence
