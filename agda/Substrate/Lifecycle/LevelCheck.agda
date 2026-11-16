------------------------------------------------------------------------
-- Substrate.Lifecycle.LevelCheck
--
-- Defines: actor-Set₀, boundary-Set₀, interlock-Set₀, terminal-Set₀
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.LevelCheck where

open import Substrate.Foundation.Eq
open import Substrate.Lifecycle.Actor
open import Substrate.Lifecycle.Boundary
open import Substrate.Lifecycle.Interlock
open import Substrate.Lifecycle.Terminal


------------------------------------------------------------------------
-- THE LEVEL IS ASSERTED AGAINST THE TYPECHECKER, NOT AGAINST A CENSUS.
--
-- The Set₁ ratchet REFUSES today (1213 of 3174 cores undecodable — "an
-- incomplete census is not a low count"), and `set1_motif` reports the
-- SPELLED annotation, which memory `set1-census-artifact-class` records is
-- a claim rather than a measurement. Neither can certify these records.
--
-- Each line below is a definitional equality the elaborator must accept, so
-- it is the strongest available statement: if any of these records were to
-- acquire a Set₁ field — a Set-valued carrier, a level-polymorphic
-- parameter — the corresponding line stops typechecking, HERE, rather than
-- surfacing as a census delta after a full catalog rebuild.
--
-- This matters at a stage boundary specifically: a level-polymorphic actor
-- would make the boundary's two sides live at different levels, and the
-- interlock's `≤` would no longer relate them without lifting. Keeping the
-- whole model in Set₀ is what keeps a boundary a comparison rather than a
-- coercion.
------------------------------------------------------------------------

boundary-Set₀ : Set
boundary-Set₀ = Boundary

actor-Set₀ : Set
actor-Set₀ = Actor

interlock-Set₀ : Actor → Actor → Set
interlock-Set₀ = Interlock

terminal-Set₀ : Actor → Set
terminal-Set₀ = Terminal
