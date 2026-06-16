------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Register.Properties
--
-- THE ADDRESSING IS FAITHFUL — completes "equal value ⟺ equal address" and
-- proves `intern` maintains it. Register.idx-inj gave the (⟸) direction
-- (equal address ⟹ equal value); here is the (⟹) direction and the
-- invariant that licenses it:
--
--   * NoDupᴿ        — the register has no duplicate shapes (the heap invariant).
--   * ∈ᴿ-unique    — under NoDupᴿ, a shape has a UNIQUE membership, so its
--                    address is well-defined.
--   * idx-cong     — (⟹): equal shapes intern to the same address.
--   * intern-NoDupᴿ — `intern` preserves NoDupᴿ (it appends only when absent),
--                    so the heap stays faithful: every shape ↦ exactly one
--                    address, forever.
--
-- With Register.idx-inj this closes the bijection: on a NoDupᴿ register,
-- index-equality and shape-equality decide each other. The exterior heap is a
-- faithful realization of the interior semantics, and interning preserves the
-- faithfulness.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Register.Properties where

open import Substrate.Foundation.Nat using (suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong; subst)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Product using (proj₁)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Algebra.Wedge.Shape using (WedgeShape)
open import Substrate.Algebra.Wedge.Shape.Register
  using (Register; _∈ᴿ_; here; there; idx; find; intern; ∈ᴿ-snoc)

------------------------------------------------------------------------
-- 1. The heap invariant: no duplicate shapes.
------------------------------------------------------------------------

data NoDupᴿ : Register → Set where
  nd-[] : NoDupᴿ []
  nd-∷  : {x : WedgeShape ℕ-div} {reg : Register} →
          ¬ (x ∈ᴿ reg) → NoDupᴿ reg → NoDupᴿ (x ∷ reg)

------------------------------------------------------------------------
-- 2. Under NoDupᴿ, the address is well-defined: equal shapes ⟹ equal index.
--    (Proved with DISTINCT parameters x,y + the equality, like idx-inj —
--    the same-parameter double-match is a UIP-shape --without-K refuses.)
------------------------------------------------------------------------

idx-unique-gen : {x y : WedgeShape ℕ-div} {reg : Register} →
                 NoDupᴿ reg → (p : x ∈ᴿ reg) (q : y ∈ᴿ reg) → x ≡ y → idx p ≡ idx q
idx-unique-gen _            here       here       _   = refl
idx-unique-gen (nd-∷ x∉ _)  here       (there q′) x≡y =
  ⊥-elim (x∉ (subst (λ w → w ∈ᴿ _) (sym x≡y) q′))
idx-unique-gen (nd-∷ x∉ _)  (there p′) here       x≡y =
  ⊥-elim (x∉ (subst (λ w → w ∈ᴿ _) x≡y p′))
idx-unique-gen (nd-∷ _  nd) (there p′) (there q′) x≡y =
  cong suc (idx-unique-gen nd p′ q′ x≡y)

-- (⟹): equal shapes intern to the same address.
idx-cong : {x y : WedgeShape ℕ-div} {reg : Register} →
           NoDupᴿ reg → x ≡ y → (p : x ∈ᴿ reg) (q : y ∈ᴿ reg) → idx p ≡ idx q
idx-cong nd x≡y p q = idx-unique-gen nd p q x≡y

------------------------------------------------------------------------
-- 3. `intern` preserves NoDupᴿ — the faithful heap stays faithful.
------------------------------------------------------------------------

-- a member of `reg ++ [x]` is either a member of `reg` or equal to `x`.
∈ᴿ-++-inv : {y x : WedgeShape ℕ-div} {reg : Register} →
            y ∈ᴿ (reg ++ (x ∷ [])) → (y ∈ᴿ reg) ⊎ (y ≡ x)
∈ᴿ-++-inv {reg = []}    here       = inj₂ refl
∈ᴿ-++-inv {reg = []}    (there ())
∈ᴿ-++-inv {reg = z ∷ r} here       = inj₁ here
∈ᴿ-++-inv {reg = z ∷ r} (there p)  with ∈ᴿ-++-inv {reg = r} p
... | inj₁ q = inj₁ (there q)
... | inj₂ e = inj₂ e

-- appending an absent shape preserves NoDupᴿ.
NoDupᴿ-snoc : {x : WedgeShape ℕ-div} {reg : Register} →
             NoDupᴿ reg → ¬ (x ∈ᴿ reg) → NoDupᴿ (reg ++ (x ∷ []))
NoDupᴿ-snoc nd-[]            x∉      = nd-∷ (λ ()) nd-[]
NoDupᴿ-snoc {x} (nd-∷ {z} z∉r nd) x∉zr =
  nd-∷ z∉ (NoDupᴿ-snoc nd (λ p → x∉zr (there p)))
  where
    z∉ : ¬ (z ∈ᴿ (_ ++ (x ∷ [])))
    z∉ mem with ∈ᴿ-++-inv mem
    ... | inj₁ q   = z∉r q
    ... | inj₂ z≡x = x∉zr (subst (λ w → w ∈ᴿ (z ∷ _)) z≡x here)

-- intern keeps the register duplicate-free.
intern-NoDupᴿ : {x : WedgeShape ℕ-div} {reg : Register} →
               NoDupᴿ reg → NoDupᴿ (proj₁ (intern x reg))
intern-NoDupᴿ {x} {reg} nd with find x reg
... | yes _  = nd
... | no  x∉ = NoDupᴿ-snoc nd x∉
