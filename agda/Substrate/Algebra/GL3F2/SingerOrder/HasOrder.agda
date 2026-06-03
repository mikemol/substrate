------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.SingerOrder.HasOrder
--
-- HasOrder-singer : the Sylow-7 generator singer-Linear has order 7 as a
-- linear endomap of Vector 3.
--
-- Lifts the basis-vector agreement (order-on-basis) to ALL vectors via
-- linear-extensionality — basis-only, so it never reduces the dense apply
-- on a general vector (robust under the linear-from-images opacity seal).
-- This is the structural replacement for the former 8-case `refl`
-- enumeration that silently banked transparent dense reduction.
--
-- Per [[expose-generator-not-orbit]] / [[multi-route-equivariance-recovery]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.SingerOrder.HasOrder where

open import Substrate.Foundation.Eq using (sym; trans)

open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; id-L)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order
  using (L-iterate; iterate-apply-as-L-iterate)
open import Substrate.Algebra.F2.FanoPlane using (singer-Linear)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
open import Substrate.Algebra.GL3F2.SingerOrder.OnBasis using (order-on-basis)

HasOrder-singer : HasOrder (apply singer-Linear) 7
HasOrder-singer v =
  trans (iterate-apply-as-L-iterate singer-Linear 7 v)
        (linear-extensionality
          (L-iterate 7 singer-Linear) id-L
          (λ i → trans (sym (iterate-apply-as-L-iterate singer-Linear 7 (basis i)))
                       (order-on-basis i))
          v)
