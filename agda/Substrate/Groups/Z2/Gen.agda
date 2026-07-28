------------------------------------------------------------------------
-- Substrate.Groups.Z2.Gen
--
-- The generator TYPE of Z₂ = Cyclic.Base at index 1, named at its index.
--
-- ⟡no-qualifiers: `Z₂.Gen` routes the type through a barrel and hides
-- which index was bound.  The instantiation is NAMED instead.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2.Gen where

open import Substrate.Groups.Coxeter.Cyclic.Base 1

Gen₂ : Set
Gen₂ = Gen
