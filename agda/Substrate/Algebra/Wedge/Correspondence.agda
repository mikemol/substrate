------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Correspondence
--
-- THE TARGET. Pass two areas' capstones (each a DivStr — the area's
-- wedge-carrier) into the wedge, and read out a BIDIRECTIONAL bridge: the
-- FORWARD translation from the result (the quotient — the numerator measured
-- in the denominator's carrier) and the BACKWARD translation from the
-- projection (the remainder — the denominator measured in the numerator's
-- carrier). That braided pair is a `Correspondence`.
--
--   Correspondence A B = Bridge A B  ×  Bridge B A      (forward, backward)
--
-- And these compose: areas as objects, correspondences as morphisms, form a
-- category (`corr-id`, `corr-∘`) that is in fact a groupoid-flavoured one
-- (`corr-sym` swaps the directions — the wedge's braiding). So the substrate's
-- areas, cross-bridged through the wedge, ARE a category — the north-star
-- object: every cross-silo correspondence, composable, both ways.
--
-- HONEST SCOPE: this builds the codomain — the `Correspondence` type and its
-- category (id / sym / compose, via Bridge composition `_⊚_`). The literal
-- producer `wedge(capstoneA, capstoneB) → Correspondence` — forward = the
-- quotient-read, backward = the remainder-read — is the TYPE-LEVEL wedge
-- (feeding the carriers themselves as operands, the deepest "feed the types
-- in" layer). Its codomain is here; the producer is the final wiring, gated
-- by the heterogeneous wedge taking a:A ÷ b:B directly (the mixing now in
-- CrossMul). Witness here is the identity correspondence (an area with
-- itself); a cross-area instance is numeral and deferred.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Correspondence where

open import Substrate.Foundation.Eq using (trans; cong)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Bridge
  using (Bridge; translate; respects; z-pres; id-bridge)

------------------------------------------------------------------------
-- 1. Bridge composition — so correspondences compose.
------------------------------------------------------------------------

_⊚_ : {CA CB CC : Set} {A : DivStr CA} {B : DivStr CB} {C : DivStr CC} → Bridge B C → Bridge A B → Bridge A C
g ⊚ f = record
  { translate = λ x → translate g (translate f x)
  ; respects  = λ q b r →
      trans (cong (translate g) (respects f q b r))
            (respects g (translate f q) (translate f b) (translate f r))
  ; z-pres    = trans (cong (translate g) (z-pres f)) (z-pres g)
  }

------------------------------------------------------------------------
-- 2. The bidirectional bridge: forward (the result) + backward (the projection).
------------------------------------------------------------------------

Correspondence : {CA CB : Set} → DivStr CA → DivStr CB → Set
Correspondence A B = Bridge A B × Bridge B A

fwd : {CA CB : Set} {A : DivStr CA} {B : DivStr CB} → Correspondence A B → Bridge A B
fwd = proj₁

bwd : {CA CB : Set} {A : DivStr CA} {B : DivStr CB} → Correspondence A B → Bridge B A
bwd = proj₂

------------------------------------------------------------------------
-- 3. The category of areas and correspondences (groupoid-flavoured).
------------------------------------------------------------------------

corr-id : {C : Set} (D : DivStr C) → Correspondence D D
corr-id D = id-bridge D , id-bridge D

-- the wedge's braiding: swapping numerator/denominator swaps the directions.
corr-sym : {CA CB : Set} {A : DivStr CA} {B : DivStr CB} → Correspondence A B → Correspondence B A
corr-sym c = bwd c , fwd c

-- compose: forwards compose forward, backwards compose in reverse.
corr-∘ : {CA CB CC : Set} {A : DivStr CA} {B : DivStr CB} {C : DivStr CC} →
         Correspondence B C → Correspondence A B → Correspondence A C
corr-∘ g f = (fwd g ⊚ fwd f) , (bwd f ⊚ bwd g)
