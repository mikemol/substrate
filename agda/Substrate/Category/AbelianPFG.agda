------------------------------------------------------------------------
-- Substrate.Category.AbelianPFG
--
-- Specialisation of PrimeFactoredGauge (T1) for ABELIAN gauge groups.
-- In the abelian case, every Sylow is normal and G ≅ ∏ Sylows (the
-- direct-product / Chinese Remainder Theorem decomposition).
--
-- W1 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Sub-arc W (Abelian/CRT instances + joint-gen discharge) foundation.
--
-- Structural framing. For finite abelian G with order ∏ pᵢ^kᵢ:
--   * Each Sylow-pᵢ subgroup Pᵢ is normal (abelian ⇒ all subgroups
--     normal).
--   * G ≅ P₁ × P₂ × ... × Pₙ (the product decomposition, = abelian
--     specialization of CRT).
--   * Joint-generation is TRIVIALLY derivable from the product
--     decomposition: every g ∈ G factors uniquely as g = p₁·p₂·...·pₙ
--     with pᵢ ∈ Pᵢ; the InGenerated chain follows by repeated
--     product application.
--
-- Per [[composite-torsion-euler-substrate]]: this is the substrate
-- naming for the CRT-abelian special case. Extended Euclid is the
-- algorithmic content of the product-decomposition construction.
--
-- Per [[multi-field-tower-architecture]]: AbelianPFG instances are
-- naturally expressible via FieldFanOut at the prime decomposition.
--
-- This slice provides the abelian-specialisation record. W2, W3
-- supply concrete instances (Z/6, Z/30). Joint-generation can be
-- derived from the product decomposition; the derivation is a per-
-- instance one-liner (mechanical via InGenerated.product chains).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.AbelianPFG where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.PrimeFactoredGauge
  using (PrimeFactoredGauge)

private
  variable
    ℓG ℓX ℓEG ℓEX : Level

------------------------------------------------------------------------
-- The AbelianPFG record.
--
-- A PrimeFactoredGauge whose underlying group is abelian. The abelian
-- constraint is captured as a commutativity field on G's operation.
--
-- Per substrate convention: minimum-axiom record. The pfg field
-- carries the full PrimeFactoredGauge structure (T0 + GTorsor); the
-- abelian-comm field adds the commutativity constraint. Derived
-- consequences (Sylows-are-normal, product-decomposition,
-- trivial-joint-gen) follow from these two but are not internal
-- fields — per-instance modules supply derivations as needed.
------------------------------------------------------------------------

record AbelianPFG
  (G : Set ℓG) (X : Set ℓX)
  (_·G_ : G → G → G) (εG : G)
  (_≈G_ : G → G → Set ℓEG)
  (_≈X_ : X → X → Set ℓEX)
  (n : ℕ) : Set (lsuc (ℓG ⊔ ℓX ⊔ ℓEG ⊔ ℓEX)) where
  constructor mkAbelianPFG
  field
    pfg         : PrimeFactoredGauge G X _·G_ εG _≈G_ _≈X_ n
    abelian-comm : (g h : G) → _≈G_ (g ·G h) (h ·G g)

open AbelianPFG public

------------------------------------------------------------------------
-- Capstone — abelian specialisation in place.
--
-- W1 of the 20-slice arc. With W1 landed, the substrate exposes the
-- abelian special case of PrimeFactoredGauge with the
-- commutativity constraint named explicitly.
--
-- Concrete instances expected (W2-W3):
--   * Z/6 = Z/2 × Z/3 — smallest non-trivial CRT abelian PFG
--   * Z/30 = Z/2 × Z/3 × Z/5 — 3-prime CRT case
--
-- Joint-generation property in the underlying pfg is auto-discharged
-- for abelian PFG instances via the product decomposition (W2/W3
-- supply the construction).
--
-- Per [[shadow-architecture]]: thin DBE-foundational slice for W2-W5.
--
-- Per [[universal-property-discipline]]: AbelianPFG names the
-- commutative-Sylow-decomposition universal property. Specific
-- instances inherit + specialize.
------------------------------------------------------------------------
