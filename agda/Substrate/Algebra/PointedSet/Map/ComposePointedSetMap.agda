------------------------------------------------------------------------
-- Substrate.Algebra.PointedSet.Map.ComposePointedSetMap
--
-- Defines: compose-PointedSetMap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.PointedSet.Map; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PointedSet.Map.ComposePointedSetMap where

open import Substrate.Algebra.PointedSet
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.PointedSet.Map.Anon



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
