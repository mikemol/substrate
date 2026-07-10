------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationCoherence
--
-- ⟡rig-13 (part 1) — the BRAIDING-UNIT COHERENCES of the symmetric rig category. The
-- braided/symmetric axioms for each braiding split into: involution (σ²=id, DONE —
-- blockSwap-invol / factorSwap-invol, rig-6/8), naturality (DONE — ⊕/⊗-comm-nat,
-- rig-7/10), the braiding-UNIT coherence (σ_{A,I} = the unitor — THIS FILE), and the
-- HEXAGON (σ vs the associator — the remaining heavy piece, see below).
--
--   blockSwap-unit  : toℕ (blockSwap m 0 x) ≡ toℕ x    -- σ with the ⊕-unit 0 is the unitor
--   factorSwap-unit : toℕ (factorSwap m 1 k) ≡ toℕ k   -- σ with the ⊗-unit 1 is the unitor
--
-- ("= the unitor" means value-preserving: on the underlying element, σ_{A,I} is identity —
-- both A⊕0 ≅ A ≅ 0⊕A and A⊗1 ≅ A ≅ 1⊗A collapse. toℕ route, via the rig-9 combine-unit
-- lemmas + blockSwap-L.)
--
-- RESIDUE (⟡rig-13 part 2, deep): the HEXAGONS (blockSwap/factorSwap vs the associator)
-- and the DISTRIBUTOR PENTAGONS. These need a functorial ⊕/⊗-on-MORPHISMS layer
-- (f ⊕map g : Fin(m+n) → Fin(m'+n')) to even STATE, plus +-assoc/*-assoc transports
-- between the composite's stages — a substantial build-out. The associator/unit PENTAGONS
-- are automatic (strict associators, r=id). Recursive-common-structure: coherence work ∝
-- non-strictness — only the up-to-iso r's carry non-trivial diagrams, and of those only the
-- hexagon/pentagon remain (involution + naturality + unit are done).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationCoherence where

open import Substrate.Foundation.Nat using (ℕ; zero; _+_; _*_)
open import Substrate.Foundation.Fin using (Fin; toℕ)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.Assoc using (toℕ-inject+; toℕ-raise)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Wedge.OrientationSumComm using (blockSwap; blockSwap-L)
open import Substrate.WitnessTower.Wedge.OrientationProductComm using (factorSwap)
open import Substrate.WitnessTower.Wedge.OrientationProductUnit
  using (combine-unitₗ; combine-unitᵣ)

------------------------------------------------------------------------
-- 1. ⊕ braiding-unit: blockSwap with the empty (0) block is value-preserving.
--    x : Fin (m + 0) is always in the m-block (the 0-block is empty).
------------------------------------------------------------------------

blockSwap-unit : ∀ m (x : Fin (m + 0)) → toℕ (blockSwap m 0 x) ≡ toℕ x
blockSwap-unit m x with splitAt-view m {0} x
... | fromₗ i = trans (cong toℕ (blockSwap-L m 0 i))
                      (trans (toℕ-raise 0 i) (sym (toℕ-inject+ 0 i)))
... | fromᵣ ()

------------------------------------------------------------------------
-- 2. ⊗ braiding-unit: factorSwap with the singleton (1) factor is value-preserving.
--    (via the rig-9 combine-unit collapses: combine with a Fin-1 factor keeps the value.)
------------------------------------------------------------------------

factorSwap-unit : ∀ m (k : Fin (m * 1)) → toℕ (factorSwap m 1 k) ≡ toℕ k
factorSwap-unit m k =
  trans (combine-unitₗ (proj₂ (remQuot {m} 1 k)) (proj₁ (remQuot {m} 1 k)))
        (sym (trans (cong toℕ (sym (combine-remQuot m 1 k)))
                    (combine-unitᵣ (proj₁ (remQuot {m} 1 k)) (proj₂ (remQuot {m} 1 k)))))
