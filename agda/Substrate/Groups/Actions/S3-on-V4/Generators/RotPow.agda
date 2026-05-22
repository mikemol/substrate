------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotPow
--
-- Iterated rotation: `rot-pow` applies `rotate` once per Z₃.a letter
-- in the input word. Thin renaming of the generic
-- IterPow.iter-pow with f = rotate; the constructor identity of the
-- letter is irrelevant, only its multiplicity matters.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotPow where

open import Substrate.Groups.V4 using (V₄)
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate  using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.IterPow using (iter-pow)

rot-pow : Word Z₃.Gen → V₄ → V₄
rot-pow = iter-pow rotate
