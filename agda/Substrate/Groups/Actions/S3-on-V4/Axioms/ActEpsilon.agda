------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon
--
-- act-ε: act S₃.ε v ≡ v (identity element acts trivially).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.S3 as S₃

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Foundation.Eq

act-ε : ∀ v → act S₃.ε v ≡ v
act-ε v = refl
