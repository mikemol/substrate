------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.FromC
--
-- Defines: from-c
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.FromC where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Bijection.FromCCanonical



from-c : Word C.Gen-V4 → V₄
from-c w = from-c-canonical (C.normalize-canonical w)
