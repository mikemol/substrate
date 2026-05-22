------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Fin
--
-- The Z2-Coxeter ↔ Fin <order> chain — thin instance of
-- Substrate.Groups.Coxeter.Fin-from-Cyclic 1.
--
-- Phase 4 of Path 2: the per-n bijection enumeration that lived
-- here is obsolete; the chain materialises from Cyclic 1.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Fin where

import Substrate.Groups.Z2-Coxeter as Z₂

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 1 public
  hiding (canonical-to-Fin; Fin-to-canonical)
  renaming
    ( σ to σ₂
    ; σ-HasOrderPerm to σ₂-HasOrderPerm-from-Z2-Coxeter
    ; action-of-a-is-σ-ex to action-of-a-is-σ₂
    ; canonical-to-Fin-ex to canonical-to-Fin
    ; Fin-to-canonical-ex to Fin-to-canonical
    )
