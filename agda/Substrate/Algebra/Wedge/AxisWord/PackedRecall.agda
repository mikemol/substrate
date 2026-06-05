------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedRecall
--
-- PERFECT RECALL, as theorems (scratch/dent_system_primer.md §9: never-discard
-- = the sheaf separation axiom). The self-balancing tree (PackedTree) reshapes
-- itself on every insert — packs, shares, splits, cascades — and the claim is
-- that NOTHING is ever lost:
--
--   * `insert-preserves` : every entry already in the tower is STILL in the
--     tower after an insert — across shares, splits, and the whole carry
--     cascade. (No-coarsening: a grade-distinction is never collapsed away.)
--   * `insert-recalls`   : the inserted entry's value IS present afterwards —
--     freshly seated, or already there as the equal it shared with. Stated
--     existentially (Σ e, e ≡ x × e ∈ᵀ …) so the sharing equality is carried,
--     not transported (no subst).
--
-- Together: insert is injective-on-content up to sharing — the no-leak,
-- no-discard guarantee the carry depends on.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedRecall where

open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.Algebra.Wedge.AxisWord.PackedNode using (module PackedNode)
open import Substrate.Algebra.Wedge.AxisWord.PackedTree using (module PackedTree)

module PackedRecall {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedNode _≟A_
  open PackedTree _≟A_

  ------------------------------------------------------------------------
  -- 1. Node membership: which entries a packed node holds.
  ------------------------------------------------------------------------

  data _∈ᴺ_ : A → Node → Set where
    in-one : {x : A}                       → x ∈ᴺ one x
    in-a   : {a b : A} {d : ¬ (a ≡ b)}     → a ∈ᴺ full a b d
    in-b   : {a b : A} {d : ¬ (a ≡ b)}     → b ∈ᴺ full a b d

  ------------------------------------------------------------------------
  -- 2. Tower membership: a member of some grade.
  ------------------------------------------------------------------------

  data _∈ᵀ_ : A → Tower → Set where
    here  : {y : A} {nd : Node} {rest : Tower} → y ∈ᴺ nd  → y ∈ᵀ (nd ∷ rest)
    there : {y : A} {nd : Node} {rest : Tower} → y ∈ᵀ rest → y ∈ᵀ (nd ∷ rest)

  ------------------------------------------------------------------------
  -- 3. pack keeps every entry of the node it acts on (the kept node of any
  --    outcome retains all prior members — shares and splits lose nothing).
  ------------------------------------------------------------------------

  outNode : PackOutcome → Node
  outNode (shared nd)  = nd
  outNode (packed nd)  = nd
  outNode (split nd _) = nd

  pack-preserves-∈ᴺ : (x : A) {y : A} (nd : Node) → y ∈ᴺ nd → y ∈ᴺ outNode (pack x nd)
  pack-preserves-∈ᴺ x empty ()
  pack-preserves-∈ᴺ x (one a) in-one with x ≟A a
  ... | yes _ = in-one
  ... | no _  = in-a
  pack-preserves-∈ᴺ x (full a b d) in-a with x ≟A a | x ≟A b
  ... | yes _ | _     = in-a
  ... | no _  | yes _ = in-a
  ... | no _  | no _  = in-a
  pack-preserves-∈ᴺ x (full a b d) in-b with x ≟A a | x ≟A b
  ... | yes _ | _     = in-b
  ... | no _  | yes _ = in-b
  ... | no _  | no _  = in-b

  ------------------------------------------------------------------------
  -- 4. PERFECT RECALL: every prior entry survives the insert (and its whole
  --    carry cascade). Nothing is ever discarded.
  ------------------------------------------------------------------------

  insert-preserves : (x y : A) (ts : Tower) → y ∈ᵀ ts → y ∈ᵀ insert x ts
  insert-preserves x y [] ()
  insert-preserves x y (nd ∷ rest) (here yp) with pack x nd | pack-preserves-∈ᴺ x nd yp
  ... | shared nd'   | yp' = here yp'
  ... | packed nd'   | yp' = here yp'
  ... | split nd' ov | yp' = here yp'
  insert-preserves x y (nd ∷ rest) (there yr) with pack x nd
  ... | shared nd'   = there yr
  ... | packed nd'   = there yr
  ... | split nd' ov = there (insert-preserves ov y rest yr)

  ------------------------------------------------------------------------
  -- 5. The inserted value is recalled: some entry equal to x is present after
  --    the insert (freshly seated, or the equal it shared with). The sharing
  --    equality is carried in the Σ — no transport.
  ------------------------------------------------------------------------

  insert-recalls : (x : A) (ts : Tower) → Σ A (λ e → (e ≡ x) × (e ∈ᵀ insert x ts))
  insert-recalls x []             = x , refl , here in-one
  insert-recalls x (empty ∷ rest) = x , refl , here in-one
  insert-recalls x (one a ∷ rest) with x ≟A a
  ... | yes p = a , sym p , here in-one
  ... | no _  = x , refl , here in-b
  insert-recalls x (full a b d ∷ rest) with x ≟A a | x ≟A b
  ... | yes p | _     = a , sym p , here in-a
  ... | no _  | yes q = b , sym q , here in-b
  ... | no _  | no _  = let (e , eq , mem) = insert-recalls x rest in e , eq , there mem
