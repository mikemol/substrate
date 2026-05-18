------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine
--
-- ONE concrete sacrifice on the V₄-equivariance ladder (per memory
-- `project_reserved_selfdual_bijection_gauge`): a Reserved → SelfDual
-- bijection that's **F₂-AFFINE (not F₂-linear)** and **V₄-equivariant**.
--
-- The sacrifice: F₂-linearity. The recovery: V₄-equivariance under a
-- specific V₄ subgroup of Aff(3, F₂) (affine translations within a
-- 2-dim subgroup of SelfDual's coefficient space).
--
-- Construction:
--
--   * V₄ = Bool × Bool (= F₂² additively); acts on Reserved by adding
--     to the axis bits (regular representation), sign untouched.
--   * shift : V₄ → Bivector mapping V₄ elements to 3 specific
--     translation bivectors (𝟎ⱽ, sd-pair-01-23, sd-pair-02-13,
--     and their sum).
--   * Affine bijection: σ(r) = base(r.sign) +ⱽ shift(r.axis), where
--     base(false) = 𝟎ⱽ and base(true) = sd-pair-03-12.
--   * V₄ acts on SelfDual via translation: ω ↦ ω +ⱽ shift(v).
--
-- The orbit structures now match: Reserved has 2 V₄-orbits of size 4
-- (one per sign value); SelfDual under translation has 2 orbits of
-- size 4 (cosets of the 2-dim translation subgroup spanned by
-- sd-pair-01-23 and sd-pair-02-13).
--
-- Equivariance follows from `shift` being a V₄ → (Bivector, +ⱽ)
-- group homomorphism + associativity / commutativity of +ⱽ. This
-- is the "factor through the group structure" pattern.
--
-- This file demonstrates the ladder structure: by sacrificing
-- F₂-linearity (the structural rigidity that forces 𝟎ⱽ ↦ 𝟎ⱽ), we
-- recover V₄-equivariance. The Cayley-Dickson analogue would be
-- "sacrifice commutativity to gain quaternion structure."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine where

open import Data.Bool using (Bool; true; false; _xor_)
open import Data.Product using (_×_; _,_; proj₁; proj₂; Σ)
open import Data.Vec using ([]; _∷_)
open import Data.Vec.Properties using (≡-dec)
open import Relation.Binary.Definitions using (DecidableEquality)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)
open import Axiom.UniquenessOfIdentityProofs using (module Decidable⇒UIP)
open import Data.Product.Properties using (Σ-≡,≡→≡)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar using (hodge-star)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual
open import Substrate.Cocycles.V4Signature.Codeword
  using (Codeword; IsReserved; Reserved)

------------------------------------------------------------------------
-- V₄ as F₂² (additive group).
------------------------------------------------------------------------

V₄ : Set
V₄ = Bool × Bool

_+V₄_ : V₄ → V₄ → V₄
(a , b) +V₄ (c , d) = (a xor c) , (b xor d)

------------------------------------------------------------------------
-- V₄ action on Reserved by axis-addition (regular representation on
-- axes; sign untouched).
------------------------------------------------------------------------

v4-act-reserved : V₄ → Reserved → Reserved
v4-act-reserved (a , b) ((b₀ , b₁ , b₂ , .false , .false) , refl , refl) =
  ((a xor b₀ , b xor b₁ , b₂ , false , false) , refl , refl)

------------------------------------------------------------------------
-- The translation bivectors (the "shift" map V₄ → Bivector).
--
-- These are the 4 elements of the 2-dim self-dual subspace spanned by
-- sd-pair-01-23 and sd-pair-02-13. Under +ⱽ they form a V₄ subgroup
-- of (Bivector, +ⱽ).
------------------------------------------------------------------------

shift : V₄ → Bivector
shift (false , false) = 𝟎ⱽ
shift (true  , false) = sd-pair-01-23
shift (false , true ) = sd-pair-02-13
shift (true  , true ) = sd-pair-01-23 +ⱽ sd-pair-02-13

------------------------------------------------------------------------
-- Each shift target is self-dual.
------------------------------------------------------------------------

shift-sd : (v : V₄) → SelfDual-Pred (shift v)
shift-sd (false , false) = sd-zero
shift-sd (true  , false) = sd-pair-01-23-self-dual
shift-sd (false , true ) = sd-pair-02-13-self-dual
shift-sd (true  , true ) =
  sd-closed-+ⱽ sd-pair-01-23 sd-pair-02-13
    sd-pair-01-23-self-dual sd-pair-02-13-self-dual

------------------------------------------------------------------------
-- Helper: xor-cancellation `a xor a ≡ false`. Used in
-- shift-homomorphism's diagonal cases.
------------------------------------------------------------------------

xor-self : (a : Bool) → (a xor a) ≡ false
xor-self false = refl
xor-self true  = refl

