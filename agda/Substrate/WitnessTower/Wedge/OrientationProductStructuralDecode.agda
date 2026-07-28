------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductStructuralDecode
--
-- ⟡rig-UP-wreath (Step B) — decode-agreement for the fold-transparent structural
-- product: decode (l₁ ⊗ˢ l₂) ≡ decode l₁ ⊗ decode l₂. This is the correctness
-- link that ⊗ˢ (OrientationProductStructural) computes the actual Perm product ⊗.
--
-- Route: the ⊗-combine characterization for ⊗ˢ (lookup at a combine index is the
-- combine of the factor lookups), then lookup-ext + combine-remQuot (as in
-- OrientationProductLaws.⊗-assoc). The characterization reduces, via the outer
-- ◂-recursion + the committed keystone (blockPunchIn-combine), to two GENERALIZED
-- facts about `replay-aux` proven by induction on the length-k FRAGMENT (stated in
-- toℕ, which sidesteps the fragment-grade / block-modulus mismatch):
--   HEAD: the first k entries are the p·n-offset replay of decode l's values.
--   TAIL: the remaining m·n entries are decode base, block-shifted by k past p·n.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductStructuralDecode where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _*_; _≤_; _<_; z≤n; s≤s; s≤s-injective)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm; +-suc; +-assoc)
open import Substrate.Foundation.Nat.Properties.Order
  using (+-monoʳ-≤; +-mono-≤; *-monoˡ-≤; ≤-trans; m≤m+n; <-irrefl)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties using (toℕ-fromℕ<; toℕ-bound; toℕ-injective)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.Combine.Assoc using (toℕ-inject+; toℕ-raise; toℕ-combine)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (lookup-map)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)
open import Substrate.WitnessTower.Wedge.OrientationProductLaws using (⊗-combine)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
  using (offsetDigit; replay-aux; _⊗ˢ_)

------------------------------------------------------------------------
-- 0. toℕ of the offset digit: p·n + toℕ q (fromℕ< round-trip).
------------------------------------------------------------------------

toℕ-offsetDigit : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ} (q : Fin (suc k)) →
                  toℕ (offsetDigit p n q) ≡ toℕ p * n + toℕ q
toℕ-offsetDigit p n q = toℕ-fromℕ< _

------------------------------------------------------------------------
-- 1. toℕ of punchIn, split by whether the point sits below or at/above the slot.
------------------------------------------------------------------------

toℕ-punchIn-< : ∀ {n} (k : Fin (suc n)) (x : Fin n) →
                toℕ x < toℕ k → toℕ (punchIn k x) ≡ toℕ x
toℕ-punchIn-< zero            x       ()
toℕ-punchIn-< (suc k) zero            _        = refl
toℕ-punchIn-< {suc _} (suc k) (suc x) (s≤s lt) = cong suc (toℕ-punchIn-< k x lt)

toℕ-punchIn-≥ : ∀ {n} (k : Fin (suc n)) (x : Fin n) →
                toℕ k ≤ toℕ x → toℕ (punchIn k x) ≡ suc (toℕ x)
toℕ-punchIn-≥ zero            x       _        = refl
toℕ-punchIn-≥ (suc k) zero            ()
toℕ-punchIn-≥ {suc _} (suc k) (suc x) (s≤s le) = cong suc (toℕ-punchIn-≥ k x le)

------------------------------------------------------------------------
-- 2. lookup of insert-at: head is the choice, successor is punchIn of the tail.
------------------------------------------------------------------------

lookup-insert-zero : ∀ {n} (p : Fin (suc n)) (σ : Perm n) →
                     lookup (insert-at p σ) zero ≡ p
lookup-insert-zero p σ = refl

lookup-insert-suc : ∀ {n} (p : Fin (suc n)) (σ : Perm n) (i : Fin n) →
                    lookup (insert-at p σ) (suc i) ≡ punchIn p (lookup σ i)
lookup-insert-suc p σ i = lookup-map (punchIn p) σ i

------------------------------------------------------------------------
-- 3. Dichotomy on ℕ (no trichotomy lemma in Foundation; local).
------------------------------------------------------------------------

