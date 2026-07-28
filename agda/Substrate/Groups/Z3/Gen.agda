------------------------------------------------------------------------
-- Substrate.Groups.Z3.Gen
--
-- The generator TYPE of Z₃ = Cyclic.Base at index 2, named at its index.
--
-- ⟡no-qualifiers: `Z₃.Gen` routes the type through a barrel and hides
-- which index was bound.  The instantiation is NAMED instead.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3.Gen where

open import Substrate.Groups.Coxeter.Cyclic.Base 2

Gen₃ : Set
Gen₃ = Gen
