------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Eval
--
-- THE TERM ↔ CATEGORY BRIDGE, ⟡ta-upterm form. UPTerm (the Set₀ free
-- category over the object-alphabet O with Hom-payload generators) folds
-- uniquely into any target category C : UPCategory O Hom.
--
--   eval  : UPTerm O Hom X Y → Hom X Y   (term → morphism; realise the stack)
--   reify : Hom X Y → UPTerm O Hom X Y   (morphism → term; a one-generator word)
--
-- and the round-trip eval ∘ reify ≡ id. This is the Free⊣Forgetful realisation:
-- UPTerm is free, C the structure, eval the unique structure-map, reify the unit.
--
-- ⚠ FLAG (i): over the ABSTRACT interface C, the round-trip / identity / assoc
-- laws are NOT refl — they ARE C's law-fields (id-leftˡ / id-rightʳ / assoc). They
-- become refl only at the concrete UPMorphism η-instance (a UPCategory whose laws
-- are λ _ → refl). K=Hom: the generator payload IS a Hom morphism (κ = id), so
-- interp = the payload itself; that keeps eval/reify/normalize/UPTerm-Canonical
-- structurally intact.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Eval where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.Quotient
  using (Quotient; ker-Quotient; split-Canonical)
  renaming (Canonical to Canonical⟦de760d07⟧)
open import Substrate.Category.UniversalProperty.Term
  using (UPGen; lift; UPTerm; []; _∷_; _++ᵤ_)
open import Substrate.Category.UniversalProperty.Category
  using (UPCategory)

