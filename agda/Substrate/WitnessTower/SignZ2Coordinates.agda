------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates
--
-- THE APEX over ◆tighten-insertion-parity: the permutation sign is ONE ℤ/2
-- read through many COORDINATES, and the twisted-Lehmer sign-MORPHISM
-- (sign-lehmer-morphism-unconditional) is the newly-added GRADED coordinate on
-- the one ℤ/2 that OrientationRigCatPermSignChirality holds as five STATIC
-- guises (inversion-count / Coxeter-length / CF-det / ε-parity / arithmetic).
--
-- This module CITES both InsertionParity (the graded coordinate) and Chirality
-- (the static guises) — it does NOT edit Chirality (which deliberately declares
-- no record, pure-proof side). It contributes:
--   ◆ip-chirality-coapex   — the graded morphism's value = the inversion-count
--                            guise (tower-sign-is-invcount = sign-as-parity ∘ decode).
--   ◆ip-invcount-recurrence — the ℕ-EXACT count recurrence Chirality's static
--                            invCount lacks: invCount (insert-at p σ) ≡ toℕ p +
--                            invCount σ (inserting value p adds EXACTLY toℕ p
--                            inversions). The un-mod-2 strengthening of
--                            InsertionParity.count-below, via the same Route-A
--                            scaffolding re-run at the ℕ level.
--   ◆ip-chirality-apex     — the cover record SignZ2AtPath: the graded coordinate
--                            agrees with the inversion-count AND Coxeter-length
--                            guises at every Lehmer path.
--
-- --safe --without-K, no Σ / Set₁, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _≤_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm; +-assoc)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; boolToℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.FromBool using (bool→F₂)
open import Substrate.Algebra.N-to-F2-Parity using (parity)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.SnGroup using (compose-id-left; compose-id-right)
open import Substrate.WitnessTower.CyclicGrounding using (compose-assoc)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
  using (sign; finLt; _<ᵇ_; swapAdj; id-perm-cons; bridge; sign-wd; signW)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
  using (CoxGen; cox-id; cox-s; cox-∘)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
  using (coxeter-complete)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; decode; decode-is-perm)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
  using (invCount; countLess; sign-as-parity)
open import Substrate.WitnessTower.InsertionParity
  using (finLt-punchIn; punchIn-lt; map-swapAdj; toℕ≤m)

------------------------------------------------------------------------
-- ◆ip-chirality-coapex — the graded coordinate meets the static guises.
------------------------------------------------------------------------

-- the tower sign morphism's value at l = the inversion-count guise (Chirality:5).
tower-sign-is-invcount : {n : ℕ} (l : LehmerPath n) →
                         signF (decode l) ≡ parity (invCount (decode l))
tower-sign-is-invcount l = sign-as-parity (decode l)

-- and = the Coxeter-length guise (via sign-wd, over any derivation).
tower-sign-is-length : {n : ℕ} (l : LehmerPath n) →
  signF (decode l) ≡ bool→F₂ (signW (coxeter-complete (decode l) (decode-is-perm l)))
tower-sign-is-length l =
  cong bool→F₂ (sign-wd (coxeter-complete (decode l) (decode-is-perm l)))

------------------------------------------------------------------------
-- ◆ip-invcount-recurrence — the ℕ-EXACT single-insertion inversion count.
-- Route A re-run at ℕ (sum, not xor): the count of tail entries below p is
-- permutation-invariant, hence = its value on id-perm = toℕ p.
------------------------------------------------------------------------

-- a + (b + c) ≡ b + (a + c) — the summand swap that adjacent transposition uses
-- (private: a local ℕ helper; NOT the F₂ `+-swap` of Algebra/F2/Linear/Cycle3).
private
  +-swap : (a b c : ℕ) → a + (b + c) ≡ b + (a + c)
  +-swap a b c =
    trans (sym (+-assoc a b c)) (trans (cong (_+ c) (+-comm a b)) (+-assoc b a c))

-- countLess is invariant under an adjacent swap (addition is commutative).
countLess-swap : {m k : ℕ} (x : Fin m) (j : Fin k) (v : Vec (Fin m) (suc k)) →
                 countLess x (swapAdj j v) ≡ countLess x v
countLess-swap x zero    (a ∷ b ∷ zs) =
  +-swap (boolToℕ (finLt b x)) (boolToℕ (finLt a x)) (countLess x zs)
countLess-swap x (suc j) (a ∷ xs)     =
  cong (boolToℕ (finLt a x) +_) (countLess-swap x j xs)

-- the punchIn-relabelled count G p — the ℕ twin of Route A's F p.
G : {m : ℕ} (p : Fin (suc m)) → Perm m → ℕ
G p v = countLess p (map (punchIn p) v)

-- G invariant under an adjacent swap of the base.
G-swap : {m : ℕ} (p : Fin (suc m)) {k : ℕ} (j : Fin k) (v : Vec (Fin m) (suc k)) →
         countLess p (map (punchIn p) (swapAdj j v)) ≡ countLess p (map (punchIn p) v)
G-swap p j v =
  trans (cong (countLess p) (map-swapAdj (punchIn p) j v))
        (countLess-swap p j (map (punchIn p) v))

