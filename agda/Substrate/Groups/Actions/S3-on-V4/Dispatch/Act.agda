------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Dispatch.Act
--
-- act: the full S₃-on-V₄ action, normalising the S₃-pair first
-- before dispatching via act-on-canonical.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Dispatch.Act where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂-Existential
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)

act : S₃.Carrier → V₄ → V₄
act (n , h) v = act-on-canonical (Z₃-Existential.normalize n) (Z₂-Existential.normalize h) v
