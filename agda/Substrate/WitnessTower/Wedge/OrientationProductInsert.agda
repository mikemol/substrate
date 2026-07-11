------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductInsert
--
-- ⟡rig-UP-wreath (keystone + recursion) — how the ⊗ product recurses over the
-- ◂ / insert-at tower step. This is the multiplicative analog of
-- OrientationSumNaturality's decode-⊕-inject/raise: there, one insert rung of the
-- FIRST factor mapped to one rung of the block-sum (the ⊕-side, via inject+); here,
-- one insert rung maps to a BLOCK of n rungs of the block-product (the ⊗-side, via
-- combine + a block punch-in on the quotient digit).
--
--   blockPunchIn p n : Fin (m*n) → Fin (suc m * n)      -- punch-in on the quotient digit
--     = combine ∘ (punchIn p × id) ∘ remQuot            -- (the clean combine/remQuot form)
--
--   KEYSTONE   : combine (punchIn p x) y ≡ blockPunchIn p n (combine x y)
--   ⊗-◂ (head) : lookup ((insert-at p σ) ⊗ τ) (combine zero    j) ≡ combine p (lookup τ j)
--   ⊗-◂ (tail) : lookup ((insert-at p σ) ⊗ τ) (combine (suc i) j)
--                  ≡ blockPunchIn p n (lookup (σ ⊗ τ) (combine i j))
--
-- The keystone is nearly definitional once blockPunchIn is given the combine/remQuot
-- form: remQuot inverts combine (remQuot-combine), so the punch-in on the quotient
-- digit of a combined index is exactly the punch-in of the high factor. No toℕ needed
-- — the reuse of remQuot-combine collapses the arithmetic (the spec's toℕ route is the
-- fallback when blockPunchIn is defined as an abstract "skip block").
--
-- The recursion then falls out of ⊗-combine (OrientationProductLaws) + tail-val
-- (IsPermutation.lookup-map, via insert-at = p ∷ map (punchIn p)) + the keystone.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductInsert where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (lookup-map)
open import Substrate.WitnessTower.LehmerPath
  using (LehmerPath; decode; encode; decode-is-perm; decode-encode)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)
open import Substrate.WitnessTower.Wedge.OrientationProductLaws using (⊗-combine)
open import Substrate.WitnessTower.Wedge.OrientationProductPerm using (⊗-is-perm)

------------------------------------------------------------------------
-- 1. blockPunchIn: punch a slot into the QUOTIENT digit of a flat Fin (m*n),
--    landing it in Fin (suc m * n). = combine ∘ (punchIn p × id) ∘ remQuot.
--    (Values in the block [p·n, p·n+n) are skipped — the τ-block of the head.)
------------------------------------------------------------------------

blockPunchIn : ∀ {m} (p : Fin (suc m)) n → Fin (m * n) → Fin (suc m * n)
blockPunchIn {m} p n k =
  combine (punchIn p (proj₁ (remQuot {m} n k))) (proj₂ (remQuot {m} n k))

------------------------------------------------------------------------
-- 2. THE KEYSTONE. Punching the high factor of a combined index = block-punching
--    the combined index. remQuot-combine collapses remQuot (combine x y) to (x , y).
------------------------------------------------------------------------

blockPunchIn-combine : ∀ {m n} (p : Fin (suc m)) (x : Fin m) (y : Fin n) →
                       combine (punchIn p x) y ≡ blockPunchIn p n (combine x y)
blockPunchIn-combine {m} {n} p x y =
  sym (cong (λ pr → combine (punchIn p (proj₁ pr)) (proj₂ pr)) (remQuot-combine x y))

------------------------------------------------------------------------
-- 3. THE ⊗-OVER-◂ RECURSION, pointwise. The head (combine zero j) is the p·n+τ block;
--    the tail (combine (suc i) j) is the block punch-in of the sub-product σ ⊗ τ.
------------------------------------------------------------------------

-- HEAD: the first n entries are combine p (τ j) — the p-th value-block. (lookup of
-- insert-at at zero is p definitionally, so this is just ⊗-combine at (zero , j).)
⊗-insert-head : ∀ {m n} (p : Fin (suc m)) (σ : Perm m) (τ : Perm n) (j : Fin n) →
                lookup ((insert-at p σ) ⊗ τ) (combine {suc m} zero j) ≡ combine p (lookup τ j)
⊗-insert-head {m} p σ τ j = ⊗-combine (insert-at p σ) τ zero j

-- TAIL: the remaining m·n entries are the block punch-in of the sub-product's values.
⊗-insert-tail : ∀ {m n} (p : Fin (suc m)) (σ : Perm m) (τ : Perm n) (i : Fin m) (j : Fin n) →
                lookup ((insert-at p σ) ⊗ τ) (combine (suc i) j)
                  ≡ blockPunchIn {m} p n (lookup (σ ⊗ τ) (combine i j))
⊗-insert-tail {m} {n} p σ τ i j =
  trans (⊗-combine (insert-at p σ) τ (suc i) j)
  (trans (cong (λ z → combine z (lookup τ j)) (lookup-map (punchIn p) σ i))
  (trans (blockPunchIn-combine p (lookup σ i) (lookup τ j))
         (cong (blockPunchIn {m} p n) (sym (⊗-combine σ τ i j)))))

------------------------------------------------------------------------
-- 4. THE LEHMERPATH PRODUCT (transport-defined) + DECODE-AGREEMENT. Define ⊗ˡ by
--    carrying the Perm product ⊗ across the decode/encode iso; decode-agreement is then
--    immediate from decode∘encode = id (decode-encode). This gives a concrete
--    LehmerPath-level product with `decode (l₁ ⊗ˡ l₂) ≡ decode l₁ ⊗ decode l₂`, the
--    multiplicative analog of OrientationSum's decode-⊕ agreement.
--
--    NOTE: this is the TRANSPORT definition, not the structural block-cons recursion.
--    It delivers decode-agreement, but NOT the ◂-recursion that a fold-⊗ catamorphism
--    (fold (l₁ ⊗ˡ l₂) ≡ fold l₁ `times` fold l₂, mirroring OrientationUniversal.fold-⊕)
--    would need — that requires an n-rung block-insert recursion on LehmerPath whose
--    decode is proven via §3's ⊗-insert-head/tail. Left as the next rung.
------------------------------------------------------------------------

infixr 7 _⊗ˡ_

_⊗ˡ_ : ∀ {m n} → LehmerPath m → LehmerPath n → LehmerPath (m * n)
l₁ ⊗ˡ l₂ =
  encode (decode l₁ ⊗ decode l₂)
         (⊗-is-perm (decode l₁) (decode l₂) (decode-is-perm l₁) (decode-is-perm l₂))

decode-⊗ˡ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
            decode (l₁ ⊗ˡ l₂) ≡ (decode l₁ ⊗ decode l₂)
decode-⊗ˡ l₁ l₂ =
  decode-encode (decode l₁ ⊗ decode l₂)
                (⊗-is-perm (decode l₁) (decode l₂) (decode-is-perm l₁) (decode-is-perm l₂))
