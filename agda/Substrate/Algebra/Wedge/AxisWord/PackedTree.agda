------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedTree
--
-- THE SELF-BALANCING TREE — packed nodes (PackedNode) stacked by grade, with
-- the promote wired in: a full node's overflow is reinterned one grade up.
-- This is the cascading B-tree insert = carry propagation = the Cayley–Dickson
-- doubling cascade. A `Tower` is the list of grades (grade 0 = head); `insert`
-- packs at grade 0 and, on a `split`, carries the overflow into grade 1, which
-- may split and carry into grade 2, … — exactly incrementing a positional
-- counter, the carry being the forced quote (orthogonal move) at each grade.
--
-- The five facts:
--   * `insert`            — the cascade; structurally terminating (each carry
--                           recurses on a shorter tail).
--   * `insert-depth`      — the tower NEVER loses a grade (perfect recall at
--                           the tower level: depth only grows).
--   * `carry-births-grade`— when the carry runs off the top, the overflow BIRTHS
--                           a new grade (`one ov`) — never dropped.
--   * `insert-carry`      — at a full grade, the flat chart is PRESERVED intact
--                           and only the overflow moves up a grade (the promote
--                           = grade-lift = orthogonal move).
--   * `insert-full-singleton-grows` — a distinct entry at a full grade creates a
--                           new grade: the forced quote adds exactly one grade
--                           (the octonion's orthogonal axis, one doubling).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedTree where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; z≤n; s≤s)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Wedge.AxisWord.PackedNode using (module PackedNode)

module PackedTree {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedNode _≟A_

  ------------------------------------------------------------------------
  -- 1. The tower and the cascading insert (carry = promote to next grade).
  ------------------------------------------------------------------------

  Tower : Set
  Tower = List Node

  insert : A → Tower → Tower
  insert x []         = one x ∷ []
  insert x (nd ∷ rest) with pack x nd
  ... | shared nd' = nd' ∷ rest
  ... | packed nd' = nd' ∷ rest
  ... | split nd' ov = nd' ∷ insert ov rest      -- carry the overflow up a grade

  ------------------------------------------------------------------------
  -- 2. The tower never loses a grade (depth only grows) — perfect recall.
  ------------------------------------------------------------------------

  depth : Tower → ℕ
  depth []        = zero
  depth (_ ∷ rest) = suc (depth rest)

  ≤-refl : (n : ℕ) → n ≤ n
  ≤-refl zero    = z≤n
  ≤-refl (suc n) = s≤s (≤-refl n)

  insert-depth : (x : A) (ts : Tower) → depth ts ≤ depth (insert x ts)
  insert-depth x []         = z≤n
  insert-depth x (nd ∷ rest) with pack x nd
  ... | shared nd' = ≤-refl (suc (depth rest))
  ... | packed nd' = ≤-refl (suc (depth rest))
  ... | split nd' ov = s≤s (insert-depth ov rest)

  ------------------------------------------------------------------------
  -- 3. When the carry runs off the top, the overflow BIRTHS a grade — the
  --    residue is never discarded, it becomes a new grade.
  ------------------------------------------------------------------------

  carry-births-grade : (ov : A) → insert ov [] ≡ one ov ∷ []
  carry-births-grade ov = refl

  ------------------------------------------------------------------------
  -- 4. At a full grade, the flat chart is preserved and ONLY the overflow
  --    moves up a grade (the promote = grade-lift = the orthogonal move).
  ------------------------------------------------------------------------

  insert-carry : (x a b : A) (d : ¬ (a ≡ b)) (rest : Tower) →
                 ¬ (x ≡ a) → ¬ (x ≡ b) →
                 insert x (full a b d ∷ rest) ≡ full a b d ∷ insert x rest
  insert-carry x a b d rest xa xb with x ≟A a | x ≟A b
  ... | yes p | _     = ⊥-elim (xa p)
  ... | no _  | yes q = ⊥-elim (xb q)
  ... | no _  | no _  = refl

  ------------------------------------------------------------------------
  -- 5. A distinct entry at a full grade creates a new grade: the forced quote
  --    adds exactly one grade — the octonion's orthogonal axis, one doubling.
  ------------------------------------------------------------------------

  insert-full-singleton-grows :
    (x a b : A) (d : ¬ (a ≡ b)) → ¬ (x ≡ a) → ¬ (x ≡ b) →
    insert x (full a b d ∷ []) ≡ full a b d ∷ one x ∷ []
  insert-full-singleton-grows x a b d xa xb = insert-carry x a b d [] xa xb
