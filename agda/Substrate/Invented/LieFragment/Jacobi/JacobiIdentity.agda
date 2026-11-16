------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.Jacobi.JacobiIdentity
--
-- Defines: jacobi-identity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.Jacobi; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.Jacobi.JacobiIdentity where

open import Substrate.Invented.LieFragment
open import Substrate.Invented.LieFragment.Jacobi.LieAlgExpr
open import Substrate.Invented.LieFragment.Jacobi.ApproxL



------------------------------------------------------------------------
-- 3. The headline axiom (named).
------------------------------------------------------------------------

jacobi-identity :
  (a b c : LieAlgExpr) →
  ((bracket a (bracket b c) ⊕L bracket b (bracket c a))
    ⊕L bracket c (bracket a b))
  ≈L zero-L
jacobi-identity = jacobi-L
