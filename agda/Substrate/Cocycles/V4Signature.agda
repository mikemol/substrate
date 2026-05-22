------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature
--
-- The CY-5 V₄-signature cocycle as an `IsomorphicCocycleStructure`
-- (catalog rule 11 strong). File-per-lemma:
--
--   V4Signature.Pairing.Type        — Pairing (3 V₄ axis-partitions)
--   V4Signature.Chirality.Type      — Chirality (even / odd)
--   V4Signature.OrbitKey.Type       — Pairing × Chirality (6 elts)
--   V4Signature.V4GroupSetoid       — V₄'s group structure as setoid
--   V4Signature.V4ToPairing         — V₄→Pairing partial fn + e-pair
--   V4Signature.V4ActsOnItself      — left-translation action
--   V4Signature.V4LeftCancel        — freeness witness
--   V4Signature.V4Transitive        — transitivity witness
--   V4Signature.V4IsTorsor          — bundled torsor instance
--   V4Signature.Fiber               — constant V₄ fiber + torsor
--   V4Signature.CY5                 — the IsomorphicCocycleStructure
--
-- Under this discipline:
--   * Invariant = OrbitKey = Pairing × Chirality (6 elements)
--   * Fiber over each orbit is V₄ itself (V₄-torsor; no canonical
--     baseline).
--   * TotalSpace = Σ OrbitKey (λ _ → V₄) — the 24 "signatures" are
--     DERIVED as (orbit_key, v4_position) pairs.
--
-- Notice what is NOT here:
--   * No primitive `Signature` record.
--   * No `project` function (it's the Σ-fst).
--   * No canonical-relative coordinate (no place in the type for one).
--
-- The current substrate's Signature + v4_delta encoding is recoverable
-- as a WeakCocycleStructure via Substrate.Cocycle.Downcast (with an
-- explicit canonical-section). The type system refuses the
-- rigidification by default.
--
-- See: catalog/cocycles.md § CY-5 and § Isomorphic storage.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature where

open import Substrate.Cocycles.V4Signature.Pairing.Type     public
open import Substrate.Cocycles.V4Signature.Chirality.Type   public
open import Substrate.Cocycles.V4Signature.OrbitKey.Type    public
open import Substrate.Cocycles.V4Signature.V4GroupSetoid    public
open import Substrate.Cocycles.V4Signature.V4ToPairing      public
open import Substrate.Cocycles.V4Signature.V4ActsOnItself   public
open import Substrate.Cocycles.V4Signature.V4LeftCancel     public
open import Substrate.Cocycles.V4Signature.V4Transitive     public
open import Substrate.Cocycles.V4Signature.V4IsTorsor       public
open import Substrate.Cocycles.V4Signature.Fiber            public
open import Substrate.Cocycles.V4Signature.CY5              public
