------------------------------------------------------------------------
-- Substrate.Category.GradedBicategorical
--
-- Capstone module for the graded bicategorical arc.
--
-- After this arc, the substrate has:
--
--   * Strict2Monoid (slice 1) — the categorical primitive for
--     1-object strict 2-categories.
--   * Strict2Monoid.FromCoxeter (slice 2) — any Coxeter Core instance
--     lifts to a Strict2Monoid.
--   * V₄-Coxeter-Strict2Monoid (slice 3) — V₄ as the canonical
--     instance demonstration.
--   * GradedMonoid (slice 4) — ℕ-graded monoid record.
--   * FreeCyclic-Coxeter-GradedMonoid (slice 5) — length is the
--     canonical grading.
--   * Z3-x-FreeCyclic-Degree (slice 6) — cycle-component ℕ-grading
--     on the 2-D word algebra.
--   * Z3-x-Z4-x-FreeCyclic (slice 7) — 3-axis strict-monoid (3
--     commuting cyclic structures + ℕ-degree).
--   * Strict2Monoid.DirectProduct (slice 8) — the categorical-level
--     direct product combinator.
--   * project_3plus1_as_graded_cocycle memory (slice 9) — connects
--     the 3+1 parity universal to the graded cocycle reading.
--   * THIS capstone (slice 10).
--
-- The substrate now has the full graded-bicategorical infrastructure
-- at the strict / 1-object level. Coxeter's Word/_++_/_≈_ trio is
-- recognized as the canonical Strict2Monoid; FreeCyclic is the
-- canonical ℕ-grading; DirectProduct iterates to give arbitrary
-- n-axis compositions; the 3+1 parity universal is named as a
-- degree-1 cocycle.
--
-- Per [[feedback-categorical-name-first]]: the substrate's word
-- algebra structures now have categorical names. The graded
-- bicategorical structure was IMPLICIT in the Coxeter framework;
-- this arc named it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GradedBicategorical where

------------------------------------------------------------------------
-- Re-export the primitive records.
------------------------------------------------------------------------

import Substrate.Category.Strict2Monoid
import Substrate.Category.Strict2Monoid.FromCoxeter
import Substrate.Category.Strict2Monoid.DirectProduct
import Substrate.Category.GradedMonoid

------------------------------------------------------------------------
-- Re-export the canonical instances.
------------------------------------------------------------------------

import Substrate.Groups.V4-Coxeter-Strict2Monoid
import Substrate.Groups.FreeCyclic-Coxeter-GradedMonoid
import Substrate.Groups.Z3-x-FreeCyclic-Degree.CycleDegree
import Substrate.Groups.Z3-x-FreeCyclic-Degree.DegreeEpsilon
import Substrate.Groups.Z3-x-FreeCyclic-Degree.DegreeDot
import Substrate.Groups.Z3-x-Z4-x-FreeCyclic

------------------------------------------------------------------------
-- Capstone — graded bicategorical arc complete.
--
-- Substrate-wide implication: every Coxeter group (Z₂, Z₃, Z₄, Z₅,
-- V₄, FreeCyclic, plus all DirectProduct combinations) inherits
-- Strict2Monoid structure. FreeCyclic + DirectProduct give the
-- grading-axis infrastructure.
--
-- The "graded bicategorical structure for free" claim the user
-- identified is now realized: 1-cells from Coxeter Words; 2-cells
-- from normalize-equality; horizontal composition strict on ++;
-- horizontal composition of 2-cells via ·-cong (= cong on
-- normalize-distrib); grading via length on the FreeCyclic axis.
--
-- Per [[project-graded-bicategorical-arc]]: arc closed. Next
-- structural arcs to consider:
--
--   * **Weak 2-monoid (Bicategory)**: use _·_ (= normalize ∘ ++)
--     as horizontal composition; associativity becomes weak (≈,
--     not on the nose). Adds coherence cells (pentagon, triangle).
--
--   * **Functor Strict2Monoid → Strict2Monoid**: monoid morphism
--     respecting both 1-cell composition and 2-cells. Phase-projection
--     (previous arc's slice 4) IS such a functor; this arc would
--     name it categorically.
--
--   * **F₂-grading (= Z/2-grading)**: generalize GradedMonoid from
--     ℕ-grading to R-grading for any commutative monoid R. Then
--     V₄ with the 3+1 parity becomes a canonical Z/2-graded instance
--     (per [[project-3plus1-as-graded-cocycle]]).
--
--   * **Higher-categorical (n > 2)**: nested DirectProduct gives
--     strict n-monoids; substrate can probe up to whatever n is
--     useful for cocycle hierarchies.
--
--   * **CRT decomposition primitive**: for coprime m, n, Z/(mn) ≅
--     Z/m × Z/n via DirectProduct + the GradedMonoid degree maps
--     into a CRT-style decomposition. Connects the prime-power
--     primitive insight (Z/4 ≠ Z/2 × Z/2 but Z/6 = Z/2 × Z/3) to
--     the categorical machinery.
--
-- Per [[feedback-roll-our-own-via-word-algebra]] and
-- [[feedback-categorical-name-first]]: the substrate's word algebra
-- is now the substrate-native answer to "where do graded
-- bicategorical structures come from." Roll our own + categorical
-- naming both honored.
------------------------------------------------------------------------
