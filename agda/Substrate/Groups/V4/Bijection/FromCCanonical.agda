------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.FromCCanonical
--
-- Defines: from-c-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.FromCCanonical where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bijection.V4



from-c-canonical : {w : Word C.Gen-V4} → C.Canonical-V4 w → V₄
from-c-canonical C.c-ε  = e
from-c-canonical C.c-A  = α
from-c-canonical C.c-B  = β
from-c-canonical C.c-AB = γ