------------------------------------------------------------------------
-- shift is a V₄ → (Bivector, +ⱽ) group homomorphism.
--
-- Proves `shift (v +V₄ w) ≡ shift v +ⱽ shift w` for all v, w ∈ V₄.
-- 16 cases (4 × 4); each closes via Vector arithmetic
-- (+ⱽ-identityˡ/ʳ, +ⱽ-self-inverse, +ⱽ-comm/assoc).
------------------------------------------------------------------------

shift-hom : (v w : V₄) → shift (v +V₄ w) ≡ shift v +ⱽ shift w
-- (false, false) +V₄ w = w; shift w = 𝟎ⱽ +ⱽ shift w
shift-hom (false , false) w = sym (+ⱽ-identityˡ (shift w))
-- (true, false) row
shift-hom (true , false) (false , false) = sym (+ⱽ-identityʳ sd-pair-01-23)
shift-hom (true , false) (true , false) =
  sym (+ⱽ-self-inverse sd-pair-01-23)
shift-hom (true , false) (false , true) = refl
shift-hom (true , false) (true , true) =
  -- shift((1,0)+(1,1)) = shift(0,1) = sd-pair-02-13
  -- shift(1,0) +ⱽ shift(1,1) = sd-pair-01-23 +ⱽ (sd-pair-01-23 +ⱽ sd-pair-02-13)
  -- Need: sd-pair-02-13 ≡ sd-pair-01-23 +ⱽ (sd-pair-01-23 +ⱽ sd-pair-02-13)
  -- = (sd-pair-01-23 +ⱽ sd-pair-01-23) +ⱽ sd-pair-02-13   [+ⱽ-assoc]
  -- = 𝟎ⱽ +ⱽ sd-pair-02-13                                 [+ⱽ-self-inverse]
  -- = sd-pair-02-13                                       [+ⱽ-identityˡ]
  sym (trans (sym (+ⱽ-assoc sd-pair-01-23 sd-pair-01-23 sd-pair-02-13))
       (trans (cong (_+ⱽ sd-pair-02-13) (+ⱽ-self-inverse sd-pair-01-23))
              (+ⱽ-identityˡ sd-pair-02-13)))
-- (false, true) row
shift-hom (false , true) (false , false) = sym (+ⱽ-identityʳ sd-pair-02-13)
shift-hom (false , true) (true , false) = +ⱽ-comm sd-pair-02-13 sd-pair-01-23
shift-hom (false , true) (false , true) =
  sym (+ⱽ-self-inverse sd-pair-02-13)
shift-hom (false , true) (true , true) =
  -- shift((0,1)+(1,1)) = shift(1,0) = sd-pair-01-23
  -- shift(0,1) +ⱽ shift(1,1) = sd-pair-02-13 +ⱽ (sd-pair-01-23 +ⱽ sd-pair-02-13)
  -- Need: sd-pair-01-23 ≡ sd-pair-02-13 +ⱽ (sd-pair-01-23 +ⱽ sd-pair-02-13)
  -- Use +ⱽ-comm on inner: = sd-pair-02-13 +ⱽ (sd-pair-02-13 +ⱽ sd-pair-01-23)
  -- = (sd-pair-02-13 +ⱽ sd-pair-02-13) +ⱽ sd-pair-01-23   [+ⱽ-assoc]
  -- = 𝟎ⱽ +ⱽ sd-pair-01-23 = sd-pair-01-23
  sym (trans (cong (sd-pair-02-13 +ⱽ_) (+ⱽ-comm sd-pair-01-23 sd-pair-02-13))
      (trans (sym (+ⱽ-assoc sd-pair-02-13 sd-pair-02-13 sd-pair-01-23))
      (trans (cong (_+ⱽ sd-pair-01-23) (+ⱽ-self-inverse sd-pair-02-13))
             (+ⱽ-identityˡ sd-pair-01-23))))
-- (true, true) row
shift-hom (true , true) (false , false) =
  sym (+ⱽ-identityʳ (sd-pair-01-23 +ⱽ sd-pair-02-13))
shift-hom (true , true) (true , false) =
  -- shift((1,1)+(1,0)) = shift(0,1) = sd-pair-02-13
  -- shift(1,1) +ⱽ shift(1,0) = (sd-pair-01-23 +ⱽ sd-pair-02-13) +ⱽ sd-pair-01-23
  sym (trans (+ⱽ-comm (sd-pair-01-23 +ⱽ sd-pair-02-13) sd-pair-01-23)
      (trans (sym (+ⱽ-assoc sd-pair-01-23 sd-pair-01-23 sd-pair-02-13))
      (trans (cong (_+ⱽ sd-pair-02-13) (+ⱽ-self-inverse sd-pair-01-23))
             (+ⱽ-identityˡ sd-pair-02-13))))
