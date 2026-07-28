------------------------------------------------------------------------
-- Substrate.Groups.Z2.Normalize
--
-- the normalizer of Z₂ = Cyclic at index 1, named at its index.
--
-- ⟡no-qualifiers: `Z₂.normalize` routes the definition through a barrel and
-- hides which index was bound.  The instantiation is NAMED instead, one
-- definition per file, so two indices can both be plainly imported.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2.Normalize where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Cyclic.Base 1
open import Substrate.Groups.Coxeter.Cyclic.Existential 1

normalize₂ : Word Gen → Word Gen
normalize₂ = normalize
