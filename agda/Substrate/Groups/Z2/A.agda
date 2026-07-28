------------------------------------------------------------------------
-- Substrate.Groups.Z2.A
--
-- The generator of Z₂ = Cyclic.Base at index 1, named at its index.
--
-- ⟡no-qualifiers: a file needing BOTH Z₂'s and Z₃'s generator cannot
-- distinguish them by a module qualifier (`Z₂.a` / `Z₃.a`) — that routes
-- the definition through a non-definer.  The instantiation is NAMED
-- instead, one definition per file, so both can be plainly imported.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2.A where

open import Substrate.Groups.Coxeter.Cyclic.Base 1

a₂ : Gen
a₂ = a
