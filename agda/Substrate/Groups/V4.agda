------------------------------------------------------------------------
-- Substrate.Groups.V4
--
-- The Klein four-group V₄ as a 4-element data type. All algebraic
-- structure (operation, identity, inverse, axioms, bundles) is sourced
-- from Substrate.Groups.V4-Coxeter via a bijection.
--
-- V₄ has four elements:
--   e  -- identity
--   α  -- (DC)(SW) double-transposition
--   β  -- (DS)(CW) double-transposition
--   γ  -- (DW)(CS) double-transposition
--
-- Multiplication table:
--
--     ·  | e  α  β  γ
--    ----+------------
--     e  | e  α  β  γ
--     α  | α  e  γ  β
--     β  | β  γ  e  α
--     γ  | γ  β  α  e
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]]: the
-- former 480-line module is now a thin re-export shim over five
-- submodules in V4/.
--
-- Submodule decomposition:
--   V4.Bijection   — carrier V₄ + to-c/from-c + round-trips.
--   V4.Operations  — _·_, ε, inv.
--   V4.Axioms      — all group axioms (refl-case enumeration).
--   V4.Bundle      — stdlib Group + Substrate.Algebra.Group bundles.
--   V4.FourProduct — V₄-4-product theorem via Coxeter bridge.
--
-- All public names from the original file remain available via the
-- re-exports below; existing callers need no edits.
--
-- See: catalog/cocycles.md § CY-5 for V₄'s gauge role;
--      Substrate.Groups.V4-Coxeter for the algebra backend;
--      Substrate.Groups.V4-as-Z2xZ2 for the Z/2 × Z/2 decomposition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4 where

open import Substrate.Groups.V4.FourProduct
-- FourProduct re-exports Bundle, which re-exports Axioms,
-- which re-exports Operations, which re-exports Bijection;
-- so the entire former-monolith surface is available here.
