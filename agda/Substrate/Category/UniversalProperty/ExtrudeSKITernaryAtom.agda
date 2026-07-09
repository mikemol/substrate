{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKITernaryAtom — ⟡extrude-ski-obs-converge, via the operator's
-- TERNARY-ATOM structure: the non-degenerate SKI quotient (the thing 253's fake wall hid) built POSITIVELY.
-- S/K/I are the three FACES/VERTICES of one irreducible ternary atom — mutually exclusive (a transformation
-- is needed to transpose them, never a reduction) — and the NEGATIVES (pairwise non-convergence, the
-- non-degeneracy) are DERIVED BY EXHAUSTION from the atom's projections. Positive object primary; negatives
-- its shadow (the Lawvere-positive thesis, 254, applied to the observation itself).
--
-- The operator pointed at the tower's INDUCTIVE n-vertex atom generator (WitnessTower). The canonical
-- 3-vertex atom is WitnessTower.M40Closure.Z3 ({z0,z1,z2}) — a genuine ternary geometric object with its
-- ℤ/3 structure (_+₃_) and the σ/rotate S₃-transposition. REUSED as the ternary atom (not an ad-hoc Face).
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: face (S/K/I ↦ z0/z1/z2,
-- the projection onto the ternary atom), face-normal (each face-term is a normal form, by exhaustion),
-- faces-dont-converge (distinct vertices ⟹ no common reduct, the negatives BY EXHAUSTION), and the specific
-- ¬Converge on the atom pairs + Y-of's fixpoint still converging. The framing ('positive atom primary,
-- negatives are projections') is (prose: the arc's Lawvere-positive thesis; Z3 is reused, not re-derived).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKITernaryAtom where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_; Converge)
open import Substrate.WitnessTower.M40Closure using (Z3; z0; z1; z2)
open import Substrate.Category.UniversalProperty.ExtrudeSKIConfluent using (reduct-obs; reduct-refl; ⇒*→converge)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of; Y-fix)

