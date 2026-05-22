------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Fin-via-Cyclic
--
-- Path 2 collapse demo: the entire Z4-Coxeter ↔ Fin 3 chain in
-- ONE LINE via Substrate.Groups.Coxeter.Fin-from-Cyclic 3.
--
-- Compare against the existing Z4-Coxeter-Fin which has per-n
-- bijection enumeration + action refls.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Fin-via-Cyclic where

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 3 public
