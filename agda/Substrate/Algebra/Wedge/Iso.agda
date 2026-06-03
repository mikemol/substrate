------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Iso
--
-- THE PRODUCER'S CODOMAIN, STRENGTHENED — per the reframe: view the wedge
-- operator AS the carrier, and a correspondence is no longer an arbitrary
-- forward/backward pair. The CODOMAIN is the INVERSE of the DOMAIN, mediated
-- by the wedge. So `Correspondence` upgrades to a `WedgeIso`: an invertible
-- bridge, `bwd` the inverse of `fwd`.
--
-- And the mediation is literal. The round-trip laws
--     translate bwd (translate fwd x) ≡ x ,  translate fwd (translate bwd y) ≡ y
-- ARE the wedge's identity corner: `x = 1·x + z`, the `(1,0)` read, which is
-- equality itself (Adjunction: `=` is the wedge with quotient 1, remainder z).
-- So "codomain is inv on the domain, mediated by the wedge" is exactly: each
-- round-trip is a wedge reading `(1, z)`. The inverse is wedge-mediated by
-- construction, not bolted on.
--
-- Consequently the category of areas-and-correspondences (Correspondence.agda)
-- is a GROUPOID: every correspondence is invertible (`iso-id`, `iso-sym`,
-- `iso-∘`). That is what "codomain = inv on domain" means at the category
-- level — all morphisms are isos.
--
-- THE PRODUCER itself — `wedge(capstoneA, capstoneB) → WedgeIso` — is the
-- self-hosted wedge (operator = carrier): the quotient is `fwd`, the
-- remainder is `bwd`, inverse-mediated. Building the self-hosting recon (the
-- wedge taking capstones as operands) is the remaining frontier; this is its
-- codomain, with the inverse structure the reframe demands.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Iso where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Wedge using (DivStr; C)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; translate; id-bridge)
open import Substrate.Algebra.Wedge.Correspondence using (_⊚_; Correspondence)

------------------------------------------------------------------------
-- 1. A correspondence is an iso: codomain inverse to domain.
------------------------------------------------------------------------

record WedgeIso (A B : DivStr) : Set where
  field
    fwd     : Bridge A B
    bwd     : Bridge B A
    -- the round-trips = the wedge's identity corner (1, z), both ways:
    bwd∘fwd : (x : C A) → translate bwd (translate fwd x) ≡ x
    fwd∘bwd : (y : C B) → translate fwd (translate bwd y) ≡ y

open WedgeIso public

------------------------------------------------------------------------
-- 2. The groupoid: identity, inverse (the braiding), composition.
------------------------------------------------------------------------

iso-id : (D : DivStr) → WedgeIso D D
iso-id D = record
  { fwd = id-bridge D ; bwd = id-bridge D
  ; bwd∘fwd = λ _ → refl ; fwd∘bwd = λ _ → refl }

iso-sym : {A B : DivStr} → WedgeIso A B → WedgeIso B A
iso-sym c = record
  { fwd = bwd c ; bwd = fwd c
  ; bwd∘fwd = fwd∘bwd c ; fwd∘bwd = bwd∘fwd c }

iso-∘ : {A B C : DivStr} → WedgeIso B C → WedgeIso A B → WedgeIso A C
iso-∘ g f = record
  { fwd = fwd g ⊚ fwd f
  ; bwd = bwd f ⊚ bwd g
  ; bwd∘fwd = λ x →
      trans (cong (translate (bwd f)) (bwd∘fwd g (translate (fwd f) x)))
            (bwd∘fwd f x)
  ; fwd∘bwd = λ y →
      trans (cong (translate (fwd g)) (fwd∘bwd f (translate (bwd g) y)))
            (fwd∘bwd g y)
  }

------------------------------------------------------------------------
-- 3. Forget the inverse laws to the bare correspondence.
------------------------------------------------------------------------

toCorrespondence : {A B : DivStr} → WedgeIso A B → Correspondence A B
toCorrespondence c = fwd c , bwd c
