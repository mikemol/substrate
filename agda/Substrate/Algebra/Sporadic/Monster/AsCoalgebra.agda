------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.Monster.AsCoalgebra
--
-- The Monster group M as a ConjugationCoalgebra — the canonical
-- EXTREME instance demonstrating the substrate's top-down framework
-- where the bottom-up (PresentedGroup) direction is intractable.
--
-- T8 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. With T0-T7 in place, T8 shows that
-- the substrate's PrimeFactoredGauge / ConjugationCoalgebra
-- machinery scales to the Monster — the largest known sporadic
-- simple group, order 2^46·3^20·5^9·...·71 ≈ 8 × 10^53.
--
-- Per Q3-Q5 of [[q1-q5-entailment-chain]]: the Monster's natural
-- substrate representation is top-down (introspection-and-diffraction
-- via conjugacy classes), not bottom-up (presentation). The Griess
-- construction (= Monster as Aut(GriessAlgebra) = Aut(V♮₂)) IS the
-- substrate-compatible identification.
--
-- Per substrate's no-postulate discipline: this module is MODULE-
-- PARAMETRIC over the Monster's abstract data (carrier, group ops,
-- 194 conjugacy classes from ATLAS, axioms). No content is
-- postulated; the module SUPPLIES the wiring to ConjugationCoalgebra,
-- downstream consumers supply the parameters (citing CFSG +
-- ATLAS-published data).
--
-- The 194 conjugacy classes are well-documented external mathematical
-- content (ATLAS of Finite Groups; Conway-Norton; Frenkel-Lepowsky-
-- Meurman). This module does not duplicate the data; it bridges it
-- into the substrate's ConjugationCoalgebra primitive.
--
-- Per [[categorical-name-first]]: "Monster as ConjugationCoalgebra"
-- is the substrate-side equivalent of "Monster = Aut(V♮)". The
-- ConjugationCoalgebra captures the class + introspection structure;
-- the VOA / Griess-algebra connection lives at downstream consumer
-- modules.
--
-- Per [[expose-generator-not-orbit]] applied at extreme scale: 194
-- classes (vs. 8 × 10^53 elements). The substrate-friendly
-- representation is the class data, not the element enumeration.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Level using (0ℓ)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra; mkConjugationCoalgebra)

module Substrate.Algebra.Sporadic.Monster.AsCoalgebra
  -- The abstract Monster carrier.
  (M : Set)
  -- Group operations on M.
  (_·M_ : M → M → M)
  (εM : M)
  (_⁻¹M : M → M)
  -- The 194 conjugacy classes (ATLAS-cited count).
  (rep-M : Fin 194 → M)
  (in-class-M : Fin 194 → M → Set)
  -- Class structure axioms.
  (in-class-rep-M : (c : Fin 194) → in-class-M c (rep-M c))
  (conjugation-respects-class-M :
    (g : M) (c : Fin 194) (h : M) →
    in-class-M c h →
    in-class-M c ((g ·M h) ·M (g ⁻¹M)))
  where

------------------------------------------------------------------------
-- 1. The Monster as a ConjugationCoalgebra.
--
-- Direct construction of the ConjugationCoalgebra record from the
-- module parameters. No substantive content beyond wiring — the
-- 194 conjugacy classes + axioms ARE the substrate-side Monster.
------------------------------------------------------------------------

Monster-ConjugationCoalgebra : ConjugationCoalgebra
Monster-ConjugationCoalgebra = mkConjugationCoalgebra
  M
  _·M_
  εM
  _⁻¹M
  (Fin 194)
  rep-M
  in-class-M
  in-class-rep-M
  conjugation-respects-class-M

------------------------------------------------------------------------
-- 2. Number of conjugacy classes (= 194; ATLAS-cited).
------------------------------------------------------------------------

Monster-class-count : ℕ
Monster-class-count = 194

------------------------------------------------------------------------
-- 3. Capstone — the Monster lives in the substrate.
--
-- T8 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. With T8 instantiated (via downstream
-- consumer supplying the 7 parameters from ATLAS data), the
-- substrate has the Monster as a SUBSTRATE-INTERNAL object —
-- accessible via the ConjugationCoalgebra primitive's interface.
--
-- Critical scope note: the 7 parameters embody all of the Monster's
-- complexity:
--   * M (the abstract carrier) — exists by CFSG + Griess construction.
--   * group operations — exist by the Monster's group structure.
--   * rep-M, in-class-M — populated from ATLAS character-table data.
--   * Axioms — verified externally (conjugation preserves classes is
--     trivially true for any group; in-class-rep is by definition).
-- This module BRIDGES external mathematical content into the
-- substrate; it does NOT prove the Monster exists internally.
--
-- Outstanding follow-ons (next arc):
--   * `Monster.WithCharacters`: extends the ConjugationCoalgebra with
--     character-table data (Class × Class → ℚ; 194 × 194 rationals
--     from ATLAS).
--   * `Monster.CentralizerDescent`: the Happy Family hierarchy as
--     recursive centralizer-of projections. Baby Monster = centralizer
--     of 2A involution, quotient by ⟨z⟩. Conway groups via 2B
--     centralizer descent. Etc.
--   * `Monster.AsGriessAlgebra`: identifies the Monster with
--     Aut(Griess algebra) per Griess's construction + FLM's V♮
--     refinement. The structure-constant inference per Q5 of
--     [[q1-q5-entailment-chain]] would live here.
--
-- Per [[shadow-architecture]]: T8 is the extreme-case
-- demonstration. The substrate's framework scales from GL(3, F₂) =
-- order 168 to M = order 10^53. The structural content is the same
-- (ConjugationCoalgebra + class structure); the difference is
-- magnitude. Substrate's coalgebraic discipline (per
-- [[coalgebraic-not-consumer-driven]]) makes this scaling possible.
--
-- Per [[reserved-selfdual-bijection-gauge]] → [[multi-route-
-- equivariance-recovery]] → [[prime-factored-gauge-arc]]: the
-- conversation chain from the substrate's original V₄-equivariance
-- question (at HodgeDim4) to the Monster (T8) is unbroken. The
-- universal property at HodgeDim4 (T7) AND the canonical extreme
-- instance (T8) live in the SAME generic framework.
------------------------------------------------------------------------
