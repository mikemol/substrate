------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Fin-via-Cyclic
--
-- Demonstration of the Path 2 collapse: the entire Z₃-Coxeter ↔ Fin 3
-- chain in ONE LINE via Substrate.Groups.Coxeter.Fin-from-Cyclic 2.
--
-- Compare against Substrate.Groups.Z3-Coxeter-Fin (the named-constructor
-- version, ~85 lines including bijection + action + roundtrip + order
-- enumeration). This file is ~3 lines of actual code; the per-n payload
-- has evaporated into the cyclic structure.
--
-- Phase 4 will migrate Z3-Coxeter-Fin to be exactly this; this demo
-- file proves the collapse works structurally before the migration.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Fin-via-Cyclic where

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 2 public
