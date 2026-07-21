{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.MonoCommMonoid — ⟡jac-det-via-sppf, RUNG 2 (monomials).
--
-- `JacobianResidue.Mono = mono ℕ ℕ ℕ` (an exponent triple xᵃyᵇzᶜ) IS the free
-- commutative monoid on {x,y,z}: the exponent vector is the canonical
-- sorted-word representative, and `addM` (componentwise +) is its operation.
-- This homes the bespoke `Mono` natively in the CommutativeMonoid tower — the
-- discoverability cover the re-aim owes (⟡memory-discoverability-owes-building):
-- `Mono`/`addM`/`mono 0 0 0` ARE the commutative-monoid ops, proven, not asserted.
--
-- ⚑ THE MONOMIAL LAYER, NOT THE POLYNOMIAL LAYER. `Mono` was never the bespoke
-- debt — an exponent triple is ALREADY canonical (`eqM` is decidable triple
-- equality). The debt is the un-normalised POLYNOMIAL `MPoly = List Term` (like
-- terms combined only at `coeff` read-off) with no `Semiring` instance.
--
-- ⚑ HONEST BOUNDARY (the det-lift gate, precisely). Reusing `LeibnizDet.det`
-- natively over `MPoly` needs `Semiring MPoly`. The `Semiring` record needs NO
-- additive commutativity — so one might hope raw `MPoly` (with `_+P_ = ++`) is a
-- Semiring up to `≡`. It is NOT: `distrib-right` FAILS — `p *P (q +P r)` lists
-- its terms `[t·q][t·r][p'·q][p'·r]` while `(p*Pq) +P (p*Pr)` gives
-- `[t·q][p'·q][t·r][p'·r]` (the middle blocks swapped), and `++` cannot reorder.
-- So `Semiring MPoly` genuinely requires a NORMALISED polynomial (sorted-by-`Mono`,
-- coefficients combined) whose `+P` is a commutative merge — this monomial
-- CommutativeMonoid is its base (`ℤ[Mono]`), and that normalised Semiring +
-- `det {3} JacMat` is the remaining det-lift rung. Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.MonoCommMonoid where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat.Properties.Add
  using (+-assoc; +-identityʳ; +-comm)
open import Substrate.Category.CommutativeMonoid using (CommutativeMonoid)
open import Substrate.Algebra.Z.JacobianResidue using (Mono; mono; addM)

-- congruence in three arguments (for the 3-generator monomial).
cong₃ : {A B C D : Set} (f : A → B → C → D)
        {a a' : A} {b b' : B} {c c' : C} →
        a ≡ a' → b ≡ b' → c ≡ c' → f a b c ≡ f a' b' c'
cong₃ f refl refl refl = refl

------------------------------------------------------------------------
-- Mono is a CommutativeMonoid under (addM, mono 0 0 0) — the free commutative
-- monoid on {x,y,z}, all laws componentwise from ℕ's additive monoid.
------------------------------------------------------------------------

addM-assoc : (m n o : Mono) → addM (addM m n) o ≡ addM m (addM n o)
addM-assoc (mono a b c) (mono d e f) (mono g h i) =
  cong₃ mono (+-assoc a d g) (+-assoc b e h) (+-assoc c f i)

-- 0 + x reduces (ℕ +-identityˡ is refl), so the left unit is definitional.
addM-idˡ : (m : Mono) → addM (mono 0 0 0) m ≡ m
addM-idˡ (mono a b c) = refl

addM-idʳ : (m : Mono) → addM m (mono 0 0 0) ≡ m
addM-idʳ (mono a b c) =
  cong₃ mono (+-identityʳ a) (+-identityʳ b) (+-identityʳ c)

addM-comm : (m n : Mono) → addM m n ≡ addM n m
addM-comm (mono a b c) (mono d e f) =
  cong₃ mono (+-comm a d) (+-comm b e) (+-comm c f)

Mono-CommMonoid : CommutativeMonoid Mono addM (mono 0 0 0)
Mono-CommMonoid = record
  { +R-assoc     = addM-assoc
  ; +R-identityˡ = addM-idˡ
  ; +R-identityʳ = addM-idʳ
  ; +R-comm      = addM-comm
  }
