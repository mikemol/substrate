------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Fin-via-Cyclic
--
-- Path 2 collapse demo: the entire Z5-Coxeter ↔ Fin 4 chain in
-- ONE LINE via Substrate.Groups.Coxeter.Fin-from-Cyclic 4.
--
-- Compare against the existing Z5-Coxeter-Fin which has per-n
-- bijection enumeration + action refls.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Fin-via-Cyclic where

open import Substrate.Groups.Coxeter.Fin-from-Cyclic 4 public
