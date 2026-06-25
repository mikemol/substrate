------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary
--
-- Ⓝ.homology (keystone increment) — the SIMPLICIAL IDENTITY, the combinatorial
-- core of the boundary chain complex ∂_k : C_k → C_{k−1}. The substrate already
-- has the FACE OBJECTS (WitnessTower.FaceSet: faces ARE F₂-vectors), the f-vector
-- COUNTS (WitnessTower.FaceCount: `faces n k`), and the F₂ COCHAIN coboundary
-- δ²=0 (CayleyDickson.Coboundary.d²-zero — "each value occurs twice, the
-- simplicial face-pairing, cancels over F₂"). What was MISSING is the CHAIN-side
-- boundary on ordered faces. This builds its load-bearing law.
--
-- A k-simplex is an ORDERED list of its vertices; `delAt i` is the i-th face map
-- (drop the i-th vertex). The SIMPLICIAL IDENTITY
--
--     delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs)        (for i ≤ j)
--
-- is the classic d_i ∘ d_j = d_{j−1} ∘ d_i (i < j). It is EXACTLY what ∂∘∂ = 0
-- reduces to: in ∂(∂ σ) every codim-2 face (drop the pair {i, j}) is reached
-- TWICE — once as (i, suc j), once as (j, i) — and the identity says those two
-- routes land on the SAME face, so with the alternating signs they cancel in
-- pairs. Proven here with NO Fin-index juggling and NO ℤ-module: ordered faces as
-- `List`, positions as ℕ (out-of-range deletion is identity), the i≤j case the
-- only live one (i>j is the symmetric statement).
--
-- SCOPED OUT (the named next increments of Ⓝ.homology, see scratch/
-- formalizable_gaps.md): the SIGNED ℤ-chain ∂ = Σᵢ (−1)ⁱ delAt i and ∂∘∂ ≡ 0 as
-- a chain equation (needs the free ℤ-module on faces); `ker ∂_k` (the k-cycles);
-- and the projected permutation rep on `ker ∂_k` with the ARITY CLIMB (v_p(disc)
-- climbs with face-dimension, f085). This increment is the combinatorial keystone
-- all of those rest on.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; z≤n; s≤s)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)

private
  variable
    A : Set

------------------------------------------------------------------------
-- 1. The i-th face map: delete the vertex at position i (total; an
--    out-of-range position deletes nothing).
------------------------------------------------------------------------

delAt : ℕ → List A → List A
delAt _       []       = []
delAt zero    (_ ∷ xs) = xs
delAt (suc n) (x ∷ xs) = x ∷ delAt n xs

------------------------------------------------------------------------
-- 2. THE SIMPLICIAL IDENTITY (the keystone): for i ≤ j, deleting the later
--    vertex first (at suc j) then the earlier (at i) equals deleting the
--    earlier first (at i) then the later (now shifted down to j).
------------------------------------------------------------------------

simplicial : (i j : ℕ) → i ≤ j → (xs : List A) →
             delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs)
simplicial i       j       _       []       = refl
simplicial zero    j       _       (x ∷ xs) = refl
simplicial (suc i) (suc j) (s≤s p) (x ∷ xs) = cong (x ∷_) (simplicial i j p xs)

------------------------------------------------------------------------
-- 3. The (unsigned) boundary: the list of all codim-1 faces, one per vertex.
--    `boundary (x ∷ xs)` = the face dropping x (= xs), then x coned onto every
--    face of xs — i.e. exactly { delAt j (x ∷ xs) : j }.
------------------------------------------------------------------------

-- cone a vertex onto every face (self-contained; Foundation.List defers map).
consAll : A → List (List A) → List (List A)
consAll x []       = []
consAll x (f ∷ fs) = (x ∷ f) ∷ consAll x fs

boundary : List A → List (List A)
boundary []       = []
boundary (x ∷ xs) = xs ∷ consAll x (boundary xs)

-- a k-simplex (k+1 vertices) has exactly k+1 codim-1 faces — the f-vector edge
-- of WitnessTower.FaceCount (the faces of a face = its vertices).
private
  len : {B : Set} → List B → ℕ
  len []       = zero
  len (_ ∷ xs) = suc (len xs)

  consAll-len : (x : A) (fs : List (List A)) → len (consAll x fs) ≡ len fs
  consAll-len x []       = refl
  consAll-len x (f ∷ fs) = cong suc (consAll-len x fs)

boundary-length : (xs : List A) → len (boundary xs) ≡ len xs
boundary-length []       = refl
boundary-length (x ∷ xs) =
  cong suc (trans (consAll-len x (boundary xs)) (boundary-length xs))
