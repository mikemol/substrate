------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Act
--
-- The Z/2-on-Z/3 action proper: `act-letter` (canonical-form dispatch)
-- and `act` (the full action via pre-canonicalisation of both args).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Act where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

act-letter : Word Z₂.Gen → Word Z₃.Gen → Word Z₃.Gen
act-letter []                            n = n
act-letter (Z₂.a ∷ [])                   n = Z₃.inv n
act-letter (Z₂.a ∷ (Z₂.a ∷ _))           n = n  -- unreachable on canonical Z₂

act : Word Z₂.Gen → Word Z₃.Gen → Word Z₃.Gen
act h n = act-letter (Z₂.normalize h) (Z₃.normalize n)
