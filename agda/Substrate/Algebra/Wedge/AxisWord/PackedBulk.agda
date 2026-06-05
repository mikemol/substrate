------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedBulk
--
-- Bulk insertion: building a self-balancing tower from a whole list, and the
-- per-insert guarantees lifted to compose. `insertAll` folds `insert` over a
-- list; the tower it builds is well-formed, keeps every prior member, recalls
-- every element of the list, and distributes over list concatenation.
--
-- This is the "load a sequence into the SPPF" operation, with its correctness
-- assembled entirely from the green per-insert theorems (PackedRecall /
-- PackedInvariant) — nothing re-proved, just composed.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedBulk where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (Dec)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.Wedge.AxisWord.PackedTree using (module PackedTree)
open import Substrate.Algebra.Wedge.AxisWord.PackedRecall using (module PackedRecall)
open import Substrate.Algebra.Wedge.AxisWord.PackedInvariant using (module PackedInvariant)

module PackedBulk {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedTree _≟A_ using (Tower; insert)
  open PackedRecall _≟A_ using (_∈ᵀ_; insert-preserves; insert-recalls)
  open PackedInvariant _≟A_ using (WellFormed; WellFormed-[]; insert-preserves-wf)

  ------------------------------------------------------------------------
  -- 1. List membership (the source side).
  ------------------------------------------------------------------------

  data _∈ˡ_ : A → List A → Set where
    lhere  : {x : A} {xs : List A} → x ∈ˡ (x ∷ xs)
    lthere : {x y : A} {xs : List A} → x ∈ˡ xs → x ∈ˡ (y ∷ xs)

  ------------------------------------------------------------------------
  -- 2. Bulk insert: fold insert over the list (head inserted last).
  ------------------------------------------------------------------------

  insertAll : List A → Tower → Tower
  insertAll []       ts = ts
  insertAll (x ∷ xs) ts = insert x (insertAll xs ts)

  ------------------------------------------------------------------------
  -- 3. Bulk insert preserves well-formedness.
  ------------------------------------------------------------------------

  insertAll-wf : (xs : List A) (ts : Tower) → WellFormed ts → WellFormed (insertAll xs ts)
  insertAll-wf []       ts wf = wf
  insertAll-wf (x ∷ xs) ts wf =
    insert-preserves-wf x (insertAll xs ts) (insertAll-wf xs ts wf)

  ------------------------------------------------------------------------
  -- 4. Bulk insert preserves every prior member (perfect recall, lifted).
  ------------------------------------------------------------------------

  insertAll-preserves : (xs : List A) (ts : Tower) (y : A) →
                        y ∈ᵀ ts → y ∈ᵀ insertAll xs ts
  insertAll-preserves []       ts y mem = mem
  insertAll-preserves (x ∷ xs) ts y mem =
    insert-preserves x y (insertAll xs ts) (insertAll-preserves xs ts y mem)

  ------------------------------------------------------------------------
  -- 5–6. Every element of the list is recalled in the result.
  ------------------------------------------------------------------------

  insertAll-recalls-head : (x : A) (xs : List A) (ts : Tower) →
    Σ A (λ e → (e ≡ x) × (e ∈ᵀ insertAll (x ∷ xs) ts))
  insertAll-recalls-head x xs ts = insert-recalls x (insertAll xs ts)

  insertAll-recalls-mem : {z : A} (xs : List A) (ts : Tower) →
    z ∈ˡ xs → Σ A (λ e → (e ≡ z) × (e ∈ᵀ insertAll xs ts))
  insertAll-recalls-mem (x ∷ xs) ts lhere = insert-recalls x (insertAll xs ts)
  insertAll-recalls-mem (x ∷ xs) ts (lthere mem) =
    let (e , eq , m) = insertAll-recalls-mem xs ts mem
    in e , eq , insert-preserves x e (insertAll xs ts) m

  ------------------------------------------------------------------------
  -- 7. insertAll distributes over list append (foldr law).
  ------------------------------------------------------------------------

  insertAll-++ : (xs ys : List A) (ts : Tower) →
    insertAll (xs ++ ys) ts ≡ insertAll xs (insertAll ys ts)
  insertAll-++ []       ys ts = refl
  insertAll-++ (x ∷ xs) ys ts = cong (insert x) (insertAll-++ xs ys ts)

  ------------------------------------------------------------------------
  -- 8–9. From the empty tower: well-formed, and every list element recalled.
  ------------------------------------------------------------------------

  insertAll-from-[]-wf : (xs : List A) → WellFormed (insertAll xs [])
  insertAll-from-[]-wf xs = insertAll-wf xs [] WellFormed-[]

  insertAll-from-[]-recalls : {z : A} (xs : List A) →
    z ∈ˡ xs → Σ A (λ e → (e ≡ z) × (e ∈ᵀ insertAll xs []))
  insertAll-from-[]-recalls xs mem = insertAll-recalls-mem xs [] mem

  ------------------------------------------------------------------------
  -- 10. Recall is stable under further bulk inserts (composition).
  ------------------------------------------------------------------------

  insertAll-preserves² : (xs ys : List A) (ts : Tower) (y : A) →
                         y ∈ᵀ ts → y ∈ᵀ insertAll ys (insertAll xs ts)
  insertAll-preserves² xs ys ts y mem =
    insertAll-preserves ys (insertAll xs ts) y (insertAll-preserves xs ts y mem)
