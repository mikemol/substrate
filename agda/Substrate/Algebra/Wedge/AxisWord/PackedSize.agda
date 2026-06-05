------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedSize
--
-- The COUNTING law of the self-balancing tower — the no-double-count side of
-- exactness (scratch/dent_system_primer.md §5: no leak, no double-count). An
-- insert adds AT MOST one entry to the total occupancy: zero if the value was
-- shared (a dependent — detector 𝟘), exactly one if it was fresh — never two.
-- This is conservation across the whole carry cascade, and together with
-- PackedRecall (never-discard) it pins insert as content-injective up to sharing.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedSize where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.Algebra.Wedge.AxisWord.PackedNode using (module PackedNode)
open import Substrate.Algebra.Wedge.AxisWord.PackedTree using (module PackedTree)
open import Substrate.Algebra.Wedge.AxisWord.PackedRecall using (module PackedRecall)

module PackedSize {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedNode _≟A_
  open PackedTree _≟A_
  open PackedRecall _≟A_

  ------------------------------------------------------------------------
  -- 1. Node occupancy (0/1/2) and 2. tower occupancy (the sum).
  ------------------------------------------------------------------------

  entries : Node → ℕ
  entries empty        = zero
  entries (one _)      = suc zero
  entries (full _ _ _) = suc (suc zero)

  size : Tower → ℕ
  size []          = zero
  size (nd ∷ rest) = entries nd + size rest

  ------------------------------------------------------------------------
  -- 3. The Artin capacity, numerically: a node holds at most two.
  ------------------------------------------------------------------------

  node-cap : (nd : Node) → entries nd ≤ 2
  node-cap empty        = z≤n
  node-cap (one _)      = s≤s z≤n
  node-cap (full _ _ _) = s≤s (s≤s z≤n)

  ------------------------------------------------------------------------
  -- 4. Per node: pack adds 0 (shared/at-capacity) or 1 (a fresh direction).
  ------------------------------------------------------------------------

  pack-entries-step : (x : A) (nd : Node) →
    (entries (outNode (pack x nd)) ≡ entries nd)
    ⊎ (entries (outNode (pack x nd)) ≡ suc (entries nd))
  pack-entries-step x empty = inj₂ refl
  pack-entries-step x (one a) with x ≟A a
  ... | yes _ = inj₁ refl
  ... | no _  = inj₂ refl
  pack-entries-step x (full a b d) with x ≟A a | x ≟A b
  ... | yes _ | _     = inj₁ refl
  ... | no _  | yes _ = inj₁ refl
  ... | no _  | no _  = inj₁ refl

  ------------------------------------------------------------------------
  -- 5. The tower law: insert adds at most one across the whole cascade —
  --    zero (shared) or exactly one (fresh). Never-double-count.
  ------------------------------------------------------------------------

  insert-size : (x : A) (ts : Tower) →
    (size (insert x ts) ≡ size ts) ⊎ (size (insert x ts) ≡ suc (size ts))
  insert-size x []             = inj₂ refl
  insert-size x (empty ∷ rest) = inj₂ refl
  insert-size x (one a ∷ rest) with x ≟A a
  ... | yes _ = inj₁ refl
  ... | no _  = inj₂ refl
  insert-size x (full a b d ∷ rest) with x ≟A a | x ≟A b
  ... | yes _ | _     = inj₁ refl
  ... | no _  | yes _ = inj₁ refl
  ... | no _  | no _  with insert-size x rest
  ...   | inj₁ eq = inj₁ (cong (entries (full a b d) +_) eq)
  ...   | inj₂ eq = inj₂ (cong (entries (full a b d) +_) eq)
