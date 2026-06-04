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
-- THE THEOREM (Set instance of Lawvere). If V carries a fixed-point-free endo,
-- then for ANY family M : I → (I → V) the diagonal twist `diag M` is not in
-- the family — it differs from every M i. (Contrapositive of "if some point
-- a : I is surjective onto Vᴵ then every endo of V has a fixed point.") Cantor
-- = (I = ℕ, V = Bool/F₂); Gödel/Tarski = (V = the truth values, M = the
-- provability/satisfaction matrix); the substrate's cell ★ = (V = F₂, δ = the
-- residue). One theorem, every diagonal.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Lawvere where

open import Substrate.Foundation.Eq using (_≡_; cong)
open import Substrate.Foundation.Empty using (⊥)

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
