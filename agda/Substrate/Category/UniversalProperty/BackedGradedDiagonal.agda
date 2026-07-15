------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.BackedGradedDiagonal — ⟡C2g-retire-part2 P1b-ground: the
-- explicit DIAGONAL grounding of the graded uniqueness. Makes machine-checked the reading the user
-- pointed at — "the residue IS the diagonal" — by supplying the wedge's residue as a Lawvere
-- fixed-point atom (`Category.Lawvere.TorsorAtom` / `FixedPointFree`).
--
-- The wedge is `a = recon q b r = q·b + r`; its ADDITIVE residue `r` (the `+r`) is a Lawvere
-- `TorsorAtom` over ℕ with `_∙_ = _+_`, `e = 0` — and `fix→unit` (a residue fixes some x only when it
-- is 0) is a 3-line induction. Then `prove-or-correct` gives the DIAGONAL DICHOTOMY: every residue is
-- EITHER 0 (the wedge reconstructs cleanly — the identity corner, `OrientationRigResidue.corner-eq`,
-- the reflexive diagonal where the residue vanishes) OR a genuine FIXED-POINT-FREE flip (translate by
-- r) — the carrier-generic Cantor/Lawvere diagonal atom. So the ν-step bounded uniqueness
-- (`BackedGradedStencil.ν-step` ← recon-bounded-unique) holds precisely BECAUSE the residue is
-- fixed-point-free off the identity corner: diagonalization ≡ fixed-point ≡ wedge-residue, as
-- `Category.Lawvere` proves generically.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.BackedGradedDiagonal where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; suc-injective)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Category.Lawvere using (TorsorAtom; FixedPointFree; prove-or-correct)

------------------------------------------------------------------------
-- ① The additive residue fixes x only when it is the unit 0 (the `fix→unit` law, by induction on x).
------------------------------------------------------------------------

+-fix→zero : (r x : ℕ) → r + x ≡ x → r ≡ 0
+-fix→zero r zero     eq = trans (sym (+-identityʳ r)) eq
+-fix→zero r (suc x') eq = +-fix→zero r x' (suc-injective (trans (sym (+-suc r x')) eq))

------------------------------------------------------------------------
-- ② The wedge residue as a Lawvere TorsorAtom (_∙_ = +, e = 0). The residue vanishes exactly at the
--    unit — the identity corner / reflexive diagonal of the wedge (a = recon 1 a 0 = a).
------------------------------------------------------------------------

residue-torsor : TorsorAtom ℕ
residue-torsor = record { _∙_ = _+_ ; e = 0 ; fix→unit = +-fix→zero }

------------------------------------------------------------------------
-- ③ The DIAGONAL DICHOTOMY (prove-or-correct): every residue is either 0 (clean — the diagonal) or a
--    genuine FIXED-POINT-FREE flip. No third branch — the residue is never a dead end. This is the
--    residue-IS-the-diagonal, the Lawvere-fixed-point uniqueness the stencil (P1b) already instantiates,
--    now made explicit as the Cantor/Lawvere atom.
------------------------------------------------------------------------

dec-zero : (r : ℕ) → (r ≡ 0) ⊎ (r ≡ 0 → ⊥)
dec-zero zero    = inj₁ refl
dec-zero (suc r) = inj₂ (λ ())

residue-diagonal : (r : ℕ) → (r ≡ 0) ⊎ FixedPointFree ℕ
residue-diagonal = prove-or-correct residue-torsor dec-zero