------------------------------------------------------------------------
-- ① THE IRREDUCIBLE TERNARY ATOM (reused: WitnessTower Z3). S/K/I are its three FACES/VERTICES — the
--    PROJECTION of the atom. atom : Z3 → Tm⟦533ef80d⟧ reads each vertex as its combinator; face : the reverse view.
--    Mutual exclusivity is BY CONSTRUCTION (z0/z1/z2 are distinct constructors — the "transposition needs a
--    transformation": the tower's σ/rotate S₃-action permutes them; identity never does).
------------------------------------------------------------------------
atom : Z3 → Tm⟦533ef80d⟧
atom z0 = S
atom z1 = K
atom z2 = I

-- ② each vertex-term is a NORMAL FORM (irreducible — a bare combinator has no reduction). By exhaustion.
atom-normal : (v : Z3) {c : Tm⟦533ef80d⟧} → atom v ⇒ c → ⊥
atom-normal z0 ()
atom-normal z1 ()
atom-normal z2 ()

-- a normal form only reduces to itself (no decision, no normalization — just: it doesn't step):
nf-fixed : {n : Tm⟦533ef80d⟧} → ({c : Tm⟦533ef80d⟧} → n ⇒ c → ⊥) → {c : Tm⟦533ef80d⟧} → n ⇒* c → n ≡ c
nf-fixed n-nf done      = refl
nf-fixed n-nf (s ◅ _)   = ⊥-elim (n-nf s)

-- the projection is INJECTIVE on vertices (distinct vertices ⟹ distinct face-terms) — by exhaustion:
atom-inj : {u v : Z3} → atom u ≡ atom v → u ≡ v
atom-inj {z0} {z0} _ = refl
atom-inj {z1} {z1} _ = refl
atom-inj {z2} {z2} _ = refl
atom-inj {z0} {z1} ()
atom-inj {z0} {z2} ()
atom-inj {z1} {z0} ()
atom-inj {z1} {z2} ()
atom-inj {z2} {z0} ()
atom-inj {z2} {z1} ()

------------------------------------------------------------------------
-- ③ THE NEGATIVES, BY EXHAUSTION FROM THE PROJECTIONS. Distinct vertices DON'T CONVERGE — one lemma, from
--    NF-ness + injectivity. This is the whole non-degeneracy: the Converge-quotient (254) keeps distinct
--    faces apart. No CR needed, no decision, no Turing spook — purely the positive ternary structure.
------------------------------------------------------------------------
faces-dont-converge : {u v : Z3} → (u ≡ v → ⊥) → Converge (atom u) (atom v) → ⊥
faces-dont-converge {u} {v} u≢v (d , au⇒*d , av⇒*d) =
  u≢v (atom-inj (trans (nf-fixed (atom-normal u) au⇒*d) (sym (nf-fixed (atom-normal v) av⇒*d))))

-- the three vertices are pairwise distinct (mutual exclusivity, by exhaustion) — and so the atoms they
-- project to are pairwise NON-convergent. ALL of it read off the ONE ternary atom:
z0≢z1 : z0 ≡ z1 → ⊥
z0≢z1 ()
z1≢z2 : z1 ≡ z2 → ⊥
z1≢z2 ()
z0≢z2 : z0 ≡ z2 → ⊥
z0≢z2 ()

-- the non-degeneracy witnesses (S≁K, K≁I, S≁I) — derived, not separately proven (atom z0 = S, etc.):
S≁K : Converge S K → ⊥
S≁K = faces-dont-converge z0≢z1
K≁I : Converge K I → ⊥
K≁I = faces-dont-converge z1≢z2
S≁I : Converge S I → ⊥
S≁I = faces-dont-converge z0≢z2

------------------------------------------------------------------------
-- ④ THE QUOTIENT IS NON-DEGENERATE, AND CARRIES Y-of's FIXPOINT. reduct-obs (254) = Converge. On the atoms:
--    reduct-obs S S is inhabited (reduct-refl) but reduct-obs S K is EMPTY (S≁K) — so the confluence-based
--    quotient distinguishes the faces (unlike 252's degenerate obs⊤). And Y-of's fixpoint still converges.
------------------------------------------------------------------------
non-degenerate : reduct-obs S S × (reduct-obs S K → ⊥)
non-degenerate = reduct-refl S , S≁K

fix-converges : (f : Tm⟦533ef80d⟧) → reduct-obs (Y-of f) (f ∙ (Y-of f))
fix-converges f = ⇒*→converge (Y-fix f)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the non-degenerate SKI quotient built POSITIVELY: S/K/I are the three
-- faces of ONE irreducible ternary atom (WitnessTower Z3); the negatives are its projections BY EXHAUSTION):
-- the pairwise either/ors "is S=K? is K=I? is S=I?" (which 253 mis-handled by reaching for a decision) do NOT
-- get answered pairwise — they DISSOLVE into ONE positive structure: the ternary atom, whose three vertices
-- are mutually exclusive by construction (a transformation — the tower's σ/rotate S₃-action — is needed to
-- transpose them; a reduction never does, atom-normal). From that ONE atom, faces-dont-converge derives ALL
-- pairwise non-convergence BY EXHAUSTION (③) — the non-degeneracy of the confluence-based Converge-quotient
-- (254, ④), which 252's obs⊤ collapsed. No decision, no CR, no Turing spook (D-no-classical-spook): the
-- negatives are SHADOWS of the positive ternary atom, exactly the Lawvere-positive thesis (254) applied to
-- the observation. And Y-of's fixpoint converges on it (④). This is the meaningful quotient the whole
-- obs-thread sought — positive, by exhaustion, from the substrate's own inductive n-vertex atom.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the ternary atom (Z3, reused) + the projection (atom) + the
-- negatives by exhaustion (faces-dont-converge ⟹ S≁K/K≁I/S≁I) + non-degeneracy + Y-of's fixpoint converging.
-- SCOPED (correctly, no spook): the FULL n-vertex generalization (the tower's inductive process at every N —
-- every combinator normal form as a vertex) is the general form, of which the ternary (S/K/I) atom is rung 2
-- (⟡extrude-ski-nvertex); the σ/rotate S₃-transposition is reused-in-spirit (the mutual-exclusivity witness),
-- its literal action on the atoms scoped. What's grounded: the non-degenerate quotient is BUILT from the
-- positive ternary atom, negatives by exhaustion — the confluence-based observation is meaningful.
------------------------------------------------------------------------
