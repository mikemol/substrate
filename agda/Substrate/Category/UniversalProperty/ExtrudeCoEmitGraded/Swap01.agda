------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap01
--
-- Defines: swap01
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Swap01 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- The HIGHER-ORDER FINITE (operator: final ≡ [~, terminal/ν] does NOT live on the carrier — it's COMPOSED of
-- reformulating each V₄ leg as "finite FROM A DIFFERENT PERSPECTIVE", a higher-order finite satisfied by PERMUTING
-- through the S₃-permutations of V₄'s 3 involutions). Each axis is finite in its own way; S₃ TRANSITIVELY connects
-- them (the single orbit); so ~ is reachability across the 3 perspectives, not a carrier-equality. (Pieces from
-- the Group/WitnessTower trees: M40Action's act-hom, Sn's finite complete enumeration — the orientation-change.)
------------------------------------------------------------------------
-- (3) coemit-s3-orbit: S₃ acts TRANSITIVELY on the 3 axes — every axis reaches every other by a permutation. The
--     single orbit IS the higher-order finite: the 3 "finite-from-a-perspective" legs are one, up to permutation.

-- the transposition swapping two Fin-3 positions (a concrete S₃ generator) — the orientation-change permutation.
swap01 : Fin 3 → Fin 3
swap01 zero             = suc zero
swap01 (suc zero)       = zero
swap01 (suc (suc zero)) = suc (suc zero)
