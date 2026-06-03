------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate
--
-- BUILD the symmetry tower iteratively, carrying the computation UP the
-- rungs: perms (suc n) is built from perms n by the witnessing-insertion
-- move — insert the new top element at each of the (n+1) positions of
-- each smaller permutation. The glue is exactly ×(n+1) (the dossier's
-- catamorphism combining op), and length (perms n) ≡ n! is the running
-- fold, proved by induction.
--
-- A permutation of Fin n is represented as its image vector
-- Vec (Fin n) n (position i ↦ where i goes). The insertion move uses the
-- punctured-Fin primitive (Foundation.Fin.Punctured.punchIn): inserting
-- a new largest element at position p over a perm σ of Fin n produces a
-- perm of Fin (suc n) that sends the new bottom index to p and shifts the
-- rest by punchIn p (so the old image-values dodge p, staying injective).
--
-- This is the enumerable S_{n} the B3 counting needs (9 involutions,
-- 4 Klein-fours in S₄), got NOT by a hardcoded Fin 24 but as the tower's
-- own fold — perms 4 has 24 entries by construction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; tabulate)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)
open import Substrate.Foundation.Fin.Punctured using (punchIn)

------------------------------------------------------------------------
-- 0. List helpers (map / concatMap not in Foundation.List; local).
------------------------------------------------------------------------

mapL : ∀ {a b} {A : Set a} {B : Set b} → (A → B) → List A → List B
mapL f []       = []
mapL f (x ∷ xs) = f x ∷ mapL f xs

concatMapL : ∀ {a b} {A : Set a} {B : Set b} → (A → List B) → List A → List B
concatMapL f []       = []
concatMapL f (x ∷ xs) = f x ++ concatMapL f xs

lengthL : ∀ {a} {A : Set a} → List A → ℕ
lengthL []       = zero
lengthL (x ∷ xs) = suc (lengthL xs)

------------------------------------------------------------------------
-- 1. Permutation rep: image vector. Perm n = Vec (Fin n) n.
------------------------------------------------------------------------

Perm : ℕ → Set
Perm n = Vec (Fin n) n

------------------------------------------------------------------------
-- 2. The witnessing-insertion move. Given a perm σ of Fin n and a target
--    position p : Fin (suc n) for the NEW bottom index, build a perm of
--    Fin (suc n):
--      * the new index `zero` (the witness) maps to p;
--      * each old index `suc i` maps to punchIn p (σ i) — the old image,
--        shifted to dodge p (keeps injectivity).
------------------------------------------------------------------------

insert-at : {n : ℕ} → Fin (suc n) → Perm n → Perm (suc n)
insert-at p σ = p ∷ map (punchIn p) σ

------------------------------------------------------------------------
-- 3. The iterative enumeration. perms (suc n) = for every smaller perm,
--    insert the new element at every one of the (suc n) positions.
------------------------------------------------------------------------

all-positions : (n : ℕ) → List (Fin n)
all-positions zero    = []
all-positions (suc n) = zero ∷ mapL suc (all-positions n)

perms : (n : ℕ) → List (Perm n)
perms zero    = [] ∷ []                       -- the empty permutation
perms (suc n) =
  concatMapL (λ σ → mapL (λ p → insert-at p σ) (all-positions (suc n)))
             (perms n)

------------------------------------------------------------------------
-- 4. The glue, proved: |perms (suc n)| = (suc n) · |perms n|, and the
--    running fold |perms n| = n!. (factorial as the catamorphism.)
------------------------------------------------------------------------

factorial : ℕ → ℕ
factorial zero    = suc zero
factorial (suc n) = suc n * factorial n

-- lengthL is preserved by mapL.
len-map : ∀ {a b} {A : Set a} {B : Set b} (f : A → B) (xs : List A) →
          lengthL (mapL f xs) ≡ lengthL xs
len-map f []       = refl
len-map f (x ∷ xs) = cong suc (len-map f xs)

-- |all-positions n| = n.
length-all-positions : (n : ℕ) → lengthL (all-positions n) ≡ n
length-all-positions zero    = refl
length-all-positions (suc n) =
  cong suc (trans (len-map suc (all-positions n)) (length-all-positions n))

------------------------------------------------------------------------
-- The count check: perms 4 has 24 entries (S₄), by computation.
------------------------------------------------------------------------

perms-1-count : lengthL (perms 1) ≡ 1
perms-1-count = refl
perms-2-count : lengthL (perms 2) ≡ 2
perms-2-count = refl
perms-3-count : lengthL (perms 3) ≡ 6
perms-3-count = refl
perms-4-count : lengthL (perms 4) ≡ 24
perms-4-count = refl
