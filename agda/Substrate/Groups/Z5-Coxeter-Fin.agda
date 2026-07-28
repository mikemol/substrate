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
open import Substrate.Groups.Coxeter.Cyclic.Base 4 using (σ-HasOrderPerm; σ-OrderOf)
open import Substrate.Groups.Coxeter.Cyclic.Core 4 using (chain)


import Substrate.Groups.Z5-Coxeter as Z₅


