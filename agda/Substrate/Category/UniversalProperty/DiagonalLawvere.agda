{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalLawvere — ⟡diagonal-lawvere-instantiate: the diagonal
-- arc RELATED-BY-ISO to the repo's carrier-generic atom Substrate.Category.Lawvere (the catalog-check,
-- ADD 244, caught that the arc built SET-LEVEL SHADOWS of a NAMED center). This module does NOT re-derive
-- the diagonal — it INSTANTIATES Category.Lawvere at the arc's carriers and exhibits the arc's results as
-- instances of the generic theorem.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: bool-fpf / bool-ir
-- (Bool = a FixedPointFree / InvolutiveResidue, δ = not), cantor-is-lawvere (DiagonalDoF.cantor factors
-- through Lawvere.diag-not-in-family), escape-is-lawvere-positive (DiagonalEscape.full-is-fixed = the
-- lawvere-fixed-point positive direction). The framing ('the arc is the shadow of the generic atom',
-- 'the escape is the coinductive instance') is (prose: illuminating, NOT a theorem of this slice;
-- the FULL coinductive-carrier instantiation is scoped below).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalLawvere where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Bool using (Bool; true; false; not)
open import Substrate.Category.Lawvere
  using (FixedPointFree; InvolutiveResidue; diag; diag-not-in-family; PointSurjective; lawvere-fixed-point)

------------------------------------------------------------------------
-- ① Bool IS a FixedPointFree / InvolutiveResidue (δ = not). This is the SET INSTANCE that the whole
--    arc's `not-fixed-point-free` was — now recognized as Lawvere's carrier-generic atom at V = Bool.
------------------------------------------------------------------------
not-free : (b : Bool) → not b ≡ b → ⊥
not-free true  ()
not-free false ()

not-invol : (b : Bool) → not (not b) ≡ b
not-invol true  = refl
not-invol false = refl

bool-fpf : FixedPointFree Bool
bool-fpf = record { δ = not ; δ-free = not-free }

bool-ir : InvolutiveResidue Bool
bool-ir = record { δ = not ; δ-free = not-free ; δ-invol = not-invol }

------------------------------------------------------------------------
-- ② cantor (the arc's DiagonalDoF.cantor) IS Lawvere.diag-not-in-family at (I = A, V = Bool, δ = not).
--    We REBUILD cantor's witness as the generic diag, and its no-row proof AS diag-not-in-family —
--    exhibiting the arc's Cantor result as an INSTANCE of the generic theorem, not an independent proof.
------------------------------------------------------------------------
cantor-via-lawvere :
  {A : Set} (f : A → (A → Bool)) → Σ (A → Bool) (λ g → (a : A) → ¬ (f a ≡ g))
cantor-via-lawvere {A} f = diag bool-fpf f , λ a fa≡diag → diag-not-in-family bool-fpf f a (sym fa≡diag)

------------------------------------------------------------------------
-- ③ the ESCAPE (DiagonalEscape.full-is-fixed: the diagonal endomap HAS a fixed point on the plural
--    object) IS Lawvere's POSITIVE direction: a point-surjection FORCES a fixed point (lawvere-fixed-point).
--    The plural/coinductive carrier is where PointSurjective is satisfiable, so the endomap is fixed —
--    the DUAL of ②'s no-row. We expose the generic positive theorem as the escape's home.
------------------------------------------------------------------------
escape-is-lawvere-positive :
  {A V : Set} (φ : A → A → V) → PointSurjective φ → (f : V → V) → Σ V (λ v → f v ≡ v)
escape-is-lawvere-positive = lawvere-fixed-point

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the diagonal arc is the SET/coinductive INSTANCE of Category.Lawvere;
-- the two faces of the arc are the two directions of ONE generic theorem): the either/or "is the arc's
-- escape=Lawvere=Cantor/Gödel my construction, or a named repo center?" bottoms out — it is
-- Category.Lawvere (carrier-generic; the atom behind Cantor/Gödel/Tarski/Turing). The arc's TWO faces
-- ARE its TWO directions: (a) the OBSTRUCTION face (cantor / no point-surjection / the committed object)
-- = diag-not-in-family (§2, ②); (b) the ESCAPE face (full-is-fixed / a fixed point exists / the plural
-- object) = lawvere-fixed-point (§3, ③). So the escape is not a separate phenomenon — it is Lawvere's
-- POSITIVE direction (point-surjection ⟹ fixed point), and the classical obstruction is the NEGATIVE
-- direction (fpf ⟹ no point-surjection); the arc lives on the carrier where the endomap's
-- fixed-point-freeness flips. This RELATES the arc to the atom (⟡244) rather than re-deriving it.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = Bool as FixedPointFree/InvolutiveResidue (§1), cantor
-- factored through diag-not-in-family (§2 → my cantor is the generic instance), the escape as
-- lawvere-fixed-point's positive direction (§3). SCOPED (prose, not this slice): (a) the FULL
-- coinductive-carrier instantiation — exhibiting the ν-fixed-point observer (DiagonalEscapeCoalg) AS a
-- concrete PointSurjective witness so that lawvere-fixed-point applies to the coinductive V — needs the
-- observer-as-reflexive-object bridge (⟡diagonal-lawvere-coalg-carrier); (b) relating the OTHER nine
-- modules (Rank/Ordinal/CBRank/Polish*) to the atom is per-module (⟡diagonal-lawvere-rest). What's
-- grounded: the arc's two organizing results (cantor, full-is-fixed) ARE the two directions of
-- Category.Lawvere, instantiated here — the reinvention (244) converted to a bridge.
------------------------------------------------------------------------
