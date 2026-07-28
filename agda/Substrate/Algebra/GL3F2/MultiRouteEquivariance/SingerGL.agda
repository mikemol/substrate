------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerGL
--
-- Sylow-7 generator as a GL3F2 value. The left witness:
--   apply (L-iterate 6 singer) (apply singer v)
--     ≡ iterate 6 (apply singer) (apply singer v)   [iterate-apply-as-L-iterate]
--     ≡ iterate 7 (apply singer) v                   [collapse]
--     ≡ v                                            [HasOrder-singer]
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerGL where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order using (iterate-apply-as-L-iterate)
open import Substrate.Algebra.GL3F2 using (GL3F2; mkGL3F2)
open import Substrate.Algebra.GL3F2.GaugeGenerators using (singer-Linear)
open import Substrate.Algebra.GL3F2.SingerOrder.HasOrder using (HasOrder-singer)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerInv using (singer-inv)

singer-GL : GL3F2
singer-GL = mkGL3F2 singer-Linear singer-inv left-witness right-witness
  where
    left-witness :
      (v : Vector 3) →
      apply singer-inv (apply singer-Linear v) ≡ v
    left-witness v =
      trans (sym (iterate-apply-as-L-iterate singer-Linear 6 (apply singer-Linear v)))
            (HasOrder-singer v)

    right-witness :
      (v : Vector 3) →
      apply singer-Linear (apply singer-inv v) ≡ v
    right-witness v =
      trans (cong (apply singer-Linear)
                  (sym (iterate-apply-as-L-iterate singer-Linear 6 v)))
            (HasOrder-singer v)
