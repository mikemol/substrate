------------------------------------------------------------------------
-- Substrate.Groups.ConsolidatedCyclicCoxeter
--
-- Capstone for the audit-driven consolidation arc.
--
-- Surfaces the parametric infrastructure introduced:
--
--   * Substrate.Groups.Zn-x-FreeCyclic
--       Parametric DirectProduct combinator: takes any cyclic Coxeter
--       instance's Core data and produces the Zₙ × ℕ 2-D structure.
--
--   * Substrate.Groups.Zn-Coxeter-Strict2Monoid
--       Parametric Strict2Monoid lift: takes Coxeter Core data and
--       produces the categorical Strict2Monoid.
--
--   * Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism
--       F₂-graded combinator: takes a Word monoid + ℕ-homomorphism
--       and produces the F₂-graded RGradedMonoid via parity ∘ hom.
--
-- After the consolidation arc, per-n cyclic Coxeter instances at
-- n=3,4,5 get ALL the structural lifts via thin one-line wrappers:
--
--   * Zn-x-FreeCyclic           (2-D word algebra)
--   * Zn-Coxeter-Strict2Monoid  (categorical Strict2Monoid)
--   * F₂-grading via FromCoxeterHomomorphism + a count/length function
--
-- The Z3 / Z4 / Z5 chain (Coxeter-Fin / Action / HasOrderPerm) was
-- ALSO unified to a single per-n module (combined pattern, matching
-- Z4's original presentation).
--
-- Net savings across the consolidation arc: ~300 LoC + structural
-- uniformity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.ConsolidatedCyclicCoxeter where

-- Parametric combinators (new):
import Substrate.Groups.Zn-x-FreeCyclic
import Substrate.Groups.Zn-Coxeter-Strict2Monoid
import Substrate.Category.RGradedMonoid.FromCoxeterHomomorphism

-- Combined Coxeter-Fin chains (Z₃ and Z₅ rewritten to Z₄'s combined
-- pattern):
import Substrate.Groups.Z3-Coxeter-Fin
import Substrate.Groups.Z4-Coxeter-Fin
import Substrate.Groups.Z5-Coxeter-Fin

-- Per-n thin instantiations of the parametrics:
import Substrate.Groups.Z3-x-FreeCyclic
import Substrate.Groups.Z4-x-FreeCyclic
import Substrate.Groups.Z5-x-FreeCyclic

import Substrate.Groups.Z3-Coxeter-Strict2Monoid
import Substrate.Groups.Z4-Coxeter-Strict2Monoid
import Substrate.Groups.Z5-Coxeter-Strict2Monoid

-- F₂-graded V₄ instances via the combinator:
import Substrate.Groups.V4-Coxeter-F2Graded
import Substrate.Groups.V4-Coxeter-F2Graded-CountA
import Substrate.Groups.V4-Coxeter-F2Graded-CountB

------------------------------------------------------------------------
-- After this arc:
--
--   * 10 slices completed.
--   * 4 files deleted (Z3/Z5 Action + HasOrderPerm splits).
--   * 3 new parametric modules (Zn-x-FreeCyclic,
--     Zn-Coxeter-Strict2Monoid, FromCoxeterHomomorphism).
--   * Per-n instances reduced to thin instantiations.
--
-- Future Zₙ instances (Z₇, Z₈, Z₁₁, …) inherit the full structural
-- lift stack mechanically via these parametrics.
--
-- Per [[feedback-file-size-one-pass-rewrite]]: each instantiation
-- file is now small enough to rewrite in one Write pass, no Edit
-- patching needed for future maintenance.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]:
-- the parametric + thin-instantiation pattern is the substrate's
-- preferred decomposition for repeated-shape instances.
------------------------------------------------------------------------
