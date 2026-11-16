------------------------------------------------------------------------
-- Substrate.Groups.Z3.NormalizeCanonical
--
-- canonicity of the normal form of Z₃ = Cyclic at index 2, named at its index.
--
-- ⟡no-qualifiers: `Z₃.normalize-canonical` routes the definition through a barrel and
-- hides which index was bound.  The instantiation is NAMED instead, one
-- definition per file, so two indices can both be plainly imported.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3.NormalizeCanonical where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Cyclic.Base 2
open import Substrate.Groups.Coxeter.Cyclic.Existential 2
-- ⚑ `normalize` / `normalize-canonical` ARE `ListPresentation`'s (Ⓐ¹⁶‴); both
-- opens above are bare, so the five arguments are already in scope.
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert

normalize-canonical₃ : (w : Word Gen) → Canonical-ex (normalize w)
normalize-canonical₃ = normalize-canonical
