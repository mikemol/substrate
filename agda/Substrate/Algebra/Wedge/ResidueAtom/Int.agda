------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.ResidueAtom.Int
--
-- ℤ as a TORSOR ATOM, and the FixedPointFree that falls out of it.
--
-- ⚑ THIS IS THE THIRD CARRIER, AND THE POINT IS THAT IT COST SIX LINES.
-- `Category.Lawvere` carries a GENERIC populator — `TorsorAtom` /
-- `translate-fpf` (Lawvere.agda:245-270) — whose hypothesis is CANCELLATION.
-- Package a carrier's cancellation once and its residue-translation is
-- fixed-point-free for free; every Cantor/Lawvere consequence follows.
--
-- ⚑ AND IT DOES NOT WAIT ON THE `r<b` KEYSTONE.  `Lawvere.agda:12-17` reads as
-- though the certified residue `r<b` were the precondition for populating
-- `FixedPointFree` generically.  It is not, and the tree already says so:
-- `ResidueAtom.agda:20-31` — *"the keystone is NOT 'still open' … what remains
-- is only the certified (r<b) CANONICALITY of that residue — a smallness
-- refinement, not a missing identity"* — with `ResidueAtom/Properties.agda:4-6`
-- calling itself *"the overclaim fix"*.  `r<b` buys residue UNIQUENESS, which
-- is a different theorem from residue EXISTENCE.
--
-- Of ~19 DivStr / GradedDivStr carriers in the tree, `F₂` and `ℕ` were packaged
-- (ResidueAtom.agda:61,80) and the rest were not.  ℤ is the natural next: its
-- cancellation is SHORTER than ℕ's, because additive inverses discharge it
-- directly where ℕ needs induction on the second argument (ResidueAtom.agda:83-85).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.ResidueAtom.Int where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Properties.Add
open import Substrate.Category.Lawvere using (FixedPointFree; TorsorAtom; translate-fpf)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. ℤ as a torsor atom: g +ℤ x ≡ x ⟹ g ≡ 0ℤ.
--
-- The proof is the group-theoretic one and needs no induction: translate
-- both sides by -ℤ x, then assoc / inverseʳ / identityʳ collapse the left.
------------------------------------------------------------------------

ℤ-torsor : TorsorAtom ℤ
ℤ-torsor = record { _∙_ = _+ℤ_ ; e = 0ℤ ; fix→unit = int-fix }
  where
    int-fix : (g x : ℤ) → (g +ℤ x) ≡ x → g ≡ 0ℤ
    int-fix g x eq =
      trans (sym (+ℤ-identityʳ g))
      (trans (cong (g +ℤ_) (sym (+ℤ-inverseʳ x)))
      (trans (sym (+ℤ-assoc g x (-ℤ x)))
             (trans (cong (_+ℤ (-ℤ x)) eq) (+ℤ-inverseʳ x))))

------------------------------------------------------------------------
-- 2. The ℤ residue flip: translation by any non-zero g is fixed-point-free.
--
-- ⚑ NOTE THE SHAPE OF THE HYPOTHESIS.  `translate-fpf` wants `g ≢ e`, so on ℤ
-- the caller supplies WHICH non-zero translation — unlike F₂, where 𝟙 is the
-- only non-unit and the instance can be closed (ResidueAtom.agda:70).  ℕ has
-- the same shape (`ℕ-residue-fpf` takes a `k` and translates by `suc k`); ℤ is
-- the first carrier where the non-units come in two signs.
------------------------------------------------------------------------

ℤ-residue-fpf : (g : ℤ) → (g ≡ 0ℤ → ⊥) → FixedPointFree ℤ
ℤ-residue-fpf g g≢0 = translate-fpf ℤ-torsor g g≢0

-- the two canonical witnesses: +1 and -1 are non-zero by constructor
-- disjointness, so each gives a closed instance with no hypothesis to discharge.
ℤ-residue-fpf-succ : FixedPointFree ℤ
ℤ-residue-fpf-succ = ℤ-residue-fpf (+ 1) (λ ())

ℤ-residue-fpf-pred : FixedPointFree ℤ
ℤ-residue-fpf-pred = ℤ-residue-fpf (-suc 0) (λ ())
