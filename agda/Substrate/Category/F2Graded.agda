------------------------------------------------------------------------
-- Substrate.Category.F2Graded
--
-- Capstone for Arc 2 (F₂-graded GradedMonoid infrastructure).
--
-- Re-exports the F₂-graded primitives + canonical instances:
--   * CommutativeMonoid record (slice 11) — foundation for R-grading.
--   * RGradedMonoid record (slice 12) — R-graded generalization.
--   * F₂-CommMonoid (slice 13) — F₂'s additive CommutativeMonoid.
--   * parity (slice 14) — ℕ → F₂ homomorphism.
--   * V₄-F2Graded (slice 15) — V₄ length-parity grading.
--   * V₄-F2Graded-CountA (slice 16) — V₄ count-A-parity grading.
--   * V₄-F2Graded-CountB (slice 17) — V₄ count-B-parity grading.
--   * Bivector-F2Graded (slice 18) — Bivector weight-parity grading.
--   * project_f2_grading_at_substrate_sites memory (slice 19).
--
-- The substrate now has comprehensive F₂-graded infrastructure.
-- Multiple F₂-gradings on V₄ (three independent monoid homomorphisms
-- into F₂); a weight-parity grading on Bivector; foundation for
-- more (any Word A, any Vec F₂ n, etc.) to follow the same pattern.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.F2Graded where

-- Primitives.
import Substrate.Category.CommutativeMonoid
import Substrate.Category.RGradedMonoid
import Substrate.Algebra.F2-CommutativeMonoid
import Substrate.Algebra.N-to-F2-Parity

-- Word.Length utility (used by length-parity).
import Substrate.Groups.Coxeter.Word.Length

-- V₄ instances.
import Substrate.Groups.V4-Coxeter-F2Graded
import Substrate.Groups.V4-Coxeter-F2Graded-CountA
import Substrate.Groups.V4-Coxeter-F2Graded-CountB

-- Bivector instance.
import Substrate.Algebra.F2.HodgeDim4.Bivector-F2Graded

------------------------------------------------------------------------
-- Capstone — F₂-graded infrastructure complete.
--
-- The 20-slice plan's Arc 2:
--
--   #11 CommutativeMonoid
--   #12 RGradedMonoid
--   #13 F₂-CommMonoid
--   #14 parity (ℕ → F₂)
--   #15 V₄-F2Graded (length-parity)
--   #16 V₄-F2Graded-CountA (count-A-parity)
--   #17 V₄-F2Graded-CountB (count-B-parity)
--   #18 Bivector-F2Graded (weight-parity)
--   #19 project_f2_grading_at_substrate_sites memory
--   #20 THIS capstone
--
-- Key structural finding (per slice 19's memory):
-- the 3+1 parity universal is CARRIER-SET DECOMPOSITION,
-- NOT a monoid grading. V₄ has three independent F₂-gradings
-- (length, count-A, count-B) but none correspond directly to the
-- 3+1 split (V₄-Nonzero + identity), because V₄-Nonzero isn't
-- closed under ·.
--
-- The F₂-graded primitives capture the parity-invariant flavor;
-- the 3+1 carrier-set decomposition is a separate (set-level)
-- structural feature.
--
-- Per [[feedback-categorical-name-first]]: "F₂-grading" is now the
-- categorical name for parity invariants throughout the substrate.
--
-- Per [[project-graded-bicategorical-arc]]: this completes the
-- R-graded extension (R = F₂). The ℕ-graded version (from the
-- previous arc) and F₂-graded version (this arc) together form
-- the substrate's grading infrastructure.
--
-- Deferred follow-ons:
--
--   * Z/p-graded for arbitrary p (using p-Coxeter instances as the
--     CommutativeMonoid R).
--
--   * F₂-graded instances at other substrate sites: codes
--     (syndrome-parity), BilinForm (det-parity), polynomial degree-
--     parity, etc.
--
--   * The 3+1 carrier-set decomposition formalised as a separate
--     primitive (subset-with-partition) rather than as a graded
--     monoid.
--
--   * Coxeter Word algebras' generic length-parity grading lifted
--     to a substrate-wide combinator (CoxeterWord → F₂-graded for
--     ANY Coxeter instance, mechanically).
------------------------------------------------------------------------
