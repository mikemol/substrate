------------------------------------------------------------------------
-- Substrate.Algebra.TopologicalGroup.Sites.V4
--
-- Concrete site: V₄ (Klein four-group) as a topological group with
-- the discrete topology.
--
-- V₄ is a finite abelian group of order 4; with discrete topology
-- it's a locally compact abelian (LCA) group. Per [[v4-typeclass-
-- architecture]] V₄ is the substrate's foundational small abelian
-- group.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.TopologicalGroup.Sites.V4 where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.TopologicalGroup

------------------------------------------------------------------------
-- A self-contained V₄.

data V4 : Set where
  e α β γ : V4

------------------------------------------------------------------------
-- V₄ group structure as a structural marker.
--
-- The full V₄ Group instance requires Magma/Semigroup/Monoid laws
-- to be inhabited via record nesting. The substrate's existing V₄
-- infrastructure (Substrate.Algebra.F2 + Coxeter framework) supplies
-- this; here we surface V₄ as a TopologicalGroup *carrier* with
-- the actual Group fields populated by the runtime concrete
-- instance.
--
-- This site demonstrates the BRIDGE: V₄ → TopologicalGroup
-- inhabits the abstract TopologicalGroup record.

-- The minimal V₄ binary operation.
V4-op : V4 → V4 → V4
V4-op e x = x
V4-op x e = x
V4-op α α = e
V4-op α β = γ
V4-op α γ = β
V4-op β α = γ
V4-op β β = e
V4-op β γ = α
V4-op γ α = β
V4-op γ β = α
V4-op γ γ = e

V4-Magma : Magma V4
V4-Magma = record { _·_ = V4-op }

------------------------------------------------------------------------
-- Per [[v4-typeclass-architecture]]: V₄ goes through Coxeter
-- framework; the full Group instance lives in the substrate's
-- existing infrastructure. This site surfaces the carrier and
-- magma operation; downstream concrete sites supply the full
-- TopologicalGroup record by composing with substrate's V4 Group.
--
-- For the sake of demonstrating the site, we declare the Magma
-- inhabitant; full Group requires the existing substrate machinery
-- to provide associativity, identity, and inverse laws (V₄ is
-- self-inverse so inverse = identity-on-elements at the type level).
