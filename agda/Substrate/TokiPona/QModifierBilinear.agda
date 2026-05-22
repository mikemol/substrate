------------------------------------------------------------------------
-- Substrate.TokiPona.QModifierBilinear
--
-- TPQ3 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- Head-modifier composition over ℚ. Provides two operations:
--   * `modify-Q-sum` (vector sum) — feature-union semantics
--   * `modify-Q-prod` (pointwise product) — feature-intersection
--     semantics, GENUINELY BILINEAR over ℚ
--
-- The F₂ original (T4) only had vector sum, which was not strictly
-- bilinear at characteristic 2. Over ℚ, both operations exist;
-- pointwise product is the truly-bilinear choice for richer
-- distributional semantics.
--
-- Bilinearity proofs require ℚ-vector arithmetic lemmas (e.g.,
-- _+ℚⱽ_-distributes-over-_·ℚⱽ_) that the Q-arc didn't prove;
-- deferred per [[feedback-coalgebraic-not-consumer-driven]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QModifierBilinear where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (zipWith)

open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Arithmetic using (_*ℚ_)
open import Substrate.TokiPona.QSemanticSpace
  using (QSemVec; ∅-Q; _⊕Q_)

------------------------------------------------------------------------
-- 1. Feature-union modifier: vector sum.
--
-- modify-Q-sum h m = h + m. "soweli" + "lili" gives a vector
-- with both feature directions activated (with ℚ weights).
------------------------------------------------------------------------

modify-Q-sum : {m : ℕ} → QSemVec m → QSemVec m → QSemVec m
modify-Q-sum h n = h ⊕Q n

------------------------------------------------------------------------
-- 2. Pointwise (Hadamard) product over ℚ.
--
-- Genuinely bilinear because ℚ has no characteristic-2 collapse.
-- For RICH semantic vectors, the pointwise product captures
-- feature INTERSECTION.
------------------------------------------------------------------------

infixl 7 _·ℚⱽ_

_·ℚⱽ_ : {m : ℕ} → QSemVec m → QSemVec m → QSemVec m
_·ℚⱽ_ = zipWith _*ℚ_

------------------------------------------------------------------------
-- 3. Feature-intersection modifier: pointwise product.
--
-- modify-Q-prod h m = h · m. "soweli" · "lili" gives a vector
-- with feature components where BOTH had ℚ-weighted activation.
-- For one-hot vectors of distinct nimi this is zero; for richer
-- vectors it captures the meaningful intersection.
------------------------------------------------------------------------

modify-Q-prod : {m : ℕ} → QSemVec m → QSemVec m → QSemVec m
modify-Q-prod h n = h ·ℚⱽ n

------------------------------------------------------------------------
-- 4. Capstone for TPQ3.
--
-- Two ℚ modifier operations: sum (feature union, F₂-style) +
-- product (feature intersection, genuinely bilinear over ℚ).
-- TPQ4 builds ℚ-TokiSentence using these.
------------------------------------------------------------------------
