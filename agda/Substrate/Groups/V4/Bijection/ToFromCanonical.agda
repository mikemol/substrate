------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.ToFromCanonical
--
-- Defines: to-from-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.ToFromCanonical where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.FromCCanonical
open import Substrate.Foundation.Eq



to-from-canonical :
  {w : Word C.Gen-V4} (c : C.Canonical-V4 w) → to-c (from-c-canonical c) ≡ w
to-from-canonical C.c-ε  = refl
to-from-canonical C.c-A  = refl
to-from-canonical C.c-B  = refl
to-from-canonical C.c-AB = refl
