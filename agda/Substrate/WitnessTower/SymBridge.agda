------------------------------------------------------------------------
-- Substrate.WitnessTower.SymBridge
--
-- The final bridge: the tower's bijective image-vectors map to the
-- substrate's genuine symmetric-group record Groups.Symmetric (Fin n),
-- as a GROUP ISOMORPHISM. This closes "the tower IS Sₙ" at the record
-- level — the inverse field is supplied by injective ⟹ surjective
-- (WitnessTower.Surjective), no postulates.
--
--   to-Sym   : (σ : Perm n) → IsPerm σ → Symmetric.Permutation (Fin n)
--   from-Sym : Symmetric.Permutation (Fin n) → Σ (Perm n) IsPerm
--   round-trips (≈ on the record side, ≡ pointwise on the vector side)
--   to-Sym is a homomorphism: to-Sym (compose σ τ) ≈ to-Sym σ · to-Sym τ
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SymBridge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose; id-perm)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.Surjective using (perm-surjective)
open import Substrate.WitnessTower.SnGroup using (apply-compose; compose-is-perm)

import Substrate.Groups.Symmetric.Permutation as SymP
import Substrate.Groups.Symmetric.Eq          as SymEq
import Substrate.Groups.Symmetric.Permutation.Compose     as SymComp
import Substrate.Groups.Symmetric.Identity    as SymId


module _ (n : ℕ) where

  open SymP    (Fin n) using (Permutation)
    renaming (apply to applyP; invₐ to invP; inv-l to inv-lP; inv-r to inv-rP)
  open SymEq   (Fin n) using (_≈_)
  open SymComp (Fin n) using (_·_)
  open SymId   (Fin n) using (ε)

  ----------------------------------------------------------------------
  -- 1. to-Sym: a bijective vector becomes a Permutation record. The
  --    inverse function is "where does σ send something to y"
  --    (perm-surjective).
  ----------------------------------------------------------------------

  to-Sym : (σ : Perm n) → IsPerm σ → Permutation
  to-Sym σ perm = record
    { apply = lookup σ
    ; invₐ  = λ y → proj₁ (perm-surjective σ perm y)
    ; inv-l = λ x → perm _ x (proj₂ (perm-surjective σ perm (lookup σ x)))
    ; inv-r = λ y → proj₂ (perm-surjective σ perm y)
    }

  ----------------------------------------------------------------------
  -- 2. from-Sym: a Permutation record becomes a bijective vector. apply
  --    is injective because invₐ ∘ apply = id (inv-l).
  ----------------------------------------------------------------------

  from-Sym : Permutation → Σ (Perm n) IsPerm
  from-Sym p = tabulate (applyP p) , vec-perm
    where
      look : (i : Fin n) → lookup (tabulate (applyP p)) i ≡ applyP p i
      look = lookup∘tabulate (applyP p)
      vec-perm : IsPerm (tabulate (applyP p))
      vec-perm i j eq =
        trans (sym (inv-lP p i))
              (trans (cong (invP p) (trans (sym (look i)) (trans eq (look j))))
                     (inv-lP p j))

  ----------------------------------------------------------------------
  -- 3. Round trips. Record side up to ≈ (pointwise apply); vector ≡.
  ----------------------------------------------------------------------

  to-from : (p : Permutation) →
            to-Sym (proj₁ (from-Sym p)) (proj₂ (from-Sym p)) ≈ p
  to-from p i = lookup∘tabulate (applyP p) i

  from-to : (σ : Perm n) (perm : IsPerm σ) →
            proj₁ (from-Sym (to-Sym σ perm)) ≡ σ
  from-to σ perm = lookup-ext (tabulate (lookup σ)) σ (lookup∘tabulate (lookup σ))

  ----------------------------------------------------------------------
  -- 4. Homomorphism + identity preservation.
  ----------------------------------------------------------------------

  to-Sym-hom :
    (σ τ : Perm n) (pσ : IsPerm σ) (pτ : IsPerm τ) →
    to-Sym (compose σ τ) (compose-is-perm σ τ pσ pτ) ≈ (to-Sym σ pσ · to-Sym τ pτ)
  to-Sym-hom σ τ pσ pτ i = apply-compose σ τ i

  to-Sym-id : (p : IsPerm (id-perm n)) → to-Sym (id-perm n) p ≈ ε
  to-Sym-id p i = lookup∘tabulate (λ k → k) i
