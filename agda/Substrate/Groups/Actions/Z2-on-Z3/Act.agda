------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Act
--
-- The Z/2-on-Z/3 action proper: `act-letter` (canonical-form dispatch)
-- and `act` (the full action via pre-canonicalisation of both args).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Act where

-- ⚑ `Cyclic.Inverse` DISSOLVED (771283c8) — `inv` is `Inverse.Inv`'s (Ⓐ¹³).
-- ⚑ AND `normalize` IS NOT `Existential`'s: it belongs to `ListPresentation`,
-- which Existential merely opened.  Each Zₙ needs its own application, at its own
-- index, with that index's Gen/Canonical-ex/c-ε/insert/insert-canonical-ex — two
-- instances, which is exactly what the two qualifiers here are for.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂-Base
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂-Existential
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv 2 as Z₃-Inverse
import Substrate.Groups.Coxeter.ListPresentation
  Z₂-Base.Gen Z₂-Existential.Canonical-ex Z₂-Existential.c-ε
  Z₂-Base.insert Z₂-Existential.insert-canonical-ex as Z₂-LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃-Base.Gen Z₃-Existential.Canonical-ex Z₃-Existential.c-ε
  Z₃-Base.insert Z₃-Existential.insert-canonical-ex as Z₃-LP
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

act-letter : Word Z₂-Base.Gen → Word Z₃-Base.Gen → Word Z₃-Base.Gen
act-letter []                            n = n
act-letter (Z₂-Base.a ∷ [])                   n = Z₃-Inverse.inv n
act-letter (Z₂-Base.a ∷ (Z₂-Base.a ∷ _))           n = n  -- unreachable on canonical Z₂

act : Word Z₂-Base.Gen → Word Z₃-Base.Gen → Word Z₃-Base.Gen
act h n = act-letter (Z₂-LP.normalize h) (Z₃-LP.normalize n)
