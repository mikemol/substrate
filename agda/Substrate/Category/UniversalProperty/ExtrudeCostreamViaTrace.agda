{-# OPTIONS --safe --without-K --guardedness #-}
------------------------------------------------------------------------
-- ExtrudeCostreamViaTrace — the stream-bisim-via-realtrace RECIPE applied to CoIO (the unbounded emit).
-- CoIO ℕ is DIRECTLY a ℕ-headed coalgebra (emit-head : ℕ, emit-rest : CoIO ℕ — no encoding needed), so it
-- factors through the terminal RealTrace via unfold, and its bisimilarity _≈ᶜ_ (same head, bisimilar rest)
-- IS the universal _~_ transported. The whole equivalence is INHERITED (Trace.Bisim's completed ~-refl/sym/trans).
-- (⟡costream-via-realtrace — the recipe generalizes: one universal carrier, the arc's stream-bisim family.)
------------------------------------------------------------------------
module Substrate.Category.UniversalProperty.ExtrudeCostreamViaTrace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Unfold using (unfold)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl; ~-sym; ~-trans)
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream using (CoIO; emit-head; emit-rest)
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim using (_≈ᶜ_; head≈; rest≈)

-- CoIO ℕ is a ℕ-headed coalgebra DIRECTLY (no parity encoding — emit-head is already the head):
coalg : CoIO ℕ → ℕ × CoIO ℕ
coalg c = emit-head c , emit-rest c

coio-trace : CoIO ℕ → RealTrace
coio-trace = unfold coalg

-- forward: the coalgebra morphism preserves bisimulation (_≈ᶜ_ → _~_):
≈ᶜ→~ : {c d : CoIO ℕ} → c ≈ᶜ d → coio-trace c ~ coio-trace d
head~ (≈ᶜ→~ p) = head≈ p
tail~ (≈ᶜ→~ p) = ≈ᶜ→~ (rest≈ p)

-- backward: and reflects it (_~_ → _≈ᶜ_) — no arithmetic needed (head is already ℕ, identity encoding):
≈ᶜ←~ : {c d : CoIO ℕ} → coio-trace c ~ coio-trace d → c ≈ᶜ d
head≈ (≈ᶜ←~ p) = head~ p
rest≈ (≈ᶜ←~ p) = ≈ᶜ←~ (tail~ p)

-- the whole equivalence of _≈ᶜ_ INHERITED from the universal carrier via the iff:
≈ᶜ-refl : (c : CoIO ℕ) → c ≈ᶜ c
≈ᶜ-refl c = ≈ᶜ←~ (~-refl (coio-trace c))

≈ᶜ-sym : {c d : CoIO ℕ} → c ≈ᶜ d → d ≈ᶜ c
≈ᶜ-sym p = ≈ᶜ←~ (~-sym (≈ᶜ→~ p))

≈ᶜ-trans : {c d e : CoIO ℕ} → c ≈ᶜ d → d ≈ᶜ e → c ≈ᶜ e
≈ᶜ-trans p q = ≈ᶜ←~ (~-trans (≈ᶜ→~ p) (≈ᶜ→~ q))
