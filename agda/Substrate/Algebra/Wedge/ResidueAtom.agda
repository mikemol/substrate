------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.ResidueAtom
--
-- KEYSTONE #1, the carrier-generic direction landed. The wedge residue r in
-- `a = recon q b r`, when r ≢ z, is a genuine distinction; concretely it gives
-- a FIXED-POINT-FREE flip (translation by r) — the same atom as Cantor's
-- diagonal, the grade ★, the cone apex (Category.Lawvere). This module shows
-- that atom is populated over DIFFERENT carriers via Lawvere.translate-fpf, so
-- it is genuinely carrier-generic, not an F₂ accident:
--
--   * F₂ : translation by 𝟙 (≢ 𝟘) is fixed-point-free   (recovers flip-disagrees)
--   * ℕ  : translation by suc k (≢ 0) is fixed-point-free (successor-translation)
--
-- The TorsorAtom hypothesis (g ∙ x ≡ x ⟹ g ≡ e) is cancellation: the only
-- translation with a fixed point is the unit. A wedge carrier with cancellative
-- recon and a non-zero residue thus ALWAYS hands back a fixed-point-free flip —
-- the residue refuses to vanish, which is exactly why the prove-or-correct
-- engine never dead-ends.
--
-- WHAT'S DONE vs WHAT REMAINS (keystone #1, scoped honestly). The Free⊣Forgetful
-- TRIANGLE is already the wedge witness itself — Algebra.Wedge.forget-correct
-- (forget w ≡ a, the reconstruction). This module adds the OTHER half: a
-- non-zero residue is a fixed-point-free correction (residue ⟹ FixedPointFree),
-- over multiple carriers. Together they ARE the prove-or-correct content of
-- keystone #1: a wedge either reconstructs cleanly (r = z) or hands back a
-- genuine fixed-point-free correction (r ≢ z) — never a dead end. What remains
-- is only the certified (r<b) CANONICALITY of that residue (uniqueness of the
-- comparison representative) — a smallness refinement, not a missing identity.
-- Both halves are MECHANIZED in Substrate.Algebra.Wedge.ResidueAtom.Properties
-- (keystone-triangle + prove-or-correct over F₂ and ℕ) — the fix is proved,
-- not just claimed.
--
-- No data/record declared here (instances are record VALUES) ⟹ exempt from the
-- def/proof gate though it imports Foundation.Nat.Properties.Add. Zero
-- postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.ResidueAtom where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-suc)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; 𝟙≢𝟘)
  renaming (_+_ to _+₂_)
open import Substrate.Category.Lawvere using (FixedPointFree; TorsorAtom; translate-fpf)

------------------------------------------------------------------------
-- 1. F₂ as a torsor atom: g +₂ x ≡ x ⟹ g ≡ 𝟘 (by F₂'s own disjointness).
------------------------------------------------------------------------

F₂-torsor : TorsorAtom F₂
F₂-torsor = record { _∙_ = _+₂_ ; e = 𝟘 ; fix→unit = f2-fix }
  where
    f2-fix : (g x : F₂) → (g +₂ x) ≡ x → g ≡ 𝟘
    f2-fix 𝟘 _ _  = refl
    f2-fix 𝟙 𝟘 ()        -- 𝟙 +₂ 𝟘 = 𝟙 ≡ 𝟘 is absurd
    f2-fix 𝟙 𝟙 ()        -- 𝟙 +₂ 𝟙 = 𝟘 ≡ 𝟙 is absurd

-- the F₂ residue flip (translate by 𝟙): fixed-point-free — recovers flip-disagrees.
F₂-residue-fpf : FixedPointFree F₂
F₂-residue-fpf = translate-fpf F₂-torsor 𝟙 𝟙≢𝟘

------------------------------------------------------------------------
-- 2. ℕ as a torsor atom: g + x ≡ x ⟹ g ≡ 0 (cancellation, by induction on x).
------------------------------------------------------------------------

suc-inj : {m n : ℕ} → suc m ≡ suc n → m ≡ n
suc-inj refl = refl

ℕ-torsor : TorsorAtom ℕ
ℕ-torsor = record { _∙_ = _+_ ; e = zero ; fix→unit = nat-fix }
  where
    nat-fix : (g x : ℕ) → (g + x) ≡ x → g ≡ zero
    nat-fix g zero    eq = trans (sym (+-identityʳ g)) eq
    nat-fix g (suc x) eq = nat-fix g x (suc-inj (trans (sym (+-suc g x)) eq))

-- the ℕ residue flip (translate by a non-zero suc k): fixed-point-free.
ℕ-residue-fpf : (k : ℕ) → FixedPointFree ℕ
ℕ-residue-fpf k = translate-fpf ℕ-torsor (suc k) (λ ())
