{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.S5.BridgeRegistry — the S5-metacircular ↔ substrate BRIDGE INDEX.
--
-- The discoverable, first-class index of the witnessed transports connecting the
-- S5 cluster to the substrate structures it reflects. Registration = this module
-- COMPILING — the reality anchor (cf. Category.UniversalProperty.Registry: "the
-- typechecker is the gate, not a grep"). Each bridge below is a genuine transport
-- by the mere fact this file typechecks; none can be a vacuous claim.
--
-- COVERAGE (the unification metric) = these bridges vs the S5 modules that re-derive
-- a substrate structure. Grow the list to unify. This is the Level-2 bridge-of-bridges
-- made first-class: the S5 cluster is a WITNESSED REFLECTION of the substrate across
-- its keystones — a 2×2 CF matrix, the coinductive reals, the wedge operator, the
-- Klein four-group — not four silent re-derivations. (Governed by
-- feedback_dedup_preserve_crossdomain_bridges: dedup CROSS-domain = witness, not collapse.)
--
--   BRIDGE                 S5 module            ≅  substrate keystone           (what it witnesses)
--   ──────────────────────────────────────────────────────────────────────────────────────────────
--   S5MatrixBridge         S5Matrix             ≅  R.Trace.CFMatrixBridge       2×2 CF matrix; det = (−1)ⁿ
--   S5RealBridge           S5Real / S5RealConv  ≅  R.Trace (RealTrace)          coinductive reals; √2; convergents
--   S5EEABridge            S5EEA                ≅  Algebra.Wedge                 wedge-zip; shape = continued fraction
--   S5TorsorWireV4 (iso)   KleinV4              ≅  Groups.V4.V₄ → BV₄            Klein four-group; delooped to the Category spine
------------------------------------------------------------------------

module Substrate.S5.BridgeRegistry where

import Substrate.S5.S5MatrixBridge
import Substrate.S5.S5RealBridge
import Substrate.S5.S5EEABridge
import Substrate.S5.S5TorsorWireV4
