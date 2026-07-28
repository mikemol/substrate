------------------------------------------------------------------------
-- Substrate.Groups.Z3.Normalize
--
-- the normalizer of Z₃ = Cyclic at index 2, named at its index.
--
-- ⟡no-qualifiers: `Z₃.normalize` routes the definition through a barrel and
-- hides which index was bound.  The instantiation is NAMED instead, one
-- definition per file, so two indices can both be plainly imported.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3.Normalize where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Cyclic.Base 2
open import Substrate.Groups.Coxeter.Cyclic.Existential 2

normalize₃ : Word Gen → Word Gen
normalize₃ = normalize
