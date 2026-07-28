------------------------------------------------------------------------
-- Substrate.Groups.Z3.A
--
-- The generator of Z₃ = Cyclic.Base at index 2, named at its index.
--
-- ⟡no-qualifiers: a file needing BOTH Z₂'s and Z₃'s generator cannot
-- distinguish them by a module qualifier (`Z₂.a` / `Z₃.a`) — that routes
-- the definition through a non-definer.  The instantiation is NAMED
-- instead, one definition per file, so both can be plainly imported.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3.A where

open import Substrate.Groups.Coxeter.Cyclic.Base 2

a₃ : Gen
a₃ = a
