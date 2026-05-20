------------------------------------------------------------------------
-- Substrate.Groups.CyclicCoxeterStrict2Monoids
--
-- Capstone for Arc 1 (Z₅ closure + Strict2Monoid instances).
--
-- Re-exports the full family of cyclic Strict2Monoid instances:
--   * Z₂, Z₃, Z₄, Z₅ (cyclic of prime / prime-power orders)
--   * V₄ (Klein four, smallest non-cyclic example)
--   * FreeCyclic (= Z/∞, the cycle-counter axis)
--   * Z₃-x-FreeCyclic (2-D structure via DirectProduct combinator)
--
-- The pattern is now mechanical: each new Coxeter instance gets a
-- Strict2Monoid via FromCoxeter (one-line wrapper); each DirectProduct
-- combination gets a Strict2Monoid via Strict2Monoid.DirectProduct.
--
-- Per [[project-graded-bicategorical-arc]]: the categorical-name-first
-- approach lands cleanly. Every cyclic Coxeter group inherits
-- Strict2Monoid structure for free.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.CyclicCoxeterStrict2Monoids where

-- The per-instance lifts:
import Substrate.Groups.Z3-Coxeter-Strict2Monoid
import Substrate.Groups.Z4-Coxeter-Strict2Monoid
import Substrate.Groups.Z5-Coxeter-Strict2Monoid
import Substrate.Groups.FreeCyclic-Coxeter-Strict2Monoid
import Substrate.Groups.V4-Coxeter-Strict2Monoid

-- The DirectProduct combinator instances:
import Substrate.Groups.Z3-x-FreeCyclic-Strict2Monoid

-- The Z₅ closure (now combined into single Z5-Coxeter-Fin module):
import Substrate.Groups.Z5-Coxeter-Fin
import Substrate.Groups.Z5-x-FreeCyclic
import Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection
import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5

------------------------------------------------------------------------
-- After Arc 1:
--
--   * Z₃ chain (Fin bijection + Action + HasOrderPerm) ✓
--   * Z₄ chain (Fin combined in Z4-Coxeter-Fin module)        ✓
--   * Z₅ chain (Fin + Action + HasOrderPerm)                   ✓ (this arc)
--   * Cycle5 instance + HasOrder via the lift                  ✓
--   * 2-D word algebra at Z₃, Z₄, Z₅ via DirectProduct         ✓
--   * Strict2Monoid lifts for Z₃, Z₄, Z₅, FreeCyclic, V₄, Z₃×F ✓
--
-- The substrate now has comprehensive cyclic Coxeter coverage at
-- n=2, 3, 4, 5, plus the FreeCyclic / DirectProduct infrastructure
-- to build any combination.
--
-- Per [[feedback-categorical-name-first]]: each instance is named
-- categorically (Strict2Monoid record); per [[feedback-roll-our-own-
-- via-word-algebra]]: all built on the substrate's own word algebra
-- without stdlib heavy deps.
--
-- Deferred follow-ons:
--
--   * **Z₆ = Z₂ × Z₃ via CRT-style DirectProduct**: substrate has
--     Z₂ and Z₃; can build Z₆ via DirectProduct (since gcd(2,3) = 1).
--     Demonstrates the CRT pattern at the simplest composite case.
--
--   * **Z₇, Z₈, Z₉ Coxeter instances**: more prime / prime-power
--     orders. Mechanical mirror; just file-creation work.
--
--   * **Z₅-x-FreeCyclic-Strict2Monoid**: same pattern as Z₃-x-F,
--     mechanical.
------------------------------------------------------------------------