<-or-≥ : (a c : ℕ) → (a < c) ⊎ (c ≤ a)
<-or-≥ zero    zero    = inj₂ z≤n
<-or-≥ zero    (suc c) = inj₁ (s≤s z≤n)
<-or-≥ (suc a) zero    = inj₂ z≤n
<-or-≥ (suc a) (suc c) with <-or-≥ a c
... | inj₁ lt = inj₁ (s≤s lt)
... | inj₂ ge = inj₂ (s≤s ge)

------------------------------------------------------------------------
-- 4. HEAD: the first k entries of decode (replay-aux p n l base) are the
--    p·n-offset replay of decode l's values. Induction on the fragment l.
------------------------------------------------------------------------

replay-head : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ}
              (l : LehmerPath k) (b : LehmerPath (m * n)) (j : Fin k) →
              toℕ (lookup (decode (replay-aux p n l b)) (inject+ (m * n) j))
                ≡ toℕ p * n + toℕ (lookup (decode l) j)
replay-head p n start   b ()
replay-head {m} p n (l ◂ q) b zero =
  trans (cong toℕ (lookup-insert-zero (offsetDigit p n q) (decode (replay-aux p n l b))))
        (toℕ-offsetDigit p n q)
replay-head {m} p n (l ◂ q) b (suc j) =
  trans (cong toℕ (lookup-insert-suc D R (inject+ (m * n) j)))
        (trans punch-eq
               (cong (λ z → toℕ p * n + toℕ z) (sym (lookup-insert-suc q (decode l) j))))
  where
  D = offsetDigit p n q
  R = decode (replay-aux p n l b)
  x = lookup R (inject+ (m * n) j)
  v = toℕ (lookup (decode l) j)
  ihx : toℕ x ≡ toℕ p * n + v
  ihx = replay-head p n l b j
  toℕD : toℕ D ≡ toℕ p * n + toℕ q
  toℕD = toℕ-offsetDigit p n q
  punch-eq : toℕ (punchIn D x) ≡ toℕ p * n + toℕ (punchIn q (lookup (decode l) j))
  punch-eq with <-or-≥ v (toℕ q)
  ... | inj₁ lt =
    trans (toℕ-punchIn-< D x xltD)
          (trans ihx (cong (λ z → toℕ p * n + z)
                           (sym (toℕ-punchIn-< q (lookup (decode l) j) lt))))
    where
    mono : toℕ p * n + v < toℕ p * n + toℕ q
    mono = subst (λ z → z ≤ toℕ p * n + toℕ q) (+-suc (toℕ p * n) v)
                 (+-monoʳ-≤ (toℕ p * n) lt)
    xltD : toℕ x < toℕ D
    xltD = subst (λ z → toℕ x < z) (sym toℕD)
                 (subst (λ z → z < toℕ p * n + toℕ q) (sym ihx) mono)
  ... | inj₂ ge =
    trans (toℕ-punchIn-≥ D x Dlex)
          (trans (cong suc ihx)
                 (trans (sym (+-suc (toℕ p * n) v))
                        (cong (λ z → toℕ p * n + z)
                              (sym (toℕ-punchIn-≥ q (lookup (decode l) j) ge)))))
    where
    Dlex : toℕ D ≤ toℕ x
    Dlex = subst (λ z → toℕ D ≤ z) (sym ihx)
                 (subst (λ z → z ≤ toℕ p * n + v) (sym toℕD)
                        (+-monoʳ-≤ (toℕ p * n) ge))

