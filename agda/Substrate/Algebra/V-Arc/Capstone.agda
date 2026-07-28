------------------------------------------------------------------------
-- Substrate.Algebra.V-Arc.Capstone
--
-- V-arc capstone: substrate-native algebraic infrastructure free of
-- stdlib's Algebra.* / Relation.Binary.* / Axiom.* / Data.Nat.Properties
-- / Data.Nat.DivMod / Induction.WellFounded.
--
-- ===================================================================
-- WHAT LANDED
-- ===================================================================
--
-- Substrate-native bridges (built in the V-arc):
--
--   Substrate.Algebra.SetoidGroup        — Group on a Setoid carrier
--   Substrate.Algebra.SetoidGroup.Properties
--                                        — inverseˡ-unique etc.
--   Substrate.Algebra.SetoidGroup.Action — action by a SetoidGroup
--   Substrate.Algebra.GroupAction        — action by a Group
--   Substrate.Algebra.Torsor             — IsTorsor record
--   Substrate.Algebra.IsomorphicCocycle  — ICS record
--   Substrate.Algebra.SemidirectProduct  — substrate-native SP
--   Substrate.Algebra.Group.ToSetoid     — Group → SetoidGroup lift
--   Substrate.Foundation.Bool.Properties — xor-assoc/comm/identity/same
--   Substrate.Foundation.Hedberg         — UIP from decidable equality
--   Substrate.Foundation.Vec.Properties  — ≡-dec on Vec
--   Substrate.Foundation.Product (+Σ-≡)  — Σ-≡,≡→≡ combinator
--
-- Migrated (now substrate-native, no stdlib Algebra / Relation.Binary):
--
--   Substrate.Groups.{Symmetric, S4, V4/Axioms, V4/Bundle, F2Cubed,
--                     S3, S4-Composed, SFin}
--   Substrate.Groups.Coxeter.{GroupAdapter, SemidirectProductGroup}
--   Substrate.Groups.Actions.Z2-on-Z3
--   Substrate.Groups.S4-Iso/{Embedding, Foundation, ForwardHom,
--                              IsoTransport, Extract, ExtractCorrect,
--                              Roundtrip, V4Normal}
--   Substrate.Cocycle                    — full rewrite, SetoidGroup-
--                                          parametric throughout
--   Substrate.Cocycles.{V4Signature, F2CubedPuncturing, KRule}
--   Substrate.Cocycles.V4Signature.{S4GroupIso, Codeword/ReservedToBivectorAffine}
--   Substrate.Discipline                 — full rewrite, monomorphic
--
-- ===================================================================
-- COCYCLE FRAMEWORK UNIFICATION
-- ===================================================================
--
-- The substrate's cocycle abstraction is now uniformly
-- SetoidGroup-parametric:
--
--   Action     (G : SetoidGroup) (B : Set)
--   IsTorsor   (G : SetoidGroup) (T : Set)
--   IsomorphicCocycleStructure  -- Gauge : SetoidGroup
--   WeakCocycleStructure        -- Gauge : SetoidGroup
--
-- Group-on-_≡_ instances (V₄, F₂³) coerce in via `to-setoid` at
-- consumer sites. SetoidGroup-shaped groups (Symmetric, SFin,
-- Coxeter Word) plug directly.
--
-- ===================================================================
-- REMAINING STDLIB OFFENDER
-- ===================================================================
--
-- Only `Substrate.Algebra.Nat.GCD.agda` remains as a top-level stdlib
-- importer (uses `Data.Nat.Divisibility`, `Data.Nat.DivMod`,
-- `Data.Nat.Induction`, `Induction.WellFounded`). Per a parallel
-- agent's investigation, the preferred resolution is to make
-- `Coprime` parametric in `gcd-ℕ` rather than rewrite the EEA
-- substrate-natively. Deferred to a future arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.V-Arc.Capstone where

open import Substrate.Algebra.SetoidGroup
  using (SetoidGroup)
open import Substrate.Algebra.SetoidGroup.Properties
  using (module Props)
open import Substrate.Algebra.SetoidGroup.Action
  using (Action)
-- Note: Substrate.Algebra.GroupAction also defines `Action` (the
-- Group-on-≡ variant); consumers needing it import directly.
open import Substrate.Algebra.Torsor
  using (IsTorsorᴳ)
open import Substrate.Algebra.IsomorphicCocycle
  using (IsomorphicCocycleStructureᴳ)
open import Substrate.Algebra.SemidirectProduct
  using (SemidirectGroupObligation)
open import Substrate.Algebra.Group.ToSetoid
  using (to-setoid)
open import Substrate.Foundation.Hedberg
  using (DecidableEquality; Decidable⇒UIP)
open import Substrate.Foundation.Bool.Properties
  using (xor-assoc; xor-comm; xor-identityˡ;
         xor-identityʳ; xor-same)
open import Substrate.Foundation.Vec.Properties
  using (≡-dec)
