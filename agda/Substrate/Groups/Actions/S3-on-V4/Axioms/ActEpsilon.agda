------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon
--
-- act-ε: act S₃.ε v ≡ v (identity element acts trivially).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)

act-ε : ∀ v → act S₃.ε v ≡ v
act-ε v = refl
