------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationSumNaturality
--
-- ⟡rig-7 — the ⊕-commutativity σ-NATURALITY: blockSwap (⟡rig-6's r) genuinely CARRIES
-- the block-sum orderings to each other, not merely exists.
--
--   ⊕-comm-nat : lookup (decode (l₂ ⊕ l₁)) (blockSwap m n k)
--              ≡ blockSwap m n (lookup (decode (l₁ ⊕ l₂)) k)
--
-- Route: decode(l₁ ⊕ l₂) IS the block-sum permutation — its lookup at a first-block index
-- (inject+) stays in the first block, at a second-block index (raise) stays in the second:
--   decode-⊕-inject : lookup (decode (l₁⊕l₂)) (inject+ n i) ≡ inject+ n (lookup (decode l₁) i)
--   decode-⊕-raise  : lookup (decode (l₁⊕l₂)) (raise m j)   ≡ raise m  (lookup (decode l₂) j)
-- proven by induction on l₁ (insert-at = p ∷ map (punchIn p)) through two clean punchIn
-- commutations (punchIn-inject+, punchIn-inject+-raise). Then the naturality closes by
-- cases on which block k is in (splitAt-view + blockSwap-L/R): each side reduces to the
-- SAME raise/inject+ of a looked-up value.
--
-- This is the σ of Category.SymmetricMonoidal made natural over the ⊕ orderings — the
-- deep half of ⟡rig-6.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationSumNaturality where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Vec using (lookup; map)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (lookup-map)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)
open import Substrate.WitnessTower.Wedge.OrientationSumComm
  using (blockSwap; blockSwap-L; blockSwap-R)

------------------------------------------------------------------------
-- 1. lookup of insert-at at a successor is punchIn of the tail lookup.
------------------------------------------------------------------------

lookup-insert-suc : ∀ {n} (p : Fin (suc n)) (σ : Perm n) (i : Fin n) →
                    lookup (insert-at p σ) (suc i) ≡ punchIn p (lookup σ i)
lookup-insert-suc p σ i = lookup-map (punchIn p) σ i

------------------------------------------------------------------------
-- 2. punchIn commutations with the block maps (clean structural inductions).
------------------------------------------------------------------------

-- punchIn commutes with inject+ (both slot and point in the first block).
punchIn-inject+ : ∀ {m} n (p : Fin (suc m)) (j : Fin m) →
                  punchIn (inject+ n p) (inject+ n j) ≡ inject+ n (punchIn p j)
punchIn-inject+ n zero    j       = refl
punchIn-inject+ n (suc p) zero    = refl
punchIn-inject+ n (suc p) (suc j) = cong suc (punchIn-inject+ n p j)

-- punchIn at a first-block slot, of a second-block point, just shifts it up.
punchIn-inject+-raise : ∀ {m} n (p : Fin (suc m)) (z : Fin n) →
                        punchIn (inject+ n p) (raise m z) ≡ suc (raise m z)
punchIn-inject+-raise         n zero    z = refl
punchIn-inject+-raise {suc m} n (suc p) z = cong suc (punchIn-inject+-raise n p z)

------------------------------------------------------------------------
-- 3. decode(l₁ ⊕ l₂) IS the block-sum: first block stays low, second stays high.
------------------------------------------------------------------------

decode-⊕-inject : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) (i : Fin m) →
                  lookup (decode (l₁ ⊕ l₂)) (inject+ n i) ≡ inject+ n (lookup (decode l₁) i)
decode-⊕-inject (l₁ ◂ x) l₂ zero    = refl
decode-⊕-inject {suc m} {n} (l₁ ◂ x) l₂ (suc i) =
  trans (lookup-insert-suc (inject+ n x) (decode (l₁ ⊕ l₂)) (inject+ n i))
        (trans (cong (punchIn (inject+ n x)) (decode-⊕-inject l₁ l₂ i))
               (trans (punchIn-inject+ n x (lookup (decode l₁) i))
                      (cong (inject+ n) (sym (lookup-insert-suc x (decode l₁) i)))))

decode-⊕-raise : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) (j : Fin n) →
                 lookup (decode (l₁ ⊕ l₂)) (raise m j) ≡ raise m (lookup (decode l₂) j)
decode-⊕-raise start    l₂ j = refl
decode-⊕-raise {suc m} {n} (l₁ ◂ x) l₂ j =
  trans (lookup-insert-suc (inject+ n x) (decode (l₁ ⊕ l₂)) (raise m j))
        (trans (cong (punchIn (inject+ n x)) (decode-⊕-raise l₁ l₂ j))
               (punchIn-inject+-raise n x (lookup (decode l₂) j)))

------------------------------------------------------------------------
-- 4. THE NATURALITY. Cases on which block k is in; each side reduces to the same
--    raise/inject+ of a looked-up value via decode-⊕-inject/raise + blockSwap-L/R.
------------------------------------------------------------------------

⊕-comm-nat : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) (k : Fin (m + n)) →
             lookup (decode (l₂ ⊕ l₁)) (blockSwap m n k)
               ≡ blockSwap m n (lookup (decode (l₁ ⊕ l₂)) k)
⊕-comm-nat {m} {n} l₁ l₂ k with splitAt-view m {n} k
... | fromₗ i =
  trans (trans (cong (lookup (decode (l₂ ⊕ l₁))) (blockSwap-L m n i))
               (decode-⊕-raise l₂ l₁ i))
        (sym (trans (cong (blockSwap m n) (decode-⊕-inject l₁ l₂ i))
                    (blockSwap-L m n (lookup (decode l₁) i))))
... | fromᵣ j =
  trans (trans (cong (lookup (decode (l₂ ⊕ l₁))) (blockSwap-R m n j))
               (decode-⊕-inject l₂ l₁ j))
        (sym (trans (cong (blockSwap m n) (decode-⊕-raise l₁ l₂ j))
                    (blockSwap-R m n (lookup (decode l₂) j))))
