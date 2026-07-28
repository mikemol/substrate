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
open import Substrate.Groups.Coxeter.Cyclic.Base 3 using (σ-HasOrderPerm; σ-OrderOf)
open import Substrate.Groups.Coxeter.Cyclic.Core 3 using (chain)


import Substrate.Groups.Z4-Coxeter as Z₄


