------------------------------------------------------------------------
-- Substrate.Algebra.PointedSet.Map.Anon
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.PointedSet.Map; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PointedSet.Map.Anon where

open import Substrate.Algebra.PointedSet
open import Substrate.Foundation.Eq



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
