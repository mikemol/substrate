------------------------------------------------------------------------
-- Substrate.Groups.V4-as-Z2xZ2
--
-- V₄ ≅ Z/2 × Z/2, as the Coxeter direct product of TWO COPIES of the
-- SAME group (Z/2 = Cyclic index 1). Both factors are index 1; the
-- duplication is the point, not two carriers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-as-Z2xZ2 where

open import Substrate.Groups.Coxeter.Word using (Word; _++_; ++-assoc)
-- ⚑ `normalize` / `normalize-canonical` / `normalize-distrib` ARE
-- `ListPresentation`'s, not `Existential`'s or `Core`'s (Ⓐ¹⁶‴).  The two clauses
-- below named three non-exports between them; a `using` naming a non-export is
-- only a WARNING, so all three bound nothing and the failure landed at the
-- DirectProduct application, which consumes exactly those names.
open import Substrate.Groups.Coxeter.Cyclic.Base 1
-- ⚑⚑ THIS LINE IS A RE-EXPORT DEPENDENCY, NOT A RESOLVED ONE (ⓉCORE-WITHLEMMAS).
-- `normalize-distrib` lives in `ListPresentation.WithLemmas` — a submodule taking
-- two proof obligations — and reaches here because `Cyclic.Core` opens that
-- submodule `public`.  So this file depends on a name whose home it cannot see,
-- which is exactly the construct the ban retires and exactly what the rest of
-- this arc dismantled.
--
-- ⚑ I FIRST WROTE THIS COMMENT AS A JUSTIFICATION — "it is genuinely Core's to
-- provide" — because the compiler went green and I stopped one level short.  It
-- is not Core's; Core is forwarding it.  The honest repair is for this file to
-- apply `WithLemmas` itself with V₄'s obligations, which is a real edit and not
-- this task's; recorded so the green does not read as done.
open import Substrate.Groups.Coxeter.Cyclic.Core 1
  using (ε; canonical-is-fixed; normalize-distrib)
open import Substrate.Groups.Coxeter.Cyclic.Existential 1
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex

open import Substrate.Groups.Coxeter.DirectProduct
  (Word Gen) _++_ ε ++-assoc
    Canonical-ex normalize normalize-canonical
    canonical-is-fixed normalize-distrib
  (Word Gen) _++_ ε ++-assoc
    Canonical-ex normalize normalize-canonical
    canonical-is-fixed normalize-distrib
  public
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert
