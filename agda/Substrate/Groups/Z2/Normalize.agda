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
-- ⚑ `normalize` IS `ListPresentation`'s, not `Existential`'s (Ⓐ¹⁶‴).  This file
-- is the UNQUALIFIED shape: it opens both bare, so `Gen`/`insert`/`Canonical-ex`
-- /`c-ε`/`insert-canonical-ex` are already in scope and the application needs no
-- new import — which is why `--lp-apply` reports these separately and declines
-- to rewrite them by the qualified rule.
--
-- ⚑ AND THE HEADER ALREADY STATES THE PRINCIPLE: *"⟡no-qualifiers: `Z₂.normalize`
-- routes the definition through a barrel and hides which index was bound."*  The
-- same sentence applies one level up — routing through `Existential` hid which
-- MODULE was bound.  Naming the instantiation is exactly this file's job.
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert

normalize₂ : Word Gen → Word Gen
normalize₂ = normalize
