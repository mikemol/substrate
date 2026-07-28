------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductCons
--
-- ⟡rig-UP-wreath (Step 1) — the Perm-level CONS form of the ⊗-over-◂ recursion.
-- Packages the committed keystone (OrientationProductInsert's ⊗-insert-head /
-- ⊗-insert-tail) into a SINGLE structural equation:
--
--   (insert-at p σ) ⊗ τ ≡ headBlock p τ ++ map (blockPunchIn p n) (σ ⊗ τ)
--
-- with headBlock p τ = tabulate (λ j → combine p (lookup τ j)) : Vec (Fin (suc m·n)) n
-- (the p-th value-block, the first n entries) and the tail the block-punch of the
-- sub-product's m·n values. Proven pointwise via lookup-ext: decompose the index
-- k by combine-remQuot, split on the quotient digit (zero → head via ⊗-insert-head +
-- lookup-of-++ at inject+ ; suc → tail via ⊗-insert-tail + lookup-of-++ at raise).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductCons where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate; map; _++_)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (lookup-map)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)
open import Substrate.WitnessTower.Wedge.OrientationProductInsert
  using (blockPunchIn; ⊗-insert-head; ⊗-insert-tail)

------------------------------------------------------------------------
-- 0. Lookup of a concatenation, keyed by the inject+/raise split — the two
--    lemmas that make combine's two clauses land in the ++ halves.
------------------------------------------------------------------------

lookup-++-inject : {A : Set} {n k : ℕ} (xs : Vec A n) (ys : Vec A k) (j : Fin n) →
                   lookup (xs ++ ys) (inject+ k j) ≡ lookup xs j
lookup-++-inject (x ∷ xs) ys zero    = refl
lookup-++-inject (x ∷ xs) ys (suc j) = lookup-++-inject xs ys j

lookup-++-raise : {A : Set} {n k : ℕ} (xs : Vec A n) (ys : Vec A k) (i : Fin k) →
                  lookup (xs ++ ys) (raise n i) ≡ lookup ys i
lookup-++-raise []       ys i = refl
lookup-++-raise (x ∷ xs) ys i = lookup-++-raise xs ys i

------------------------------------------------------------------------
-- 1. The head block: the first n entries of (insert-at p σ) ⊗ τ, = the p-th
--    value-block combine p (τ j).
------------------------------------------------------------------------

headBlock : ∀ {m n} (p : Fin (suc m)) (τ : Perm n) → Vec (Fin (suc m * n)) n
headBlock {m} p τ = tabulate (λ j → combine {suc m} p (lookup τ j))

------------------------------------------------------------------------
-- 2. THE CONS FORM. (insert-at p σ) ⊗ τ = head block ++ block-punch of σ ⊗ τ.
------------------------------------------------------------------------

⊗-insert-cons : ∀ {m n} (p : Fin (suc m)) (σ : Perm m) (τ : Perm n) →
                (insert-at p σ) ⊗ τ ≡ headBlock p τ ++ map (blockPunchIn {m} p n) (σ ⊗ τ)
⊗-insert-cons {m} {n} p σ τ = lookup-ext _ _ pointwise
  where
  RHS : Vec (Fin (suc m * n)) (suc m * n)
  RHS = headBlock p τ ++ map (blockPunchIn {m} p n) (σ ⊗ τ)

  at-combine : (i2 : Fin (suc m)) (j : Fin n) →
               lookup ((insert-at p σ) ⊗ τ) (combine i2 j) ≡ lookup RHS (combine i2 j)
  at-combine zero j =
    trans (⊗-insert-head p σ τ j)
          (sym (trans (lookup-++-inject (headBlock p τ) (map (blockPunchIn {m} p n) (σ ⊗ τ)) j)
                      (lookup∘tabulate (λ j′ → combine {suc m} p (lookup τ j′)) j)))
  at-combine (suc i) j =
    trans (⊗-insert-tail p σ τ i j)
          (sym (trans (lookup-++-raise (headBlock p τ) (map (blockPunchIn {m} p n) (σ ⊗ τ))
                                       (combine i j))
                      (lookup-map (blockPunchIn {m} p n) (σ ⊗ τ) (combine i j))))

  pointwise : (k : Fin (suc m * n)) →
              lookup ((insert-at p σ) ⊗ τ) k ≡ lookup RHS k
  pointwise k =
    trans (cong (lookup ((insert-at p σ) ⊗ τ)) (sym kd))
          (trans (at-combine (proj₁ (remQuot {suc m} n k)) (proj₂ (remQuot {suc m} n k)))
                 (cong (lookup RHS) kd))
    where
    kd : combine (proj₁ (remQuot {suc m} n k)) (proj₂ (remQuot {suc m} n k)) ≡ k
    kd = combine-remQuot (suc m) n k
