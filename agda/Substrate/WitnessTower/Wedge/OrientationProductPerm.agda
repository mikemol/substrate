------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductPerm
--
-- ⟡rig-2 — the `×` of the graded Lehmer rig is closed on the orderings: the product
-- of two permutations is a permutation. So `_⊗_` (OrientationProduct) maps orderings
-- to orderings, not merely Vecs to Vecs.
--
-- Injectivity, via the finite-type product's round-trips: `lookup (σ⊗τ) k = combine (σ ·
-- i) (τ · j)` for (i,j) = remQuot k; if two such combines agree, `remQuot-combine`
-- splits them into equal factors, `σ`/`τ` injectivity pulls back to equal (i,j), and
-- `combine-remQuot` re-assembles to `k₁ ≡ k₂`.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductPerm where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Vec using (lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)

⊗-is-perm : ∀ {m n} (σ : Perm m) (τ : Perm n) →
            IsPerm σ → IsPerm τ → IsPerm (σ ⊗ τ)
⊗-is-perm {m} {n} σ τ σp τp k₁ k₂ eq =
  trans (sym (combine-remQuot m n k₁))
        (trans (cong₂ combine a-eq b-eq) (combine-remQuot m n k₂))
  where
    f : Fin (m * n) → Fin (m * n)
    f k = combine (lookup σ (proj₁ (remQuot {m} n k))) (lookup τ (proj₂ (remQuot {m} n k)))

    -- lookup of the tabulated product IS f (defeq of _⊗_), so eq becomes f k₁ ≡ f k₂.
    eqf : f k₁ ≡ f k₂
    eqf = trans (sym (lookup∘tabulate f k₁)) (trans eq (lookup∘tabulate f k₂))

    -- remQuot splits both combines: (σ·i₁, τ·j₁) ≡ (σ·i₂, τ·j₂).
    pair-eq : (lookup σ (proj₁ (remQuot {m} n k₁)) , lookup τ (proj₂ (remQuot {m} n k₁)))
            ≡ (lookup σ (proj₁ (remQuot {m} n k₂)) , lookup τ (proj₂ (remQuot {m} n k₂)))
    pair-eq =
      trans (sym (remQuot-combine (lookup σ (proj₁ (remQuot {m} n k₁)))
                                  (lookup τ (proj₂ (remQuot {m} n k₁)))))
            (trans (cong (remQuot {m} n) eqf)
                   (remQuot-combine (lookup σ (proj₁ (remQuot {m} n k₂)))
                                    (lookup τ (proj₂ (remQuot {m} n k₂)))))

    -- σ/τ injectivity pulls back to equal factors of remQuot.
    a-eq : proj₁ (remQuot {m} n k₁) ≡ proj₁ (remQuot {m} n k₂)
    a-eq = σp _ _ (cong proj₁ pair-eq)

    b-eq : proj₂ (remQuot {m} n k₁) ≡ proj₂ (remQuot {m} n k₂)
    b-eq = τp _ _ (cong proj₂ pair-eq)
