------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit
--
-- Z-arc: the "reference earlier output" generator family. Per
-- [[expose-generator-not-orbit]] and the Z-arc analysis: QUOT
-- (alias-define) and DEFLATE back-reference are SISTER ORBITS at
-- the same generator. Each orbit is parameterised by three binary
-- axes:
--
--   SourceClass    : ExistingRuleSlice ∨ ArbitraryRecentSpan
--   Permanence     : PermanentRule     ∨ OneShot
--   BindingClass   : ChamberBound      ∨ ChamberFree
--
-- The 2³ = 8 orbits at this generator catalogue the substrate's
-- reference-emission family.
--
-- Per [[3plus1-parity-universal]]: the (3-axis × 1-binding) shape
-- with one chirality axis (the binding-class) might realise another
-- instance of the substrate's 3+1 universal — the binding axis
-- carries the chirality of substrate-aligned vs structure-agnostic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- The three axes.

data SourceClass : Set where
  ExistingRuleSlice    : SourceClass
  ArbitraryRecentSpan  : SourceClass

data Permanence : Set where
  PermanentRule  : Permanence
  OneShot        : Permanence

data BindingClass : Set where
  ChamberBound   : BindingClass
  ChamberFree    : BindingClass

------------------------------------------------------------------------
-- A reference orbit is a point in the 2³ orbit space.

record ReferenceOrbit : Set where
  field
    source       : SourceClass
    permanence   : Permanence
    binding      : BindingClass

open ReferenceOrbit public

------------------------------------------------------------------------
-- The 8 orbits, named.

QUOT : ReferenceOrbit
QUOT = record { source = ExistingRuleSlice
              ; permanence = PermanentRule
              ; binding = ChamberBound }

-- Z1: chain-symbol LZ77-style backref. ArbitraryRecentSpan ×
-- OneShot × ChamberBound (operates in chain space, so chamber-state
-- alignment is required — but no V₄ residue compensation yet, so
-- effectively ChamberBound).
ChainBackRef : ReferenceOrbit
ChainBackRef = record { source = ArbitraryRecentSpan
                       ; permanence = OneShot
                       ; binding = ChamberBound }

-- Z2: byte-level LZ77-style backref. Operates on raw output bytes,
-- bypassing chamber state.
ByteBackRef : ReferenceOrbit
ByteBackRef = record { source = ArbitraryRecentSpan
                       ; permanence = OneShot
                       ; binding = ChamberFree }

-- A QUOT-style permanent rule from an ARBITRARY recent span (not
-- restricted to existing-rule slices). The U-arc's QUOT-stack
-- design ([[quot-stack-associativity-scope]]) at full generality.
QUOTRecent : ReferenceOrbit
QUOTRecent = record { source = ArbitraryRecentSpan
                     ; permanence = PermanentRule
                     ; binding = ChamberBound }

-- A one-shot reference to an existing rule's slice. Cheaper than
-- QUOT (no rule growth) but still chamber-state-bound.
OneShotSlice : ReferenceOrbit
OneShotSlice = record { source = ExistingRuleSlice
                       ; permanence = OneShot
                       ; binding = ChamberBound }

-- Chamber-free variants — would require V₄/S₄ residue compensation
-- in the matcher. Reserved for future arcs (X-arc residue runtime).

ChamberFreeQUOT : ReferenceOrbit
ChamberFreeQUOT = record { source = ExistingRuleSlice
                          ; permanence = PermanentRule
                          ; binding = ChamberFree }

ChamberFreeQUOTRecent : ReferenceOrbit
ChamberFreeQUOTRecent = record { source = ArbitraryRecentSpan
                                ; permanence = PermanentRule
                                ; binding = ChamberFree }

ChamberFreeOneShotSlice : ReferenceOrbit
ChamberFreeOneShotSlice = record { source = ExistingRuleSlice
                                  ; permanence = OneShot
                                  ; binding = ChamberFree }

------------------------------------------------------------------------
-- The 8 orbits collected.

data OrbitName : Set where
  QUOT-orbit                    : OrbitName
  ChainBackRef-orbit            : OrbitName
  ByteBackRef-orbit             : OrbitName
  QUOTRecent-orbit              : OrbitName
  OneShotSlice-orbit            : OrbitName
  ChamberFreeQUOT-orbit         : OrbitName
  ChamberFreeQUOTRecent-orbit   : OrbitName
  ChamberFreeOneShotSlice-orbit : OrbitName

orbit-of : OrbitName → ReferenceOrbit
orbit-of QUOT-orbit                    = QUOT
orbit-of ChainBackRef-orbit            = ChainBackRef
orbit-of ByteBackRef-orbit             = ByteBackRef
orbit-of QUOTRecent-orbit              = QUOTRecent
orbit-of OneShotSlice-orbit            = OneShotSlice
orbit-of ChamberFreeQUOT-orbit         = ChamberFreeQUOT
orbit-of ChamberFreeQUOTRecent-orbit   = ChamberFreeQUOTRecent
orbit-of ChamberFreeOneShotSlice-orbit = ChamberFreeOneShotSlice

------------------------------------------------------------------------
-- The 3+1 parity reading.
--
-- Three independent binary axes (SourceClass, Permanence,
-- BindingClass) give 2³ = 8 orbits. The BindingClass axis carries
-- the chirality of substrate-aligned (ChamberBound, structural) vs
-- structure-agnostic (ChamberFree, LZ77-style). The (3, 1) split:
--   3 = the orbit-internal axes (source, permanence, binding within
--       the same alignment class)
--   1 = the chirality between aligned and free
--
-- Per [[3plus1-parity-universal]] this is the universal substrate
-- pattern showing up at the reference-generator level.

chirality-of : ReferenceOrbit → BindingClass
chirality-of o = binding o

------------------------------------------------------------------------
-- Categorical reading.
--
-- The ReferenceOrbit family is the operad's "ring of reference
-- generators." Each orbit instantiates ONE element of V7's
-- generator ring. Per [[v-arc-generator-operad]] the codec's full
-- expressive space at the reference axis is the operad over
-- ReferenceOrbit instances.
--
-- Per [[expose-generator-not-orbit]]: prior arcs picked QUOT and
-- ChainBackRef without exposing the 8-orbit family. The Z-arc names
-- the family so future codec work can speculate over orbits per
-- emission rather than rigidifying any single one.
------------------------------------------------------------------------
