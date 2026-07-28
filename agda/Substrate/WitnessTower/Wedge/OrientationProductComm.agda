------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductComm
--
-- ⟡rig-8 (the multiplicative-commutativity iso) — the ⊗ analog of ⟡rig-6's blockSwap.
-- Commutativity of `×` is up-to-iso (r ≠ id): σ ⊗ τ and τ ⊗ σ are related by the
-- FACTOR-swap — exchange the two factors of each pair through Fin(m·n) ≅ Fin m × Fin n.
-- This file exhibits that r and proves it is a genuine iso (swaps factors + involution),
-- using ONLY the existing remQuot/combine round-trips — NOT combine-assoc (⊗-assoc, the
-- product associator, is the deep residue that DOES need it).
--
--   factorSwap m n : Fin (m · n) → Fin (n · m)     -- the ⊗-commutativity iso r
--
-- It is the mirror of blockSwap: where blockSwap swapped the two ⊎-blocks (splitAt), this
-- swaps the two ×-factors (remQuot). Proven: factorSwap-combine (it swaps the factors of a
-- combine) and factorSwap-invol (its own inverse — order-2, a genuine bijection). This is
-- the r that GradedStarV4's colSwap (⟡rig-1/4) abstracts, made concrete.
--
-- RESIDUE (still ⟡rig-8): ⊗-assoc (the product associator, needs combine-assoc — the
-- probe walls at combine-over-inject+ distribution) and the factorSwap NATURALITY (that it
-- carries σ⊗τ to τ⊗σ on the actual orderings — the ⊗ mirror of ⟡rig-7).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductComm where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

------------------------------------------------------------------------
-- 1. THE MULTIPLICATIVE-COMMUTATIVITY ISO r = factorSwap: the factor-transposition.
------------------------------------------------------------------------

factorSwap : ∀ m n → Fin (m * n) → Fin (n * m)
factorSwap m n k = combine (proj₂ (remQuot {m} n k)) (proj₁ (remQuot {m} n k))

------------------------------------------------------------------------
-- 2. IT SWAPS THE TWO FACTORS. On a combine (i,j) it returns combine (j,i), directly
--    from the remQuot/combine round-trip.
------------------------------------------------------------------------

factorSwap-combine : ∀ {m n} (i : Fin m) (j : Fin n) →
                     factorSwap m n (combine i j) ≡ combine j i
factorSwap-combine i j = cong (λ pr → combine (proj₂ pr) (proj₁ pr)) (remQuot-combine i j)

------------------------------------------------------------------------
-- 3. IT IS AN INVOLUTION (r is order-2, a genuine iso): factorSwap n m ∘ factorSwap m n =
--    id. Swap the factors, swap them back, then reassemble via combine-remQuot.
------------------------------------------------------------------------

factorSwap-invol : ∀ m n (k : Fin (m * n)) → factorSwap n m (factorSwap m n k) ≡ k
factorSwap-invol m n k =
  trans (factorSwap-combine (proj₂ (remQuot {m} n k)) (proj₁ (remQuot {m} n k)))
        (combine-remQuot m n k)
