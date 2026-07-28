------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationSumComm
--
-- ⟡rig-6 (additive side, the iso) — the COMMUTATIVITY of the graded rig's `+` is the
-- one law whose orientation-residue r ≠ id: `l₁ ⊕ l₂` and `l₂ ⊕ l₁` are NOT equal even
-- after a grade-transport (block₁-first vs block₂-first), they are related by a genuine
-- TRANSPOSITION — the block-swap. This file exhibits that r concretely and proves it is
-- an honest iso (the ≅ of the symmetric rig groupoid), NOT a strict equality.
--
--   blockSwap m n : Fin (m + n) → Fin (n + m)     -- the additive-commutativity iso r
--
-- It is the ⊎-swap read through Fin ≅ ⊎: split the first block off, and send the first
-- block (inject+) to the second position (raise) and vice-versa. Proven here: it swaps
-- the two blocks (blockSwap-L/R, via splitAt-inject/raise) and it is an INVOLUTION on the
-- nose (blockSwap-invol — its own inverse, order-2, so a genuine bijection Fin(m+n) ≅
-- Fin(n+m)). This is the r that GradedStarV4's rowSwap (⟡rig-1/4) abstracts.
--
-- RESIDUE (⟡rig-7): the NATURALITY — that this same blockSwap carries decode(l₁ ⊕ l₂)
-- to decode(l₂ ⊕ l₁) — needs a decode-⊕ block characterization and is the next layer.
-- Here we prove r IS the block-transposition and IS an iso; that it acts correctly on the
-- specific orderings is ⟡rig-7.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationSumComm where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Fin.SplitAt.InjectIdentity using (splitAt-inject)
open import Substrate.Foundation.Fin.SplitAt.RaiseIdentity using (splitAt-raise)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂; [_,_])
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

------------------------------------------------------------------------
-- 1. THE ADDITIVE-COMMUTATIVITY ISO r = blockSwap: the block-transposition.
------------------------------------------------------------------------

blockSwap : ∀ m n → Fin (m + n) → Fin (n + m)
blockSwap m n k = [ raise n , inject+ m ] (splitAt m k)

------------------------------------------------------------------------
-- 2. IT SWAPS THE TWO BLOCKS. First block (inject+) ↦ second position (raise); second
--    block (raise) ↦ first position (inject+). Directly from the splitAt round-trips.
------------------------------------------------------------------------

blockSwap-L : ∀ m n (j : Fin m) → blockSwap m n (inject+ n j) ≡ raise n j
blockSwap-L m n j = cong [ raise n , inject+ m ] (splitAt-inject m {n} j)

blockSwap-R : ∀ m n (i : Fin n) → blockSwap m n (raise m i) ≡ inject+ m i
blockSwap-R m n i = cong [ raise n , inject+ m ] (splitAt-raise m {n} i)

------------------------------------------------------------------------
-- 3. IT IS AN INVOLUTION (r is order-2, a genuine iso): blockSwap n m ∘ blockSwap m n =
--    id on the nose (both grades m+n). Case on which block k is in (splitAt-view).
------------------------------------------------------------------------

blockSwap-invol : ∀ m n (k : Fin (m + n)) → blockSwap n m (blockSwap m n k) ≡ k
blockSwap-invol m n k with splitAt-view m {n} k
... | fromₗ j = trans (cong (blockSwap n m) (blockSwap-L m n j)) (blockSwap-R n m j)
... | fromᵣ i = trans (cong (blockSwap n m) (blockSwap-R m n i)) (blockSwap-L n m i)