------------------------------------------------------------------------
-- 5. The block-shift: a value w is kept if below the block offset, else pushed
--    up past the cnt inserted slots. (blkShift off n · IS blockPunchIn's toℕ.)
------------------------------------------------------------------------

blkShift : (off cnt w : ℕ) → ℕ
blkShift off cnt w with <-or-≥ w off
... | inj₁ _ = w
... | inj₂ _ = cnt + w

blkShift-0 : (off w : ℕ) → blkShift off zero w ≡ w
blkShift-0 off w with <-or-≥ w off
... | inj₁ _ = refl
... | inj₂ _ = refl

-- blkShift reduces once the dichotomy is resolved (its own `with` is opaque to
-- callers, so we expose these rewrites explicitly).
blkShift-< : (off cnt w : ℕ) → w < off → blkShift off cnt w ≡ w
blkShift-< off cnt w lt with <-or-≥ w off
... | inj₁ _  = refl
... | inj₂ ge = ⊥-elim (<-irrefl w (≤-trans lt ge))

blkShift-≥ : (off cnt w : ℕ) → off ≤ w → blkShift off cnt w ≡ cnt + w
blkShift-≥ off cnt w ge with <-or-≥ w off
... | inj₁ lt = ⊥-elim (<-irrefl w (≤-trans lt ge))
... | inj₂ _  = refl

------------------------------------------------------------------------
-- 6. TAIL: the remaining m·n entries of decode (replay-aux p n l base) are
--    decode base, block-shifted by k (the fragment length) past p·n.
------------------------------------------------------------------------

replay-tail : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k : ℕ}
              (l : LehmerPath k) (b : LehmerPath (m * n)) (i : Fin (m * n)) →
              toℕ (lookup (decode (replay-aux p n l b)) (raise k i))
                ≡ blkShift (toℕ p * n) k (toℕ (lookup (decode b) i))
replay-tail p n start   b i = sym (blkShift-0 (toℕ p * n) (toℕ (lookup (decode b) i)))
replay-tail {m} p n (_◂_ {k} l q) b i =
  trans (cong toℕ (lookup-insert-suc D R (raise k i))) punch-eq
  where
  D = offsetDigit p n q
  R = decode (replay-aux p n l b)
  y = lookup R (raise k i)
  w = toℕ (lookup (decode b) i)
  off = toℕ p * n
  ihy : toℕ y ≡ blkShift off k w
  ihy = replay-tail p n l b i
  q≤k : toℕ q ≤ k
  q≤k = s≤s-injective (toℕ-bound q)
  toℕD : toℕ D ≡ off + toℕ q
  toℕD = toℕ-offsetDigit p n q
  -- Case-split on the dichotomy inside a helper whose return type is FIXED
  -- (not `with`-abstracted), so blkShift-< / blkShift-≥ rewrite the goal cleanly.
  punch-eq : toℕ (punchIn D y) ≡ blkShift off (suc k) w
  punch-eq = helper (<-or-≥ w off)
    where
    helper : (w < off) ⊎ (off ≤ w) → toℕ (punchIn D y) ≡ blkShift off (suc k) w
    helper (inj₁ lt) =
      -- w < off : nothing inserted below w ; y stays, D is above y.
      trans (trans (toℕ-punchIn-< D y yltD) ihyw) (sym (blkShift-< off (suc k) w lt))
      where
      ihyw : toℕ y ≡ w
      ihyw = trans ihy (blkShift-< off k w lt)
      off≤D : off ≤ toℕ D
      off≤D = subst (off ≤_) (sym toℕD) (m≤m+n off (toℕ q))
      yltD : toℕ y < toℕ D
      yltD = subst (λ z → z < toℕ D) (sym ihyw) (≤-trans lt off≤D)
    helper (inj₂ ge) =
      -- off ≤ w : y = k + w sits above D = off + toℕ q ; punch bumps by one.
      trans (trans (toℕ-punchIn-≥ D y Dley) (cong suc ihykw))
            (sym (blkShift-≥ off (suc k) w ge))
      where
      ihykw : toℕ y ≡ k + w
      ihykw = trans ihy (blkShift-≥ off k w ge)
      Dley : toℕ D ≤ toℕ y
      Dley = subst (λ z → toℕ D ≤ z) (sym ihykw)
                   (subst (λ z → z ≤ k + w) (sym toℕD)
                          (subst (λ z → off + toℕ q ≤ z) (+-comm w k)
                                 (+-mono-≤ ge q≤k)))

------------------------------------------------------------------------
-- 7. THE KEYSTONE (toℕ form): the block-shift of a combined index a·n+b, offset by
--    p·n and count n, IS the punchIn of the quotient — blockPunchIn's arithmetic.
------------------------------------------------------------------------

blockBound : ∀ {m n} (p : Fin (suc m)) (A : Fin m) (B : Fin n) →
             toℕ A < toℕ p → toℕ A * n + toℕ B < toℕ p * n
