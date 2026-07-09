------------------------------------------------------------------------
-- Substrate.Algebra.PointedSet.Map
--
-- F1m2 of the F₁-modules arc per [scratch/m_mod_arc_plan.md].
--
-- A PointedSetMap is a function f : A → B between PointedSets that
-- preserves the basepoint: f base ≡ base. This is the
-- structure-preserving morphism for pointed sets.
--
-- F₁-Module-Hom = PointedSetMap. The base-preservation discipline
-- is what makes F₁ semantics structural rather than ad-hoc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PointedSet.Map where

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.PointedSet using (PointedSet; Carrier; base)

------------------------------------------------------------------------
-- 1. The PointedSetMap record.
------------------------------------------------------------------------

-- ⟡set1-paydown (PointedSet now parameterizes its carrier): the record takes the
-- two carriers as module parameters; `Carrier P`/`Carrier Q` resolve via the compat
-- accessor. PointedSetMap already lived in Set — this only threads the carrier index.
module _ {A B : Set} where
  record PointedSetMap (P : PointedSet A) (Q : PointedSet B) : Set where
    field
      apply        : Carrier P → Carrier Q
      base-preserv : apply (base P) ≡ base Q

  open PointedSetMap public

------------------------------------------------------------------------
-- 2. Identity + composition.
------------------------------------------------------------------------

id-PointedSetMap : {A : Set} (P : PointedSet A) → PointedSetMap P P
id-PointedSetMap P = record
  { apply        = λ x → x
  ; base-preserv = refl
  }

compose-PointedSetMap :
  {A B D : Set} {P : PointedSet A} {Q : PointedSet B} {R : PointedSet D} →
  PointedSetMap Q R →
  PointedSetMap P Q →
  PointedSetMap P R
compose-PointedSetMap g f = record
  { apply        = λ x → apply g (apply f x)
  ; base-preserv = trans (cong (apply g) (base-preserv f)) (base-preserv g)
  }

------------------------------------------------------------------------
-- 3. Capstone for F1m2.
--
-- PointedSetMap + category structure (identity + composition)
-- landed. F1m3 identifies F₁-Module ≡ PointedSet.
------------------------------------------------------------------------
