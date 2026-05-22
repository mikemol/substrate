------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle7
--
-- σ₇ on Fin 7 + HasOrderPerm, derived as a thin instance of
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic.
--
-- σ₇ = cyclic-suc {6}; σ₇-HasOrderPerm comes free (no per-position
-- enumeration). This is the first Cycleₙ instance to use the
-- structural cyclic-suc; future Cycleₖ should follow the same pattern.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle7 where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm)

σ₇ : Fin 7 → Fin 7
σ₇ = cyclic-suc {6}

σ₇-HasOrderPerm : HasOrderPerm σ₇ 7
σ₇-HasOrderPerm = cyclic-suc-HasOrderPerm {6}
