------------------------------------------------------------------------
-- Substrate.Algebra.Module.Hom
--
-- Mod2 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- A ModuleHom is a function between two R-modules preserving both
-- + (the AbelianGroup structure) and scalar mult. The standard
-- structure-preserving map of module theory.
--
-- ModuleHom is the universal "Linear map" — F₂.Linear and ℚ.Linear
-- both retrofit as ModuleHom instances at Mod6 / Mod7.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Module.Hom where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup)
open import Substrate.Algebra.Group using (Group; monoid)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup; group)
open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.Module using (Module; M-abelian; _·ₛ_)

------------------------------------------------------------------------
-- 1. The ModuleHom record.
--
-- Parametric in a Ring R + two R-modules M and N. The hom is a
-- function M → N preserving the AbelianGroup + and the scalar mult.
------------------------------------------------------------------------

record ModuleHom
  {A : Set} {R : Ring A} {M N : Set}
  (Mod-M : Module R M)
  (Mod-N : Module R N)
  : Set where
  field
    apply : M → N
    preserves-+ :
      (m n : M) →
      let _+M_ = Magma._·_ (magma (semigroup (monoid (group (M-abelian Mod-M)))))
          _+N_ = Magma._·_ (magma (semigroup (monoid (group (M-abelian Mod-N)))))
      in apply (m +M n) ≡ (apply m) +N (apply n)
    preserves-scalar :
      (r : A) (m : M) →
      apply (Module._·ₛ_ Mod-M r m) ≡ Module._·ₛ_ Mod-N r (apply m)

open ModuleHom public

------------------------------------------------------------------------
-- 2. Capstone for Mod2.
--
-- ModuleHom defined. Mod3 supplies identity + composition; Mod4
-- the FreeModule R n; Mod5 the basis universal property.
------------------------------------------------------------------------
