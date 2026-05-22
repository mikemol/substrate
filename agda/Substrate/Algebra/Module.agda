------------------------------------------------------------------------
-- Substrate.Algebra.Module
--
-- Mod1 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- A Module over a Ring R bundles:
--   * The Ring R (the scalar source)
--   * An AbelianGroup on the module carrier M (the additive structure)
--   * A scalar multiplication R × M → M
--   * Four module axioms:
--     - distributivity over scalar sum: (r + s) ·M m = r·M m + s·M m
--     - distributivity over vector sum: r ·M (m + n) = r·M m + r·M n
--     - scalar-mult associativity:      (r ·R s) ·M m = r ·M (s ·M m)
--     - identity scalar:                1 ·M m = m
--
-- F₂-Vector and ℚ-Vector retrofit as Module instances at Mod6 /
-- Mod7. The visible-surface vector laws cascade as Module-
-- accessor projections.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Module where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup)
open import Substrate.Algebra.Group using (Group; monoid)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup; group)
open import Substrate.Algebra.Semiring using (Semiring; +-monoid; *-monoid)
open import Substrate.Algebra.Ring using (Ring; semiring)

------------------------------------------------------------------------
-- 1. The Module record.
--
-- Parametric in a Ring R and a carrier M (set). Bundles the
-- AbelianGroup on M + scalar multiplication + 4 module axioms.
------------------------------------------------------------------------

record Module {A : Set} (R : Ring A) (M : Set) : Set where
  field
    -- Additive structure on M.
    M-abelian : AbelianGroup M
    -- Scalar multiplication R × M → M.
    _·ₛ_ : A → M → M
    -- Module axioms.
    distrib-scalar :
      (r s : A) (m : M) →
      let _+R_ = Magma._·_ (magma (semigroup (+-monoid (semiring R))))
          _+M_ = Magma._·_ (magma (semigroup (monoid (group M-abelian))))
      in (r +R s) ·ₛ m ≡ (r ·ₛ m) +M (s ·ₛ m)
    distrib-vector :
      (r : A) (m n : M) →
      let _+M_ = Magma._·_ (magma (semigroup (monoid (group M-abelian))))
      in r ·ₛ (m +M n) ≡ (r ·ₛ m) +M (r ·ₛ n)
    scalar-mult-assoc :
      (r s : A) (m : M) →
      let _·R_ = Magma._·_ (magma (semigroup (*-monoid (semiring R))))
      in (r ·R s) ·ₛ m ≡ r ·ₛ (s ·ₛ m)
    identity-scalar :
      (m : M) →
      let 1R = Monoid.ε (*-monoid (semiring R))
      in 1R ·ₛ m ≡ m

open Module public

------------------------------------------------------------------------
-- 2. Capstone for Mod1.
--
-- Module-over-Ring defined. Mod2 supplies ModuleHom records (the
-- structure-preserving maps between Modules).
------------------------------------------------------------------------
