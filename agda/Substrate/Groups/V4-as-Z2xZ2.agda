------------------------------------------------------------------------
-- Substrate.Groups.V4-as-Z2xZ2
--
-- Klein four-group V₄ constructed compositionally as the direct
-- product Z/2 × Z/2.
--
-- This is the load-bearing demonstration of the Coxeter framework's
-- composability: V₄ can be ASSEMBLED from atomic pieces (Z/2) via
-- a generic combinator (Coxeter.DirectProduct), not just hand-coded
-- as a bespoke Coxeter presentation (cf. Substrate.Groups.V4-Coxeter).
--
-- Both presentations exist in the codebase and are isomorphic:
--   * V4-Coxeter: ⟨A, B | A²=B²=ε, AB=BA⟩, Word = List {A, B}.
--   * V4-as-Z2xZ2: pair of Z/2 elements, Word = Z2.Word × Z2.Word.
--
-- The mapping under the iso:
--   V4-Coxeter        V4-as-Z2xZ2
--   ε = []            ε = ([], [])
--   A = [A]           α = ([a], [])
--   B = [B]           β = ([], [a])
--   AB = [A, B]       γ = ([a], [a])
--
-- The DirectProduct inherits everything from the abstract Core:
-- _·_ (= componentwise normalize-then-pair), _≈_, _≉_, ε,
-- normalize-{idem,append,append-right,cong-right,distrib,triple,quad},
-- clash, ≉-idem, ++-assoc-4. So V₄-style theorems lift via this
-- combinator for free; per-product theorems (like a 4-product
-- analog) are written against this presentation just as they are
-- against V4-Coxeter.
--
-- Per the encoding survey: this is the COORDINATE encoding of V₄ —
-- each element is two GF(2) bits, addition is componentwise XOR via
-- the Z/2 normalize. The V4-Coxeter file is the MOVE encoding (single
-- list of generators with cancellation/commutativity relations).
-- Both presentations have identical group structure; the choice is
-- about which inferences become structural vs combinatorial.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-as-Z2xZ2 where

import Substrate.Groups.Z2-Coxeter as Z₁
import Substrate.Groups.Z2-Coxeter as Z₂

------------------------------------------------------------------------
-- Instantiate DirectProduct with two independent Z/2-Coxeter Cores.
--
-- Both Z₁ and Z₂ refer to the same Z2-Coxeter module — they're two
-- COPIES of Z/2 acting on independent coordinates. The DirectProduct
-- combinator treats them as distinct components.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.DirectProduct
  (Z₁.Word Z₁.Gen) (Z₁._++_) Z₁.ε Z₁.++-assoc
    Z₁.Canonical Z₁.normalize Z₁.normalize-canonical
    Z₁.canonical-is-fixed Z₁.normalize-distrib
  (Z₂.Word Z₂.Gen) (Z₂._++_) Z₂.ε Z₂.++-assoc
    Z₂.Canonical Z₂.normalize Z₂.normalize-canonical
    Z₂.canonical-is-fixed Z₂.normalize-distrib
  public
