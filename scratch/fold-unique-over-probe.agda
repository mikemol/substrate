-- (--guardedness because this probe sits OUTSIDE the library, so it does not
-- inherit substrate.agda-lib's global `flags:` — ⟡guardedness-global, e66a541.)
{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- ⟡fold-unique-over — THE NON-VACUITY POLE.
--
-- fold-unique-over is only worth having if it ADMITS a case `fold-unique`
-- (at _≡_) cannot reach without funext. This probe exhibits one: a
-- FUNCTION-VALUED carrier with the pointwise equality _≐_.
--
-- This is the shape ⟡leibniz-over-Sn's flat matrix carrier needs
-- (C n = Fin (n * n) → A), and the shape `Endo n = Fin n → Fin n` already
-- uses via `lookup-hom : GradedHomOver ⊗-over endo-over _≐_`.
------------------------------------------------------------------------

module fold-unique-over-probe where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold; fold-unique; fold-unique-over)

-- A FUNCTION-VALUED graded carrier — the `Fin <index> → A` shape the flat
-- matrix carrier wants. `_≡_` on these is useless without funext.
-- ⚑ The index must be GENUINE: a constant family (FC _ = ℕ → ℕ) leaves `n`
-- un-inferable in `_≐_ : {n} → FC n → FC n → Set` and yields unsolved metas.
FC : ℕ → Set
FC n = Fin n → ℕ

-- the pointwise / funext-free target equality (the `_≐_` shape)
_≐_ : {n : ℕ} → FC n → FC n → Set
_≐_ {n} f g = (k : Fin n) → f k ≡ g k

-- ⚑ ONLY transitivity and step-congruence are required — NOT an equivalence.
-- Note we never write ≐-refl or ≐-sym: the induction genuinely does not use them.
≐-trans : {n : ℕ} {x y z : FC n} → x ≐ y → y ≐ z → x ≐ z
≐-trans p q k = trans (p k) (q k)

-- a concrete grade-raising step that GENUINELY uses its argument (so the
-- congruence below is not vacuous): extend by a new slot at position zero.
ext : {n : ℕ} → FC n → FC (suc n)
ext c zero    = zero
ext c (suc k) = suc (c k)

sucAlg : LehmerAlgebra FC
sucAlg = record { base = λ () ; step = λ c _ → ext c }

≐-step-suc : {n : ℕ} {x y : FC n} (p : Fin (suc n)) →
             x ≐ y → step sucAlg x p ≐ step sucAlg y p
≐-step-suc _ e zero    = refl
≐-step-suc _ e (suc k) = cong suc (e k)

------------------------------------------------------------------------
-- THE POLE: initiality of the tower at a FUNCTION-valued carrier, stated
-- POINTWISE. `fold-unique` cannot state this (its conclusion would be a
-- function `_≡_`); `fold-unique-over` discharges it by instantiation.
------------------------------------------------------------------------

sucAlg-unique :
  (g : ∀ {n} → LehmerPath n → FC n) →
  (g start ≐ base sucAlg) →
  (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≐ step sucAlg (g l) p) →
  ∀ {n} (l : LehmerPath n) → g l ≐ fold sucAlg l
sucAlg-unique = fold-unique-over _≐_ ≐-trans sucAlg ≐-step-suc

------------------------------------------------------------------------
-- AND THE CO-APEX HOLDS DEFINITIONALLY: `fold-unique` IS the _≡_ instance.
-- If the identification were merely asserted in prose this would not typecheck.
------------------------------------------------------------------------

fold-unique-is-the-≡-instance :
  ∀ {C : ℕ → Set} (alg : LehmerAlgebra C) →
  fold-unique alg
  ≡ fold-unique-over _≡_ trans alg (λ p e → cong (λ z → step alg z p) e)
fold-unique-is-the-≡-instance alg = refl