-- The whole bridge lives over an object-alphabet O, a Hom family, and a target
-- category C. `open UPCategory C` names id-hom / compose-hom / the three laws.
module _ (O : Set) (Hom : O → O → Set) (C : UPCategory O Hom) where

  open UPCategory C

  ----------------------------------------------------------------------
  -- eval — the term → morphism bridge. [] ↦ identity; (lift m ∷ t) ↦ compose.
  ----------------------------------------------------------------------

  eval : {X Y : O} → UPTerm O Hom X Y → Hom X Y
  eval []            = id-hom _
  eval (lift m ∷ t) = compose-hom (eval t) m

  ----------------------------------------------------------------------
  -- reify — the morphism → term bridge: a single-generator word.
  ----------------------------------------------------------------------

  reify : {X Y : O} → Hom X Y → UPTerm O Hom X Y
  reify m = lift m ∷ []

  -- The round-trip: eval (reify m) = compose-hom (id-hom _) m ≡ m by C's LEFT
  -- identity law (FLAG i — NOT refl over abstract C).
  eval-reify : {X Y : O} (m : Hom X Y) → eval (reify m) ≡ m
  eval-reify m = id-leftˡ m

  ----------------------------------------------------------------------
  -- eval IS A FUNCTOR: it carries term concatenation to morphism composition.
  -- eval (s ++ᵤ t) ≡ compose-hom (eval t) (eval s). Uses C's RIGHT identity
  -- (base) and assoc (step) — the FLAG (i) laws again.
  ----------------------------------------------------------------------

  eval-++ : {X Y Z : O} (s : UPTerm O Hom X Y) (t : UPTerm O Hom Y Z)
          → eval (s ++ᵤ t) ≡ compose-hom (eval t) (eval s)
  eval-++ []            t = sym (id-rightʳ (eval t))
  eval-++ (lift m ∷ s) t =
    trans (cong (λ X → compose-hom X m) (eval-++ s t))
          (assoc (eval t) (eval s) m)

  eval-cong : {X Y : O} {s t : UPTerm O Hom X Y} → s ≡ t → eval s ≡ eval t
  eval-cong = cong eval

  ----------------------------------------------------------------------
  -- THE COMMON STRUCTURE: eval = foldUPTerm into C (interp = unlift). The free
  -- catamorphism — the unique functor out of the free category UPTerm. (Same
  -- centre as FreeUP.extend / eea-fold: a word folds uniquely into any target.)
  ----------------------------------------------------------------------

  foldUPTerm : {T : O → O → Set}
              → ({X : O} → T X X)
              → ({X Y Z : O} → T Y Z → T X Y → T X Z)
              → ({X Y : O} → UPGen O Hom X Y → T X Y)
              → {X Y : O} → UPTerm O Hom X Y → T X Y
  foldUPTerm idT cmpT interp []            = idT
  foldUPTerm idT cmpT interp (g ∷ t)       = cmpT (foldUPTerm idT cmpT interp t) (interp g)

  unlift : {X Y : O} → UPGen O Hom X Y → Hom X Y
  unlift (lift m) = m

  eval-is-fold : {X Y : O} (t : UPTerm O Hom X Y)
               → eval t ≡ foldUPTerm (λ {Z} → id-hom Z) compose-hom unlift t
  eval-is-fold []            = refl
  eval-is-fold (lift m ∷ t) = cong (λ w → compose-hom w m) (eval-is-fold t)

  -- The universal property: ANY functor G (sends [] to idT, g∷t to cmp) IS the
  -- fold. (FreeUP.extend-unique at UPTerm.)
  foldUPTerm-unique :
    {T : O → O → Set}
    (idT : {X : O} → T X X)
    (cmpT : {X Y Z : O} → T Y Z → T X Y → T X Z)
    (interp : {X Y : O} → UPGen O Hom X Y → T X Y)
    (G : {X Y : O} → UPTerm O Hom X Y → T X Y)
    → ({X : O} → G ([] {X = X}) ≡ idT {X})
    → ({X Y Z : O} (g : UPGen O Hom X Y) (t : UPTerm O Hom Y Z)
       → G (g ∷ t) ≡ cmpT (G t) (interp g))
    → {X Y : O} (t : UPTerm O Hom X Y) → G t ≡ foldUPTerm idT cmpT interp t
  foldUPTerm-unique idT cmpT interp G Gnil Gcons []            = Gnil
  foldUPTerm-unique idT cmpT interp G Gnil Gcons (g ∷ t) =
    trans (Gcons g t)
          (cong (λ X → cmpT X (interp g))
                (foldUPTerm-unique idT cmpT interp G Gnil Gcons t))

  ----------------------------------------------------------------------
  -- UP4: the congruence induced by eval's kernel pair. s ≈ᵤ t iff eval s ≡ eval t;
  -- it respects composition (the kernel of a functor is a congruence), so the
  -- quotient UPTerm / ≈ᵤ is a category.
  ----------------------------------------------------------------------

  _≈ᵤ_ : {X Y : O} → UPTerm O Hom X Y → UPTerm O Hom X Y → Set
  s ≈ᵤ t = eval s ≡ eval t

  ≈ᵤ-cong-++ : {X Y Z : O} {s s' : UPTerm O Hom X Y} {t t' : UPTerm O Hom Y Z}
             → s ≈ᵤ s' → t ≈ᵤ t' → (s ++ᵤ t) ≈ᵤ (s' ++ᵤ t')
  ≈ᵤ-cong-++ {s = s} {s'} {t} {t'} ss tt =
    trans (eval-++ s t)
          (trans (cong₂ compose-hom tt ss)
                 (sym (eval-++ s' t')))

  ----------------------------------------------------------------------
  -- THE QUOTIENT — the substrate way: a section-based Quotient (the ℚ pattern).
  -- normalize = reify ∘ eval is the canonical form (idempotent); ≈ᵤ is decided by
  -- normal-form equality. UPTerm/≈ᵤ IS split-Canonical eval reify eval-reify.
  ----------------------------------------------------------------------

  normalize : {X Y : O} → UPTerm O Hom X Y → UPTerm O Hom X Y
  normalize t = reify (eval t)

  normalize-eval : {X Y : O} (t : UPTerm O Hom X Y) → eval (normalize t) ≡ eval t
  normalize-eval t = eval-reify (eval t)

  normalize-idem : {X Y : O} (t : UPTerm O Hom X Y)
                 → normalize (normalize t) ≡ normalize t
  normalize-idem t = cong reify (normalize-eval t)

  ≈ᵤ→normal : {X Y : O} {s t : UPTerm O Hom X Y} → s ≈ᵤ t → normalize s ≡ normalize t
  ≈ᵤ→normal e = cong reify e

  normal→≈ᵤ : {X Y : O} {s t : UPTerm O Hom X Y} → normalize s ≡ normalize t → s ≈ᵤ t
  normal→≈ᵤ {s = s} {t} p =
    trans (sym (normalize-eval s)) (trans (cong eval p) (normalize-eval t))

  UPTerm-Quotient : (X Y : O) → Quotient (UPTerm O Hom X Y) _≈ᵤ_
  UPTerm-Quotient X Y = ker-Quotient (eval {X} {Y})

  UPTerm-Canonical : (X Y : O) → Canonical⟦de760d07⟧ (UPTerm-Quotient X Y)
  UPTerm-Canonical X Y = split-Canonical (eval {X} {Y}) reify eval-reify
