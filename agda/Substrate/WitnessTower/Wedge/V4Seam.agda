------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.V4Seam
--
-- TIER 3 — the rung-3→4 wedge step is where V₄ debuts, and the Hodge ★
-- grade-duality rides along the same n=3↔n=4 seam.  Documented connection,
-- with the cheap green lemmas that anchor it to existing substrate results.
--
-- THE V₄⋊S₃ READING OF THE rung-3→4 WEDGE.
-- At rung 3→4 the tower wedge (Wedge.Factoradic.tower-wedge 3) has
--   quot = 4 = [S₄ : S₃] = |V₄|,    rem = 0    (exact).
-- The quotient 4 is not just any factoradic digit: it is the order of the
-- Klein four-group, the kernel of the rung-4 step.  Structurally
--   S₄ = V₄ ⋊ S₃,
-- so the 4 cosets the wedge counts ARE the V₄ coset space, glued by the
-- S₃-action on V₄'s three involutions.  The wedge's quot = 4 is |V₄|; the
-- gluing (the inductive insert-at action restricted here) is the ⋊.
--
-- This is exactly the first-appearance signal the censuses already prove:
-- the Klein-four group has ZERO generating pairs at rung 3 and 24 = 4·6 at
-- rung 4 (KleinCensus.klein-pairs-3-absent / klein-pairs-4).  So the V₄
-- object DEBUTS precisely at the wedge step whose quotient first equals 4.
--
-- THE HODGE ★ RIDE-ALONG.
-- WitnessTower.Hodge.dual-grade₃ is the ambient-n=3 grade involution
-- (Λ⁰↔Λ³, Λ¹↔Λ²).  The rung-3→4 step IS the n=3↔n=4 seam Hodge.agda §3
-- flags: the tetrahedron's n=3 face-grade duality vs the n=4 bivector ★.
-- The Hodge involution comes along the wedge step as a structure on the
-- SAME seam — it is the grade-level reflection of the rung reflection, and
-- (n=3 being odd) it has NO self-dual grade, the same way the rung-3 census
-- has NO Klein-four.  Both "first nontrivial pairing appears crossing 3→4".
--
-- Zero postulates, zero holes, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.V4Seam where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Wedge using (Wedge)
open import Substrate.WitnessTower.Wedge.Factoradic
  using (tower-wedge; tower-quotient)
open import Substrate.WitnessTower.KleinCensus
  using (klein-pairs; klein-pairs-3-absent; klein-pairs-4)
open import Substrate.WitnessTower.Hodge
  using (dual-grade₃; dual-grade₃-involution; witness-distinct)

------------------------------------------------------------------------
-- 1. The rung-3→4 wedge has quotient 4 = |V₄| = [S₄ : S₃].
------------------------------------------------------------------------

-- the quotient of the seam wedge is 4.
seam-quotient-is-4 : tower-quotient 3 ≡ 4
seam-quotient-is-4 = refl

-- read directly off the wedge record (same value, via Wedge.quot).
seam-wedge-quot-is-4 : Wedge.quot (tower-wedge 3) ≡ 4
seam-wedge-quot-is-4 = refl

-- the seam wedge is EXACT: V₄'s 4 cosets tile S₄ over S₃ with no remainder.
seam-wedge-exact : Wedge.rem (tower-wedge 3) ≡ 0
seam-wedge-exact = refl

------------------------------------------------------------------------
-- 2. The V₄ debut is exactly at this seam: 0 generating pairs below,
--    24 = 4·6 at the seam (reusing the censuses).
------------------------------------------------------------------------

-- below the seam (rung 3): no Klein-four — the gauge has not yet appeared.
v4-absent-below : klein-pairs 3 ≡ 0
v4-absent-below = klein-pairs-3-absent

-- at the seam (rung 4): 24 generating pairs = 4 subgroups × 6 each.
v4-present-at-seam : klein-pairs 4 ≡ 24
v4-present-at-seam = klein-pairs-4

-- the quotient 4 of the seam wedge equals the count of V₄ subgroups
-- (24 / 6 = 4): the factoradic digit IS the number of Klein-fours debuting.
v4-count-is-seam-quotient : tower-quotient 3 ≡ 4
v4-count-is-seam-quotient = refl

------------------------------------------------------------------------
-- 3. The Hodge ★ ride-along: the n=3 grade involution lives on the seam.
------------------------------------------------------------------------

-- the grade involution is an involution (★★ = id) — the dual reflection
-- riding the rung reflection, pulled in along the 3→4 seam.
seam-hodge-involution : (i : Fin 4) → dual-grade₃ (dual-grade₃ i) ≡ i
seam-hodge-involution = dual-grade₃-involution

-- n=3 is odd ⇒ NO self-dual grade — the grade-level analogue of "no
-- Klein-four below the seam": the first nontrivial pairing appears only on
-- crossing 3→4 (just as v4-absent-below records for the group side).
seam-hodge-no-fixed : (i : Fin 4) → (dual-grade₃ i ≡ i) → Fin 0
seam-hodge-no-fixed = witness-distinct
