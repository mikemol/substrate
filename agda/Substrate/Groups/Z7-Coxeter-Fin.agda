------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Fin
--
-- The Z7-Coxeter ↔ Fin <order> chain — thin instance of
-- Substrate.Groups.Coxeter.Fin-from-Cyclic 6.
--
-- Phase 4 of Path 2: the per-n bijection enumeration that lived
-- here is obsolete; the chain materialises from Cyclic 6.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Fin where

import Substrate.Groups.Z7-Coxeter as Z₇

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 6 public
  hiding (canonical-to-Fin; Fin-to-canonical)
  renaming
    ( σ to σ₇
    ; σ-HasOrderPerm to σ₇-HasOrderPerm-from-Z7-Coxeter
    ; action-of-a-is-σ-ex to action-of-a-is-σ₇
    ; canonical-to-Fin-ex to canonical-to-Fin
    ; Fin-to-canonical-ex to Fin-to-canonical
    )
