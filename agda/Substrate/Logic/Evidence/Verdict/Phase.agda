------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase
--
-- The phase class (el-atlas §5.10c) — the H² SEPARATION rung. The chart
-- involutions of the evidence carrier carry the phase obstruction of the
-- central extension
--
--        1 → ℤ₂ → D₄ → V₄ → 1
--
-- as a class in H²(V₄, ℤ₂). The cocycle is exhibited by the commutator
-- [N₊, S] = −id of the chart involutions (pin-negate N₊ = negPos and
-- pin-swap S = swapE); the class is NON-TRIVIAL (D₄ ≇ V₄ × ℤ₂) — N₊ and S
-- do not commute, so the phase cannot be globally trivialized.
--
-- The diagonal involutions {id, N₊, N₋, −id} are the Klein four-group V₄
-- (Thm 5.4), here LINKED to the substrate's own `Substrate.Groups.V4`
-- (id↦e, negPos↦α, negNeg↦β, negBoth↦γ); the pin-swap S sits outside V₄
-- (an S₃-frame transposition). Per §5.10c this module exhibits the DATA of
-- the extension — the involutions, the commutator cocycle, its
-- non-triviality — not a free-standing D₄ object.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase where

open import Substrate.Foundation.Bool  using (true; false)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Eq    using (_≡_; refl; cong)
open import Substrate.Groups.V4
  using (V₄; e; α; β; γ; _·_; ε; ·-assoc; ·-comm; ε-left; ε-right)
open import Substrate.Category.CommutativeMonoid using (CommutativeMonoid)

open import Substrate.Logic.Evidence.Verdict
  using (Evidence; ⟨_,_⟩; pos; swapE; negPos; negNeg; negBoth; eP)

------------------------------------------------------------------------
-- The chart involutions are involutions (each squares to the identity).
------------------------------------------------------------------------

negPos-invol : (x : Evidence) → negPos (negPos x) ≡ x
negPos-invol ⟨ true  , n ⟩ = refl
negPos-invol ⟨ false , n ⟩ = refl

negNeg-invol : (x : Evidence) → negNeg (negNeg x) ≡ x
negNeg-invol ⟨ p , true  ⟩ = refl
negNeg-invol ⟨ p , false ⟩ = refl

negBoth-invol : (x : Evidence) → negBoth (negBoth x) ≡ x
negBoth-invol ⟨ true  , true  ⟩ = refl
negBoth-invol ⟨ true  , false ⟩ = refl
negBoth-invol ⟨ false , true  ⟩ = refl
negBoth-invol ⟨ false , false ⟩ = refl

------------------------------------------------------------------------
-- The diagonal involutions form V₄: they compose as the Klein four-group
-- (negPos ∘ negNeg = negBoth) and commute. Realized on the substrate's V₄
-- via id↦e, negPos↦α, negNeg↦β, negBoth↦γ — the composition negPos∘negNeg
-- = negBoth mirrors α · β = γ.
------------------------------------------------------------------------

negPos∘negNeg : (x : Evidence) → negPos (negNeg x) ≡ negBoth x
negPos∘negNeg ⟨ p , n ⟩ = refl

negNeg∘negPos : (x : Evidence) → negNeg (negPos x) ≡ negBoth x
negNeg∘negPos ⟨ p , n ⟩ = refl

-- the diagonal V₄ is abelian: negPos and negNeg commute.
negPos-negNeg-comm : (x : Evidence) → negPos (negNeg x) ≡ negNeg (negPos x)
negPos-negNeg-comm ⟨ p , n ⟩ = refl

-- the substrate-V₄ image of that relation.
α·β≡γ : α · β ≡ γ
α·β≡γ = refl

------------------------------------------------------------------------
-- The cocycle (el-atlas §5.10c): the commutator [N₊, S] = −id, with
-- N₊ = negPos and S = swapE (both involutions, so the commutator is the
-- alternating fourfold product).
------------------------------------------------------------------------

commutator-N₊-S : (x : Evidence) → negPos (swapE (negPos (swapE x))) ≡ negBoth x
commutator-N₊-S ⟨ p , n ⟩ = refl

------------------------------------------------------------------------
-- THE H² SEPARATION: the class is non-trivial. If N₊ and S commuted, the
-- group ⟨N₊, S⟩ they generate would be abelian — the SPLIT extension
-- V₄ × ℤ₂ — and the phase would globally trivialize. They do not: their
-- commutator is −id ≠ id, witnessed on the probe eP, so D₄ ≇ V₄ × ℤ₂.
------------------------------------------------------------------------

private
  t≢f : true ≡ false → ⊥
  t≢f ()

N₊-S-noncommute : ((x : Evidence) → negPos (swapE x) ≡ swapE (negPos x)) → ⊥
N₊-S-noncommute h = t≢f (cong pos (h eP))

------------------------------------------------------------------------
-- The kernel ℤ₂ = {id, −id} is CENTRAL: −id commutes with both generators
-- of the extension (this is what makes 1 → ℤ₂ → D₄ → V₄ → 1 *central*).
------------------------------------------------------------------------

negBoth-central-swapE : (x : Evidence) → negBoth (swapE x) ≡ swapE (negBoth x)
negBoth-central-swapE ⟨ p , n ⟩ = refl

negBoth-central-negPos : (x : Evidence) → negBoth (negPos x) ≡ negPos (negBoth x)
negBoth-central-negPos ⟨ p , n ⟩ = refl

------------------------------------------------------------------------
-- GROUNDED: the diagonal involutions {id, negPos, negNeg, negBoth} ARE V₄
-- (id↦e, negPos↦α, negNeg↦β, negBoth↦γ — the α·β≡γ link above), and V₄ IS a
-- substrate-named `Category.CommutativeMonoid` (abelian, exponent 2), reusing
-- V₄'s own group laws. So the involution structure sits on the categorical
-- spine; the central twist (the commutator cocycle above) is the non-abelian
-- residue D₄ carries on top of this abelian V₄.
------------------------------------------------------------------------

V₄-CommutativeMonoid : CommutativeMonoid V₄ _·_ ε
V₄-CommutativeMonoid = record
  { +R-assoc     = ·-assoc
  ; +R-identityˡ = ε-left
  ; +R-identityʳ = ε-right
  ; +R-comm      = ·-comm
  }
