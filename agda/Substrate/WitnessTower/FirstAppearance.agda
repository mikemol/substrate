------------------------------------------------------------------------
-- Substrate.WitnessTower.FirstAppearance
--
-- "Objects make a first-appearance at a given rung; identifying WHERE
--  reveals the inductive step's structure."
--
-- Running the iterated enumeration (WitnessTower.Enumerate.perms) up the
-- tower and CLASSIFYING each permutation by its cycle-type lets us read
-- off, per rung, which structural objects newly become realizable. The
-- signal that pins the inductive step is the involution census split by
-- MOVED-POINT COUNT (= twice the number of 2-cycles):
--
--   rung n   |Sₙ|   involutions   moved-2 (transposition)   moved-4 ((2,2))
--   ----------------------------------------------------------------------
--     2        2         1                 1                      0
--     3        6         3                 3                      0
--     4       24         9                 6                      3   ← debut
--
-- The "moved-4" column is EMPTY until rung 4 and then equals 3 — and those
-- 3 double-transpositions are exactly the non-identity elements of the
-- normal gauge V₄ (the dossier's B3). So the inductive step n→n+1 is "which
-- cycle-types newly fit": a (2,2) needs 4 points, hence the gauge V₄ cannot
-- exist below rung 4. Each count below is a refl over the enumeration — the
-- census is COMPUTED, not asserted.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FirstAppearance where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_) renaming (_≟_ to _≟ℕ_)
open import Substrate.Foundation.Fin using (Fin; zero; suc; _≟_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_; not; if_then_else_)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.WitnessTower.Enumerate
  using (Perm; perms; mapL; lengthL; all-positions)

------------------------------------------------------------------------
-- 0. Local glue: Dec→Bool, List filter / ℕ-sum.
------------------------------------------------------------------------

⌊_⌋ : ∀ {A : Set} → Dec A → Bool
⌊ yes _ ⌋ = true
⌊ no  _ ⌋ = false

filterL : {A : Set} → (A → Bool) → List A → List A
filterL p []       = []
filterL p (x ∷ xs) = if p x then x ∷ filterL p xs else filterL p xs

sumL : List ℕ → ℕ
sumL []       = zero
sumL (x ∷ xs) = x + sumL xs

------------------------------------------------------------------------
-- 1. Permutation arithmetic on the image-vector rep.
------------------------------------------------------------------------

-- identity permutation of Fin n.
id-perm : (n : ℕ) → Perm n
id-perm n = tabulate (λ i → i)

-- composition: (compose σ τ) i = σ (τ i).
compose : {n : ℕ} → Perm n → Perm n → Perm n
compose σ τ = tabulate (λ i → lookup σ (lookup τ i))

-- pointwise Boolean equality of Fin-vectors (the tail of a square Perm
-- is not itself square, so this is generic in both indices).
_≡ᵇ_ : {m n : ℕ} → Vec (Fin m) n → Vec (Fin m) n → Bool
[]      ≡ᵇ []      = true
(x ∷ σ) ≡ᵇ (y ∷ τ) = ⌊ x ≟ y ⌋ ∧ (σ ≡ᵇ τ)

------------------------------------------------------------------------
-- 2. Cycle-type signals.
------------------------------------------------------------------------

-- number of points actually moved by σ (#{ i : σ i ≠ i }).
moved-count : {n : ℕ} → Perm n → ℕ
moved-count {n} σ =
  sumL (mapL (λ i → if ⌊ lookup σ i ≟ i ⌋ then zero else suc zero)
             (all-positions n))

-- σ is an involution: σ∘σ = id and σ ≠ id.
is-involution : {n : ℕ} → Perm n → Bool
is-involution {n} σ =
  (compose σ σ ≡ᵇ id-perm n) ∧ not (σ ≡ᵇ id-perm n)

-- σ is an involution moving exactly `m` points.
is-involution-moving : {n : ℕ} → ℕ → Perm n → Bool
is-involution-moving {n} m σ =
  is-involution σ ∧ ⌊ moved-count σ ≟ℕ m ⌋

------------------------------------------------------------------------
-- 3. The census: counts per rung, each a refl over the enumeration.
------------------------------------------------------------------------

-- total involutions at rung n.
involutions : (n : ℕ) → ℕ
involutions n = lengthL (filterL is-involution (perms n))

-- involutions moving exactly m points at rung n.
involutions-moving : (n m : ℕ) → ℕ
involutions-moving n m = lengthL (filterL (is-involution-moving m) (perms n))

------------------------------------------------------------------------
-- 4. The CENSUS, each line a refl over the iterated enumeration. If any
--    number were wrong the module would not typecheck — these are the
--    computation carried up the tower, not assertions.
------------------------------------------------------------------------

-- Total involutions per rung: 0, 1, 3, 9 (the 0,1,3,9 OEIS telephone /
-- involution sequence — the involutory elements of Sₙ).
census-invol-1 : involutions 1 ≡ 0
census-invol-1 = refl
census-invol-2 : involutions 2 ≡ 1
census-invol-2 = refl
census-invol-3 : involutions 3 ≡ 3
census-invol-3 = refl
census-invol-4 : involutions 4 ≡ 9
census-invol-4 = refl

-- Transpositions (moved-count 2) per rung: 0, 1, 3, 6.
census-moved2-2 : involutions-moving 2 2 ≡ 1
census-moved2-2 = refl
census-moved2-3 : involutions-moving 3 2 ≡ 3
census-moved2-3 = refl
census-moved2-4 : involutions-moving 4 2 ≡ 6
census-moved2-4 = refl

-- Double-transpositions (moved-count 4): ABSENT below rung 4, then 3.
-- THIS is the first-appearance that pins the inductive step — a (2,2)
-- needs 4 points, so the gauge V₄ cannot exist until rung 4.
census-moved4-3-absent : involutions-moving 3 4 ≡ 0
census-moved4-3-absent = refl
census-moved4-4-debut : involutions-moving 4 4 ≡ 3
census-moved4-4-debut = refl

-- The reconciliation: at rung 4, every involution is a transposition or a
-- double-transposition (6 + 3 = 9); the +3 jump over rung 3's involution
-- count is EXACTLY the 3 newly-realizable double-transpositions = the
-- gauge V₄ minus identity (dossier B3).
census-rung4-split : involutions-moving 4 2 + involutions-moving 4 4
                   ≡ involutions 4
census-rung4-split = refl
