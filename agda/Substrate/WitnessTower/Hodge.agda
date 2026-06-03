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
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- 1. Rung grades of the ambient n-simplex: a face has a grade in
--    Fin (suc n) (0 = empty/point-witness end, n = full simplex). The
--    Hodge dual of grade k is grade n−k, given as a concrete involution
--    on Fin (suc n). We build it for the tetrahedron (n = 3): grades
--    0,1,2,3 with dual 3,2,1,0.
------------------------------------------------------------------------

-- dual grade in the n=3 ambient (the tetrahedron's faces): k ↦ 3−k.
dual-grade₃ : Fin 4 → Fin 4
dual-grade₃ zero                = suc (suc (suc zero))   -- Λ⁰ ↔ Λ³
dual-grade₃ (suc zero)          = suc (suc zero)         -- Λ¹ ↔ Λ²
dual-grade₃ (suc (suc zero))    = suc zero               -- Λ² ↔ Λ¹
dual-grade₃ (suc (suc (suc zero))) = zero                -- Λ³ ↔ Λ⁰

-- The duality is an involution: ★★ = id at the grade level. Proved by
-- computation on all 4 grades — this is the narration's "witness of a
-- witness returns the simplex" at the index level.
dual-grade₃-involution : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
dual-grade₃-involution zero                      = refl
dual-grade₃-involution (suc zero)                = refl
dual-grade₃-involution (suc (suc zero))          = refl
dual-grade₃-involution (suc (suc (suc zero)))    = refl

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
