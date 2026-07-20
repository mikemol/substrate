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
open import Substrate.Foundation.Bool using (Bool; true; false; boolToℕ; _xor_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.FromBool using (bool→F₂)
open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.Algebra.Wedge.Graded.Morphism using (GradedDivStrMorphism; comp-gdsm; map-C)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; insert-at-preserves)
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
open import Substrate.WitnessTower.LehmerTowerMorphism
  using (lehmer-graded; F₂-target)
open import Substrate.WitnessTower.InsertionParity
  using (finLt-punchIn; punchIn-lt; map-swapAdj; toℕ≤m;
         oddB; signB-insert; sign-lehmer-morphism-unconditional)

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

------------------------------------------------------------------------
-- THE SINGLE-INSERTION SIGN LAW, as a TOTAL DICHOTOMY (not a ¬∀ quantification):
-- the circumstance where it HOLDS, the circumstance where it FAILS, and the two
-- combined are TOTAL — via decidability (Bool has decidable equality; Dec/Set₀,
-- our set₁-avoiding machinery). The bare carrier Perm n = Vec (Fin n) n includes
-- NON-permutations; the law is base-dependent there, base-independent (= the
-- digit parity) exactly on permutations.
------------------------------------------------------------------------

-- the law equation at (p, σ) — a Bool equality, so Set₀ (a …→Set family, uncounted).
insert-parity-law : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → Set
insert-parity-law p σ = sign (insert-at p σ) ≡ (oddB (toℕ p) xor sign σ)

-- CIRCUMSTANCE 1 — it HOLDS when σ is a permutation (Route A / Route B).
holds-on-perm : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ → insert-parity-law p σ
holds-on-perm = signB-insert

-- CIRCUMSTANCE 2 — it FAILS off permutations: a concrete non-perm witness
-- (σ = zero ∷ zero ∷ [] ∉ IsPerm, p = suc zero): sign = false, oddB 1 xor false = true.
σ-nonperm : Perm 2
σ-nonperm = zero ∷ zero ∷ []

fails-off-perm : ¬ insert-parity-law (suc zero) σ-nonperm
fails-off-perm ()

-- the two circumstances are TOTAL: the law is DECIDABLE at every (p, σ), so
-- holds ⊎ ¬holds is exhaustive by construction — no quantified negative needed.
private
  _≟B_ : (a b : Bool) → Dec (a ≡ b)
  true  ≟B true  = yes refl
  true  ≟B false = no (λ ())
  false ≟B true  = no (λ ())
  false ≟B false = yes refl

insert-parity-dec : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → Dec (insert-parity-law p σ)
insert-parity-dec p σ = sign (insert-at p σ) ≟B (oddB (toℕ p) xor sign σ)

------------------------------------------------------------------------
-- ◆ip-general-signW — proven, not pre-judged. For ANY perm σ, the Coxeter-length
-- parity signW of a completed derivation of insert-at p σ equals the sign fact
-- (= sym sign-wd ∘ signB-insert). Committed so the shape-DB can find a twin — if
-- one exists, that IS the "second construction" the filing worry denied.
------------------------------------------------------------------------

general-signW : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) (pf : IsPerm σ) →
  signW (coxeter-complete (insert-at p σ) (insert-at-preserves p σ pf))
    ≡ (oddB (toℕ p) xor sign σ)
general-signW p σ pf =
  trans (sym (sign-wd (coxeter-complete (insert-at p σ) (insert-at-preserves p σ pf))))
        (signB-insert p σ pf)

------------------------------------------------------------------------
-- THE Fₙ PICTURE — the sign (F₂) is the mod-2 shadow of a UNIVERSAL ℕ (= F_∞)
-- cocycle, and Route A (inversion count) is that universal object while Route B
-- (the sign homomorphism) is F₂-terminal. This dissolves the "no tower→F₂
-- composition": it composes — through ℕ, not through the bare tower.
------------------------------------------------------------------------

-- the additive-ℕ graded target (F_∞: mirror F₂-target at ℕ; reduces to every Fₙ).
ℕ⁺-target : GradedDivStr (λ _ → ℕ) (λ _ → ℕ)
ℕ⁺-target = record { recon = λ n b r → r + b }

-- ROUTE A as a genuine ℕ-graded morphism out of the Lehmer tower — inserting
-- digit p adds toℕ p inversions (invcount-insert). The universal count cocycle.
invcount-graded : GradedDivStrMorphism lehmer-graded ℕ⁺-target
invcount-graded = record
  { map-C          = λ l → invCount (decode l)
  ; map-R          = toℕ
  ; respects-recon = λ n l p → invcount-insert p (decode l) (decode-is-perm l)
  }

-- mod-2: parity IS a graded morphism ℕ⁺-target → F₂-target (parity-+). The n=2
-- reduction; the analogous mod-n reduction exists for every n (Route A lifts to
-- all Fₙ) — but there is NO mod-n SIGN for n>2 (Sₙ's abelianisation is Z/2), so
-- Route B is F₂-terminal. That asymmetry is the retained route-distinction, sharp.
mod2-graded : GradedDivStrMorphism ℕ⁺-target F₂-target
mod2-graded = record
  { map-C = parity ; map-R = parity ; respects-recon = λ n b r → parity-+ r b }

-- THE FACTORIZATION (◆ip-tower-f2-compose, dissolved through ℕ): the twisted F₂
-- sign-morphism is the mod-2 of the universal ℕ inversion-count morphism — a
-- SECOND construction of it, via comp-gdsm, distinct from Route B's sign-hom one.
sign-lehmer-via-invcount : GradedDivStrMorphism lehmer-graded F₂-target
sign-lehmer-via-invcount = comp-gdsm mod2-graded invcount-graded

-- the two constructions of the twisted sign-morphism (Route B directly; Route A
-- through the ℕ count) AGREE on carriers — sign-as-parity, i.e. tower-sign-is-
-- invcount. Two graded morphisms, one F₂ cocycle: the content-cover route-
-- agreement wanted, now at the intermediate (count) level, not F₂-UIP.
sign-two-constructions-agree : {n : ℕ} (l : LehmerPath n) →
  map-C sign-lehmer-morphism-unconditional l ≡ map-C sign-lehmer-via-invcount l
sign-two-constructions-agree l = tower-sign-is-invcount l
