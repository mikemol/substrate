------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
--
-- The Linear LIFT of the cyclic-suc permutation: cyclic-Linear /
-- cyclic-HasOrder / cyclic-Linear-basis. Cycle{N}.agda for N ∈ {2,3,4,5,7}
-- were thin renamings of these (now dissolved into the Sylow registry +
-- the generic generator).
--
-- Ⓖ.tower-basis (2026-07-05): the F₂-FREE generator (cyclic-suc,
-- cyclic-suc-toℕ, σ-iterate-toℕ, cyclic-suc-HasOrderPerm) moved DOWN to its
-- own layer, Substrate.Algebra.Nat.CyclicSuc — pure Fin/Nat mod-suc
-- arithmetic, no Vector/Linear. It is re-exported below so this module's
-- surface is unchanged, but the generator no longer drags the F2.Linear
-- stack: permutation-only consumers now import Algebra.Nat.CyclicSuc
-- directly. What remains HERE is exactly the part that genuinely needs
-- F2.Linear — the Linear lift that FALLS OUT of the generator by
-- basis-permutation-Linear ([[tower-as-combinatorial-basis]]).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic where

open import Substrate.Foundation.Nat using (suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear using (basis-permutation-Linear; apply-basis-permutation-Linear)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order using (HasOrder-from-perm)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

-- Re-export the F₂-free cyclic generator (relocated to Algebra.Nat.CyclicSuc):
-- surface unchanged for existing consumers of Permutation.Cyclic.
open import Substrate.Algebra.Nat.CyclicSuc
  using (cyclic-suc; cyclic-suc-toℕ; σ-iterate-toℕ; cyclic-suc-HasOrderPerm)

------------------------------------------------------------------------
-- cyclic-Linear / cyclic-HasOrder — the Linear lift, parametric.
--
-- Lifts the cyclic-suc permutation through basis-permutation-Linear to a
-- Linear (suc n) (suc n), and transports cyclic-suc-HasOrderPerm through
-- HasOrder-from-perm.
------------------------------------------------------------------------

-- OPACITY BOUNDARY (memory architecture): the dense Linear lift and its
-- order witness are sealed in an `opaque` block. They are type-checked
-- ONCE here, generically at abstract n (cheap — this module is light).
-- A consumer that instantiates at a concrete n (e.g. Cycle7 = {6}) then
-- references them as black boxes and NEVER normalises the
-- `linear-from-images` sum / the L-iterate matrix power. Without this,
-- instantiating `cyclic-HasOrder {6}` forces a 7×7 dense map raised to
-- the 7th power in normal form — the super-exponential blowup that made
-- Cycle7 the single heaviest file in the repo (OOM). The proven basis-
-- level equation (basis-permutation-order-k) already lives behind
-- HasOrder-from-perm, so nothing downstream needs the dense unfolding.
-- Same lesson as the def/proof split, one level deeper: hand consumers
-- the lemma, not the unfolded construction.
opaque
  cyclic-Linear : ∀ {n} → Linear (suc n) (suc n)
  cyclic-Linear {n} = basis-permutation-Linear (cyclic-suc {n})

  cyclic-HasOrder : ∀ {n} → HasOrder (apply (cyclic-Linear {n})) (suc n)
  cyclic-HasOrder {n} =
    HasOrder-from-perm (cyclic-suc {n}) (suc n) (cyclic-suc-HasOrderPerm {n})

  -- The exposed basis-action (the "hand consumers the lemma, not the unfolded
  -- construction" pattern): cyclic-Linear stays sealed, but its effect on a
  -- basis vector is available — eₖ ↦ e_{cyclic-suc k}. Proved inside the opaque
  -- block where cyclic-Linear unfolds to basis-permutation-Linear cyclic-suc.
  cyclic-Linear-basis : ∀ {n} (k : Fin (suc n)) →
                        apply (cyclic-Linear {n}) (basis k) ≡ basis (cyclic-suc {n} k)
  cyclic-Linear-basis {n} k = apply-basis-permutation-Linear (cyclic-suc {n}) k
