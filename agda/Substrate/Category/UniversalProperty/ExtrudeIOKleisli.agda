{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOKleisli — ⟡extrude-io-kleisli-record: the MULTI-object
-- Kleisli category of IO, with its category laws via POINTWISE IO-equality (bisimilarity) — each law a
-- VALUE-≡, NO funext. 285's 𝔼mit was the single-object case (Mor = IO Unit, a concrete type). The multi-object
-- case has Mor a b = ⟦a⟧ → IO ⟦b⟧ (a function type), so the category laws are equalities of FUNCTIONS — which
-- would need funext at ≡. The operator's frame: use bisimilarity/pointwise, not funext. So the morphism-
-- equality is POINTWISE IO-equality (_≐_ : f ≐ g iff ∀ x, f x ≡ g x), and the category laws hold at _≐_ —
-- each instance a value-≡ (the monad laws), NO funext. Since IO is inductive/finite, pointwise-≡ IS
-- bisimilarity; _≐_ is the non-funext morphism-equality the repo's setoid-style categories want.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: the Kleisli data (𝕆/⟦_⟧
-- supplied, Kmor/Kid/Kcompose), the pointwise morphism-equality _≐_ (+ its equivalence: refl/sym/trans), and
-- the category laws at _≐_ (left-id/right-id/assoc — each a value-≡ via the monad laws). The framing ('multi-
-- object Kleisli via bisimilarity, no funext') is (prose: 285 + Category.CategoryOf; the CategoryOf RECORD at
-- ≡ needs funext, so the setoid-form _≐_ is the honest non-funext packaging).
------------------------------------------------------------------------

-- MODULE PARAMETERS: the output O, the objects 𝕆, and their carriers ⟦_⟧ — all caller-supplied (parametrized,
-- no Set₁, no quantifying over all types):
module Substrate.Category.UniversalProperty.ExtrudeIOKleisli
  (O : Set) (𝕆 : Set) (⟦_⟧ : 𝕆 → Set) where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Category.UniversalProperty.ExtrudeIO O
  using (IO; ret; _>>=_; >>=-right-id; >>=-assoc)

------------------------------------------------------------------------
-- ① THE KLEISLI DATA: morphisms are emit-computations ⟦a⟧ → IO ⟦b⟧; id = ret; compose = Kleisli bind.
------------------------------------------------------------------------
Kmor : 𝕆 → 𝕆 → Set
Kmor a b = ⟦ a ⟧ → IO ⟦ b ⟧

Kid : (a : 𝕆) → Kmor a a
Kid a = ret

Kcompose : {a b c : 𝕆} → Kmor b c → Kmor a b → Kmor a c
Kcompose g f = λ x → f x >>= g

------------------------------------------------------------------------
-- ② THE POINTWISE MORPHISM-EQUALITY _≐_ (the non-funext equality — for finite IO this IS bisimilarity): two
--    Kleisli morphisms are equal iff they agree on every input, at ≡ on IO-VALUES. An equivalence relation.
------------------------------------------------------------------------
_≐_ : {a b : 𝕆} → Kmor a b → Kmor a b → Set
_≐_ {a} f g = (x : ⟦ a ⟧) → f x ≡ g x

infix 4 _≐_

≐-refl  : {a b : 𝕆} (f : Kmor a b) → f ≐ f
≐-refl f x = refl

≐-sym   : {a b : 𝕆} {f g : Kmor a b} → f ≐ g → g ≐ f
≐-sym p x = sym (p x)

≐-trans : {a b : 𝕆} {f g h : Kmor a b} → f ≐ g → g ≐ h → f ≐ h
≐-trans p q x = trans (p x) (q x)

------------------------------------------------------------------------
-- ③ THE CATEGORY LAWS at _≐_ (each a VALUE-≡ via the monad laws — NO funext): the multi-object Kleisli
--    category is a genuine category, its laws holding up to the pointwise/bisimilar morphism-equality.
------------------------------------------------------------------------
K-left-id : {a b : 𝕆} (f : Kmor a b) → Kcompose (Kid b) f ≐ f
K-left-id f x = >>=-right-id (f x)                       -- (f x >>= ret) ≡ f x

K-right-id : {a b : 𝕆} (f : Kmor a b) → Kcompose f (Kid a) ≐ f
K-right-id f x = refl                                    -- (ret x >>= f) = f x

K-assoc : {a b c d : 𝕆} (f : Kmor a b) (g : Kmor b c) (h : Kmor c d) →
          Kcompose h (Kcompose g f) ≐ Kcompose (Kcompose h g) f
K-assoc f g h x = >>=-assoc (f x) g h                    -- ((f x >>= g) >>= h) ≡ (f x >>= λ y → g y >>= h)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the multi-object Kleisli category of IO is a genuine category up to the
-- POINTWISE/bisimilar morphism-equality _≐_, its laws each a VALUE-≡ via the monad laws — NO funext): 285's
-- 𝔼mit handled the single object (Mor = IO Unit, a concrete type, laws at ≡ on values). The multi-object case
-- (①: Kmor a b = ⟦a⟧ → IO ⟦b⟧) has FUNCTION morphisms, so category laws at ≡ would need funext. The operator's
-- frame dissolves this: the morphism-equality is _≐_ (②, pointwise IO-equality — an equivalence, and for
-- finite IO exactly bisimilarity), and the laws (③: K-left-id/K-right-id/K-assoc) hold at _≐_, each instance a
-- VALUE-≡ discharged by the monad laws (>>=-right-id / refl / >>=-assoc) — NO funext, NO Set₁, all module-
-- parametrized over supplied 𝕆/⟦_⟧. So the Kleisli category is a genuine category enriched in the pointwise/
-- bisimilar setoid — the non-funext multi-object instance the operator asked for. Chain: 285 (single-object
-- 𝔼mit) → 286c (multi-object Kleisli via bisimilarity).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the Kleisli data (Kmor/Kid/Kcompose), the pointwise equality _≐_
-- (equivalence: refl/sym/trans), the category laws at _≐_ (each a value-≡, NO funext). SCOPED: bundling into
-- the repo's CategoryOf RECORD (whose laws are ≡, not _≐_) needs either funext (to turn _≐_ into ≡ — NOT
-- taken) or a setoid-enriched CategoryOf variant (Mor-equality a supplied relation — ⟡extrude-setoid-category,
-- if the repo grows one). What's grounded: the multi-object Kleisli category up to the pointwise/bisimilar
-- morphism-equality, laws NO funext — the operator's non-funext frame, parametrized.
------------------------------------------------------------------------