shift-hom (true , true) (false , true) =
  -- shift((1,1)+(0,1)) = shift(1,0) = sd-pair-01-23
  -- shift(1,1) +ⱽ shift(0,1) = (sd-pair-01-23 +ⱽ sd-pair-02-13) +ⱽ sd-pair-02-13
  sym (trans (+ⱽ-assoc sd-pair-01-23 sd-pair-02-13 sd-pair-02-13)
      (trans (cong (sd-pair-01-23 +ⱽ_) (+ⱽ-self-inverse sd-pair-02-13))
             (+ⱽ-identityʳ sd-pair-01-23)))
shift-hom (true , true) (true , true) =
  -- shift((1,1)+(1,1)) = shift(0,0) = 𝟎ⱽ
  -- shift(1,1) +ⱽ shift(1,1) = (sd-pair-01-23+sd-pair-02-13) +ⱽ (sd-pair-01-23+sd-pair-02-13)
  sym (+ⱽ-self-inverse (sd-pair-01-23 +ⱽ sd-pair-02-13))

------------------------------------------------------------------------
-- V₄ action on SelfDual via translation by shift.
------------------------------------------------------------------------

v4-act-selfdual : V₄ → Σ Bivector SelfDual-Pred → Σ Bivector SelfDual-Pred
v4-act-selfdual v (ω , sd) =
  (ω +ⱽ shift v) ,
  sd-closed-+ⱽ ω (shift v) sd (shift-sd v)

------------------------------------------------------------------------
-- The base bivector for each sign value (the "sign-dependent offset").
------------------------------------------------------------------------

base-bivector : Bool → Bivector
base-bivector false = 𝟎ⱽ
base-bivector true  = sd-pair-03-12

base-bivector-sd : (b : Bool) → SelfDual-Pred (base-bivector b)
base-bivector-sd false = sd-zero
base-bivector-sd true  = sd-pair-03-12-self-dual

------------------------------------------------------------------------
-- The affine bijection.
--
-- σ(cw) = base(cw.sign) +ⱽ shift(cw.axis).
------------------------------------------------------------------------

reserved-to-selfdual-affine :
  Reserved → Σ Bivector SelfDual-Pred
reserved-to-selfdual-affine ((b₀ , b₁ , b₂ , .false , .false) , refl , refl) =
  (base-bivector b₂ +ⱽ shift (b₀ , b₁)) ,
  sd-closed-+ⱽ (base-bivector b₂) (shift (b₀ , b₁))
    (base-bivector-sd b₂) (shift-sd (b₀ , b₁))

------------------------------------------------------------------------
-- V₄-equivariance: σ(v · r) ≡ v · σ(r).
--
-- Concretely (with v = (a, b) and r = ((b₀, b₁, b₂, false, false), refl, refl)):
--
--   LHS = base(b₂) +ⱽ shift(a xor b₀, b xor b₁)
--   RHS = (base(b₂) +ⱽ shift(b₀, b₁)) +ⱽ shift(a, b)
--
-- By shift-hom: shift(a xor b₀, b xor b₁) = shift((a,b) +V₄ (b₀,b₁))
--                                          = shift(a,b) +ⱽ shift(b₀, b₁)
-- By +ⱽ-comm + +ⱽ-assoc: equals shift(b₀, b₁) +ⱽ shift(a, b)
-- Then RHS = base(b₂) +ⱽ shift(b₀, b₁) +ⱽ shift(a, b)
--          = base(b₂) +ⱽ (shift(b₀, b₁) +ⱽ shift(a, b))  [+ⱽ-assoc]
--          ≡ LHS                                          [shift-hom + +ⱽ-comm]
--
-- Σ-equality via cong on the bivector component (self-dual proof
-- components agree by proof irrelevance after the bivectors match —
-- here, both are constructed via sd-closed-+ⱽ).
------------------------------------------------------------------------

-- Helper: the bivector-level equivariance equation.
bivector-equivariance :
  (a b b₀ b₁ : Bool) (β₂ : Bivector) →
  β₂ +ⱽ shift ((a xor b₀) , (b xor b₁)) ≡
  (β₂ +ⱽ shift (b₀ , b₁)) +ⱽ shift (a , b)
bivector-equivariance a b b₀ b₁ β₂ =
  trans (cong (β₂ +ⱽ_) (shift-hom (a , b) (b₀ , b₁)))
  (trans (cong (β₂ +ⱽ_) (+ⱽ-comm (shift (a , b)) (shift (b₀ , b₁))))
         (sym (+ⱽ-assoc β₂ (shift (b₀ , b₁)) (shift (a , b)))))

