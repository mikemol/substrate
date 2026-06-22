------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Hilbert2DContinuous
--
-- ⊙.hilbert∀n — the ∀n continuity of the 2D Hilbert curve, generalizing the
-- concrete `Hilbert2D.hilbert-2-continuous`. DONE here (the full infrastructure):
--   * `hilbert-entry` / `hilbert-exit` — the entry/exit RECURSION: hilbert n runs
--     from (0,0) to (2ⁿ−1, 0) for every order n.
--   * the four quadrant transforms named (A/B/C/D = Hilbert2D's lambdas, definitionally)
--     and proved Manhattan ISOMETRIES (`manh-A/B/C/D`; D's reflection via the
--     bounded-monus lemma (k∸a)∸(k∸b) ≡ b∸a).
--   * the coordinate-BOUND invariant `hilbert-bounded` (coords < 2ⁿ), which feeds D's
--     isometry.
--   * `Cont` (consecutive points adjacent) + `Cont-app` gluing the four isometric
--     sub-curves, the 3 quadrant seams = 1 (computed from entry/exit).
-- THEOREM `hilbert-continuous` : Cont (hilbert n) for EVERY n — the 2D Hilbert curve
-- is continuous at all orders (generalizing the concrete hilbert-2-continuous). Done.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Hilbert2DContinuous where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_; _≤_; _<_; z≤n; s≤s)
open import Substrate.Foundation.Nat.Properties.Sub using (m∸m≡0; ∸-∸-cancel; ∸-≤-self)
open import Substrate.Foundation.Nat.Properties.Add using (+-suc; +-identityʳ; +-comm)
open import Substrate.Foundation.Nat.Properties.Order
  using (≤-refl; ≤-suc-r; ≤-trans; ≤-<-trans; <-suc-self; m≤m+n; +-monoˡ-≤)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym; subst)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Product using (Σ; _×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.CayleyDickson.Hilbert2D
  using (Pt; pow2; mapL; hilbert; manh)

------------------------------------------------------------------------
-- 1. first / last of a point-list, and how they pass through ++ and mapL.
------------------------------------------------------------------------

firstP : List Pt → Pt
firstP []      = (0 , 0)
firstP (p ∷ _) = p

lastP : List Pt → Pt
lastP []           = (0 , 0)
lastP (p ∷ [])     = p
lastP (p ∷ q ∷ ps) = lastP (q ∷ ps)

-- first of (x ∷ xs) ++ ys is the head of the left list.
firstP-++ : (p : Pt) (xs ys : List Pt) → firstP ((p ∷ xs) ++ ys) ≡ p
firstP-++ p xs ys = refl

-- last of xs ++ (q ∷ ys) is the last of the right list (the left can't be last).
lastP-++ : (xs : List Pt) (q : Pt) (ys : List Pt) → lastP (xs ++ q ∷ ys) ≡ lastP (q ∷ ys)
lastP-++ []           q ys = refl
lastP-++ (p ∷ [])     q ys = refl
lastP-++ (p ∷ r ∷ rs) q ys = lastP-++ (r ∷ rs) q ys

firstP-mapL : (f : Pt → Pt) (p : Pt) (xs : List Pt) → firstP (mapL f (p ∷ xs)) ≡ f p
firstP-mapL f p xs = refl

lastP-mapL : (f : Pt → Pt) (p : Pt) (xs : List Pt) → lastP (mapL f (p ∷ xs)) ≡ f (lastP (p ∷ xs))
lastP-mapL f p []        = refl
lastP-mapL f p (q ∷ qs)  = lastP-mapL f q qs

------------------------------------------------------------------------
-- 2. The entry/exit recursion: hilbert n starts (0,0), ends (2ⁿ−1, 0).
------------------------------------------------------------------------

-- hilbert n is non-empty AND its head is (0,0): the curve starts at the origin
-- for every order. (A = transpose fixes (0,0); the other quadrants follow it.)
hilbert-head : (n : ℕ) → Σ (List Pt) (λ ys → hilbert n ≡ (0 , 0) ∷ ys)
hilbert-head zero    = [] , refl
hilbert-head (suc n) with hilbert-head n
... | ys , eq rewrite eq = _ , refl

-- the entry point of hilbert n is (0,0), for every n.
hilbert-entry : (n : ℕ) → firstP (hilbert n) ≡ (0 , 0)
hilbert-entry n with hilbert-head n
... | ys , eq rewrite eq = refl

------------------------------------------------------------------------
-- 3. The four quadrant transforms, named (definitionally = Hilbert2D's lambdas),
--    and the monus lemmas the reflection-isometry needs.
------------------------------------------------------------------------

A : Pt → Pt
A p = (proj₂ p , proj₁ p)                              -- transpose (entry rotation)
B C D : ℕ → Pt → Pt
B s p = (proj₁ p , proj₂ p + s)                        -- shift up
C s p = (proj₁ p + s , proj₂ p + s)                    -- shift up-right
D s p = (((s + s) ∸ 1) ∸ proj₂ p , (s ∸ 1) ∸ proj₁ p)  -- anti-diagonal reflect (exit rotation)

0∸n≡0 : (n : ℕ) → zero ∸ n ≡ 0
0∸n≡0 zero    = refl
0∸n≡0 (suc n) = refl

≤→∸≡0 : {m n : ℕ} → m ≤ n → m ∸ n ≡ 0
≤→∸≡0 {n = n} z≤n = 0∸n≡0 n
≤→∸≡0 (s≤s p)     = ≤→∸≡0 p

∸-+-cancel : (a b s : ℕ) → (a + s) ∸ (b + s) ≡ a ∸ b
∸-+-cancel a b zero    = cong₂ _∸_ (+-identityʳ a) (+-identityʳ b)
∸-+-cancel a b (suc s) = trans (cong₂ _∸_ (+-suc a s) (+-suc b s)) (∸-+-cancel a b s)

-- reflection preserves the (one-sided) gap: for a,b ≤ k, (k∸a)∸(k∸b) ≡ b∸a.
monus-reflect : (k a b : ℕ) → a ≤ k → b ≤ k → (k ∸ a) ∸ (k ∸ b) ≡ b ∸ a
monus-reflect k       zero     b        _         b≤k       = ∸-∸-cancel k b b≤k
monus-reflect (suc k) (suc a)  zero     (s≤s a≤k) _         = ≤→∸≡0 (≤-suc-r (∸-≤-self k a))
monus-reflect (suc k) (suc a)  (suc b)  (s≤s a≤k) (s≤s b≤k) = monus-reflect k a b a≤k b≤k

<⇒≤∸1 : {x s : ℕ} → x < s → x ≤ s ∸ 1
<⇒≤∸1 (s≤s p) = p

------------------------------------------------------------------------
-- 4. Each transform is a Manhattan ISOMETRY (so a sub-curve stays continuous).
--    manh p q = adist (x p)(x q) + adist (y p)(y q), adist a b = (a∸b)+(b∸a).
------------------------------------------------------------------------

adist : ℕ → ℕ → ℕ
adist a b = (a ∸ b) + (b ∸ a)

adist-+s : (a b s : ℕ) → adist (a + s) (b + s) ≡ adist a b
adist-+s a b s = cong₂ _+_ (∸-+-cancel a b s) (∸-+-cancel b a s)

adist-reflect : (k a b : ℕ) → a ≤ k → b ≤ k → adist (k ∸ a) (k ∸ b) ≡ adist a b
adist-reflect k a b a≤k b≤k =
  trans (cong₂ _+_ (monus-reflect k a b a≤k b≤k) (monus-reflect k b a b≤k a≤k))
        (+-comm (b ∸ a) (a ∸ b))

manh-A : (p q : Pt) → manh (A p) (A q) ≡ manh p q
manh-A p q = +-comm (adist (proj₂ p) (proj₂ q)) (adist (proj₁ p) (proj₁ q))

manh-B : (s : ℕ) (p q : Pt) → manh (B s p) (B s q) ≡ manh p q
manh-B s p q = cong (adist (proj₁ p) (proj₁ q) +_) (adist-+s (proj₂ p) (proj₂ q) s)

manh-C : (s : ℕ) (p q : Pt) → manh (C s p) (C s q) ≡ manh p q
manh-C s p q = cong₂ _+_ (adist-+s (proj₁ p) (proj₁ q) s) (adist-+s (proj₂ p) (proj₂ q) s)

-- D needs the coordinate bounds (coords < s) so the reflections don't truncate.
manh-D : (s : ℕ) (p q : Pt) →
         proj₁ p < s → proj₂ p < s → proj₁ q < s → proj₂ q < s →
         manh (D s p) (D s q) ≡ manh p q
manh-D s p q x₁ y₁ x₂ y₂ =
  trans (cong₂ _+_ (adist-reflect ((s + s) ∸ 1) (proj₂ p) (proj₂ q)
                      (<⇒≤∸1 (≤-trans y₁ (m≤m+n s s))) (<⇒≤∸1 (≤-trans y₂ (m≤m+n s s))))
                   (adist-reflect (s ∸ 1) (proj₁ p) (proj₁ q) (<⇒≤∸1 x₁) (<⇒≤∸1 x₂)))
        (+-comm (adist (proj₂ p) (proj₂ q)) (adist (proj₁ p) (proj₁ q)))

------------------------------------------------------------------------
-- 5. The coordinate-BOUND invariant: every point of hilbert n has coords < 2ⁿ
--    (so the D-isometry's reflections don't truncate).
------------------------------------------------------------------------

InB : ℕ → Pt → Set
InB s p = (proj₁ p < s) × (proj₂ p < s)

AllInB : ℕ → List Pt → Set
AllInB s []       = ⊤
AllInB s (p ∷ ps) = InB s p × AllInB s ps

AllInB-++ : (s : ℕ) (xs ys : List Pt) → AllInB s xs → AllInB s ys → AllInB s (xs ++ ys)
AllInB-++ s []       ys _          ay = ay
AllInB-++ s (p ∷ ps) ys (ip , aps) ay = ip , AllInB-++ s ps ys aps ay

AllInB-mapL : (f : Pt → Pt) (s s′ : ℕ) (xs : List Pt) →
              ((p : Pt) → InB s p → InB s′ (f p)) → AllInB s xs → AllInB s′ (mapL f xs)
AllInB-mapL f s s′ []       _    _          = tt
AllInB-mapL f s s′ (p ∷ ps) pres (ip , aps) = pres p ip , AllInB-mapL f s s′ ps pres aps

pow2-pos : (n : ℕ) → 1 ≤ pow2 n
pow2-pos zero    = ≤-refl 1
pow2-pos (suc n) = ≤-trans (pow2-pos n) (m≤m+n (pow2 n) (pow2 n))

m∸1<m : (m : ℕ) → 1 ≤ m → m ∸ 1 < m
m∸1<m (suc m) _ = <-suc-self m

<-weaken : {x s : ℕ} → x < s → x < s + s
<-weaken {x} {s} x<s = ≤-trans x<s (m≤m+n s s)

+s-< : {x s : ℕ} → x < s → x + s < s + s
+s-< {x} {s} x<s = +-monoˡ-≤ s x<s

A-bound : (s : ℕ) (p : Pt) → InB s p → InB (s + s) (A p)
A-bound s p (x< , y<) = <-weaken y< , <-weaken x<

B-bound : (s : ℕ) (p : Pt) → InB s p → InB (s + s) (B s p)
B-bound s p (x< , y<) = <-weaken x< , +s-< y<

C-bound : (s : ℕ) (p : Pt) → InB s p → InB (s + s) (C s p)
C-bound s p (x< , y<) = +s-< x< , +s-< y<

D-bound : (s : ℕ) → 1 ≤ s → (p : Pt) → InB s p → InB (s + s) (D s p)
D-bound s 1≤s p (x< , y<) =
    ≤-<-trans (∸-≤-self ((s + s) ∸ 1) (proj₂ p)) (m∸1<m (s + s) (≤-trans 1≤s (m≤m+n s s)))
  , ≤-trans (≤-<-trans (∸-≤-self (s ∸ 1) (proj₁ p)) (m∸1<m s 1≤s)) (m≤m+n s s)

-- every point of hilbert n is in bounds 2ⁿ.
hilbert-bounded : (n : ℕ) → AllInB (pow2 n) (hilbert n)
hilbert-bounded zero    = (s≤s z≤n , s≤s z≤n) , tt
hilbert-bounded (suc n) =
  AllInB-++ (s + s) (mapL A h) _ (AllInB-mapL A s (s + s) h (A-bound s) bh)
  (AllInB-++ (s + s) (mapL (B s) h) _ (AllInB-mapL (B s) s (s + s) h (B-bound s) bh)
  (AllInB-++ (s + s) (mapL (C s) h) (mapL (D s) h)
             (AllInB-mapL (C s) s (s + s) h (C-bound s) bh)
             (AllInB-mapL (D s) s (s + s) h (D-bound s (pow2-pos n)) bh)))
  where s = pow2 n
        h = hilbert n
        bh = hilbert-bounded n

------------------------------------------------------------------------
-- 6. The EXIT recursion: hilbert n ends at (2ⁿ−1, 0). (Peel the first three
--    quadrants off the back; the last point is the D-image of hilbert n's last.)
------------------------------------------------------------------------

lastP-hilbert-suc : (n : ℕ) → lastP (hilbert (suc n)) ≡ D (pow2 n) (lastP (hilbert n))
lastP-hilbert-suc n with hilbert-head n
... | ys , eq rewrite eq =
  trans (lastP-++ (mapL A ((0 , 0) ∷ ys)) _ _)
  (trans (lastP-++ (mapL (B (pow2 n)) ((0 , 0) ∷ ys)) _ _)
  (trans (lastP-++ (mapL (C (pow2 n)) ((0 , 0) ∷ ys)) _ _)
         (lastP-mapL (D (pow2 n)) (0 , 0) ys)))

hilbert-exit : (n : ℕ) → lastP (hilbert n) ≡ (pow2 n ∸ 1 , 0)
hilbert-exit zero    = refl
hilbert-exit (suc n) =
  trans (lastP-hilbert-suc n)
  (trans (cong (D (pow2 n)) (hilbert-exit n))
         (cong (λ z → ((pow2 n + pow2 n) ∸ 1 , z)) (m∸m≡0 (pow2 n ∸ 1))))

------------------------------------------------------------------------
-- 7. Continuity: consecutive points are adjacent (Manhattan 1). The four
--    isometric sub-curves glue because the 3 quadrant seams are distance 1.
------------------------------------------------------------------------

-- seam value lemmas: adist at a predecessor gap is 1; at equal points is 0.
sm∸m≡1 : (m : ℕ) → suc m ∸ m ≡ 1
sm∸m≡1 zero    = refl
sm∸m≡1 (suc m) = sm∸m≡1 m

m∸pred≡1 : (s : ℕ) → 1 ≤ s → s ∸ (s ∸ 1) ≡ 1
m∸pred≡1 (suc m) _ = sm∸m≡1 m

pred-+ : (a b : ℕ) → 1 ≤ a → (a ∸ 1) + b ≡ (a + b) ∸ 1
pred-+ (suc a) b _ = refl

adist-self : (x : ℕ) → adist x x ≡ 0
adist-self x = cong₂ _+_ (m∸m≡0 x) (m∸m≡0 x)

adist-pred : (s : ℕ) → 1 ≤ s → adist (s ∸ 1) s ≡ 1
adist-pred s 1≤s = cong₂ _+_ (≤→∸≡0 (∸-≤-self s 1)) (m∸pred≡1 s 1≤s)

adist-pred′ : (s : ℕ) → 1 ≤ s → adist s (s ∸ 1) ≡ 1
adist-pred′ s 1≤s = cong₂ _+_ (m∸pred≡1 s 1≤s) (≤→∸≡0 (∸-≤-self s 1))

Cont : List Pt → Set
Cont []           = ⊤
Cont (_ ∷ [])     = ⊤
Cont (p ∷ q ∷ ps) = (manh p q ≡ 1) × Cont (q ∷ ps)

-- glue a cons-headed list onto xs, given continuity of each and a distance-1 seam.
Cont-app : (xs : List Pt) (q : Pt) (ys : List Pt) →
           Cont xs → Cont (q ∷ ys) → manh (lastP xs) q ≡ 1 → Cont (xs ++ q ∷ ys)
Cont-app []           q ys _           cqys _    = cqys
Cont-app (p ∷ [])     q ys _           cqys seam = seam , cqys
Cont-app (p ∷ r ∷ rs) q ys (mpr , crs) cqys seam = mpr , Cont-app (r ∷ rs) q ys crs cqys seam

-- an isometry (using the bounds) carries continuity through mapL.
Cont-mapL : (f : Pt → Pt) (s : ℕ) (xs : List Pt) →
            ((p q : Pt) → InB s p → InB s q → manh (f p) (f q) ≡ manh p q) →
            AllInB s xs → Cont xs → Cont (mapL f xs)
Cont-mapL f s []           _   _                _            = tt
Cont-mapL f s (p ∷ [])     _   _                _            = tt
Cont-mapL f s (p ∷ q ∷ ps) iso (ip , iq , aps) (mpq , cqps) =
  trans (iso p q ip iq) mpq , Cont-mapL f s (q ∷ ps) iso (iq , aps) cqps

-- THE THEOREM: the 2D Hilbert curve is continuous at every order. Glue the four
-- isometric sub-curves (Cont-mapL), the seams distance-1 (from entry/exit).
hilbert-continuous : (n : ℕ) → Cont (hilbert n)
hilbert-continuous zero    = tt
hilbert-continuous (suc n) with hilbert-head n
... | ys , eq rewrite eq =
  Cont-app (mapL A z0) (B s (0 , 0)) _ cA
  (Cont-app (mapL (B s) z0) (C s (0 , 0)) _ cB
  (Cont-app (mapL (C s) z0) (D s (0 , 0)) _ cC cD seam-CD)
    seam-BC)
    seam-AB
  where
    s  = pow2 n
    z0 = (0 , 0) ∷ ys
    bh : AllInB s z0
    bh = subst (AllInB s) eq (hilbert-bounded n)
    ch : Cont z0
    ch = subst Cont eq (hilbert-continuous n)
    exitY : lastP z0 ≡ (pow2 n ∸ 1 , 0)
    exitY = trans (cong lastP (sym eq)) (hilbert-exit n)
    cA = Cont-mapL A     s z0 (λ p q _  _  → manh-A   p q) bh ch
    cB = Cont-mapL (B s) s z0 (λ p q _  _  → manh-B s p q) bh ch
    cC = Cont-mapL (C s) s z0 (λ p q _  _  → manh-C s p q) bh ch
    cD = Cont-mapL (D s) s z0
           (λ p q ip iq → manh-D s p q (proj₁ ip) (proj₂ ip) (proj₁ iq) (proj₂ iq)) bh ch
    seam-AB : manh (lastP (mapL A z0)) (B s (0 , 0)) ≡ 1
    seam-AB = trans (cong (λ w → manh w (B s (0 , 0))) (lastP-mapL A (0 , 0) ys))
              (trans (cong (λ w → manh (A w) (B s (0 , 0))) exitY)
                     (adist-pred s (pow2-pos n)))
    seam-BC : manh (lastP (mapL (B s) z0)) (C s (0 , 0)) ≡ 1
    seam-BC = trans (cong (λ w → manh w (C s (0 , 0))) (lastP-mapL (B s) (0 , 0) ys))
              (trans (cong (λ w → manh (B s w) (C s (0 , 0))) exitY)
              (trans (cong (adist (s ∸ 1) s +_) (adist-self s))
              (trans (+-identityʳ (adist (s ∸ 1) s)) (adist-pred s (pow2-pos n)))))
    seam-CD : manh (lastP (mapL (C s) z0)) (D s (0 , 0)) ≡ 1
    seam-CD = trans (cong (λ w → manh w (D s (0 , 0))) (lastP-mapL (C s) (0 , 0) ys))
              (trans (cong (λ w → manh (C s w) (D s (0 , 0))) exitY)
              (trans (cong (_+ adist s (s ∸ 1))
                        (trans (cong (λ w → adist w ((s + s) ∸ 1)) (pred-+ s s (pow2-pos n)))
                               (adist-self ((s + s) ∸ 1))))
                     (adist-pred′ s (pow2-pos n))))
