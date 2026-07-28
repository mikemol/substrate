------------------------------------------------------------------------
-- Substrate.WitnessTower.ParityCoordIsoApex
--
-- ◆AI-2b — the MOD-2 flagship of the grade-map invariant (◆AI-1h'). Two parts:
--
-- (a) the THREE V₄-parities ARE the Z/2×Z/2 coordinate iso. TowerLiftSplit's
--     lifts-v4-parity-{diagonal,A,B} (V4-F2Graded / -CountA / -CountB) are three
--     separate F₂-gradings; the repo already states (V4-Coxeter-F2Graded-CountB)
--     that "length-parity + count-A-parity + count-B-parity give the V₄ ≅ Z/2×Z/2
--     coordinate iso". ◆AI-2b' TIGHTENS this from a prose pointer to a WIRED
--     TERM: coord : V₄ → Bool×Bool (the two axis-parities) is a group iso
--     (bijection + homomorphism, all refl) below — not just cited, built.
--
-- (b) THE DEEP QUESTION (the ◆AI-2 G8 residue): does the sign-parity itself lift
--     general-n, with sign-stab-total merely its n=4 instance? ANSWER, framed by
--     the grade-map invariant:
--
--       · sign AS A MOD-2 PARITY lifts general-n. sign : Perm n → Bool is a
--         homomorphism at EVERY grade (OrientationRigCatPermSign.sign-hom:
--         sign(compose σ τ) ≡ sign σ xor sign τ, all n). This is the MOD-2 role
--         (◆AI-1h'): the grade-mod-2 collapse, defined at every grade. It LIFTS.
--
--       · sign FACTORING THROUGH STAB is the n=4 instance. sign-stab-total (sign
--         factors through the V₄-normal-complement retraction) needs V₄ ◁ S₄,
--         true only at n=4 (TowerLiftSplit's rung-3-bound leg). So it is NOT a
--         general-n fact — it is the n=4 meeting of the general MOD-2 parity with
--         the rung-3-bound V₄-complement.
--
--     So the honest resolution: the PARITY (MOD-2) lifts; the FACTORISATION
--     (which routes the parity through a grade-fixed rung-3 subgroup) does not.
--     sign-stab-total is not "the n=4 instance of a general sign-stab theorem";
--     it is the general MOD-2 parity (sign-hom) COMPOSED with an n=4-only
--     structural retraction. The grade-map invariant separates the two cleanly:
--     MOD-2 (lifts) vs the V₄-complement (no grade-role, rung-3-bound).
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.ParityCoordIsoApex where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Bool using (Bool; true; false)

------------------------------------------------------------------------
-- (a) the three V₄-parities, named together as the coordinate apex. Each is an
--     F₂-grading of V₄ (parity ∘ a homomorphism); together they are the
--     Z/2×Z/2 coordinate iso — now WIRED as `coord` below (◆AI-2b') and PROVEN
--     to be the actual gradings (◆AI-2b'': coord-fst-is-parity-A / -snd-is-parity-B).
------------------------------------------------------------------------

open import Substrate.Groups.V4-Coxeter-F2Graded        using (V4-F2Graded)
open import Substrate.Groups.V4-Coxeter-F2Graded-CountA  using (V4-F2Graded-CountA)
open import Substrate.Groups.V4-Coxeter-F2Graded-CountB  using (V4-F2Graded-CountB)

-- the three coordinate parities (length / count-A / count-B). The apex over the
-- three lifts-v4-parity-* re-exports of TowerLiftSplit: they are the coordinates
-- of V₄ ≅ Z/2×Z/2. length-parity fixes the AB-diagonal (even); count-A and
-- count-B are the two axis coordinates; AB is odd under both counts = the shared
-- point of the two Z/2 factors.
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4 using (_+V₄_)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Groups.V4.Bijection using (to-c)
open import Substrate.Algebra.F2.FromBool using (F₂→bool)
open import Substrate.Category.RGradedMonoid using (RGradedMonoid)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign; sign-hom)
open import Substrate.WitnessTower.SignStabTotal using (sign-stab-total)
open import Substrate.WitnessTower.TowerLiftSplit using (rung3-sign-stab)
parity-length = V4-F2Graded
parity-A      = V4-F2Graded-CountA
parity-B      = V4-F2Graded-CountB

------------------------------------------------------------------------
-- (a-tight, ◆AI-2b') the coordinate iso as an ACTUAL TERM (not a prose pointer).
-- coord sends v : V₄ to its two axis-parities (count-A mod 2, count-B mod 2):
--   e ↦ (F,F)   α=A ↦ (T,F)   β=B ↦ (F,T)   γ=AB ↦ (T,T).
-- This is V₄ ≅ Z/2×Z/2 as GROUPS: a bijection (both roundtrips) AND a
-- homomorphism (coord (x·y) = coord x ⊕ coord y, componentwise xor = the Z/2×Z/2
-- operation). All by refl on the 4-element enumeration. The AB-diagonal γ is
-- (T,T): odd under BOTH coordinates — the shared point of the two Z/2 factors,
-- exactly as the parity story requires.
------------------------------------------------------------------------


coord : V₄ → Bool × Bool
coord e = false , false
coord α = true  , false
coord β = false , true
coord γ = true  , true

uncoord : Bool × Bool → V₄
uncoord (false , false) = e
uncoord (true  , false) = α
uncoord (false , true ) = β
uncoord (true  , true ) = γ

coord-uncoord : (v : V₄) → uncoord (coord v) ≡ v
coord-uncoord e = refl
coord-uncoord α = refl
coord-uncoord β = refl
coord-uncoord γ = refl

uncoord-coord : (p : Bool × Bool) → coord (uncoord p) ≡ p
uncoord-coord (false , false) = refl
uncoord-coord (true  , false) = refl
uncoord-coord (false , true ) = refl
uncoord-coord (true  , true ) = refl

-- the Z/2×Z/2 operation: componentwise xor — IMPORT the canonical F₂²/V₄-affine op
-- (_+V₄_ over V₄ = Bool × Bool) instead of redeclaring it here (carrier-locality).

-- coord is a group homomorphism V₄ → (Bool×Bool, +V₄): the iso is not just a
-- bijection of carriers but respects the group structure. All 16 cases by refl.
coord-hom : (x y : V₄) → coord (x · y) ≡ (coord x +V₄ coord y)
coord-hom e e = refl
coord-hom e α = refl
coord-hom e β = refl
coord-hom e γ = refl
coord-hom α e = refl
coord-hom α α = refl
coord-hom α β = refl
coord-hom α γ = refl
coord-hom β e = refl
coord-hom β α = refl
coord-hom β β = refl
coord-hom β γ = refl
coord-hom γ e = refl
coord-hom γ α = refl
coord-hom γ β = refl
coord-hom γ γ = refl

------------------------------------------------------------------------
-- (a-link, ◆AI-2b'') coord's coordinates ARE the actual parity gradings — not a
-- coincidentally-matching standalone map. Each coordinate equals the REAL degree
-- of the corresponding F₂-graded record (V4-F2Graded-CountA/B), transported to
-- Bool: coord's fst v ≡ F₂→bool (degree_CountA (to-c v)), and snd likewise for
-- CountB. degree is the grading's own parity∘hom (on Coxeter words, via to-c :
-- V₄ → Word). This closes the last prose pointer: coord IS the parity coordinate
-- pair, proven, not asserted. All refl on the 4 elements.
------------------------------------------------------------------------


-- the real degree functions from the graded records (parity ∘ count-by, on Words):
degree-A = RGradedMonoid.degree V4-F2Graded-CountA
degree-B = RGradedMonoid.degree V4-F2Graded-CountB

-- coord's first coordinate IS the count-A parity (the real graded degree):
coord-fst-is-parity-A : (v : V₄) → proj₁ (coord v) ≡ F₂→bool (degree-A (to-c v))
coord-fst-is-parity-A e = refl
coord-fst-is-parity-A α = refl
coord-fst-is-parity-A β = refl
coord-fst-is-parity-A γ = refl

-- coord's second coordinate IS the count-B parity:
coord-snd-is-parity-B : (v : V₄) → proj₂ (coord v) ≡ F₂→bool (degree-B (to-c v))
coord-snd-is-parity-B e = refl
coord-snd-is-parity-B α = refl
coord-snd-is-parity-B β = refl
coord-snd-is-parity-B γ = refl

------------------------------------------------------------------------
-- (b) the general-n sign-parity (MOD-2 role) — the resolution of the deep
--     question. sign is a grade-mod-2 homomorphism at EVERY grade; this LIFTS.
--     Re-exported with its general-n type to exhibit the lift.
------------------------------------------------------------------------


-- the MOD-2 parity lifts general-n: sign is a homomorphism sign(compose σ τ) ≡
-- sign σ xor sign τ at ALL n (with the IsPerm side-conditions the repo requires).
-- This is the grade-mod-2 role of ◆AI-1h', defined at every grade — the part of
-- the sign story that LIFTS. Re-exported by its own general-n type (no restatement).
sign-parity-lifts = sign-hom

------------------------------------------------------------------------
-- the SPLIT, stated: sign-parity-lifts (MOD-2, general-n) vs the n=4-only
-- factorisation. sign-stab-total is re-exported to sit beside the general parity
-- so the contrast is one import: the parity lifts; routing it through V₄ (the
-- factorisation) is rung-3-bound.
------------------------------------------------------------------------


-- sign-stab-total : (σ : Permutation) → sign(perm4 σ) ≡ sign(perm4 (s-for σ)) —
-- the n=4 instance (Permutation = the 4 axes). Named here as the NON-lifting
-- companion of sign-parity-lifts: the general MOD-2 parity composed with the
-- rung-3-bound V₄-complement retraction.
n4-sign-factorisation = sign-stab-total
