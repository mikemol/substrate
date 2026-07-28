------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Act
--
-- The Z/2-on-Z/3 action proper: `act-letter` (canonical-form dispatch)
-- and `act` (the full action via pre-canonicalisation of both args).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Act where

import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂-Base
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂-Existential
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.Coxeter.Cyclic.Inverse 2 as Z₃-Inverse
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

act-letter : Word Z₂-Base.Gen → Word Z₃-Base.Gen → Word Z₃-Base.Gen
act-letter []                            n = n
act-letter (Z₂-Base.a ∷ [])                   n = Z₃-Inverse.inv n
act-letter (Z₂-Base.a ∷ (Z₂-Base.a ∷ _))           n = n  -- unreachable on canonical Z₂

act : Word Z₂-Base.Gen → Word Z₃-Base.Gen → Word Z₃-Base.Gen
act h n = act-letter (Z₂-Existential.normalize h) (Z₃-Existential.normalize n)
