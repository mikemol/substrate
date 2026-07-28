------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributor
--
-- ⟡rig-12 — the DISTRIBUTOR: the last rig-category law, cross-connecting ⊗ and the
-- Perm-level ⊕ (blockSum). σ ⊗ (τ ⊞ υ) and (σ⊗τ) ⊞ (σ⊗υ) are genuinely DIFFERENT
-- orderings (interleaved vs separated blocks), related by the distribute iso δ — so the
-- distributor is up-to-iso (r = δ ≠ id), like the commutativities.
--
--   blockSum σ τ : Perm (m + n)                    -- the Perm-side ⊕ (= decode∘⊕, rig-7)
--   δ m n p      : Fin (m·(n+p)) → Fin (m·n + m·p)  -- the distribute iso r
--   dist-nat     : lookup (blockSum (σ⊗τ) (σ⊗υ)) (δ m n p k) ≡ δ m n p (lookup (σ ⊗ blockSum τ υ) k)
--
-- This file (part 1): blockSum + its lookup characterization, and δ + its block-lemmas
-- (δ-inject/raise). The naturality dist-nat is in .Naturality (def/proof split — this
-- exports blockSum, a def).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributor where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Fin.SplitAt.InjectIdentity using (splitAt-inject)
open import Substrate.Foundation.Fin.SplitAt.RaiseIdentity using (splitAt-raise)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Vec using (lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂; [_,_])
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)
open import Substrate.WitnessTower.Wedge.OrientationProductLaws using (⊗-combine)

------------------------------------------------------------------------
-- 1. blockSum — the Perm-side ⊕ (the block-sum permutation). First block ordered by σ
--    (values stay low, inject+), second by τ (values stay high, raise).
------------------------------------------------------------------------

blockSum : ∀ {m n} → Perm m → Perm n → Perm (m + n)
blockSum {m} {n} σ τ =
  tabulate (λ k → [ (λ i → inject+ n (lookup σ i)) , (λ j → raise m (lookup τ j)) ] (splitAt m k))

blockSum-inject : ∀ {m n} (σ : Perm m) (τ : Perm n) (i : Fin m) →
                  lookup (blockSum σ τ) (inject+ n i) ≡ inject+ n (lookup σ i)
blockSum-inject {m} {n} σ τ i =
  trans (lookup∘tabulate _ (inject+ n i))
        (cong [ (λ i → inject+ n (lookup σ i)) , (λ j → raise m (lookup τ j)) ]
              (splitAt-inject m {n} i))

blockSum-raise : ∀ {m n} (σ : Perm m) (τ : Perm n) (j : Fin n) →
                 lookup (blockSum σ τ) (raise m j) ≡ raise m (lookup τ j)
blockSum-raise {m} {n} σ τ j =
  trans (lookup∘tabulate _ (raise m j))
        (cong [ (λ i → inject+ n (lookup σ i)) , (λ j → raise m (lookup τ j)) ]
              (splitAt-raise m {n} j))

------------------------------------------------------------------------
-- 2. δ — the distribute iso. Decompose k = combine i k' (remQuot), split k' (splitAt n):
--    an n-part (i,j) goes to the first output block, a p-part (i,l) to the second.
------------------------------------------------------------------------

δ : ∀ m n p → Fin (m * (n + p)) → Fin (m * n + m * p)
δ m n p k with remQuot {m} (n + p) k
... | (i , k') with splitAt n {p} k'
...   | inj₁ j = inject+ (m * p) (combine i j)
...   | inj₂ l = raise (m * n) (combine i l)

-- δ on the two block forms (rewrite the remQuot/splitAt round-trips through).
δ-inject : ∀ m n p (i : Fin m) (j : Fin n) →
           δ m n p (combine i (inject+ p j)) ≡ inject+ (m * p) (combine i j)
δ-inject m n p i j
  rewrite remQuot-combine {m} {n + p} i (inject+ p j) | splitAt-inject n {p} j = refl

δ-raise : ∀ m n p (i : Fin m) (l : Fin p) →
          δ m n p (combine i (raise n l)) ≡ raise (m * n) (combine i l)
δ-raise m n p i l
  rewrite remQuot-combine {m} {n + p} i (raise n l) | splitAt-raise n {p} l = refl

------------------------------------------------------------------------
-- 3. THE DISTRIBUTOR NATURALITY. δ intertwines σ ⊗ (blockSum τ υ) with blockSum (σ⊗τ)
--    (σ⊗υ). Cases on which block k's second factor is in (splitAt-view): each side
--    reduces, via δ-inject/raise + ⊗-combine + blockSum-inject/raise, to the SAME
--    inject+/raise of combine (σ·i) (τ·j / υ·l).
------------------------------------------------------------------------

dist-nat : ∀ {m n p} (σ : Perm m) (τ : Perm n) (υ : Perm p) (k : Fin (m * (n + p))) →
           lookup (blockSum (σ ⊗ τ) (σ ⊗ υ)) (δ m n p k)
             ≡ δ m n p (lookup (σ ⊗ blockSum τ υ) k)
dist-nat {m} {n} {p} σ τ υ k =
  subst (λ z → lookup (blockSum (σ ⊗ τ) (σ ⊗ υ)) (δ m n p z)
                 ≡ δ m n p (lookup (σ ⊗ blockSum τ υ) z))
        (combine-remQuot m (n + p) k)
        (aux (proj₁ (remQuot {m} (n + p) k)) (proj₂ (remQuot {m} (n + p) k)))
  where
  aux : (i : Fin m) (k' : Fin (n + p)) →
        lookup (blockSum (σ ⊗ τ) (σ ⊗ υ)) (δ m n p (combine i k'))
          ≡ δ m n p (lookup (σ ⊗ blockSum τ υ) (combine i k'))
  aux i k' with splitAt-view n {p} k'
  ... | fromₗ j =
    trans (trans (cong (lookup (blockSum (σ ⊗ τ) (σ ⊗ υ))) (δ-inject m n p i j))
          (trans (blockSum-inject (σ ⊗ τ) (σ ⊗ υ) (combine i j))
                 (cong (inject+ (m * p)) (⊗-combine σ τ i j))))
      (sym (trans (cong (δ m n p) (⊗-combine σ (blockSum τ υ) i (inject+ p j)))
           (trans (cong (λ z → δ m n p (combine (lookup σ i) z)) (blockSum-inject τ υ j))
                  (δ-inject m n p (lookup σ i) (lookup τ j)))))
  ... | fromᵣ l =
    trans (trans (cong (lookup (blockSum (σ ⊗ τ) (σ ⊗ υ))) (δ-raise m n p i l))
          (trans (blockSum-raise (σ ⊗ τ) (σ ⊗ υ) (combine i l))
                 (cong (raise (m * n)) (⊗-combine σ υ i l))))
      (sym (trans (cong (δ m n p) (⊗-combine σ (blockSum τ υ) i (raise n l)))
           (trans (cong (λ z → δ m n p (combine (lookup σ i) z)) (blockSum-raise τ υ l))
                  (δ-raise m n p (lookup σ i) (lookup υ l)))))
