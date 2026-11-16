------------------------------------------------------------------------
-- Substrate.Groups.Z2.NormalizeCanonical
--
-- canonicity of the normal form of Z₂ = Cyclic at index 1, named at its index.
--
-- ⟡no-qualifiers: `Z₂.normalize-canonical` routes the definition through a barrel and
-- hides which index was bound.  The instantiation is NAMED instead, one
-- definition per file, so two indices can both be plainly imported.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2.NormalizeCanonical where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Cyclic.Base 1
open import Substrate.Groups.Coxeter.Cyclic.Existential 1
-- ⚑ `normalize` / `normalize-canonical` ARE `ListPresentation`'s (Ⓐ¹⁶‴); both
-- opens above are bare, so the five arguments are already in scope.
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert

normalize-canonical₂ : (w : Word Gen) → Canonical-ex (normalize w)
normalize-canonical₂ = normalize-canonical
