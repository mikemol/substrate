------------------------------------------------------------------------
-- Substrate.Lifecycle.Boundary
--
-- Defines: Boundary
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Boundary where

open import Substrate.Foundation.Nat.Nat


------------------------------------------------------------------------
-- A stage boundary, identified by its INDEX into the lifecycle chain.
--
-- A boundary is "any point where we've chosen to have side effects" — so it
-- is observable in the code rather than declared, and naming one by a string
-- (`"sourced→observed"`) would be a second spelling of the chain that can
-- drift from it. An index cannot.
--
-- Boundary i sits between chain link i-1 and link i, so boundary 0 is the
-- edge at which the pipeline draws from OUTSIDE itself (for the ingest, the
-- filesystem — whose watermark is already `st_mtime_ns`).
------------------------------------------------------------------------

Boundary : Set
Boundary = ℕ
