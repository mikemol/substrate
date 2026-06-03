------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.SingerOrder
--
-- Re-export shim (theorem-per-file policy): the structural order-7 proof
-- for the Sylow-7 Singer generator is decomposed into SingerOrder/.
-- HasOrder-singer remains available here for existing consumers
-- (AlternativesAsOrbit, MultiRouteEquivariance.SingerGL).
--
-- Decomposition (each file one lemma, one-pass-reasonable):
--   SingerOrder.Commutes  — singer-commutes (action ∘ point-to-vec)
--   SingerOrder.Iterate   — singer^ + iterate-commutes
--   SingerOrder.OnBasis   — order-on-basis (via the Point 7-cycle)
--   SingerOrder.HasOrder  — HasOrder-singer (linear-extensionality lift)
--
-- The proof routes through the Fano Point 7-cycle, never the dense matrix
-- power — robust under the linear-from-images opacity seal. See the
-- submodules for the structural detail.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.SingerOrder where

open import Substrate.Algebra.GL3F2.SingerOrder.HasOrder public
  using (HasOrder-singer)
