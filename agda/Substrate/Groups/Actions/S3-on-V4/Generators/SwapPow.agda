------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow
--
-- Iterated swap: `swap-pow` runs `swap-αβ` once per `Z₂.a` letter
-- in the input word.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)

swap-pow : Word Z₂.Gen → V₄ → V₄
swap-pow []         v = v
swap-pow (Z₂.a ∷ w) v = swap-αβ (swap-pow w v)
