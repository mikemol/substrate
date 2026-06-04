------------------------------------------------------------------------
-- Substrate.WitnessTower.Hodge
--
-- BUILD (not assert) the narration's claim: the witness is the Hodge
-- dual of the simplex below it.
--
-- The Hodge star pairs graded pieces Λᵏ ↔ Λⁿ⁻ᵏ in an ambient dimension n
-- (Substrate.Category.GenericHodgeStar). For the witness-tower whose top
-- rung is the tetrahedron, the ambient simplex has n = 3 (a 3-simplex;
-- its faces are the rungs 0..3). A rung-k face and its WITNESS are
-- Hodge-dual when their grades sum to the ambient: k and (n−k) are
-- ★-paired. This file builds that pairing at the rung-INDEX level, where
-- it is provable by computation, and connects the load-bearing
-- middle-grade rung to the existing concrete Hodge ★ on bivectors.
--
-- Scope honesty: the rung-index duality (dual-rung, involution) is built
-- and proved here. The identification of the rung-1 ↔ rung-2 (witness ↔
-- triangle) pairing with the substrate's grade-2 bivector ★ is recorded
-- as the bridge to discharge against HodgeDim4.HodgeStar — that ★ is on
-- Λ²(F₂⁴) (the (4 choose 2)=6 bivectors), the SELF-dual middle grade,
-- which is a DIFFERENT ambient (n=4) than the tetrahedron's n=3. That
-- mismatch is a real finding, surfaced not smoothed (see §3).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Hodge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc; fromℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)

------------------------------------------------------------------------
-- 1. Rung grades of the ambient n-simplex: a face has a grade in
--    Fin (suc n) (0 = empty/point-witness end, n = full simplex). The
--    Hodge dual of grade k is grade n−k, given as a STRUCTURAL involution
--    on Fin (suc n) — built for EVERY ambient n, not just the tetrahedron.
--
--    This is the narration's grade spine, founded from the bottom:
--    "In the beginning there was nothing; then came the first point, which
--     witnessed the universe (nothing else to differentiate against)."
--    That first point is the n=0 ambient — Fin 1, one grade — and it is
--    its OWN Hodge dual (`dual-grade-point`): the FIRST ★. Each climb to
--    ambient n+1 wraps a fresh (Λ⁰, Λⁿ⁺¹) dual pair — the new point and
--    the new simplex, the two ends that "both witness the universe" —
--    around the prior simplex, which becomes an interior face. The clean
--    involution lives at the GRADE-LABEL level; the cell COUNTS behind the
--    grades (Δ³: 4 vertices, 6 edges, 4 faces, 1 cell) are NOT label-
--    symmetric — that divergence (6 edges vs 4 faces) is the grading
--    boundary made manifest, the very thing this spine traces by climbing
--    from the point (where label and cell coincide) upward. See §3.
------------------------------------------------------------------------

-- inject a grade as the non-top end of the next ambient (Λᵏ ↪ Λᵏ at n+1).
inject₁ : {n : ℕ} → Fin n → Fin (suc n)
inject₁ zero    = zero
inject₁ (suc i) = suc (inject₁ i)

-- the Hodge dual at the grade level in ambient n: k ↦ n − k.
-- dual-grade 0 = id (the self-dual point); each suc wraps the prior dual
-- inside inject₁, so the top grade (fromℕ n) pairs with the point (zero).
dual-grade : (n : ℕ) → Fin (suc n) → Fin (suc n)
dual-grade n       zero    = fromℕ n
dual-grade (suc m) (suc i) = inject₁ (dual-grade m i)

-- the top grade Λⁿ is the dual of the point Λ⁰ (the (point, simplex) pair).
dual-grade-fromℕ : (n : ℕ) → dual-grade n (fromℕ n) ≡ zero
dual-grade-fromℕ zero    = refl
dual-grade-fromℕ (suc m) = cong inject₁ (dual-grade-fromℕ m)

