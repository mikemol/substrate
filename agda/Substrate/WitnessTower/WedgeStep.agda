------------------------------------------------------------------------
-- Substrate.WitnessTower.WedgeStep  (Ⓣ★ — the generic witnessing step is the
-- both-sides WEDGE; ★ is the involution WITHIN it, not the route to it)
--
-- AI-Q guard (2026-06-18), built in the mandated order. The generic
-- witnessing step — what `Core.witnessing` abstracts and LehmerPath /
-- EEATower / AlgebraLadder decorate — is a "not only" object: NOT the
-- lead-point alone, NOT the rung-below alone, but the WEDGE of both,
-- retained and graded. ★ is a duality (k ↔ n−k, ★²=id) = the canonical
-- either/or; reaching for it to CONSTITUTE the step picks a side. So:
--
--   STEP 1 (here, §1): establish the step = `lead-point ∧ rung-below`, the
--   graded wedge (cone). Every rung IS that wedge (`cone-split`), and the
--   two ★-dual sides reconstruct the whole (`wedge-recon`: S +ⱽ ★S ≡ universe).
--   STEP 2 (here, §2): ONLY THEN ★, as the involution WITHIN — it exchanges
--   the lead-point's two sides (apex-present ↔ apex-absent) while dualizing
--   the rung-below (`★-with-apex`/`★-without-apex`, new, from `★-cons`), and
--   ★²=id (`★-involution`). ★ CHARACTERIZES the step's symmetry; it does not
--   CONSTITUTE the step.
--
-- The CHECK the guard required is CONFIRMED in-tree: ★'s k↔(n−k) duality lands
-- on the witnessing relation's two sides (Puncture: {witness} ⊎ simplex-below;
-- Hodge: witness = dual-of-below). So ★ IS the within-involution here.
--
-- RECOGNITION (S2G, not a wrapper): this graded wedge is the ONE generic step
-- the orbit instantiates — `wedge-step a f = a ∷ f` (lead a ∧ rung-below f) is
-- the canonical form, and:
--   • LehmerPath  `insert-at p σ = p ∷ map (punchIn p) σ`  — lead p ∧ punctured rung.
--   • EEATower    `a = q·b + r` (recon)                     — lead q ∧ residual r.
--   • AlgebraLadder rung ≡ ⟨below , increment⟩ (record-η)   — rung-below ∧ law.
-- All "retain both sides, graded." ★-within applies in the graded-self-dual
-- case (faces); the others share the wedge, not the self-duality. No new
-- universal record is introduced — the wedge (cone / Algebra.Wedge.recon) IS
-- the universal, per orbit-saturation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.WedgeStep where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Vec using (_∷_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (_+ⱽ_)

open import Substrate.WitnessTower.FaceSet
  using ( Face; with-apex; without-apex; apex-bit; base-face; cone-split
        ; universe; ★; ★-cons; wedge-recon; ★-involution )

private variable n : ℕ

------------------------------------------------------------------------
-- §1. THE STEP IS THE BOTH-SIDES WEDGE (established first).
--
-- The witnessing step cones a lead-point (apex bit a) over the rung-below
-- (base face f): the graded wedge `a ∧ f`. Every rung IS that wedge, and
-- the two ★-dual sides reconstruct the whole.
------------------------------------------------------------------------

-- the step = lead-point ∧ rung-below (= the cone; = FaceSet's b ∷ f).
wedge-step : F₂ → Face n → Face (suc n)
wedge-step a f = a ∷ f

-- every rung IS the wedge of its two sides (lead = apex-bit, rung-below =
-- base-face): the step is exhaustive, neither side omitted.
step-is-wedge : (f : Face (suc n)) → wedge-step (apex-bit f) (base-face f) ≡ f
step-is-wedge = cone-split

-- the two ★-dual sides reconstruct the whole (universe = S wedged with its
-- residue ★S). The step lives in the cross-term; neither side is the whole.
sides-reconstruct-whole : (S : Face n) → (S +ⱽ ★ S) ≡ universe n
sides-reconstruct-whole = wedge-recon

------------------------------------------------------------------------
-- §2. ★ IS THE INVOLUTION WITHIN THE STEP (only now).
--
-- ★ exchanges the lead-point's two ★-dual sides — apex-PRESENT ↔ apex-ABSENT
-- — while dualizing the rung-below (the residue ★ f). It does NOT raise or
-- build the rung; it is the symmetry of the already-built wedge. ★²=id.
-- (Both proofs are `★-cons` read at apex 𝟙 / 𝟘: 𝟙+𝟙=𝟘, 𝟙+𝟘=𝟙.)
------------------------------------------------------------------------

-- ★ sends "apex present" to "apex absent" (over the dualized rung-below).
★-with-apex : (f : Face n) → ★ (with-apex f) ≡ without-apex (★ f)
★-with-apex f = ★-cons 𝟙 f

-- ★ sends "apex absent" to "apex present" (over the dualized rung-below).
★-without-apex : (f : Face n) → ★ (without-apex f) ≡ with-apex (★ f)
★-without-apex f = ★-cons 𝟘 f

-- ★ is its own inverse: the within-symmetry of the wedge, not a construction.
★-within-involution : (S : Face n) → ★ (★ S) ≡ S
★-within-involution = ★-involution