-- G invariant under right-composition by ANY Coxeter word (a permutation).
G-mult : {m : ℕ} (p : Fin (suc m)) (v : Perm m) {τ : Perm m} →
         CoxGen τ → G p (compose v τ) ≡ G p v
G-mult p v cox-id      = cong (G p) (compose-id-right v)
G-mult p v (cox-s j)   = trans (cong (G p) (bridge v j)) (G-swap p j v)
G-mult p v (cox-∘ {σ = σ'} {τ = τ'} g h) =
  trans (cong (G p) (sym (compose-assoc v σ' τ')))
        (trans (G-mult p (compose v σ') h) (G-mult p v g))

-- the ℕ count over id-perm, given the bound t ≤ m, is exactly t.
countBelowN : (t : ℕ) {m k : ℕ} → Vec (Fin m) k → ℕ
countBelowN t []       = 0
countBelowN t (x ∷ xs) = boolToℕ (toℕ x <ᵇ t) + countBelowN t xs

countBelowN-zero : {m k : ℕ} (v : Vec (Fin m) k) → countBelowN zero v ≡ zero
countBelowN-zero []       = refl
countBelowN-zero (x ∷ xs) = countBelowN-zero xs

countBelowN-map-suc : (t : ℕ) {m k : ℕ} (v : Vec (Fin m) k) →
                      countBelowN (suc t) (map suc v) ≡ countBelowN t v
countBelowN-map-suc t []       = refl
countBelowN-map-suc t (x ∷ xs) =
  cong (boolToℕ (toℕ x <ᵇ t) +_) (countBelowN-map-suc t xs)

countBelowN-exact : (t m : ℕ) → t ≤ m → countBelowN t (id-perm m) ≡ t
countBelowN-exact zero    m       le       = countBelowN-zero (id-perm m)
countBelowN-exact (suc t) zero    ()
countBelowN-exact (suc t) (suc m) (s≤s le) =
  trans (cong (countBelowN (suc t) {suc m} {suc m}) id-perm-cons)
        (cong suc (trans (countBelowN-map-suc t (id-perm m)) (countBelowN-exact t m le)))

-- countLess p ∘ map (punchIn p) IS the ℕ count at bound toℕ p (via punchIn-lt).
countLess-bridge : {m k : ℕ} (p : Fin (suc m)) (v : Vec (Fin m) k) →
                   countLess p (map (punchIn p) v) ≡ countBelowN (toℕ p) v
countLess-bridge p []       = refl
countLess-bridge p (x ∷ xs) =
  cong₂ _+_ (cong boolToℕ (punchIn-lt p x)) (countLess-bridge p xs)

countLess-id : {m : ℕ} (p : Fin (suc m)) →
               countLess p (map (punchIn p) (id-perm m)) ≡ toℕ p
countLess-id {m} p =
  trans (countLess-bridge p (id-perm m)) (countBelowN-exact (toℕ p) m (toℕ≤m p))

-- the exact count-below: for a perm σ, #{tail entries < p} = toℕ p.
countLess-exact : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ →
                  countLess p (map (punchIn p) σ) ≡ toℕ p
countLess-exact {m} p σ pf =
  trans (cong (G p) (sym (compose-id-left σ)))
        (trans (G-mult p (id-perm m) (coxeter-complete σ pf)) (countLess-id p))

-- the punchIn relabel preserves the ℕ inversion count.
countLess-punchIn : {m k : ℕ} (p : Fin (suc m)) (x : Fin m) (v : Vec (Fin m) k) →
                    countLess (punchIn p x) (map (punchIn p) v) ≡ countLess x v
countLess-punchIn p x []       = refl
countLess-punchIn p x (y ∷ ys) =
  cong₂ _+_ (cong boolToℕ (finLt-punchIn p y x)) (countLess-punchIn p x ys)

invCount-map-punchIn : {m k : ℕ} (p : Fin (suc m)) (v : Vec (Fin m) k) →
                       invCount (map (punchIn p) v) ≡ invCount v
invCount-map-punchIn p []       = refl
invCount-map-punchIn p (x ∷ xs) =
  cong₂ _+_ (countLess-punchIn p x xs) (invCount-map-punchIn p xs)

-- THE RECURRENCE: inserting value p at the front adds exactly toℕ p inversions.
invcount-insert : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ →
                  invCount (insert-at p σ) ≡ toℕ p + invCount σ
invcount-insert p σ pf =
  cong₂ _+_ (countLess-exact p σ pf) (invCount-map-punchIn p σ)

------------------------------------------------------------------------
-- ◆ip-chirality-apex — THE COVER = the two cross-linking TERMS above
-- (tower-sign-is-invcount + tower-sign-is-length), which meet the flagship
-- terms sign-as-parity (Chirality) and sign-wd (the ℤ/2 well-defined). The
-- cover is PURE PROOF, NOT a record: a record fielding these proofs would drag
-- proof-module imports into a def-provider (def/proof-separation), and it would
-- add no content over the terms — exactly why Chirality itself "declares no
-- record". The graded sign coordinate agreeing with both static guises IS the
-- pair of terms; no bundling is needed or wanted.
------------------------------------------------------------------------
