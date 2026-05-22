------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActEpsilon
--
-- act-ε: the Z/2 identity acts trivially.
--
-- Z₂.ε = []. act [] n = act-letter [] (Z₃.normalize n) = Z₃.normalize n.
-- Outer Z₃.normalize: Z₃.normalize (Z₃.normalize n) = Z₃.normalize n (idem).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActEpsilon where

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z2-Coxeter-Group as Z₂G
import Substrate.Groups.Z3-Coxeter-Group as Z₃G

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)

act-ε : ∀ n → act Z₂G.ε n Z₃G.≈ n
act-ε n = Z₃.normalize-idem n
