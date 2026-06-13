------------------------------------------------------------------------
-- Substrate.Logic.Evidence.SWP
--
-- Semiring-weighted parsing through the NEDGE dual rail (el-atlas SWP). The packed
-- parse forest is `Algebra.Semiring.SPPF.SPPF`; here it is folded TWICE:
--   * insideC  — single rail: the weighted parse over the carrier C (probability).
--   * insideDR — dual rail: the same fold via the nedge connectives ⊗E/⊕E, carrying
--                BOTH rails of `EvCarrier C = C × C` at once (never-discard-residue).
--
-- THE SWP CLAIM, made precise: "probability is the positive-rail section." Projecting
-- the positive rail of the dual-rail parse (`posR = proj₁`) recovers the single-rail
-- parse — `posR-section`. So the dual rail carries the probability reading in its
-- positive rail with the negative rail as kept residue, and posR is a fold
-- homomorphism (one chart, the semiring plugged rail-wise, the reading a projection).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.SWP where

open import Substrate.Foundation.Product using (_×_; _,_; proj₁)
open import Substrate.Foundation.Eq      using (_≡_; refl; cong₂)
open import Substrate.Algebra.Semiring.SPPF using (SPPF; gen; one; _⊗_; _⊕_)
open import Substrate.Logic.Evidence.DualRail using (EvCarrier)
import Substrate.Logic.Evidence.DualRail as DR

module _ {C : Set} (add mul : C → C → C) (oneC : C) where
  open DR.Connectives add mul using (_⊗E_; _⊕E_)

  -- single rail: the weighted parse over C (⊕ ↦ add packs multiplicity, ⊗ ↦ mul).
  insideC : {G : Set} → (G → C) → SPPF G → C
  insideC w (gen g) = w g
  insideC w one     = oneC
  insideC w (a ⊗ b) = mul (insideC w a) (insideC w b)
  insideC w (a ⊕ b) = add (insideC w a) (insideC w b)

  -- dual rail: the same fold via the nedge connectives, both rails at once.
  insideDR : {G : Set} → (G → EvCarrier C) → SPPF G → EvCarrier C
  insideDR v (gen g) = v g
  insideDR v one     = oneC , oneC
  insideDR v (a ⊗ b) = insideDR v a ⊗E insideDR v b
  insideDR v (a ⊕ b) = insideDR v a ⊕E insideDR v b

  -- probability IS the positive-rail section: the positive rail of the dual-rail
  -- parse equals the single-rail parse of the positive valuation. posR is a fold hom.
  posR-section : {G : Set} (v : G → EvCarrier C) (t : SPPF G) →
                 proj₁ (insideDR v t) ≡ insideC (λ g → proj₁ (v g)) t
  posR-section v (gen g) = refl
  posR-section v one     = refl
  posR-section v (a ⊗ b) = cong₂ mul (posR-section v a) (posR-section v b)
  posR-section v (a ⊕ b) = cong₂ add (posR-section v a) (posR-section v b)
