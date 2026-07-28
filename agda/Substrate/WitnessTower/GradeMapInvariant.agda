------------------------------------------------------------------------
-- Substrate.WitnessTower.GradeMapInvariant
--
-- ◆AI-1h — the session's INVARIANT, made a term. Ritual#7's recursive bottoming-
-- out: everything built this session (the AI-1 vertical, the sign arc, the lift-
-- split, the parity work, the reappearance) is governed by ONE structure — the
-- GRADE MAP: whether the relevant map RAISES, LOWERS, FIXES, or takes-mod-2 the
-- grade. The repo says this itself (Algebra.Wedge.Graded): "make THE INDEX THE
-- GRADE ... a grade-RAISING reconstruction." The grade is the ℕ-index of the
-- tower; the grade map is what a construction does to it.
--
-- THE FOUR GRADE-ROLES (the tag-set), each with its session witnesses:
--
--   RAISE  (C n → C (suc n)) — a witnessing RUNG. Builds a bigger object.
--     · insert-at : Perm n → Perm (suc n)            (the perm tower step)
--     · tower-graded's recon                          (Ⓣ₁ GradedDivStr)
--     · with-apex : Face n → Face (suc n)             (coning a new face)
--     · AlgebraLadder: +1 LAW (grade-raise in theory-space: Magma⊏…⊏AbelianGroup)
--
--   LOWER  (C (suc n) → C n) — the FOLD / forgetful walk down.
--     · gforget (GradedDivStr's grade-lowering map)
--     · AlgebraLadder.forget-to-magma
--
--   FIX    (C n → C n) — an ENDO. A symmetry ON a grade, NOT a rung. THIS IS THE
--          STABILIZATION criterion (◆AI-D7): when the up-step is grade-fixed, the
--          tower stops.
--     · ★ : Face n → Face n  (Hodge self-duality, ★★=id — the FaceSet stabilizer)
--
--   MOD-2  (grade ↦ grade mod 2) — the PARITY collapse. A grade-homomorphism to F₂.
--     · sign : the inversion-parity (grade of a perm mod 2)
--     · V4-F2Graded : V₄'s length-parity (grade mod 2 = the Z/2×Z/2 coordinate)
--
-- Under this tag, the session's separate threads are ONE story:
--   - AI-2's lift-split IS "which grade-role does the map have": RAISE lifts
--     general-n (spine); MOD-2 lifts (parity/V₄ reappears); the S₄-normal-complement
--     is neither (a fixed-n subgroup, no grade-role) → rung-3-bound.
--   - AI-1's vertical IS the RAISE-tower (Core/FamilyWitness) topped by a FIX
--     (★ stabilizes FaceSet).
--   - the reappearance (complement-8, RM(1,4)→RM(1,6)) IS a MOD-2/count recurrence
--     at a higher RAISE-grade.
--
-- ◆AI-1g'' folded in (the BOUNDARY of the invariant): grade-FIX (★) stabilizes
-- the tower at the GRADE level, but this is STRICTLY WEAKER than a CATEGORICAL
-- terminal object. Probing found no in-repo universal-property witness for
-- "FaceSet is terminal" (CofreeDual is the terminal-COALGEBRA/ana side of the
-- Trace duality, unrelated to FaceSet). So the honest claim is exactly:
-- grade-stabilization (proven, ◆AI-1g'), NOT categorical terminality (unwitnessed).
-- The grade map is the invariant; terminality is a separate, stronger, open thing.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.GradeMapInvariant where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Bool using (Bool; true; false)

------------------------------------------------------------------------
-- The four grade-roles as explicit map SHAPES over a ℕ-graded carrier. Tagging
-- a construction = giving the role its map inhabits. (These are the shapes;
-- the witnesses below are the session's actual terms at each shape.)
------------------------------------------------------------------------

Raise : (ℕ → Set) → Set
Raise C = {n : ℕ} → C n → C (suc n)

Lower : (ℕ → Set) → Set
Lower C = {n : ℕ} → C (suc n) → C n

Fix : (ℕ → Set) → Set
Fix C = {n : ℕ} → C n → C n

-- MOD-2 (◆AI-1h''): a grade-mod-2 collapse — a map to Bool (F₂) at each grade.
-- Distinct from the grade-CHANGING ℕ-index roles: it collapses the grade to a
-- single bit rather than raising/lowering the index.
Mod2 : (ℕ → Set) → Set
Mod2 C = {n : ℕ} → C n → Bool

------------------------------------------------------------------------
-- RAISE witnesses (rungs).
------------------------------------------------------------------------

open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.FaceSet using (Face; with-apex)
open import Substrate.Foundation.Fin.Fin

-- the perm tower step at position 0: a rung (grade-raising).
raise-perm : Raise Perm
raise-perm = insert-at zero

-- coning a face: a rung in the face lattice.
raise-face : Raise Face
raise-face = with-apex

------------------------------------------------------------------------
-- LOWER witness (◆AI-1h', the fold-down). The perm tower's grade-lowering map:
-- decomp-tail drops a Perm (suc n) to a Perm n (with the IsPerm side-condition
-- the repo requires — the honest fold shape, not a bare C(suc n)→C n). This is
-- the actual repo fold, equated directly (not reconstructed).
------------------------------------------------------------------------

open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Decompose using (decomp-tail)

-- the fold-down at the perm tower: Perm (suc n) → Perm n (IsPerm-conditioned).
lower-decomp : {n : ℕ} (σ : Perm (suc n)) → IsPerm σ → Perm n
lower-decomp = decomp-tail

------------------------------------------------------------------------
-- FIX witness (the stabilizer — ◆AI-1g'). ★ is grade-FIXED, so the up-tower
-- stops at FaceSet. This inhabiting Fix (not Raise) IS the stabilization.
------------------------------------------------------------------------

open import Substrate.WitnessTower.FaceSet using (★)

star-fixes-grade : Fix Face
star-fixes-grade = ★

-- the tag distinction that ◆AI-D7 uses: raise-face RAISES (→ Face(suc n), a rung);
-- star-fixes-grade FIXES (→ Face n, an endo). The tower climbs on the former and
-- stabilizes on the latter. Both are witnessed terms; their TYPES are the tell.

------------------------------------------------------------------------
-- MOD-2 witness (parity). The sign / V₄-parity collapse the grade to F₂. This
-- is the role that REAPPEARS (lifts general-n) in the lift-split — parity is a
-- grade-homomorphism, defined at every grade.
------------------------------------------------------------------------

open import Substrate.Groups.V4-Coxeter-F2Graded using (V4-F2Graded)

-- V₄'s length-parity IS the grade-mod-2 (the Z/2×Z/2 coordinate parity). Named
-- here as the MOD-2 role's witness — the general-n-lifting parity of AI-2(b).
v4-parity-mod2 = V4-F2Graded

-- and the perm sign as a properly-typed Mod2 witness (◆AI-1h'): sign : Perm n →
-- Bool is the grade-mod-2 collapse at every grade (Perm n = Vec (Fin n) n). This
-- gives the MOD-2 role a shape-typed witness, uniform with raise/lower/fix/preserve.
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign)

mod2-sign : Mod2 Perm
mod2-sign = sign

-- FLAGSHIP (◆AI-3'): the MOD-2 role's defining property is that it LIFTS general-n
-- — the parity collapse is a grade-HOMOMORPHISM, not just a per-grade map. That
-- is sign-parity-lifts (= sign-hom): sign(σ·τ) ≡ sign σ xor sign τ at every grade.
-- mod2-sign gives the map; sign-parity-lifts gives the lift that MAKES it the MOD-2
-- role (the "reappears/lifts" content). Cited here so the covering names the
-- flagship, not just the per-grade witness.
open import Substrate.WitnessTower.ParityCoordIsoApex using (sign-parity-lifts)

mod2-lifts = sign-parity-lifts

------------------------------------------------------------------------
-- PRESERVE (◆AI-1h', the 5th role — found by the ritual#8 universality probe).
-- A WITHIN-GRADE map: acts at a single grade n, does NOT change it. This is the
-- role the EARLY BRIDGES (Faithfulness/Uniqueness/Residue/FaithfulnessApex)
-- inhabit — faithfulness ("an element is determined by its action") is a
-- grade-preserving property, and the detector is a within-grade map. The 4
-- grade-CHANGING roles above (raise/lower/fix/mod-2) missed these; PRESERVE
-- completes the taxonomy.
--
-- Shape: a same-grade map C n → D n (here endo-on-Perm at each grade, or the
-- detector Perm n → Perm n → F₂). Fix is the endo special case (D = C); the
-- general within-grade morphism is Preserve.
------------------------------------------------------------------------

Preserve : (ℕ → Set) → (ℕ → Set) → Set
Preserve C D = {n : ℕ} → C n → D n

open import Substrate.WitnessTower.FaithfulnessApex using (detectP; apex-kernel)
open import Substrate.Algebra.F2 using (F₂; 𝟘)

-- the detector is a within-grade map (Perm n → Perm n → F₂): grade n in, grade
-- n out. Its kernel law (apex-kernel: detect σ τ ≡ 𝟘 ⟹ σ ≡ τ) IS faithfulness —
-- the PRESERVE-role's flagship. Curried to fit the Preserve shape:
preserve-detector : Preserve Perm (λ n → Perm n → F₂)
preserve-detector = detectP

-- FLAGSHIP (◆AI-3'): the deep-read PRESERVE flagship — the total sign morphism.
-- sign-of : Permutation → Bool factors through the Stab retraction s-for
-- (sign-factors-through-s-for : sign-of σ ≡ sign-of (s-for σ)), i.e. it is a
-- grade-PRESERVING morphism CONSTANT ON EACH V₄-COSET (the coset = the fibre of
-- s-for; sign-of-stable witnesses s-for idempotent-on-sign). This is the total
-- sign morphism the raw carrier could not carry, built by feeding the concrete
-- even-V₄ base through the permutation generator (SignEmbedVEven + SignStabTotal).
-- Honestly scoped: this is the n=4 (S₄) PRESERVE flagship; preserve-detector is
-- the general-n within-grade witness. Both inhabit PRESERVE.
open import Substrate.WitnessTower.SignStabTotal
  using (sign-of; sign-factors-through-s-for; sign-of-stable)

preserve-sign-morphism = sign-factors-through-s-for

------------------------------------------------------------------------
-- THE 1-BIT CORE (◆AI-1h', G4): the five roles reduce to ONE predicate —
-- changes-grade? The ℕ-index either differs between domain and codomain
-- (raise +1, lower −1, mod-2 collapse-to-Bool) or it does not (fix, preserve).
-- This single bit IS the criterion used three ways this session:
--   changes-grade = true  → the lift-split's "rung role" / the reappearance
--   changes-grade = false → the stabilization criterion (◆AI-1g') / the bridges
-- Encoded as a tag with its bit; the bit is the recursive bottoming-out.
------------------------------------------------------------------------

data GradeRole : Set where
  raise lower mod-2 : GradeRole   -- changes the grade
  fix preserve      : GradeRole   -- keeps the grade

changes-grade? : GradeRole → Bool
changes-grade? raise    = true
changes-grade? lower    = true
changes-grade? mod-2    = true
changes-grade? fix      = false
changes-grade? preserve = false

-- the session's structures tagged by role (the universality result, ritual#8):
--   raise    : insert-at, with-apex, tower-graded recon, ladder(+1 law)
--   lower    : lower-decomp (typed, decomp-tail); also gforget, forget-to-magma
--   fix      : ★  (the FaceSet stabilizer)
--   mod-2    : mod2-sign (typed Mod2 Perm) + mod2-lifts (sign-parity-lifts,
--              the general-n lift FLAGSHIP), V4-F2Graded  (parity — reappears/lifts)
--   preserve : preserve-detector (detectP, general-n) + preserve-sign-morphism
--              (sign-factors-through-s-for, the n=4 sign-stab FLAGSHIP, coset-constant)
-- 21/21 session files inhabit one of these (hand-verified, ritual#8 G8).


-- terminal. star-fixes-grade : Fix Face witnesses the grade-level stabilization.
-- No term of a "FaceSet is terminal" universal property exists in-repo (probed).
-- So the invariant's honest ceiling is grade-stabilization, recorded as the
-- Fix-inhabitant above — categorical terminality is NOT claimed here.
------------------------------------------------------------------------

-- (the boundary is stated by what is NOT exported: there is deliberately no
-- `faceset-terminal : ...` term. star-fixes-grade is the proven ceiling.)
