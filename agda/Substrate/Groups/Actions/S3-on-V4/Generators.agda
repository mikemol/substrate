------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators
--
-- Generator-level structure for the dihedral decomposition of act-∙
-- (file-per-lemma):
--   Generators.Rotate              — αβγ-cycle V₄ automorphism
--   Generators.SwapAB              — αβ-swap V₄ automorphism
--   Generators.RotPow              — iterated rotate
--   Generators.SwapPow             — iterated swap
--   Generators.RotPowAppend        — rot-pow composes over ++
--   Generators.SwapPowAppend       — swap-pow composes over ++
--   Generators.RotateCubeId        — rotate³ ≡ id
--   Generators.SwapSquareId        — swap-αβ² ≡ id
--   Generators.RotPowNormalizeEq   — rot-pow respects Z₃-normalize
--   Generators.SwapPowNormalizeEq  — swap-pow respects Z₂-normalize
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators where

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPowAppend
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowAppend
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPowNormalizeEq
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowNormalizeEq