------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Fin
--
-- The Z₃-Coxeter ↔ Fin 3 chain — thin instance of
-- Substrate.Groups.Coxeter.Fin-from-Cyclic 2.
--
-- Phase 4 of Path 2: with Z3-Coxeter migrated to use Cyclic 2, the
-- per-n bijection enumeration that lived here is now obsolete. The
-- chain materialises from the cyclic structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Fin where

import Substrate.Groups.Z3-Coxeter as Z₃

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 2 public
  hiding (canonical-to-Fin; Fin-to-canonical)
  renaming
    ( σ to σ₃
    ; σ-HasOrderPerm to σ₃-HasOrderPerm-from-Z3-Coxeter
    ; action-of-a-is-σ-ex to action-of-a-is-σ₃
    ; canonical-to-Fin-ex to canonical-to-Fin
    ; Fin-to-canonical-ex to Fin-to-canonical
    )
