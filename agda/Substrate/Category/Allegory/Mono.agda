{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.Allegory.Mono — ⟡allegory-mono-upstream: the monotonicity, congruence,
-- and †-functor lemmas for the allegory of relations, consolidated into a canonical home
-- (a sibling of Allegory.Maps/Division/Power/Refinement). These are genuine additions the
-- core Category.Allegory lacked as named lemmas — assembled ad hoc across the stencil's
-- Dedekind sub-arc (StencilDedekind †-∧ 198, StencilDedekindCollapse ⨾-mono/∧-mono/det→incl
-- 199, StencilDedekindDagger †-mono/⨾-cong/∧-cong 201) — now upstreamed and de-duplicated.
--
-- Content: ≈ is an equivalence; † is an order-preserving FUNCTOR (†-mono/†-cong) that
-- distributes over meet (†-∧); ⨾ and ∧ are monotone and congruent in each argument; and a
-- map's determinism is the allegory inclusion f†⨾f ⊆ idR (det→incl). All --safe --without-K,
-- zero postulates — one-line Σ/×-manipulations or reductions to the core GLB lemmas.
------------------------------------------------------------------------

module Substrate.Category.Allegory.Mono where

open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Category.Allegory
  using (Rel; _⨾_; _∧_; _†; _⊆_; _≈_; idR; ⊆-refl; ⊆-trans; ∧-⊆ˡ; ∧-⊆ʳ; ∧-greatest)
open import Substrate.Category.Allegory.Maps using (deterministic)

------------------------------------------------------------------------
-- ① ≈ IS AN EQUIVALENCE (from ⊆-refl/⊆-trans, ≈ = ⊆ × ⊆).
------------------------------------------------------------------------
≈-refl : {A B : Set} {R : Rel A B} → R ≈ R
≈-refl = ⊆-refl , ⊆-refl

≈-sym : {A B : Set} {R S : Rel A B} → R ≈ S → S ≈ R
≈-sym (p , q) = q , p

≈-trans : {A B : Set} {R S T : Rel A B} → R ≈ S → S ≈ T → R ≈ T
≈-trans (p , q) (r , s) = ⊆-trans p r , ⊆-trans s q

------------------------------------------------------------------------
-- ② THE CONVERSE † IS AN ORDER-PRESERVING FUNCTOR that distributes over meet.
------------------------------------------------------------------------
†-mono : {A B : Set} {X Y : Rel A B} → X ⊆ Y → (X †) ⊆ (Y †)
†-mono p b a xba = p a b xba

†-cong : {A B : Set} {X Y : Rel A B} → X ≈ Y → (X †) ≈ (Y †)
†-cong (p , q) = †-mono p , †-mono q

-- converse distributes over meet: (R ∧ S)† ≈ (R† ∧ S†).  (definitional: both = R a b × S a b)
†-∧ : {A B : Set} (R S : Rel A B) → ((R ∧ S) †) ≈ ((R †) ∧ (S †))
†-∧ R S = (λ b a h → h) , (λ b a h → h)

------------------------------------------------------------------------
-- ③ COMPOSITION ⨾ IS MONOTONE AND CONGRUENT in each argument.
------------------------------------------------------------------------
⨾-mono-l : {A B C : Set} {X Y : Rel A B} (Z : Rel B C) → X ⊆ Y → (X ⨾ Z) ⊆ (Y ⨾ Z)
⨾-mono-l Z p a c (b , (xab , zbc)) = b , (p a b xab , zbc)

⨾-mono-r : {A B C : Set} (Z : Rel A B) {X Y : Rel B C} → X ⊆ Y → (Z ⨾ X) ⊆ (Z ⨾ Y)
⨾-mono-r Z p a c (b , (zab , xbc)) = b , (zab , p b c xbc)

⨾-mono : {A B C : Set} {X X' : Rel A B} {Y Y' : Rel B C}
       → X ⊆ X' → Y ⊆ Y' → (X ⨾ Y) ⊆ (X' ⨾ Y')
⨾-mono p q a c (b , (x , y)) = b , (p a b x , q b c y)

⨾-cong : {A B C : Set} {X X' : Rel A B} {Y Y' : Rel B C}
       → X ≈ X' → Y ≈ Y' → (X ⨾ Y) ≈ (X' ⨾ Y')
⨾-cong (p , p') (q , q') = ⨾-mono p q , ⨾-mono p' q'

------------------------------------------------------------------------
-- ④ MEET ∧ IS MONOTONE AND CONGRUENT in each argument (via the core GLB lemmas).
------------------------------------------------------------------------
∧-mono-l : {A B : Set} {X Y : Rel A B} (W : Rel A B) → X ⊆ Y → (X ∧ W) ⊆ (Y ∧ W)
∧-mono-l {X = X} W p = ∧-greatest (⊆-trans (∧-⊆ˡ X W) p) (∧-⊆ʳ X W)

∧-mono-r : {A B : Set} (W : Rel A B) {X Y : Rel A B} → X ⊆ Y → (W ∧ X) ⊆ (W ∧ Y)
∧-mono-r W {X} p = ∧-greatest (∧-⊆ˡ W X) (⊆-trans (∧-⊆ʳ W X) p)

∧-mono : {A B : Set} {X X' Y Y' : Rel A B} → X ⊆ X' → Y ⊆ Y' → (X ∧ Y) ⊆ (X' ∧ Y')
∧-mono p q a b (x , y) = p a b x , q a b y

∧-cong : {A B : Set} {X X' Y Y' : Rel A B} → X ≈ X' → Y ≈ Y' → (X ∧ Y) ≈ (X' ∧ Y')
∧-cong (p , p') (q , q') = ∧-mono p q , ∧-mono p' q'

------------------------------------------------------------------------
-- ⑤ A MAP'S DETERMINISM AS AN ALLEGORY INCLUSION: f single-valued ⟺ f† ⨾ f ⊆ idR.
------------------------------------------------------------------------
det→incl : {A B : Set} (f : Rel A B) → deterministic f → ((f †) ⨾ f) ⊆ idR B
det→incl f det b b' (a , (fab , fab')) = det a b b' fab fab'
