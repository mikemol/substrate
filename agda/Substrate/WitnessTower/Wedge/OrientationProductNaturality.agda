------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductNaturality
--
-- ⟡rig-10 — the ⊗-commutativity σ-NATURALITY: factorSwap (⟡rig-8-comm's r) genuinely
-- CARRIES the products to each other. The factorSwap dual of ⟡rig-7's ⊕-comm-nat, but
-- cleaner — combine (not insert-at), so no punchIn, no induction.
--
--   ⊗-comm-nat : lookup (τ ⊗ σ) (factorSwap m n k) ≡ factorSwap m n (lookup (σ ⊗ τ) k)
--
-- Direct: factorSwap m n k = combine j i (i,j = remQuot k), so the LHS is a ⊗-combine of
-- the swapped factors; the RHS unfolds σ⊗τ at k (lookup∘tabulate) then factorSwap-combine
-- swaps them — both land on combine (τ·j) (σ·i).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductNaturality where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)
open import Substrate.WitnessTower.Wedge.OrientationProductComm using (factorSwap; factorSwap-combine)
open import Substrate.WitnessTower.Wedge.OrientationProductLaws using (⊗-combine)

⊗-comm-nat : ∀ {m n} (σ : Perm m) (τ : Perm n) (k : Fin (m * n)) →
             lookup (τ ⊗ σ) (factorSwap m n k) ≡ factorSwap m n (lookup (σ ⊗ τ) k)
⊗-comm-nat {m} {n} σ τ k =
  trans (⊗-combine τ σ j i)
        (sym (trans (cong (factorSwap m n) unfold-k)
                    (factorSwap-combine (lookup σ i) (lookup τ j))))
  where
  i = proj₁ (remQuot {m} n k)
  j = proj₂ (remQuot {m} n k)
  unfold-k : lookup (σ ⊗ τ) k ≡ combine (lookup σ i) (lookup τ j)
  unfold-k = lookup∘tabulate _ k
