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
open import Substrate.Groups.Coxeter.Cyclic.Base 6 using (σ-HasOrderPerm; σ-OrderOf)
open import Substrate.Groups.Coxeter.Cyclic.Core 6 using (chain)


import Substrate.Groups.Z7-Coxeter as Z₇


