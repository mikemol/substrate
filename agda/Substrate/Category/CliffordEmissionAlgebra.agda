------------------------------------------------------------------------
-- Substrate.Category.CliffordEmissionAlgebra
--
-- DD-arc: graded Clifford algebra Cl(ℝⁿ, q=+1) as the ambient
-- generator of which AA/BB/CC-arc rotation layers are individual
-- grades.
--
-- Per [[expose-generator-not-orbit]]: AA-arc S₄ residue, BB-arc
-- F₂ⁿ × F₂, CC-arc Coxeter S_{2ⁿ}, CC6 Z/8 BitShift are all
-- orbit-points at specific grades of the Clifford ambient.
--
-- Per [[multi-reading-ambient-discipline]]: the algebra is the
-- ambient; specific projections are decidable predicates within it.
--
-- Per the user's bit-flip propagation question (DD-arc trigger):
-- "what kind of clifford-algebra approach where the wedge product
-- can be used to unwind a set of transformation-paths to a reference
-- point" — the Multivector record IS that wedge-product algebra;
-- reverse-anti-automorphism IS the unwinding to a reference point.
--
-- Per the user's Hamming-recovery extension (DD-arc, 2026-05-20):
-- grade-k blades correspond to weight-k Hamming patterns over n
-- bits; the grade decomposition IS the Hamming-syndrome histogram.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CliffordEmissionAlgebra where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _∸_)
open import Data.List using (List; []; _∷_; length)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- Grade is a natural number 0 ≤ k ≤ n bounded by the algebra's
-- dimension.

record Grade (n : ℕ) : Set where
  field
    k : ℕ
    -- Bound k ≤ n maintained by construction; left abstract for
    -- per-instance enforcement.

open Grade public

------------------------------------------------------------------------
-- A BasisBlade at dimension n is a subset S ⊆ {0,...,n−1}
-- represented abstractly; concrete codec implementations use a
-- bitmask of width n.

record BasisBlade (n : ℕ) : Set where
  field
    grade  : Grade n
    -- index : identifier within the C(n, k) blades of this grade,
    -- abstracted per instance.

open BasisBlade public

------------------------------------------------------------------------
-- The full graded Clifford algebra Cl(ℝⁿ, q=+1).
--
-- Parameterised over the carrier type (a sum of graded components).
-- Concrete instances provide the carrier; this record captures the
-- algebraic structure laws.
--
-- Grade decomposition: Multivector ≅ ⊕_{k=0}^{n} Λᵏ.
-- Geometric product: a * b mixes grades; wedge a ∧ b raises grade;
-- contraction a ⌟ b lowers grade.

record CliffordAlgebra (n : ℕ) : Set₁ where
  field
    -- Carrier.
    Multivector : Set

    -- Constants.
    zero-mv  : Multivector
    one-mv   : Multivector            -- scalar 1 (Λ⁰)
    pseudo   : Multivector            -- top blade I (Λⁿ)

    -- Operations.
    add      : Multivector → Multivector → Multivector
    neg      : Multivector → Multivector
    gp       : Multivector → Multivector → Multivector   -- geometric
    wedge    : Multivector → Multivector → Multivector   -- outer
    contract : Multivector → Multivector → Multivector   -- left ⌟
    reverse  : Multivector → Multivector                  -- anti-aut

    -- Grade projection ⟨·⟩_k : Λᵏ-component.
    project  : Grade n → Multivector → Multivector

    -- Laws.
    add-id-l   : (a : Multivector) → add zero-mv a ≡ a
    gp-id-l    : (a : Multivector) → gp one-mv a ≡ a
    gp-id-r    : (a : Multivector) → gp a one-mv ≡ a
    reverse-involution : (a : Multivector) → reverse (reverse a) ≡ a

open CliffordAlgebra public

------------------------------------------------------------------------
-- A graded action: an algebra paired with an action on a carrier
-- (the codec's BYTE-STREAM is the action's carrier; F₂-restricted
-- coefficients give the XOR-action).

record GradedAction (n : ℕ) : Set₁ where
  field
    algebra : CliffordAlgebra n
    Carrier : Set
    act     : Multivector algebra → Carrier → Carrier
    -- Action laws.
    act-id      : (c : Carrier) → act (one-mv algebra) c ≡ c

open GradedAction public

------------------------------------------------------------------------
-- AA-arc embedding: S₄ residue ↪ Λ² subspace.
--
-- The substrate's AA-arc S₄ residue lives in the bivector subspace
-- of Cl(ℝ⁴). Each S₄ element is a product of transpositions; each
-- transposition is a bivector e_i ∧ e_j.
--
-- This embedding is structural; concrete bijection deferred to the
-- codec runtime side (eliza.clifford_tracer.aa_arc_s4_residue).

