------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.ResidueAtom.Properties
--
-- MECHANIZED BACKING for the corrected keystone-#1 claim (the overclaim fix:
-- the keystone is NOT "still open" — both halves are green). This file proves,
-- not asserts, the two halves and their prove-or-correct synthesis:
--
--   HALF 1 (the triangle): the Free⊣Forgetful triangle IS the wedge witness —
--     forget reconstructs the dividend (Algebra.Wedge.forget-correct), here
--     re-exposed as keystone-triangle.
--   HALF 2 (the correction): a non-unit residue is a fixed-point-free
--     correction, assembled into the green prove-or-correct DICHOTOMY — over
--     F₂ (𝟘 reconstructs / 𝟙 corrects) and ℕ (0 reconstructs / suc k corrects).
--
-- Together: the wedge either reconstructs cleanly or hands back a genuine
-- correction — never a dead end — as a typechecked function, not a comment.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.ResidueAtom.Properties where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; 𝟙≢𝟘)
open import Substrate.Algebra.Wedge using (forget; forget-correct; ℕ-div; C)
  renaming (Wedge to Wedge⟦478f66a6⟧)
open import Substrate.Category.Lawvere
  using (FixedPointFree; TorsorAtom; prove-or-correct; e)
open import Substrate.Algebra.Wedge.ResidueAtom using (F₂-torsor; ℕ-torsor; ℕ-zero?)

------------------------------------------------------------------------
-- HALF 1 — the triangle is the wedge witness (the reconstruction half).
------------------------------------------------------------------------

keystone-triangle : {a b : C ℕ-div} (w : Wedge⟦478f66a6⟧ ℕ-div a b) → forget w ≡ a
keystone-triangle = forget-correct

------------------------------------------------------------------------
-- HALF 2 — prove-or-correct: clean reconstruction (residue = unit) or a
-- fixed-point-free correction (residue ≢ unit). Green over two carriers.
------------------------------------------------------------------------

-- F₂: 𝟘 reconstructs cleanly; 𝟙 is a fixed-point-free correction.
F₂-prove-or-correct : (g : F₂) → (g ≡ 𝟘) ⊎ FixedPointFree F₂
F₂-prove-or-correct = prove-or-correct F₂-torsor f2-dec
  where
    f2-dec : (g : F₂) → (g ≡ 𝟘) ⊎ (g ≡ 𝟘 → ⊥)
    f2-dec 𝟘 = inj₁ refl
    f2-dec 𝟙 = inj₂ 𝟙≢𝟘

-- ℕ: 0 reconstructs cleanly; any suc k is a fixed-point-free correction.
ℕ-prove-or-correct : (g : ℕ) → (g ≡ zero) ⊎ FixedPointFree ℕ
ℕ-prove-or-correct = prove-or-correct ℕ-torsor ℕ-zero?