-- dual commutes with the non-top embedding: the spine respects the climb.
dual-grade-inject₁ : (n : ℕ) (i : Fin (suc n)) →
                     dual-grade (suc n) (inject₁ i) ≡ suc (dual-grade n i)
dual-grade-inject₁ n       zero    = refl
dual-grade-inject₁ (suc m) (suc i) = cong inject₁ (dual-grade-inject₁ m i)

-- THE GENERAL INVOLUTION: ★★ = id in every ambient n — the narration's
-- "the witness of a witness returns the simplex", at every rung at once.
dual-grade-involution : (n : ℕ) (i : Fin (suc n)) →
                        dual-grade n (dual-grade n i) ≡ i
dual-grade-involution n       zero    = dual-grade-fromℕ n
dual-grade-involution (suc m) (suc i) =
  trans (dual-grade-inject₁ m (dual-grade m i))
        (cong suc (dual-grade-involution m i))

-- THE FIRST POINT IS THE FIRST ★: ambient n=0 has one grade, self-dual.
-- "There was nothing else to differentiate against." Proved by refl.
dual-grade-point : dual-grade 0 zero ≡ zero
dual-grade-point = refl

-- The tetrahedron (n=3) is now an INSTANCE of the general spine, not a
-- parallel definition: k ↦ 3−k. dual-grade 3 computes to Λ⁰↔Λ³, Λ¹↔Λ².
dual-grade₃ : Fin 4 → Fin 4
dual-grade₃ = dual-grade 3

-- The involution at n=3 is the general lemma specialised — the four refl
-- cases collapse into `dual-grade-involution 3`.
dual-grade₃-involution : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
dual-grade₃-involution = dual-grade-involution 3

------------------------------------------------------------------------
-- 2. The witness pairing. In the n=3 ambient the witnessing step pairs a
--    rung-k face with its dual rung-(3−k): the WITNESS of grade k sits at
--    grade 3−k. Λ⁰↔Λ³ (point-witness ↔ whole tetrahedron) and Λ¹↔Λ²
--    (edge ↔ triangle) are the two ★-pairs; there is no fixed grade
--    (3 is odd → no self-dual middle), so every face has a DISTINCT
--    witness grade. This is built, not claimed: `witness-grade` and its
--    "distinct from its source" property below.
------------------------------------------------------------------------

witness-grade : Fin 4 → Fin 4
witness-grade = dual-grade₃

-- No grade is its own witness (n=3 odd ⇒ ★ has no fixed point): proved
-- by computation. (Contrast n=4, where grade 2 is self-dual — that is
-- the bivector ★ in §3, a genuinely different ambient.)
witness-distinct : (i : Fin 4) → (dual-grade₃ i ≡ i) → Fin 0
witness-distinct zero                   ()
witness-distinct (suc zero)             ()
witness-distinct (suc (suc zero))       ()
witness-distinct (suc (suc (suc zero))) ()

------------------------------------------------------------------------
-- 3. BRIDGE TO THE CONCRETE ★ (open seam, stated precisely).
--
-- The substrate's concrete Hodge ★ (HodgeDim4.HodgeStar.hodge-star) is
--   ★ : Linear 6 6   on Λ²(F₂⁴) — the 6 bivectors — at ambient n = 4,
-- the SELF-DUAL middle grade (Λ² ↔ Λ⁴⁻² = Λ²). That is the n=4 story
-- (the tetrahedron-algebra / dossier §6), distinct from this file's n=3
-- face-grade duality. The two are NOT the same ★: n=3 has no self-dual
-- grade (witness-distinct), n=4's grade-2 is entirely self-dual.
--
-- So the narration "witness = Hodge dual of the simplex below" holds at
-- the GRADE-INDEX level here (built, dual-grade₃-involution), but the
-- specific concrete ★ in the tree is the n=4 bivector star, which
-- realises a DIFFERENT pairing (the self-dual 6 = 3+3 split). Reconciling
-- "which ambient n indexes the witness-tower" is the genuine open
-- question — surfaced, not papered over.
------------------------------------------------------------------------
