------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedMembership
--
-- The membership theory of the self-balancing tower, completing PackedRecall:
-- inversion (SOUNDNESS — a member is exactly one of the stored entries), fresh
-- seating, the split-overflow reaching a DEEPER grade (the promote landed it
-- up), and the recall capstone (old members survive + new value recalled).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedMembership where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.Algebra.Wedge.AxisWord.PackedNode using (module PackedNode)
open import Substrate.Algebra.Wedge.AxisWord.PackedTree using (module PackedTree)
open import Substrate.Algebra.Wedge.AxisWord.PackedRecall using (module PackedRecall)

module PackedMembership {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedNode _≟A_
  open PackedTree _≟A_
  open PackedRecall _≟A_

  ------------------------------------------------------------------------
  -- 1–3. Node membership inversion: a member is one of the node's entries.
  ------------------------------------------------------------------------

  ∈ᴺ-one-inv : {y a : A} → y ∈ᴺ one a → y ≡ a
  ∈ᴺ-one-inv in-one = refl

  ∈ᴺ-full-inv : {y a b : A} {d : ¬ (a ≡ b)} → y ∈ᴺ full a b d → (y ≡ a) ⊎ (y ≡ b)
  ∈ᴺ-full-inv in-a = inj₁ refl
  ∈ᴺ-full-inv in-b = inj₂ refl

  ∉ᴺ-empty : {y : A} → ¬ (y ∈ᴺ empty)
  ∉ᴺ-empty ()

  ------------------------------------------------------------------------
  -- 4–5. Tower membership inversion.
  ------------------------------------------------------------------------

  ∉ᵀ-[] : {y : A} → ¬ (y ∈ᵀ [])
  ∉ᵀ-[] ()

  ∈ᵀ-∷-inv : {y : A} {nd : Node} {rest : Tower} →
             y ∈ᵀ (nd ∷ rest) → (y ∈ᴺ nd) ⊎ (y ∈ᵀ rest)
  ∈ᵀ-∷-inv (here yp) = inj₁ yp
  ∈ᵀ-∷-inv (there yr) = inj₂ yr

  ------------------------------------------------------------------------
  -- 6–7. Fresh seating: a genuinely new entry takes a slot and is a member.
  ------------------------------------------------------------------------

  pack-seats-fresh : {x a : A} → ¬ (x ≡ a) → x ∈ᴺ outNode (pack x (one a))
  pack-seats-fresh {x} {a} ne with x ≟A a
  ... | yes p = ⊥-elim (ne p)
  ... | no _  = in-b

  insert-seats-fresh-one : {x a : A} (rest : Tower) →
                           ¬ (x ≡ a) → x ∈ᵀ insert x (one a ∷ rest)
  insert-seats-fresh-one {x} {a} rest ne with x ≟A a
  ... | yes p = ⊥-elim (ne p)
  ... | no _  = here in-b

  ------------------------------------------------------------------------
  -- 8. The split overflow lands a grade DEEPER: at a full head distinct from
  --    both seats, the recalled value is in the TAIL (`there`) — the promote
  --    pushed it past the preserved flat chart.
  ------------------------------------------------------------------------

  insert-full-distinct-deeper :
    {x a b : A} {d : ¬ (a ≡ b)} (rest : Tower) →
    ¬ (x ≡ a) → ¬ (x ≡ b) →
    Σ A (λ e → (e ≡ x) × (e ∈ᵀ insert x (full a b d ∷ rest)))
  insert-full-distinct-deeper {x} {a} {b} {d} rest xa xb with x ≟A a | x ≟A b
  ... | yes p | _     = ⊥-elim (xa p)
  ... | no _  | yes q = ⊥-elim (xb q)
  ... | no _  | no _  = let (e , eq , mem) = insert-recalls x rest in e , eq , there mem

  ------------------------------------------------------------------------
  -- 9. Recall through repeated inserts (composition): a member survives any
  --    number of later inserts — perfect recall is stable under iteration.
  ------------------------------------------------------------------------

  insert-preserves² : (x₁ x₂ y : A) (ts : Tower) →
                      y ∈ᵀ ts → y ∈ᵀ insert x₂ (insert x₁ ts)
  insert-preserves² x₁ x₂ y ts mem =
    insert-preserves x₂ y (insert x₁ ts) (insert-preserves x₁ y ts mem)

  ------------------------------------------------------------------------
  -- 10. The recall capstone: after an insert, every prior member survives AND
  --     the inserted value is recalled. No leak, no discard, in one statement.
  ------------------------------------------------------------------------

  insert-recall-complete : (x : A) (ts : Tower) →
    ((y : A) → y ∈ᵀ ts → y ∈ᵀ insert x ts)
    × Σ A (λ e → (e ≡ x) × (e ∈ᵀ insert x ts))
  insert-recall-complete x ts =
    (λ y → insert-preserves x y ts) , insert-recalls x ts