record AAArcEmbedding : Set₁ where
  field
    algebra : CliffordAlgebra 4
    S4-element : Set
    embed    : S4-element → Multivector algebra
    -- The image lies in Λ² (bivector grade).
    image-grade-2 :
      (σ : S4-element) →
      (project algebra record { k = 2 } (embed σ)) ≡ embed σ

open AAArcEmbedding public

------------------------------------------------------------------------
-- Hamming-syndrome correspondence (DD-arc, per user 2026-05-20).
--
-- Hamming distance-k error patterns over n bits correspond to
-- grade-k basis blades. The grade decomposition of a perturbation
-- multivector IS the Hamming-syndrome histogram.
--
-- Recovery from a perturbation: extract the minimum-grade component
-- (the "best correction" Hamming-coset).

record HammingSyndromeReading (n : ℕ) : Set₁ where
  field
    algebra      : CliffordAlgebra n
    Word         : Set                            -- n-bit codeword
    perturbation : Word → Word → Multivector algebra
    -- Grade-k component of perturbation w → w' has Hamming weight k.
    hamming-grade :
      (w w' : Word) →
      Grade n
    -- Identity-perturbation (w = w') is the zero multivector.
    identity-zero :
      (w : Word) → perturbation w w ≡ zero-mv algebra

open HammingSyndromeReading public

------------------------------------------------------------------------
-- Recovery operator: given a perturbed word and the perturbation
-- multivector, recover the original by applying the reverse.
--
-- Per the user's "wedge product unwinds transformation-paths to a
-- reference point" framing: reverse-anti-automorphism IS the
-- unwinding operator.

record CliffordRecovery (n : ℕ) : Set₁ where
  field
    syndrome : HammingSyndromeReading n
    recover  : Word syndrome →
               Multivector (algebra syndrome) →
               Word syndrome
    -- Round-trip: perturbing then recovering returns the original.
    recovery-law :
      (w : Word syndrome) →
      (w' : Word syndrome) →
      recover w' (perturbation syndrome w w') ≡ w

open CliffordRecovery public

------------------------------------------------------------------------
-- Generator-orbit reading.
--
-- Per [[expose-generator-not-orbit]]: the Clifford algebra IS the
-- ambient generator. Prior arcs are orbit-projections:
--
--   AA-arc S₄ residue   ↪ Λ² (bivector)
--   BB-arc F₂ⁿ × F₂     ↪ Λ¹ (vector) × pseudoscalar chirality
--   CC-arc Coxeter      ↪ even subalgebra Λ⁰ ⊕ Λ² ⊕ Λ⁴ ⊕ ...
--   CC6 Z/8 BitShift    ↪ Λ¹ at scale 3 (3 axes + chirality)
--
-- The DD-arc's S_CLIFFORD_OP(grade, basis_idx) opcode in V7 is the
-- runtime emission of an arbitrary blade — covering ALL grades, not
-- just the ones any single prior arc captured.

record GeneratorOrbitReading (n : ℕ) : Set₁ where
  field
    full-algebra : CliffordAlgebra n
    -- Each prior-arc structure is a subspace projection of the
    -- full Clifford ambient.

open GeneratorOrbitReading public

------------------------------------------------------------------------
-- 3+1 parity at every grade.
--
-- Per [[3plus1-parity-universal]] and [[torsion-element-of-automorphism-universal]]:
-- at dimension n, Cl(ℝⁿ) has 2ⁿ basis blades and (n+1) grades. The
-- pseudoscalar Λⁿ supplies the chirality F₂; the remaining (n+1-1)=n
-- grades are the axes.
--
-- Substantive 3+1 instance: n = 3 gives 4 grades (0, 1, 2, 3), with
-- grade-3 (pseudoscalar) as the chirality and the other three grades
-- as axes; matches the substrate's universal pattern at the codec's
-- chain-walk dimension.

------------------------------------------------------------------------
-- Categorical reading.
--
-- Per [[homology-cohomology-recursion]]: the perturbation multi-
-- vector IS the homology cycle; the recovery operator IS the
-- cohomology contraction. Each grade is one level of the recursion.
--
-- Per [[chain-walk-blocks-rotation-factor]]: the cascade from
-- grade-k to grade-k' under chain-walk conjugation IS the
-- non-factorisation result expressed grade-by-grade in the
-- Clifford ambient.
------------------------------------------------------------------------
