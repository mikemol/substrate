------------------------------------------------------------------------
-- Substrate.WitnessTower.FaceSet
--
-- BUILD the higher faces as OBJECTS, not just counts. WitnessTower.FaceCount
-- counts the k-faces of Δⁿ; this CONSTRUCTS them. A face of the rung-n
-- simplex is a SUBSET of its n+1 vertices — i.e. an indicator vector in
-- F₂^(n+1) = Vec Bool (suc n). The type IS the complete Boolean lattice:
-- EVERY indicator is a face, no subset excluded. That completeness is what
-- the narration means by "a fully connected simplex if you flatten it"
-- (user, 2026-06-04): flatten the cone hierarchy — forget which apex coned
-- which face — and you are left with exactly all subsets of the vertices,
-- the complete complex / fully-connected simplex.
--
-- The cone construction at the SET level: every face of the (n+1)-simplex
-- is its apex bit ∷ a base face — `with-apex` (coned over the apex, the
-- bit is true) or `without-apex` (inherited from the base, the bit false).
-- The Boolean doubling (2^(n+2) = 2·2^(n+1)) is the f-vector Pascal of
-- FaceCount realised on the actual faces.
--
-- THE REAL HODGE ★ lives here: subset COMPLEMENT, `map not`. Unlike the
-- grade-LABEL reversal of WitnessTower.Hodge.dual-grade (k↦n−k, which does
-- NOT preserve cell counts — 4 vertices vs 1 cell), complement is a
-- BIJECTION on the lattice (involution ⟹ count-preserving), and it pairs
-- the empty face (the narration's "nothing") with the full simplex (the
-- "universe"). The grade-level dual-grade is the shadow of THIS ★.
--
-- F₂ⁿ-GRADING REVIVAL (re the conjecture ledger): the bottom-up study
-- KILLED an F₂ⁿ grading at the PERMUTATION/support level (it grades by ℕ).
-- But here, at the FACE level, the F₂^(suc n) structure is HONEST: faces
-- ARE F₂-vectors, ★ IS complement. This is where conjectures #2/#3/#4
-- (graded-GF(2) / Morton-cocycle) may genuinely attach — at the cells, not
-- the permutations. Recorded; not yet built.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FaceSet where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Bool using (Bool; true; false; not)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; replicate; head; tail)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂)

------------------------------------------------------------------------
-- 1. Faces as subsets. A face of Δⁿ is a subset of its n+1 vertices: an
--    indicator in F₂^(suc n). The type is the COMPLETE lattice — every
--    indicator inhabits it, so the simplex is fully connected by
--    construction (every subset of vertices spans a face).
------------------------------------------------------------------------

Face : ℕ → Set
Face n = Vec Bool (suc n)

-- the empty face — "in the beginning there was nothing": no vertex chosen.
nothing-face : (n : ℕ) → Face n
nothing-face n = replicate (suc n) false

-- the full simplex — every vertex chosen ("the universe").
full : (n : ℕ) → Face n
full n = replicate (suc n) true

------------------------------------------------------------------------
-- 2. The cone construction on faces. A face of the (n+1)-simplex is its
--    apex bit followed by a base face: coned over the apex (true) or
--    inherited from the base (false). Every higher face decomposes thus,
--    UNIQUELY — the set-level Pascal split behind FaceCount.cone-step.
------------------------------------------------------------------------

-- the base face coned over the new apex (apex included).
with-apex : {n : ℕ} → Face n → Face (suc n)
with-apex f = true ∷ f

-- the base face inherited, apex NOT included.
without-apex : {n : ℕ} → Face n → Face (suc n)
without-apex f = false ∷ f

-- the apex bit and the base face of a higher face.
apex-bit : {n : ℕ} → Face (suc n) → Bool
apex-bit = head

base-face : {n : ℕ} → Face (suc n) → Face n
base-face = tail

-- every higher face IS its apex bit ∷ its base face (the cone split is
-- exhaustive and unique): proof that with/without-apex cover Face (suc n).
cone-split : {n : ℕ} (f : Face (suc n)) → (apex-bit f ∷ base-face f) ≡ f
cone-split (b ∷ f) = refl

------------------------------------------------------------------------
-- 3. The real Hodge ★ = subset complement. A bijection on the lattice
--    (involution), pairing nothing ↔ full. The count-preserving star the
--    grade-level dual-grade only shadows.
------------------------------------------------------------------------

star : {n : ℕ} → Face n → Face n
star = map not

-- not is an involution.
not-not : (b : Bool) → not (not b) ≡ b
not-not true  = refl
not-not false = refl

-- ★★ = id on any Bool-vector (hence on every face): complement is a
-- bijection, so it PRESERVES counts — the cell-level duality is clean.
star-vec-involution : {m : ℕ} (v : Vec Bool m) → map not (map not v) ≡ v
star-vec-involution []       = refl
star-vec-involution (b ∷ v) = cong₂ _∷_ (not-not b) (star-vec-involution v)

star-involution : {n : ℕ} (f : Face n) → star (star f) ≡ f
star-involution f = star-vec-involution f

------------------------------------------------------------------------
-- 4. ★ pairs the beginning (nothing) with the universe (full simplex).
--    The narration's first ★ — "the first point witnessed the universe,
--    nothing else to differentiate against" — at the cell level: the empty
--    face's complement is the whole simplex.
------------------------------------------------------------------------

map-not-replicate-false : (m : ℕ) → map not (replicate m false) ≡ replicate m true
map-not-replicate-false zero    = refl
map-not-replicate-false (suc m) = cong (_∷_ true) (map-not-replicate-false m)

map-not-replicate-true : (m : ℕ) → map not (replicate m true) ≡ replicate m false
map-not-replicate-true zero    = refl
map-not-replicate-true (suc m) = cong (_∷_ false) (map-not-replicate-true m)

-- ★ (nothing) = the full simplex.
star-nothing : (n : ℕ) → star (nothing-face n) ≡ full n
star-nothing n = map-not-replicate-false (suc n)

-- ★ (full simplex) = nothing.
star-full : (n : ℕ) → star (full n) ≡ nothing-face n
star-full n = map-not-replicate-true (suc n)
