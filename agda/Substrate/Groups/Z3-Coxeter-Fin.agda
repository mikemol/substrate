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
open import Substrate.Groups.Coxeter.Cyclic.Base 2 using (σ-HasOrderPerm; σ-OrderOf)
open import Substrate.Groups.Coxeter.Cyclic.Core 2 using (chain)


import Substrate.Groups.Z3-Coxeter as Z₃


