------------------------------------------------------------------------
-- Substrate.Geometry.PG
--
-- M-11 full machinery sub-slice 2. The projective space PG(n, F₂) =
-- (F₂^(n+1) \ {𝟎}) / F₂* as a parametric type.
--
-- File-per-lemma decomposition per [[s3-on-v4-file-per-lemma]]:
--
--   Type         — the PG record (Σ of nonzero vectors)
--   Projections  — PG-coords, PG-nonzero
--   Preserves    — Preserves-Nonzero predicate
--   Action       — PG-act (linear action on PG)
--
-- Specific instances in the codebase:
--   PG(0, F₂) = F₂ \ {𝟎} = {𝟙}                  (1 point)
--   PG(1, F₂) = F₂² \ {𝟎}                       (3 points)
--   PG(2, F₂) = F₂³ \ {𝟎}                       (7 points = Fano plane)
--   PG(3, F₂) = F₂⁴ \ {𝟎}                       (15 points)
--
-- PG(n, F₂) is the "chirality-choice phase space" at dimension n+1.
-- The GL(n+1, F₂) action permutes points via Preserves-Nonzero
-- (automatic for invertible maps).
--
-- Connection to existing types:
--   * Fano (M-9): Substrate.Geometry.Fano.Point = Fin 7 parametrises
--     PG(2, F₂) via point-coords : Fin 7 → Vector 3. A formal
--     Bijection Point (PG 2) requires a "decoder" from Vector 3 ≠ 𝟎ⱽ
--     to Fin 7 (syndrome lookup); deferred.
--   * M-11.fano: chirality at Fano point p ↔ chirality at PG-coords p.
--   * Gl3.agda provides σ and τ generators; transitivity of the
--     orbit at n=2 is concrete via combined cycle structures.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.PG where

open import Substrate.Geometry.PG.Type
open import Substrate.Geometry.PG.Projections
open import Substrate.Geometry.PG.Preserves
open import Substrate.Geometry.PG.Action