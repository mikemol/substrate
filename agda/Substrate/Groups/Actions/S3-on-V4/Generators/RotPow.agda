------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotPow
--
-- Iterated rotation: `rot-pow` runs `rotate` once per `Z₃.a` letter
-- in the input word.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotPow where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)

rot-pow : Word Z₃.Gen → V₄ → V₄
rot-pow []         v = v
rot-pow (Z₃.a ∷ w) v = rotate (rot-pow w v)
