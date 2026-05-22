------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow
--
-- Iterated swap: `swap-pow` applies `swap-αβ` once per Z₂.a letter in
-- the input word. Thin renaming of the generic IterPow.iter-pow with
-- f = swap-αβ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow where

open import Substrate.Groups.V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word using (Word)

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB  using (swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.IterPow using (iter-pow)

swap-pow : Word Z₂.Gen → V₄ → V₄
swap-pow = iter-pow swap-αβ
