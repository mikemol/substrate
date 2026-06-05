------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedReadoutDynamics
--
-- The readout (PackedReadout.toList) under insertion: every value in the
-- readout survives an insert (and a bulk insert), and every inserted value
-- appears in the readout afterwards. Assembled by composing the membership
-- bijection (∈ᵀ ↔ ∈ˡ∘toList) with the recall theorems — nothing re-proved.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedReadoutDynamics where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_; Dec)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.List using (List; [])
open import Substrate.Algebra.Wedge.AxisWord.PackedTree using (module PackedTree)
open import Substrate.Algebra.Wedge.AxisWord.PackedRecall using (module PackedRecall)
open import Substrate.Algebra.Wedge.AxisWord.PackedBulk using (module PackedBulk)
open import Substrate.Algebra.Wedge.AxisWord.PackedReadout using (module PackedReadout)

module PackedReadoutDynamics {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedTree _≟A_ using (Tower; insert)
  open PackedRecall _≟A_ using (_∈ᵀ_; insert-preserves; insert-recalls)
  open PackedBulk _≟A_ using (_∈ˡ_; insertAll; insertAll-preserves; insertAll-recalls-mem)
  open PackedReadout _≟A_ using (toList; ∈ᵀ→∈ˡ-toList; ∈ˡ-toList→∈ᵀ)

  ------------------------------------------------------------------------
  -- 35–36. Single insert: readout members survive; the new value appears.
  ------------------------------------------------------------------------

  toList-insert-preserves : (x y : A) (ts : Tower) →
                            y ∈ˡ toList ts → y ∈ˡ toList (insert x ts)
  toList-insert-preserves x y ts m =
    ∈ᵀ→∈ˡ-toList (insert-preserves x y ts (∈ˡ-toList→∈ᵀ ts m))

  toList-insert-recalls : (x : A) (ts : Tower) →
    Σ A (λ e → (e ≡ x) × (e ∈ˡ toList (insert x ts)))
  toList-insert-recalls x ts =
    let (e , eq , m) = insert-recalls x ts in e , eq , ∈ᵀ→∈ˡ-toList m

  ------------------------------------------------------------------------
  -- 37–39. Bulk insert: readout members survive; every list value appears.
  ------------------------------------------------------------------------

  toList-insertAll-preserves : (xs : List A) (ts : Tower) (y : A) →
                               y ∈ˡ toList ts → y ∈ˡ toList (insertAll xs ts)
  toList-insertAll-preserves xs ts y m =
    ∈ᵀ→∈ˡ-toList (insertAll-preserves xs ts y (∈ˡ-toList→∈ᵀ ts m))

  toList-insertAll-recalls : {z : A} (xs : List A) (ts : Tower) →
    z ∈ˡ xs → Σ A (λ e → (e ≡ z) × (e ∈ˡ toList (insertAll xs ts)))
  toList-insertAll-recalls xs ts mem =
    let (e , eq , m) = insertAll-recalls-mem xs ts mem in e , eq , ∈ᵀ→∈ˡ-toList m

  toList-from-[]-recalls : {z : A} (xs : List A) →
    z ∈ˡ xs → Σ A (λ e → (e ≡ z) × (e ∈ˡ toList (insertAll xs [])))
  toList-from-[]-recalls xs mem = toList-insertAll-recalls xs [] mem

  ------------------------------------------------------------------------
  -- 40. The empty tower reads out empty (nothing is a readout member of []).
  ------------------------------------------------------------------------

  ∉ˡ-toList-[] : {y : A} → ¬ (y ∈ˡ toList [])
  ∉ˡ-toList-[] ()
