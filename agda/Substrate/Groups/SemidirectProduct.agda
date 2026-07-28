------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct
--
-- S9 of slice 3: the V_4 ⋊ S_3 ≅ S_4 factorisation theorem.
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]] +
-- [[feedback-expose-generator-not-orbit]]: the former 378-line module
-- is now a re-export shim over four submodules in SemidirectProduct/.
-- Pre-generator orbit-cataloguing (13 per-axis sibling aliases) was
-- deleted; the parametric *-anchor forms are the load-bearing surface.
--
-- Re-published intentionally (parametric forms only):
--   * Stab (axis-parametric predicate)
--   * v-of-axis-unique, v-for
--   * v-of-axis-anchor, v-of-axis-anchor-sends
--   * v-for-anchor, v-for-anchor-sends
--   * s-for, s-for-anchor, s-for-fixes-anchor
--   * factorisation, V₄-cap-Stab-trivial
--   * (transitive) v-of-axis, axis-of-v, act-axis-as-V₄-mult, round-trips
--
-- Deleted (D-specialised orbit elements — callers use parametric forms):
--   * Stab-{D,C,S,W} — use `Stab X` directly
--   * v-of-axis-sends-D — use `v-of-axis-anchor-sends D` (definitionally same)
--   * s-for-fixes-D — use `s-for-fixes-anchor D` (definitionally same via
--     v-of-axis-anchor D x ≡ v-of-axis x special case in V.agda)
--   * v-for-sends-D, factorisation-unique-V₄, SemidirectFactorisation,
--     semidirect-factorisation — no callers
--
-- See: catalog/cocycles.md § CY-5 — Hodge-dual reading;
--      catalog/cocycles.md § Metacircularity — V_4 ⋊ S_3 as primary
--      formal foundation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct where

open import Substrate.Groups.SemidirectProduct.Stab
open import Substrate.Groups.SemidirectProduct.V
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Groups.SemidirectProduct.Factorisation
-- Historic re-export of V4-Embedding names that downstream modules
-- imported from SemidirectProduct.
open import Substrate.Groups.V4-Embedding
  using (v-of-axis; axis-of-v; act-axis-as-V₄-mult;
         axis-of-v-v-of-axis; v-of-axis-axis-of-v)
