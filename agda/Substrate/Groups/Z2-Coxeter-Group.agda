------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Group
--
-- Lifts Substrate.Groups.Z2-Coxeter to a stdlib Group bundle via
-- the generic Substrate.Groups.Coxeter.GroupAdapter.
--
-- Z/2's inversion is identity (self-inverse on canonical forms).
--
-- This is the first instantiation of GroupAdapter, validating the
-- lift pattern. Z3-Coxeter-Group follows the same template.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Group where

import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- 1. Z/2 inversion = identity (every element is its own inverse).
------------------------------------------------------------------------

inv : Word Z₂.Gen → Word Z₂.Gen
inv w = w

inv-canonical : {w : Word Z₂.Gen} → Z₂.Canonical w → Z₂.Canonical (inv w)
inv-canonical c = c

inv-left-canonical : {w : Word Z₂.Gen} → Z₂.Canonical w →
                     Z₂.normalize (inv w ++ w) ≡ []
inv-left-canonical Z₂.c-ε = refl
inv-left-canonical Z₂.c-a = refl

inv-right-canonical : {w : Word Z₂.Gen} → Z₂.Canonical w →
                      Z₂.normalize (w ++ inv w) ≡ []
inv-right-canonical Z₂.c-ε = refl
inv-right-canonical Z₂.c-a = refl

------------------------------------------------------------------------
-- 2. Open GroupAdapter with Z/2's Core + inversion data.
--
-- Re-exports the Coxeter Core surface (_·_, _≈_, _≉_, ε, normalize-*,
-- ≉-idem, clash, ++-assoc-4) PLUS the Group bundle and inv-word.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.GroupAdapter
  (Word Z₂.Gen)
  _++_
  []
  (λ a b c → Z₂.++-assoc a b c)
  Z₂.Canonical
  Z₂.c-ε
  Z₂.normalize
  Z₂.normalize-canonical
  Z₂.canonical-is-fixed
  Z₂.normalize-distrib
  ++-identity-left
  ++-identity-right
  inv
  inv-canonical
  inv-left-canonical
  inv-right-canonical
  public

------------------------------------------------------------------------
-- 3. Re-export the Z₂ generator and Canonical constructors for
-- downstream code (e.g., the Z/2 → Aut(Z/3) action).
------------------------------------------------------------------------

open Z₂ public using (Gen; a; c-ε; c-a)
