------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.FromTo
--
-- Defines: from-to
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.FromTo where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.FromC
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- Round-trips.
------------------------------------------------------------------------

from-to : (x : V₄) → from-c (to-c x) ≡ x
from-to e = refl
from-to α = refl
from-to β = refl
from-to γ = refl
