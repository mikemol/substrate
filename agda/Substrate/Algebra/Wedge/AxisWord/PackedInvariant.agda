------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.PackedInvariant
--
-- Two structural completions of the self-balancing tower:
--
--   * WELL-FORMEDNESS (the maintained self-balance invariant): every grade a
--     tower built by `insert` holds is NON-EMPTY — no wasted grade. `insert`
--     preserves it, and the empty tower has it, so every reachable tower is
--     well-formed (the cascade never strands an empty cell).
--
--   * EXACT SIZE CONDITIONS: pinning precisely WHEN insert adds 0 vs 1 at each
--     position — shared (the value matched a seat) adds 0, fresh adds 1. These
--     refine `PackedSize.insert-size` from "at most one" to "exactly one iff
--     the value is new here", transport-free (the deciding equality is used
--     directly via `_≟A_`, never subst).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.PackedInvariant where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.Algebra.Wedge.AxisWord.PackedNode using (module PackedNode)
open import Substrate.Algebra.Wedge.AxisWord.PackedTree using (module PackedTree)
open import Substrate.Algebra.Wedge.AxisWord.PackedSize using (module PackedSize)

module PackedInvariant {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  open PackedNode _≟A_
  open PackedTree _≟A_
  open PackedSize _≟A_

  outNode : PackOutcome → Node
  outNode (shared nd)  = nd
  outNode (packed nd)  = nd
  outNode (split nd _) = nd

  ------------------------------------------------------------------------
  -- 1. A node is non-empty (one / full).
  ------------------------------------------------------------------------

  data NonEmpty : Node → Set where
    ne-one  : {a : A}                   → NonEmpty (one a)
    ne-full : {a b : A} {d : ¬ (a ≡ b)} → NonEmpty (full a b d)

  ------------------------------------------------------------------------
  -- 2. pack's kept node is ALWAYS non-empty (even from an empty node).
  ------------------------------------------------------------------------

  outNode-nonempty : (x : A) (nd : Node) → NonEmpty (outNode (pack x nd))
  outNode-nonempty x empty = ne-one
  outNode-nonempty x (one a) with x ≟A a
  ... | yes _ = ne-one
  ... | no _  = ne-full
  outNode-nonempty x (full a b d) with x ≟A a | x ≟A b
  ... | yes _ | _     = ne-full
  ... | no _  | yes _ = ne-full
  ... | no _  | no _  = ne-full

  ------------------------------------------------------------------------
  -- 3–4. Well-formed = every grade non-empty; the empty tower qualifies.
  ------------------------------------------------------------------------

  WellFormed : Tower → Set
  WellFormed []          = ⊤
  WellFormed (nd ∷ rest) = NonEmpty nd × WellFormed rest

  WellFormed-[] : WellFormed []
  WellFormed-[] = tt

  ------------------------------------------------------------------------
  -- 5. insert preserves well-formedness — the cascade never strands an empty
  --    grade. (With WellFormed-[], every tower built by insert is well-formed.)
  ------------------------------------------------------------------------

  insert-preserves-wf : (x : A) (ts : Tower) → WellFormed ts → WellFormed (insert x ts)
  insert-preserves-wf x []         _              = ne-one , tt
  insert-preserves-wf x (nd ∷ rest) (_ , rest-wf) with pack x nd | outNode-nonempty x nd
  ... | shared nd'   | ne' = ne' , rest-wf
  ... | packed nd'   | ne' = ne' , rest-wf
  ... | split nd' ov | ne' = ne' , insert-preserves-wf ov rest rest-wf

  ------------------------------------------------------------------------
  -- 6–10. Exact size conditions: when does insert add 0 (shared) vs 1 (fresh)?
  ------------------------------------------------------------------------

  -- empty grade: the value is always fresh here → +1.
  insert-size-fresh-empty : (x : A) (rest : Tower) →
    size (insert x (empty ∷ rest)) ≡ suc (size (empty ∷ rest))
  insert-size-fresh-empty x rest = refl

  -- a singleton grade: matched → +0, distinct → +1.
  insert-size-shared-one : (x a : A) (rest : Tower) →
    x ≡ a → size (insert x (one a ∷ rest)) ≡ size (one a ∷ rest)
  insert-size-shared-one x a rest p with x ≟A a
  ... | yes _  = refl
  ... | no ¬p = ⊥-elim (¬p p)

  insert-size-fresh-one : (x a : A) (rest : Tower) →
    ¬ (x ≡ a) → size (insert x (one a ∷ rest)) ≡ suc (size (one a ∷ rest))
  insert-size-fresh-one x a rest ne with x ≟A a
  ... | yes p = ⊥-elim (ne p)
  ... | no _  = refl

  -- a full grade: matched either seat → +0 (the value is already held).
  insert-size-shared-full-a : (x a b : A) (d : ¬ (a ≡ b)) (rest : Tower) →
    x ≡ a → size (insert x (full a b d ∷ rest)) ≡ size (full a b d ∷ rest)
  insert-size-shared-full-a x a b d rest p with x ≟A a | x ≟A b
  ... | yes _  | _     = refl
  ... | no ¬p | _      = ⊥-elim (¬p p)

  insert-size-shared-full-b : (x a b : A) (d : ¬ (a ≡ b)) (rest : Tower) →
    x ≡ b → size (insert x (full a b d ∷ rest)) ≡ size (full a b d ∷ rest)
  insert-size-shared-full-b x a b d rest q with x ≟A a | x ≟A b
  ... | yes _ | _      = refl
  ... | no _  | yes _  = refl
  ... | no _  | no ¬q = ⊥-elim (¬q q)
