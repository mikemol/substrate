------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationSumDecode
--
-- `decode` is a ⊕-HOMOMORPHISM: decode (l₁ ⊕ l₂) ≡ blockSum (decode l₁)(decode l₂).
-- The additive analog of OrientationProductStructuralDecode.decode-⊗ˢ (decode is a
-- ⊗-hom) — packaging OrientationSumNaturality's pointwise decode-⊕-inject/raise
-- against blockSum's lookup lemmas, split by which block the index lands in.
--
-- (Relocated here from PyAstRewriteSnRig, where it was proven locally: it is a
-- general tower naturality fact, not pyast-specific — single-source-of-truth,
-- surfaced by the reuse interner.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationSumDecode where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; trans; sym)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; decode)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationSumNaturality using (decode-⊕-inject; decode-⊕-raise)
open import Substrate.WitnessTower.Wedge.OrientationDistributor using (blockSum; blockSum-inject; blockSum-raise)

decode-⊕ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
           decode (l₁ ⊕ l₂) ≡ blockSum (decode l₁) (decode l₂)
decode-⊕ {m} {n} l₁ l₂ = lookup-ext _ _ pw
  where
  pw : (k : Fin (m + n)) → _
  pw k with splitAt-view m {n} k
  ... | fromₗ i = trans (decode-⊕-inject l₁ l₂ i) (sym (blockSum-inject (decode l₁) (decode l₂) i))
  ... | fromᵣ j = trans (decode-⊕-raise l₁ l₂ j) (sym (blockSum-raise (decode l₁) (decode l₂) j))
