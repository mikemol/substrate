------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Dispatch.Act
--
-- act: the full S₃-on-V₄ action, normalising the S₃-pair first
-- before dispatching via act-on-canonical.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Dispatch.Act where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)

act : S₃.Carrier → V₄ → V₄
act (n , h) v = act-on-canonical (Z₃.normalize n) (Z₂.normalize h) v
