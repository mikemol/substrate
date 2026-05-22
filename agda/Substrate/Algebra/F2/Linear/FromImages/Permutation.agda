------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]]: the
-- former 413-line module is now a thin re-export shim over six
-- submodules in Permutation/.
--
-- Submodule decomposition:
--   Permutation.Iterate      — σ-iterate, HasOrderPerm, additivity,
--                              HasOrderPerm-multiple.
--   Permutation.Compose      — HasOrderPerm-compose-commute-order-2
--                              (V₄-shape).
--   Permutation.Linear       — basis-permutation-Linear,
--                              apply-basis-permutation-Linear,
--                              compose-at-basis, id-at-basis.
--   Permutation.Involution   — basis-permutation-involution (order-2).
--   Permutation.IterateLift  — iterate-on-basis,
--                              basis-permutation-order-k.
--   Permutation.Order        — L-iterate, iterate-apply-as-L-iterate,
--                              HasOrder-from-perm,
--                              HasOrderPerm-multiple-Linear.
--
-- All public names from the original file remain available via the
-- re-exports below; existing callers (HodgeStar, etc.) need no edits.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]: the
-- decomposition is purely structural — each submodule names one
-- universal-property cluster; the shim is the colimit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation where

open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate     public
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Compose     public
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear      public
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Involution  public
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.IterateLift public
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order       public