------------------------------------------------------------------------
-- V₄-equivariance at the bivector projection level.
--
-- We prove the equation on `proj₁` (the bivector). The full Σ
-- equality is the same modulo proof-irrelevance of the self-dual
-- witness (both sides construct via sd-closed-+ⱽ with the same
-- bivector arguments after the bivector equation holds).
------------------------------------------------------------------------

v4-equivariance-proj :
  (v : V₄) (r : Reserved) →
  proj₁ (reserved-to-selfdual-affine (v4-act-reserved v r)) ≡
  proj₁ (v4-act-selfdual v (reserved-to-selfdual-affine r))
v4-equivariance-proj (a , b) ((b₀ , b₁ , b₂ , .false , .false) , refl , refl) =
  bivector-equivariance a b b₀ b₁ (base-bivector b₂)

------------------------------------------------------------------------
-- Phase 1: Σ-level equivariance via proof-irrelevance.
--
-- Lifts v4-equivariance-proj (the bivector-projection equivariance)
-- to the full Σ Bivector SelfDual-Pred level. The self-dual witness
-- components on both sides are different syntactic terms (built via
-- different applications of sd-closed-+ⱽ) but prove the same equation
-- `apply hodge-star ω ≡ ω` for the SAME ω (after bivector equivariance
-- closes). By Hedberg's theorem (decidable equality on Bivector →
-- UIP), any two proofs of an equality in Bivector are propositionally
-- equal — hence the self-dual proofs are equal.
------------------------------------------------------------------------

-- Decidable equality on Bivector (= Vec F₂ 6), via componentwise F₂ check.
bivector-≟ : DecidableEquality Bivector
bivector-≟ = ≡-dec _≟_

-- UIP on Bivector via Hedberg's theorem.
open Decidable⇒UIP bivector-≟ using () renaming (≡-irrelevant to bivector-uip)

-- Proof-irrelevance for SelfDual-Pred: since SelfDual-Pred ω is itself
-- a Bivector equality (`apply hodge-star ω ≡ ω`), two proofs are equal
-- by Bivector UIP.
selfdual-pred-irr :
  (ω : Bivector) → (p q : SelfDual-Pred ω) → p ≡ q
selfdual-pred-irr _ = bivector-uip

------------------------------------------------------------------------
-- The Σ-level V₄-equivariance.
--
-- Σ-≡,≡→≡ from Data.Product.Properties: build a Σ-equality from
-- (proj₁-equality, subst-along-proj₁-then-proj₂-equality). The first
-- component is v4-equivariance-proj; the second is the substituted
-- self-dual proof's equality with the target, which is forced by
-- selfdual-pred-irr (any two SelfDual-Pred proofs of the same
-- bivector are equal).
------------------------------------------------------------------------

v4-equivariance :
  (v : V₄) (r : Reserved) →
  reserved-to-selfdual-affine (v4-act-reserved v r) ≡
  v4-act-selfdual v (reserved-to-selfdual-affine r)
v4-equivariance v r =
  Σ-≡,≡→≡ (v4-equivariance-proj v r , selfdual-pred-irr _ _ _)

------------------------------------------------------------------------
-- Status (documentation).
--
-- This file demonstrates ONE rung on the V₄-equivariance sacrifice
-- ladder:
--
--   Sacrificed: F₂-linearity (the affine bijection has
--               σ(𝟎ⱽ-coded reserved) = base(false) +ⱽ shift(false, false)
--               = 𝟎ⱽ — but the V₄ action on SelfDual by translation
--               is NOT F₂-linear since it doesn't fix 𝟎ⱽ).
--
--   Recovered:  V₄-equivariance under V₄ = F₂² acting on Reserved by
--               axis-addition and on SelfDual by translation in the
--               2-dim self-dual subgroup ⟨sd-pair-01-23, sd-pair-02-13⟩.
--
-- The Cayley-Dickson analogue: trading commutativity for quaternion
-- structure, or associativity for octonion structure. Here, trading
-- F₂-linearity for V₄-equivariance.
--
-- Equivariance proved at the bivector-projection level
-- (v4-equivariance-proj). The full Σ-level equality requires the
-- self-dual witness to also agree; both witnesses construct via
-- sd-closed-+ⱽ with identical bivector arguments (after the bivector
-- equation), so they coincide modulo proof-irrelevance of equalities
-- in Bivector × Bivector → SelfDual-Pred. Strict propositional Σ
-- equality is deferred.
--
-- Other rungs of the sacrifice ladder remain unformalised:
--   * Sacrifice the V₄ subgroup choice (use a different V₄ ⊂ Sym(8)).
--   * Sacrifice cardinality (quotient by V₄ orbits).
--   * Sacrifice bijectivity (many-to-one collapse).
--   * Sacrifice embedding domain (lift to a larger F₂-space).
--
-- See memory `project_reserved_selfdual_bijection_gauge`.
------------------------------------------------------------------------