blockBound {m} {n} p A B A<p =
  subst (λ z → z ≤ toℕ p * n) (+-suc (toℕ A * n) (toℕ B))
        (≤-trans (+-monoʳ-≤ (toℕ A * n) (toℕ-bound B))
                 (subst (λ z → z ≤ toℕ p * n) (sym (+-comm (toℕ A * n) n))
                        (*-monoˡ-≤ n A<p)))

blkShift-combine : ∀ {m n} (p : Fin (suc m)) (A : Fin m) (B : Fin n) →
                   blkShift (toℕ p * n) n (toℕ A * n + toℕ B)
                     ≡ toℕ (punchIn p A) * n + toℕ B
blkShift-combine {m} {n} p A B with <-or-≥ (toℕ A) (toℕ p)
... | inj₁ A<p =
      trans (blkShift-< (toℕ p * n) n (toℕ A * n + toℕ B) (blockBound p A B A<p))
            (cong (λ z → z * n + toℕ B) (sym (toℕ-punchIn-< p A A<p)))
... | inj₂ p≤A =
      trans (blkShift-≥ (toℕ p * n) n (toℕ A * n + toℕ B)
                        (≤-trans (*-monoˡ-≤ n p≤A) (m≤m+n (toℕ A * n) (toℕ B))))
            (trans (sym (+-assoc n (toℕ A * n) (toℕ B)))
                   (cong (λ z → z * n + toℕ B) (sym (toℕ-punchIn-≥ p A p≤A))))

------------------------------------------------------------------------
-- 8. THE ⊗-COMBINE CHARACTERIZATION for ⊗ˢ, then decode-agreement. Induction on
--    l₁: the head (combine zero) via replay-head, the tail (combine suc) via
--    replay-tail + blkShift-combine + the outer IH. lookup-ext closes decode-⊗ˢ.
------------------------------------------------------------------------

⊗ˢ-combine : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) (i : Fin m) (j : Fin n) →
             lookup (decode (l₁ ⊗ˢ l₂)) (combine i j)
               ≡ combine (lookup (decode l₁) i) (lookup (decode l₂) j)
⊗ˢ-combine (l₁ ◂ p) l₂ zero    j = toℕ-injective
  (trans (replay-head p _ l₂ (l₁ ⊗ˢ l₂) j)
         (sym (toℕ-combine p (lookup (decode l₂) j))))
⊗ˢ-combine {suc m} {n} (l₁ ◂ p) l₂ (suc i) j = toℕ-injective
  (trans (replay-tail p n l₂ (l₁ ⊗ˢ l₂) (combine i j))
  (trans (cong (blkShift (toℕ p * n) n) ihComb)
  (trans (blkShift-combine p (lookup (decode l₁) i) (lookup (decode l₂) j))
  (trans (sym (toℕ-combine (punchIn p (lookup (decode l₁) i)) (lookup (decode l₂) j)))
         (cong (λ z → toℕ (combine z (lookup (decode l₂) j)))
               (sym (lookup-insert-suc p (decode l₁) i)))))))
  where
  ihComb : toℕ (lookup (decode (l₁ ⊗ˢ l₂)) (combine i j))
             ≡ toℕ (lookup (decode l₁) i) * n + toℕ (lookup (decode l₂) j)
  ihComb = trans (cong toℕ (⊗ˢ-combine l₁ l₂ i j))
                 (toℕ-combine (lookup (decode l₁) i) (lookup (decode l₂) j))

decode-⊗ˢ : ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
            decode (l₁ ⊗ˢ l₂) ≡ (decode l₁ ⊗ decode l₂)
decode-⊗ˢ {m} {n} l₁ l₂ = lookup-ext _ _ pointwise
  where
  pointwise : (k : Fin (m * n)) →
              lookup (decode (l₁ ⊗ˢ l₂)) k ≡ lookup (decode l₁ ⊗ decode l₂) k
  pointwise k =
    trans (cong (lookup (decode (l₁ ⊗ˢ l₂))) (sym kd))
          (trans (⊗ˢ-combine l₁ l₂ i j)
                 (trans (sym (⊗-combine (decode l₁) (decode l₂) i j))
                        (cong (lookup (decode l₁ ⊗ decode l₂)) kd)))
    where
    i = proj₁ (remQuot {m} n k)
    j = proj₂ (remQuot {m} n k)
    kd : combine i j ≡ k
    kd = combine-remQuot m n k
