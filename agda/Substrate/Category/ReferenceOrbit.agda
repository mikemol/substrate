------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit
--
-- Z-arc: the "reference earlier output" generator family. The 2³ = 8
-- orbits at the reference generator, parameterised by three binary
-- axes (SourceClass × Permanence × BindingClass). File-per-lemma:
--
--   ReferenceOrbit.SourceClass    — ExistingRuleSlice ∨ ArbitraryRecentSpan
--   ReferenceOrbit.Permanence     — PermanentRule ∨ OneShot
--   ReferenceOrbit.BindingClass   — ChamberBound ∨ ChamberFree (chirality)
--   ReferenceOrbit.Record         — the 3-field record
--
-- The 8 named orbits:
--   ReferenceOrbit.QUOT                    — substrate-aligned alias-define
--   ReferenceOrbit.ChainBackRef            — Z1 chain-symbol backref
--   ReferenceOrbit.ByteBackRef             — Z2 byte-level backref
--   ReferenceOrbit.QUOTRecent              — permanent recent-span rule
--   ReferenceOrbit.OneShotSlice            — one-shot rule-slice ref
--   ReferenceOrbit.ChamberFreeQUOT         — chamber-free variants
--   ReferenceOrbit.ChamberFreeQUOTRecent
--   ReferenceOrbit.ChamberFreeOneShotSlice
--
--   ReferenceOrbit.OrbitName      — 8-tag data + orbit-of dispatch
--   ReferenceOrbit.Chirality      — chirality-of projection
--
-- Per [[expose-generator-not-orbit]] + [[3plus1-parity-universal]]:
-- the 3 internal axes plus the binding-chirality axis instantiate the
-- substrate's 3+1 universal at the reference-generator level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit where

open import Substrate.Category.ReferenceOrbit.SourceClass              public
open import Substrate.Category.ReferenceOrbit.Permanence               public
open import Substrate.Category.ReferenceOrbit.BindingClass             public
open import Substrate.Category.ReferenceOrbit.Record                   public
open import Substrate.Category.ReferenceOrbit.QUOT                     public
open import Substrate.Category.ReferenceOrbit.ChainBackRef             public
open import Substrate.Category.ReferenceOrbit.ByteBackRef              public
open import Substrate.Category.ReferenceOrbit.QUOTRecent               public
open import Substrate.Category.ReferenceOrbit.OneShotSlice             public
open import Substrate.Category.ReferenceOrbit.ChamberFreeQUOT          public
open import Substrate.Category.ReferenceOrbit.ChamberFreeQUOTRecent    public
open import Substrate.Category.ReferenceOrbit.ChamberFreeOneShotSlice  public
open import Substrate.Category.ReferenceOrbit.OrbitName                public
open import Substrate.Category.ReferenceOrbit.Chirality                public
