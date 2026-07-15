------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Eval
--
-- THE TERM ↔ CATEGORY BRIDGE, ⟡ta-upterm form. UPTermO (the Set₀ free
-- category over the object-alphabet O with Hom-payload generators) folds
-- uniquely into any target category C : UPCategory O Hom.
--
--   eval  : UPTermO O Hom X Y → Hom X Y   (term → morphism; realise the stack)
--   reify : Hom X Y → UPTermO O Hom X Y   (morphism → term; a one-generator word)
--
-- and the round-trip eval ∘ reify ≡ id. This is the Free⊣Forgetful realisation:
-- UPTermO is free, C the structure, eval the unique structure-map, reify the unit.
--
-- ⚠ FLAG (i): over the ABSTRACT interface C, the round-trip / identity / assoc
-- laws are NOT refl — they ARE C's law-fields (id-leftˡ / id-rightʳ / assoc). They
-- become refl only at the concrete UPMorphism η-instance (a UPCategory whose laws
-- are λ _ → refl). K=Hom: the generator payload IS a Hom morphism (κ = id), so
-- interp = the payload itself; that keeps eval/reify/normalize/UPTermO-Canonical
-- structurally intact.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Eval where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.Quotient
  using (Quotient; ker-Quotient; split-Canonical)
  renaming (Canonical to Canonical⟦de760d07⟧)
open import Substrate.Category.UniversalProperty.Term
  using (UPGenO; liftO; UPTermO; []O; _∷O_; _++ᵤO_)
open import Substrate.Category.UniversalProperty.Category
  using (UPCategory)

