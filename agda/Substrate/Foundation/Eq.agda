------------------------------------------------------------------------
-- Substrate.Foundation.Eq
--
-- Substrate-native propositional equality. Phase 2: native datatype +
-- BUILTIN EQUALITY + standard combinators, level-polymorphic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq where

open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Level using (Level; _⊔_)

private variable
  a b c : Level

infix 4 _≡_ _≢_

data _≡_ {A : Set a} (x : A) : A → Set a where
  refl : x ≡ x

{-# BUILTIN EQUALITY _≡_ #-}

_≢_ : {A : Set a} → A → A → Set a
x ≢ y = x ≡ y → ⊥

sym : {A : Set a} {x y : A} → x ≡ y → y ≡ x
sym refl = refl

trans : {A : Set a} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
trans refl q = q

cong : {A : Set a} {B : Set b} (f : A → B) {x y : A} → x ≡ y → f x ≡ f y
cong f refl = refl

cong₂ : {A : Set a} {B : Set b} {C : Set c} (f : A → B → C) {x y : A} {u v : B} →
        x ≡ y → u ≡ v → f x u ≡ f y v
cong₂ f refl refl = refl

subst : {A : Set a} (P : A → Set b) {x y : A} → x ≡ y → P x → P y
subst _ refl p = p

-- `subst` over a CONSTANT family is the identity. Agda cannot reduce this
-- under an abstract proof, so the step must be named — and it recurs: it was
-- proved locally at OrientationRigCatSym (Σ-≡ pairing, the second component
-- transported along the first) and again at Algebra.Z.JacobianNegSemiring
-- (GradedAssocOver at a constant carrier family). Same shape, same argument
-- order (proof, value); homed here beside `subst`, level-polymorphic.
-- (⟡subst-const-home — DISCHARGED.)
subst-const : {A : Set a} {B : Set b} {x y : A} (p : x ≡ y) (v : B) →
              subst (λ _ → B) p v ≡ v
subst-const refl v = refl

------------------------------------------------------------------------
-- Naturality-step combinator: `trans (cong f p) q` packaged as one
-- inference rule. Categorically a chain-cong / naturality-square step;
-- recognisable site-shape across the repo (338+ occurrences in 124
-- files at extraction time). Naming the step makes the rewrite-chain
-- structure visible to the similarity checker.
------------------------------------------------------------------------

cong-trans : {A : Set a} {B : Set b} (f : A → B) {x y : A} {z : B} →
             x ≡ y → f y ≡ z → f x ≡ z
cong-trans f p q = trans (cong f p) q

------------------------------------------------------------------------
-- Sym-composition pair. `sym-trans p q` rewrites the source of `q`
-- backwards along `p`; `trans-sym p q` rewrites the target of `p`
-- backwards along `q`. Together they package the two dual triangles
-- against a shared endpoint: `sym-trans` shares the source, `trans-sym`
-- shares the target. 72 + 81 occurrences across the repo at extraction.
------------------------------------------------------------------------

sym-trans : {A : Set a} {x y z : A} → x ≡ y → x ≡ z → y ≡ z
sym-trans p q = trans (sym p) q

trans-sym : {A : Set a} {x y z : A} → x ≡ y → z ≡ y → x ≡ z
trans-sym p q = trans p (sym q)

------------------------------------------------------------------------
-- Equational-reasoning syntax.
------------------------------------------------------------------------

module ≡-Reasoning {a : Level} where
  infix  3 _∎
  infixr 2 _≡⟨_⟩_ _≡⟨⟩_
  infix  1 begin_

  begin_ : {A : Set a} {x y : A} → x ≡ y → x ≡ y
  begin_ p = p

  _≡⟨_⟩_ : {A : Set a} (x : A) {y z : A} → x ≡ y → y ≡ z → x ≡ z
  _ ≡⟨ p ⟩ q = trans p q

  _≡⟨⟩_ : {A : Set a} (x : A) {y : A} → x ≡ y → x ≡ y
  _ ≡⟨⟩ q = q

  _∎ : {A : Set a} (x : A) → x ≡ x
  _ ∎ = refl
