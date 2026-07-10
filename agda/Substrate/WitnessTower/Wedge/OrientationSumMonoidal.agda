------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationSumMonoidal
--
-- THE REUSE ASSEMBLY — the additive orderings are a GradedMonoidalAdjunction.
--
-- The graded rig's `+` (OrientationSum's ⊕ : LehmerPath m → LehmerPath n → LehmerPath
-- (m+n), unit 0# = start : LehmerPath 0) IS a `GradedProduct LehmerPath` — the existing
-- graded-monoidal interface (Algebra.Wedge.Product): `u : C 0`, `_∧_ : C i → C j →
-- C (i+j)`. And rig-5's ⊕-assoc / ⊕-unit-left / ⊕-unit-right are, VERBATIM, the law-types
-- GradedAssoc / GradedUnitˡ / GradedUnitʳ (Product.LawTypes). So they assemble a
-- `GradedMonoidalAdjunction LehmerPath` — the uniting record that gives, at once, the
-- graded wedge carrier, the flattened DivStr, the degree GradedMonoid, and the graded
-- Free⊣Forgetful adjunction (MonoidalAdjunction's "five faces").
--
-- This is the reuse-search win (catalog.db → GradedMonoidalAdjunction / GradedProduct /
-- Product.LawTypes): rig-5 was not bespoke lemmas — it PROVED the graded-monoidal fields
-- of the orderings. The commutativity (rig-6 blockSwap) is NOT here — Product.LawTypes has
-- no GradedComm; the symmetry's home is Category.SymmetricMonoidal's σ / σ-involution,
-- which blockSwap / blockSwap-invol match.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationSumMonoidal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Wedge.Product using (GradedProduct)
open import Substrate.Algebra.Wedge.Product.LawTypes
  using (GradedAssoc; GradedUnitˡ; GradedUnitʳ)
open import Substrate.Algebra.Wedge.Graded.MonoidalAdjunction
  using (GradedMonoidalAdjunction)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_; 0#; ⊕-unit-left)
open import Substrate.WitnessTower.Wedge.OrientationSumLaws using (⊕-assoc; ⊕-unit-right)

------------------------------------------------------------------------
-- 1. ⊕ IS a GradedProduct on LehmerPath (u = 0#, _∧_ = ⊕).
------------------------------------------------------------------------

⊕-GradedProduct : GradedProduct LehmerPath
⊕-GradedProduct = record { u = 0# ; _∧_ = _⊕_ }

------------------------------------------------------------------------
-- 2. rig-5's laws ARE the graded law-types for this product.
------------------------------------------------------------------------

⊕-assoc-law : GradedAssoc ⊕-GradedProduct
⊕-assoc-law = ⊕-assoc

⊕-unitˡ-law : GradedUnitˡ ⊕-GradedProduct
⊕-unitˡ-law = ⊕-unit-left

⊕-unitʳ-law : GradedUnitʳ ⊕-GradedProduct
⊕-unitʳ-law = ⊕-unit-right

------------------------------------------------------------------------
-- 3. THE ASSEMBLY — the additive orderings as a GradedMonoidalAdjunction (five faces).
------------------------------------------------------------------------

⊕-GradedMonoidalAdjunction : GradedMonoidalAdjunction LehmerPath
⊕-GradedMonoidalAdjunction = record
  { prod  = ⊕-GradedProduct
  ; assoc = ⊕-assoc-law
  ; unitˡ = ⊕-unitˡ-law
  ; unitʳ = ⊕-unitʳ-law
  }
