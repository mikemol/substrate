------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle2
--
-- σ₂ on Fin 2 (= the swap) + HasOrderPerm, derived as a thin instance
-- of Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic.
--
-- σ₂ = cyclic-suc {1}; σ₂-HasOrderPerm comes free. The swap maps
-- zero ↔ suc zero.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle2 where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-HasOrderPerm)

σ₂ : Fin 2 → Fin 2
σ₂ = cyclic-suc {1}

σ₂-HasOrderPerm : HasOrderPerm σ₂ 2
σ₂-HasOrderPerm = cyclic-suc-HasOrderPerm {1}
