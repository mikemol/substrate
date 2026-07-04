{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilDedekindDagger — ⟡dedekind-via-dagger: the
-- Dedekind form (modular-2) derived MECHANICALLY from the substrate's modular law (modular-1)
-- by transport through the converse †. 198 proved `dedekind` DIRECTLY (a Σ-rearrangement)
-- and NOTED it is modular-1's †-mirror; here that mirror is made a THEOREM — modular-2 =
-- †-mono(modular-1) at renamed args, with †-∧/†-comp/†-invol aligning the types. The
-- chirality (198) realized as †-FUNCTORIALITY: the two modular forms are one law, transported.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilDedekindDagger where

open import Substrate.Foundation.Product using (_,_; _×_; proj₁; proj₂)
open import Substrate.Category.Allegory
  using (Rel; _⨾_; _∧_; _†; _⊆_; _≈_; ⊆-refl; ⊆-trans; †-comp; †-invol; modular)
open import Substrate.Category.Allegory.Mono
  using (≈-refl; ≈-sym; ≈-trans; †-mono; ⨾-cong; ∧-cong; †-∧)

------------------------------------------------------------------------
-- ② THE TRANSPORT: modular-2 = the †-image of modular-1 (at Q†,P†,U†), with the LHS/RHS
-- aligned by the † laws. This IS the chirality (198) as †-functoriality.
------------------------------------------------------------------------
module _ {A B C : Set} (P : Rel A B) (Q : Rel B C) (U : Rel A C) where

  -- LHS alignment: ((Q†⨾P†) ∧ U†)† ≈ (P⨾Q) ∧ U  (†-∧, then †-comp + †-invol under ∧).
  lhs≈ : ((((Q †) ⨾ (P †)) ∧ (U †)) †) ≈ ((P ⨾ Q) ∧ U)
  lhs≈ = ≈-trans (†-∧ ((Q †) ⨾ (P †)) (U †))
         (≈-trans (∧-cong (†-comp (Q †) (P †)) (†-invol U))
                  (∧-cong (⨾-cong (†-invol P) (†-invol Q)) ≈-refl))

  -- RHS alignment: ((Q† ∧ (U†⨾P)) ⨾ P†)† ≈ P ⨾ (Q ∧ (P†⨾U))  (†-comp, then †-∧/†-comp/†-invol).
  rhs≈ : ((((Q †) ∧ ((U †) ⨾ P)) ⨾ (P †)) †) ≈ (P ⨾ (Q ∧ ((P †) ⨾ U)))
  rhs≈ = ≈-trans (†-comp ((Q †) ∧ ((U †) ⨾ P)) (P †))
         (≈-trans (⨾-cong (†-invol P) (†-∧ (Q †) ((U †) ⨾ P)))
         (≈-trans (⨾-cong ≈-refl (∧-cong (†-invol Q) (†-comp (U †) P)))
                  (⨾-cong ≈-refl (∧-cong ≈-refl (⨾-cong ≈-refl (†-invol U))))))

  -- MODULAR-2 (Dedekind) by transport: φ_L then †-mono(modular-1) then φ_R. No witnesses.
  dedekind-via-† : ((P ⨾ Q) ∧ U) ⊆ (P ⨾ (Q ∧ ((P †) ⨾ U)))
  dedekind-via-† =
    ⊆-trans (proj₂ lhs≈)
      (⊆-trans (†-mono (modular (Q †) (P †) (U †)))
               (proj₁ rhs≈))

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the chirality (198) is †-FUNCTORIALITY; the two modular
-- forms are ONE law transported): dedekind-via-† derives the Dedekind form (modular-2)
-- MECHANICALLY from the substrate's modular (modular-1) — instantiate modular-1 at (Q†,P†,
-- U†), apply †-mono (the converse is order-preserving), and align the LHS/RHS by the †
-- laws (†-∧, †-comp, †-invol). NO witness-casing: the transport is pure †-functoriality.
-- So 198's DIRECT `dedekind` and this transported `dedekind-via-†` prove the SAME modular-2
-- — the chirality-opposition (198) is now a THEOREM (the † image), not just an observation.
-- The either/or "modular-1 vs modular-2 (Dedekind)" DISSOLVES: they are one law seen through
-- the converse †, exactly as residual-duality (194: left/right division = one residual
-- through †) and self-converse (193). The † involution is THE mirror; the two modular forms
-- its two hands; the transport the mechanical proof of the chirality. The derived †-functor
-- glue (†-mono, †-cong-implicit via ≈, ⨾-cong, ∧-cong, ≈-trans/sym) is upstreamable
-- (⟡allegory-mono-upstream). The stencil's chirality bottoms out at †-functoriality.
------------------------------------------------------------------------
