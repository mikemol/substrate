------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Fin-via-Cyclic
--
-- Path 2 collapse demo: the entire Z7-Coxeter ↔ Fin 6 chain in
-- ONE LINE via Substrate.Groups.Coxeter.Fin-from-Cyclic 6.
--
-- Compare against the existing Z7-Coxeter-Fin which has per-n
-- bijection enumeration + action refls.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Fin-via-Cyclic where

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 6 public
