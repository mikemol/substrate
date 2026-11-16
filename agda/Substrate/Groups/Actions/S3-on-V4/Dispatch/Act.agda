------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Dispatch.Act
--
-- act: the full S₃-on-V₄ action, normalising the S₃-pair first
-- before dispatching via act-on-canonical.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Dispatch.Act where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection.V4
-- ⚑ `normalize` IS `ListPresentation`'s, not `Existential`'s (Ⓐ¹⁶) — one
-- application per index, each with that index's five arguments.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂-Base
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂-Existential
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.Coxeter.ListPresentation
  Z₂-Base.Gen Z₂-Existential.Canonical-ex Z₂-Existential.c-ε
  Z₂-Base.insert Z₂-Existential.insert-canonical-ex as Z₂-LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃-Base.Gen Z₃-Existential.Canonical-ex Z₃-Existential.c-ε
  Z₃-Base.insert Z₃-Existential.insert-canonical-ex as Z₃-LP
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)

act : S₃.Carrier → V₄ → V₄
act (n , h) v = act-on-canonical (Z₃-LP.normalize n) (Z₂-LP.normalize h) v