-- The whole bridge lives over an object-alphabet O, a Hom family, and a target
-- category C. `open UPCategory C` names id-hom / compose-hom / the three laws.
module _ (O : Set) (Hom : O → O → Set) (C : UPCategory O Hom) where

  open UPCategory C

  ----------------------------------------------------------------------
  -- eval — the term → morphism bridge. []O ↦ identity; (liftO m ∷O t) ↦ compose.
  ----------------------------------------------------------------------

  eval : {X Y : O} → UPTermO O Hom X Y → Hom X Y
  eval []O            = id-hom _
  eval (liftO m ∷O t) = compose-hom (eval t) m

  ----------------------------------------------------------------------
  -- reify — the morphism → term bridge: a single-generator word.
  ----------------------------------------------------------------------

  reify : {X Y : O} → Hom X Y → UPTermO O Hom X Y
  reify m = liftO m ∷O []O

  -- The round-trip: eval (reify m) = compose-hom (id-hom _) m ≡ m by C's LEFT
  -- identity law (FLAG i — NOT refl over abstract C).
  eval-reify : {X Y : O} (m : Hom X Y) → eval (reify m) ≡ m
  eval-reify m = id-leftˡ m

  ----------------------------------------------------------------------
  -- eval IS A FUNCTOR: it carries term concatenation to morphism composition.
  -- eval (s ++ᵤO t) ≡ compose-hom (eval t) (eval s). Uses C's RIGHT identity
  -- (base) and assoc (step) — the FLAG (i) laws again.
  ----------------------------------------------------------------------

  eval-++ : {X Y Z : O} (s : UPTermO O Hom X Y) (t : UPTermO O Hom Y Z)
          → eval (s ++ᵤO t) ≡ compose-hom (eval t) (eval s)
  eval-++ []O            t = sym (id-rightʳ (eval t))
  eval-++ (liftO m ∷O s) t =
    trans (cong (λ X → compose-hom X m) (eval-++ s t))
          (assoc (eval t) (eval s) m)

  eval-cong : {X Y : O} {s t : UPTermO O Hom X Y} → s ≡ t → eval s ≡ eval t
  eval-cong = cong eval

  ----------------------------------------------------------------------
  -- THE COMMON STRUCTURE: eval = foldUPTermO into C (interp = unlift). The free
  -- catamorphism — the unique functor out of the free category UPTermO. (Same
  -- centre as FreeUP.extend / eea-fold: a word folds uniquely into any target.)
  ----------------------------------------------------------------------

  foldUPTermO : {T : O → O → Set}
              → ({X : O} → T X X)
              → ({X Y Z : O} → T Y Z → T X Y → T X Z)
              → ({X Y : O} → UPGenO O Hom X Y → T X Y)
              → {X Y : O} → UPTermO O Hom X Y → T X Y
  foldUPTermO idT cmpT interp []O            = idT
  foldUPTermO idT cmpT interp (g ∷O t)       = cmpT (foldUPTermO idT cmpT interp t) (interp g)

  unlift : {X Y : O} → UPGenO O Hom X Y → Hom X Y
  unlift (liftO m) = m

  eval-is-fold : {X Y : O} (t : UPTermO O Hom X Y)
               → eval t ≡ foldUPTermO (λ {Z} → id-hom Z) compose-hom unlift t
  eval-is-fold []O            = refl
  eval-is-fold (liftO m ∷O t) = cong (λ w → compose-hom w m) (eval-is-fold t)

  -- The universal property: ANY functor G (sends []O to idT, g∷t to cmp) IS the
  -- fold. (FreeUP.extend-unique at UPTermO.)
  foldUPTermO-unique :
    {T : O → O → Set}
    (idT : {X : O} → T X X)
    (cmpT : {X Y Z : O} → T Y Z → T X Y → T X Z)
    (interp : {X Y : O} → UPGenO O Hom X Y → T X Y)
    (G : {X Y : O} → UPTermO O Hom X Y → T X Y)
    → ({X : O} → G ([]O {X = X}) ≡ idT {X})
    → ({X Y Z : O} (g : UPGenO O Hom X Y) (t : UPTermO O Hom Y Z)
       → G (g ∷O t) ≡ cmpT (G t) (interp g))
    → {X Y : O} (t : UPTermO O Hom X Y) → G t ≡ foldUPTermO idT cmpT interp t
  foldUPTermO-unique idT cmpT interp G Gnil Gcons []O            = Gnil
  foldUPTermO-unique idT cmpT interp G Gnil Gcons (g ∷O t) =
    trans (Gcons g t)
          (cong (λ X → cmpT X (interp g))
                (foldUPTermO-unique idT cmpT interp G Gnil Gcons t))

  ----------------------------------------------------------------------
  -- UP4: the congruence induced by eval's kernel pair. s ≈ᵤ t iff eval s ≡ eval t;
  -- it respects composition (the kernel of a functor is a congruence), so the
  -- quotient UPTermO / ≈ᵤ is a category.
  ----------------------------------------------------------------------

  _≈ᵤ_ : {X Y : O} → UPTermO O Hom X Y → UPTermO O Hom X Y → Set
  s ≈ᵤ t = eval s ≡ eval t

  ≈ᵤ-cong-++ : {X Y Z : O} {s s' : UPTermO O Hom X Y} {t t' : UPTermO O Hom Y Z}
             → s ≈ᵤ s' → t ≈ᵤ t' → (s ++ᵤO t) ≈ᵤ (s' ++ᵤO t')
  ≈ᵤ-cong-++ {s = s} {s'} {t} {t'} ss tt =
    trans (eval-++ s t)
          (trans (cong₂ compose-hom tt ss)
                 (sym (eval-++ s' t')))

  ----------------------------------------------------------------------
  -- THE QUOTIENT — the substrate way: a section-based Quotient (the ℚ pattern).
  -- normalize = reify ∘ eval is the canonical form (idempotent); ≈ᵤ is decided by
  -- normal-form equality. UPTermO/≈ᵤ IS split-Canonical eval reify eval-reify.
  ----------------------------------------------------------------------

  normalize : {X Y : O} → UPTermO O Hom X Y → UPTermO O Hom X Y
  normalize t = reify (eval t)

  normalize-eval : {X Y : O} (t : UPTermO O Hom X Y) → eval (normalize t) ≡ eval t
  normalize-eval t = eval-reify (eval t)

  normalize-idem : {X Y : O} (t : UPTermO O Hom X Y)
                 → normalize (normalize t) ≡ normalize t
  normalize-idem t = cong reify (normalize-eval t)

  ≈ᵤ→normal : {X Y : O} {s t : UPTermO O Hom X Y} → s ≈ᵤ t → normalize s ≡ normalize t
  ≈ᵤ→normal e = cong reify e

  normal→≈ᵤ : {X Y : O} {s t : UPTermO O Hom X Y} → normalize s ≡ normalize t → s ≈ᵤ t
  normal→≈ᵤ {s = s} {t} p =
    trans (sym (normalize-eval s)) (trans (cong eval p) (normalize-eval t))

  UPTermO-Quotient : (X Y : O) → Quotient (UPTermO O Hom X Y) _≈ᵤ_
  UPTermO-Quotient X Y = ker-Quotient (eval {X} {Y})

  UPTermO-Canonical : (X Y : O) → Canonical⟦de760d07⟧ (UPTermO-Quotient X Y)
  UPTermO-Canonical X Y = split-Canonical (eval {X} {Y}) reify eval-reify
