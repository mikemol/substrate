------------------------------------------------------------------------
-- Substrate.TokiPona.QSemanticSpace
--
-- TPQ1 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- ℚ-valued semantic vector space for Toki Pona, replacing the
-- F₂ encoding of the original T1 SemanticSpace. Per
-- [[feedback-q-over-r-constructive]]: ℚ retains decision structure
-- where ℝ would collapse it; the substrate uses ℚ as the richer
-- carrier than F₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.QSemanticSpace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_)

-- Re-export ℚ-Vector publicly so consumers get the whole carrier.
open import Substrate.Algebra.Q.Vector public
  using (Vector; 𝟎ℚⱽ; _+ℚⱽ_; _*ℚₛ_; basis-ℚ)

------------------------------------------------------------------------
-- 1. Linguistic alias.
--
-- A QSemVec m is an ℚ-vector of dimension m. Each nimi will get
-- a ℚ-vector via the FreeLinearization-over-ℚ universal property
-- (TPQ2).
------------------------------------------------------------------------

QSemVec : ℕ → Set
QSemVec m = Vector m

------------------------------------------------------------------------
-- 2. Linguistic-named operations.
------------------------------------------------------------------------

∅-Q : ∀ {m} → QSemVec m
∅-Q = 𝟎ℚⱽ

infixl 6 _⊕Q_

_⊕Q_ : ∀ {m} → QSemVec m → QSemVec m → QSemVec m
_⊕Q_ = _+ℚⱽ_

------------------------------------------------------------------------
-- 3. Capstone for TPQ1.
--
-- ℚ-valued semantic carrier defined. TPQ2 builds the
-- ℚ-NimiSpace via FreeLinearization-over-ℚ (FLQ7).
------------------------------------------------------------------------
