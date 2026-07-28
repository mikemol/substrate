------------------------------------------------------------------------
-- Substrate.Groups.Z2.CPos
--
-- the canonical-position pattern of Z₂ = Cyclic at index 1, named at its index.
--
-- ⟡no-qualifiers: `Z₂.c-pos` routes the definition through a barrel and
-- hides which index was bound.  The instantiation is NAMED instead, one
-- definition per file, so two indices can both be plainly imported.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2.CPos where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Cyclic.Base 1
open import Substrate.Groups.Coxeter.Cyclic.Existential 1

pattern c-pos₂ k = c-pos k
