------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Fin-via-Cyclic
--
-- Path 2 collapse demo: the entire Z2-Coxeter ↔ Fin 1 chain in
-- ONE LINE via Substrate.Groups.Coxeter.Fin-from-Cyclic 1.
--
-- Compare against the existing Z2-Coxeter-Fin which has per-n
-- bijection enumeration + action refls.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Fin-via-Cyclic where

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 1 public
