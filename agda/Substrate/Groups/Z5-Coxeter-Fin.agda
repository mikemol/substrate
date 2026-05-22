------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Fin
--
-- The Z5-Coxeter ↔ Fin <order> chain — thin instance of
-- Substrate.Groups.Coxeter.Fin-from-Cyclic 4.
--
-- Phase 4 of Path 2: the per-n bijection enumeration that lived
-- here is obsolete; the chain materialises from Cyclic 4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Fin where

import Substrate.Groups.Z5-Coxeter as Z₅

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 4 public
  hiding (canonical-to-Fin; Fin-to-canonical)
  renaming
    ( σ to σ₅
    ; σ-HasOrderPerm to σ₅-HasOrderPerm-from-Z5-Coxeter
    ; action-of-a-is-σ-ex to action-of-a-is-σ₅
    ; canonical-to-Fin-ex to canonical-to-Fin
    ; Fin-to-canonical-ex to Fin-to-canonical
    )
