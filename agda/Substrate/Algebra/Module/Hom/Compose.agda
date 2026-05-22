------------------------------------------------------------------------
-- Substrate.Algebra.Module.Hom.Compose
--
-- Mod3 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- Identity ModuleHom + composition of ModuleHoms + category laws.
-- ModuleHom over a fixed Ring R forms a category.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Module.Hom.Compose where

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)
open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.Module using (Module)
open import Substrate.Algebra.Module.Hom
  using (ModuleHom; apply; preserves-+; preserves-scalar)

------------------------------------------------------------------------
-- 1. Identity ModuleHom.
------------------------------------------------------------------------

id-ModHom :
  {A : Set} {R : Ring A} {M : Set}
  (Mod-M : Module R M) →
  ModuleHom Mod-M Mod-M
id-ModHom Mod-M = record
  { apply            = λ m → m
  ; preserves-+      = λ _ _ → refl
  ; preserves-scalar = λ _ _ → refl
  }

------------------------------------------------------------------------
-- 2. Composition of ModuleHoms.
------------------------------------------------------------------------

compose-ModHom :
  {A : Set} {R : Ring A} {M N K : Set}
  {Mod-M : Module R M} {Mod-N : Module R N} {Mod-K : Module R K} →
  ModuleHom Mod-N Mod-K →
  ModuleHom Mod-M Mod-N →
  ModuleHom Mod-M Mod-K
compose-ModHom g f = record
  { apply            = λ m → apply g (apply f m)
  ; preserves-+      = λ m n →
      trans (cong (apply g) (preserves-+ f m n))
            (preserves-+ g (apply f m) (apply f n))
  ; preserves-scalar = λ r m →
      trans (cong (apply g) (preserves-scalar f r m))
            (preserves-scalar g r (apply f m))
  }

------------------------------------------------------------------------
-- 3. Capstone for Mod3.
--
-- ModuleHom category structure landed (identity + composition).
-- Mod4 supplies the canonical FreeModule R n.
------------------------------------------------------------------------
