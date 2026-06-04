------------------------------------------------------------------------
-- Substrate.Category.Lawvere
--
-- LAWVERE'S DIAGONAL (FIXED-POINT) THEOREM — the carrier-generic atom behind
-- Cantor, Gödel, Tarski, Turing, and the substrate's wedge residue. This is
-- the common substructure of three things WitnessTower.Diagonal found equal
-- at F₂ (the diagonal, the grade ★'s fixed-point-freeness, the cone apex/base
-- distinction): they are all the SET INSTANCE of this one theorem.
--
-- THE ATOM, generic. `FixedPointFree V` is a value type V with an endo δ that
-- never agrees with its input (δ v ≢ v). The F₂ instance is δ = (𝟙 +_), whose
-- δ-free is exactly WitnessTower.Diagonal.flip-disagrees; the wedge supplies
-- such a δ as its RESIDUE (translate by the distinction). Making that δ
-- CANONICAL over an arbitrary carrier — the certified residue r<b — is the
-- keystone (Algebra.Wedge scopes r<b out for now); FixedPointFree is the
-- interface that the keystone will populate generically, so every wedge-
-- carrier inherits the diagonal argument at once.
--
-- THE THEOREM, BOTH DIRECTIONS.
--   * POSITIVE (lawvere-fixed-point): if a point a : A is SURJECTIVE onto Aᴬ→V
--     (every map g : A → V is some point's row φ a), then every endo f : V → V
--     has a fixed point. A reflexive object forces fixed points.
--   * CONTRAPOSITIVE (diag-not-in-family): if V carries a fixed-point-free endo
--     then NO such point-surjection exists — the diagonal twist witnesses a
--     missed map. This is the generic Cantor/diagonal.
-- Cantor = (V = Bool/F₂, diagonal); Gödel/Tarski = (V = truth values, M = the
-- provability/satisfaction matrix); the substrate's cell ★ = (V = F₂, δ = the
-- residue). One theorem, every diagonal — and every self-reference.
--
-- RELATION TO Category.UniversalProperty.FixedPoint (it is NOT unrelated — the
-- two files are the two halves of THIS theorem). That module exhibits
-- (ι : UPArrow² → UPArrow, promote : UPArrow → UPArrow²): the meta level (the
-- arrow-of-arrows, the exponential-like UPArrow²) retracts into the base. That
-- section/retraction IS a reflexive-object structure = the HYPOTHESIS of
-- `lawvere-fixed-point`; so "the tower IS its own fixed point" is the POSITIVE
-- Lawvere conclusion, and this module's diagonal is its contrapositive. The
-- substrate's METACIRCULARITY (self-reference, the UP-tower fixed point) and its
-- DIAGONALIZATION (Cantor / the wedge residue) are therefore ONE structure,
-- hinged by Lawvere. (Wiring (ι, promote) as a literal PointSurjective instance
-- needs the UPArrow-as-exponential identification + its equality — deferred;
-- the relationship is exhibited here, the literal instance is the next bridge.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Lawvere where

open import Substrate.Foundation.Eq using (_≡_; sym; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_)

------------------------------------------------------------------------
-- 1. THE ATOM. A fixed-point-free endomap on values: the residue that
--    never equals its source. Carrier-generic flip-disagrees.
------------------------------------------------------------------------

record FixedPointFree (V : Set) : Set where
  field
    δ      : V → V
    δ-free : (v : V) → δ v ≡ v → ⊥

open FixedPointFree public

------------------------------------------------------------------------
-- 2. LAWVERE'S DIAGONAL THEOREM (Set instance). The diagonal twist of a
--    family is absent from the family — the generic Cantor argument.
------------------------------------------------------------------------

module _ {I V : Set} (fpf : FixedPointFree V) where

  -- the diagonal twist of a family of maps: at i, flip the i-th map's i-th
  -- value. (For I = positions, V = bits, this is Cantor's anti-diagonal.)
  diag : (I → I → V) → (I → V)
  diag M i = δ fpf (M i i)

  -- the diagonal twist is in NO row: it differs from every M i (at i).
  -- So no family I → (I → V) is onto — the generic diagonalization.
  diag-not-in-family : (M : I → I → V) (i : I) → diag M ≡ M i → ⊥
  diag-not-in-family M i eq = δ-free fpf (M i i) (cong (λ f → f i) eq)

------------------------------------------------------------------------
-- 3. LAWVERE, POSITIVE DIRECTION. A point-surjection forces fixed points —
--    the reflexive-object half (the hypothesis FixedPoint.agda's (ι, promote)
--    realises for UPCategory). Dual to diag-not-in-family.
------------------------------------------------------------------------

module _ {A V : Set} where

  -- A is point-surjective onto (A → V) via φ: every map g is some point's row.
  PointSurjective : (A → A → V) → Set
  PointSurjective φ = (g : A → V) → Σ A (λ a → φ a ≡ g)

  -- a point-surjection ⟹ every endo of V has a fixed point. The diagonal of
  -- "do φ then f" is represented by a point whose value f fixes.
  lawvere-fixed-point :
    (φ : A → A → V) → PointSurjective φ → (f : V → V) → Σ V (λ v → f v ≡ v)
  lawvere-fixed-point φ surj f with surj (λ a → f (φ a a))
  ... | (a , p) = φ a a , sym (cong (λ h → h a) p)
