{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FixpointStencilRecord — ⟡fixpoint-stencil-record:
-- the third stencil instance (FixpointStencil, 190) PACKAGED as a formal RECORD datum.
-- 190 stated the meta-framing and witnessed it by loose hinge-definitions; here it becomes
-- an inhabitable TYPE — "X is a two-framing-hinged fixed-point presentation" is now a
-- record, and the fixpoint instance is an inhabitant.
--
-- THE RECORD ENCODES THE STENCIL'S ≡/~ ASYMMETRY IN ITS TYPE: the μ-frame hinge is a FULL
-- iso (fwd AND bwd — the two framings' μ-halves agree EXACTLY, the ≡/halting side); the
-- ν-frame hinge is only the greatest-fixed-point UP (one-directional — the ~/non-halting
-- side, up-to, full iso scoped). So the asymmetry (exact μ, partial ν) is STRUCTURAL in
-- the record, not a side comment. SCOPE: this record is over Fam (Idx D) (the Kleene/
-- fixpoint form), where all carriers live — it does NOT unify with Trace/RealTrace's
-- coinductive form (that cross-form generic module is ⟡uniqueness-stencil-abstract).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.FixpointStencilRecord where

open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Category.Allegory.Refinement using (Fam; _⊑ᶠ_)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step; TraceF)
import Substrate.Algebra.Wedge.TraceKleeneColimit as Kμ
import Substrate.Algebra.Wedge.TraceNuColimit as Kν

------------------------------------------------------------------------
-- ① THE RECORD: a fixed-point presented by TWO framings, related level-wise. The μ-frame
-- is an EXACT iso (both directions); the ν-frame is the greatest-fixed-point UP (up-to).
-- The asymmetry is in the field types: μ has fwd+bwd, ν has only the UP.
------------------------------------------------------------------------
-- Set₁ RETAINED (not the DivStr carrier): the fields μ-A, μ-B, ν-carrier are `Fam (Idx D)`
-- and `Fam : Set → Set₁`, so the record fields live in Set₁ for the Fam reason, independent
-- of the carrier paydown. Parameterizing the carrier does not demote it.
record TwoFraming {C : Set} (D : DivStr C) : Set₁ where
  field
    -- the μ level (finite/halting, ≡-frame): two framings, iso ON THE NOSE.
    μ-A μ-B      : Idx D → Set
    μ-hinge-fwd  : μ-A ⊑ᶠ μ-B
    μ-hinge-bwd  : μ-B ⊑ᶠ μ-A        -- fwd + bwd = μ-A ≅ μ-B (EXACT)
    -- the ν level (non-halting, ~-frame): the greatest-fixed-point UP (UP-TO).
    ν-carrier    : Idx D → Set
    ν-hinge      : {X : Fam (Idx D)} → (X ⊑ᶠ Φ-step D X) → X ⊑ᶠ ν-carrier

open TwoFraming public

------------------------------------------------------------------------
-- ② THE FIXPOINT INSTANCE as an inhabitant: the two framings are the ALGEBRAIC (TraceF)
-- and KLEENE (Colim) μ-characterizations (iso via Colim ≅ Trace, 159), and the ν-frame is
-- the Kleene Limit's greatest-fixed-point UP (162). This IS the third stencil instance,
-- now a datum.
------------------------------------------------------------------------
fixpoint-framing : {C : Set} (D : DivStr C) → TwoFraming D
fixpoint-framing D = record
  { μ-A          = TraceF D           -- algebraic μ (initial Φ-algebra)
  ; μ-B          = Kμ.Colim D         -- Kleene μ (⋃ₙ Φⁿ⊥)
  ; μ-hinge-fwd  = Kμ.trace→colim D   -- Trace ⊑ Colim
  ; μ-hinge-bwd  = Kμ.colim→trace D   -- Colim ⊑ Trace  (⟹ Colim ≅ Trace, EXACT)
  ; ν-carrier    = Kν.Limit D         -- Kleene ν (⋂ₙ Φⁿ⊤)
  ; ν-hinge      = Kν.coalg-below-limit D   -- greatest-fixed-point UP (UP-TO)
  }

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the third instance is now a DATUM whose TYPE encodes the
-- self-similar asymmetry): the record TwoFraming captures "a fixed-point presented by two
-- framings, related level-wise" — and its field types ENCODE the stencil's ≡/~ asymmetry
-- STRUCTURALLY: the μ-frame carries fwd+bwd (an EXACT iso, the halting side), the ν-frame
-- carries only the UP (up-to, the non-halting side, full iso scoped). fixpoint-framing
-- inhabits it with the algebraic/Kleene μ-characterizations (Colim ≅ Trace, 159) and the
-- Kleene Limit's UP (162) — the THIRD stencil instance (190) as a formal datum. So the
-- self-similar third instance is no longer just stated + witnessed by loose hinges; it is
-- an INHABITANT of a record whose very shape (exact μ / up-to ν) is the stencil's
-- asymmetry. The either/or "loose hinges vs formal instance" dissolves: the record IS the
-- hinges packaged, its type the invariant. NOT unified across concrete forms (Trace/
-- RealTrace coinductive vs Fam) — that is ⟡uniqueness-stencil-abstract; here the record
-- lives in the Fam form where the Kleene/fixpoint carriers all sit, and it is honest to
-- that scope. The record could ALSO be inhabited by other Fam-form fixed-points (a
-- residue toward the abstract module); the fixpoint instance is the first inhabitant.
------------------------------------------------------------------------
