------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedReadout
--
-- The extensional readout of the self-balancing tower: `toList` flattens it to
-- the list of stored entries, and tower membership coincides EXACTLY with list
-- membership of the readout (`∈ᵀ ↔ ∈ˡ ∘ toList`). The SPPF reads out precisely
-- its members — no more, no less.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedReadout where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (Dec)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.Wedge.AxisWord.PackedNode using (module PackedNode)
open import Substrate.Algebra.Wedge.AxisWord.PackedTree using (module PackedTree)
open import Substrate.Algebra.Wedge.AxisWord.PackedRecall using (module PackedRecall)
open import Substrate.Algebra.Wedge.AxisWord.PackedBulk using (module PackedBulk)

module PackedReadout {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedNode _≟A_ using (Node; empty; one; full)
  open PackedTree _≟A_ using (Tower)
  open PackedRecall _≟A_ using (_∈ᴺ_; in-one; in-a; in-b; _∈ᵀ_; here; there)
  open PackedBulk _≟A_ using (_∈ˡ_; lhere; lthere)

  ------------------------------------------------------------------------
  -- 11–12. The readout.
  ------------------------------------------------------------------------

  nodeToList : Node → List A
  nodeToList empty        = []
  nodeToList (one a)      = a ∷ []
  nodeToList (full a b _) = a ∷ b ∷ []

  toList : Tower → List A
  toList []          = []
  toList (nd ∷ rest) = nodeToList nd ++ toList rest

  ------------------------------------------------------------------------
  -- 13–14. Node membership ↔ readout membership.
  ------------------------------------------------------------------------

  ∈ᴺ→∈ˡ-node : {y : A} {nd : Node} → y ∈ᴺ nd → y ∈ˡ nodeToList nd
  ∈ᴺ→∈ˡ-node in-one = lhere
  ∈ᴺ→∈ˡ-node in-a   = lhere
  ∈ᴺ→∈ˡ-node in-b   = lthere lhere

  ∈ˡ-node→∈ᴺ : {y : A} (nd : Node) → y ∈ˡ nodeToList nd → y ∈ᴺ nd
  ∈ˡ-node→∈ᴺ empty ()
  ∈ˡ-node→∈ᴺ (one a) lhere = in-one
  ∈ˡ-node→∈ᴺ (one a) (lthere ())
  ∈ˡ-node→∈ᴺ (full a b d) lhere = in-a
  ∈ˡ-node→∈ᴺ (full a b d) (lthere lhere) = in-b
  ∈ˡ-node→∈ᴺ (full a b d) (lthere (lthere ()))

  ------------------------------------------------------------------------
  -- 15–17. List append membership (inject left / right, and split).
  ------------------------------------------------------------------------

  ∈-++ˡ : {y : A} {xs ys : List A} → y ∈ˡ xs → y ∈ˡ (xs ++ ys)
  ∈-++ˡ lhere      = lhere
  ∈-++ˡ (lthere m) = lthere (∈-++ˡ m)

  ∈-++ʳ : {y : A} (xs : List A) {ys : List A} → y ∈ˡ ys → y ∈ˡ (xs ++ ys)
  ∈-++ʳ []       m = m
  ∈-++ʳ (x ∷ xs) m = lthere (∈-++ʳ xs m)

  ∈-++-inv : {y : A} (xs : List A) {ys : List A} →
             y ∈ˡ (xs ++ ys) → (y ∈ˡ xs) ⊎ (y ∈ˡ ys)
  ∈-++-inv []       m          = inj₂ m
  ∈-++-inv (x ∷ xs) lhere      = inj₁ lhere
  ∈-++-inv (x ∷ xs) (lthere m) with ∈-++-inv xs m
  ... | inj₁ m' = inj₁ (lthere m')
  ... | inj₂ m' = inj₂ m'

  ------------------------------------------------------------------------
  -- 18–20. Tower membership ↔ readout membership (the bijection).
  ------------------------------------------------------------------------

  ∈ᵀ→∈ˡ-toList : {y : A} {ts : Tower} → y ∈ᵀ ts → y ∈ˡ toList ts
  ∈ᵀ→∈ˡ-toList (here yp)  = ∈-++ˡ (∈ᴺ→∈ˡ-node yp)
  ∈ᵀ→∈ˡ-toList (there yr) = ∈-++ʳ _ (∈ᵀ→∈ˡ-toList yr)

  ∈ˡ-toList→∈ᵀ : {y : A} (ts : Tower) → y ∈ˡ toList ts → y ∈ᵀ ts
  ∈ˡ-toList→∈ᵀ [] ()
  ∈ˡ-toList→∈ᵀ (nd ∷ rest) m with ∈-++-inv (nodeToList nd) m
  ... | inj₁ mn = here (∈ˡ-node→∈ᴺ nd mn)
  ... | inj₂ mr = there (∈ˡ-toList→∈ᵀ rest mr)

  ∈ᵀ↔∈ˡ-toList : {y : A} (ts : Tower) →
                 (y ∈ᵀ ts → y ∈ˡ toList ts) × (y ∈ˡ toList ts → y ∈ᵀ ts)
  ∈ᵀ↔∈ˡ-toList ts = (λ m → ∈ᵀ→∈ˡ-toList m) , (λ m → ∈ˡ-toList→∈ᵀ ts m)
