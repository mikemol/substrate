------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Fin
--
-- The Z4-Coxeter ↔ Fin <order> chain — thin instance of
-- Substrate.Groups.Coxeter.Fin-from-Cyclic 3.
--
-- Phase 4 of Path 2: the per-n bijection enumeration that lived
-- here is obsolete; the chain materialises from Cyclic 3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Fin where

import Substrate.Groups.Z4-Coxeter as Z₄

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 3 public
  hiding (canonical-to-Fin; Fin-to-canonical)
  renaming
    ( σ to σ₄
    ; σ-HasOrderPerm to σ₄-HasOrderPerm-from-Z4-Coxeter
    ; action-of-a-is-σ-ex to action-of-a-is-σ₄
    ; canonical-to-Fin-ex to canonical-to-Fin
    ; Fin-to-canonical-ex to Fin-to-canonical
    )
