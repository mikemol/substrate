------------------------------------------------------------------------
-- Substrate.Category.Allegory
--
-- The allegory of (proof-relevant) relations — `Rel A B = A → B → Set`,
-- a relation presented as its FIBER FAMILY (the `Dir : Pos → Set` of a
-- polynomial functor IS this fiber family; `Poly.◁` IS relational
-- composition). Steps 0→4 of the allegory build:
--   0. Rel + the inclusion order `_⊆_` (and `_≈_` = mutual ⊆).
--   1. identity `idR` + composition `_⨾_` (= Σ over the middle = Poly ◁);
--      Rel is a `TwoCategory` with TwoCell = ⊆.
--   2. converse `_†` (fiber-flip) + the three dagger laws (up to ≈).
--   3. meets `_∧_` (pointwise ×) + the GLB universal property.
--   4. the MODULAR LAW — the axiom that earns the name "allegory".
--
-- POSET-ENRICHED, NOT strict-≡.  Set-valued relations form a category
-- only UP TO ≈ (mutual ⊆): `(idR ⨾ R) a b = Σ[a'] (a≡a') × R a' b` is
-- merely ISO to `R a b`, and contracting that singleton needs
-- univalence/propext — unavailable under `--safe --without-K` (no funext
-- in Foundation; postulates banned).  So we do NOT instantiate the
-- strict-≡ `CategoryOf`/`DaggerCategory` records (their laws are
-- unprovable here); we reuse `TwoCategory`'s 2-cell layer (`TwoCell f g
-- = f ⊆ g`, `comp-2-vertical = ⊆-trans`), whose coherence is "supplied
-- by concrete consumers" — exactly the order-enrichment an allegory is.
--
-- This closes the semantic-relation-algebra obligation DEFERRED in
-- `Kelen.RelationCompose` ("Rel-category morphisms, dagger structure,
-- residuals") — that module is the word-level home and names this as its
-- sequel.  Residuals (division allegory: root/log unified) are Step 6.
--
-- Φ-FLOOR (the recursion's actual bottom): a relation is the fiber
-- family `R : Pos → Set`; a MAP is the special case where every fiber is
-- a singleton.  `GradedDivStr.R : ℕ → Set` is the stage-n iterate `Rⁿ`
-- of a monotone fiber-refinement operator `Φ`; `Certified (rem<b)` is one
-- Φ-step; `recon-bounded-unique` is the theorem that Φ converges to a
-- singleton (a map).  "Map vs relation" is not a chosen structure but
-- the singleton-vs-not READOUT of μΦ — Steps 5/7 make this a theorem.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory where

open import Substrate.Foundation.Level using (Level; _⊔_; 0ℓ) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Category.TwoCategory using (TwoCategory)

------------------------------------------------------------------------
-- Step 0 — relations as fiber families, with the inclusion order.
------------------------------------------------------------------------

Rel : Set → Set → Set₁
Rel A B = A → B → Set

infix 4 _⊆_
_⊆_ : {A B : Set} → Rel A B → Rel A B → Set
_⊆_ {A} {B} R S = (a : A) (b : B) → R a b → S a b

⊆-refl : {A B : Set} {R : Rel A B} → R ⊆ R
⊆-refl _ _ r = r

⊆-trans : {A B : Set} {R S T : Rel A B} → R ⊆ S → S ⊆ T → R ⊆ T
⊆-trans p q a b r = q a b (p a b r)

-- hom-equivalence = mutual inclusion (the ≈ the laws hold up to).
_≈_ : {A B : Set} → Rel A B → Rel A B → Set
R ≈ S = (R ⊆ S) × (S ⊆ R)

------------------------------------------------------------------------
-- Step 1 — identity + composition (relational comp = Σ over the middle = Poly ◁).
------------------------------------------------------------------------

idR : (A : Set) → A → A → Set
idR A a a' = a ≡ a'

infixr 9 _⨾_
_⨾_ : {A B C : Set} → Rel A B → Rel B C → A → C → Set
_⨾_ {A} {B} {C} R S a c = Σ B (λ b → (R a b) × (S b c))

⨾-identityˡ : {A B : Set} (R : Rel A B) → (idR A ⨾ R) ≈ R
⨾-identityˡ R = (λ { a b (_ , (refl , r)) → r })
              , (λ a b r → a , (refl , r))

⨾-identityʳ : {A B : Set} (R : Rel A B) → (R ⨾ idR B) ≈ R
⨾-identityʳ R = (λ { a b (_ , (r , refl)) → r })
              , (λ a b r → b , (r , refl))

⨾-assoc : {A B C D : Set} (R : Rel A B) (S : Rel B C) (T : Rel C D)
        → ((R ⨾ S) ⨾ T) ≈ (R ⨾ (S ⨾ T))
⨾-assoc R S T = (λ { a d (c , ((b , (r , s)) , t)) → b , (r , (c , (s , t))) })
              , (λ { a d (b , (r , (c , (s , t)))) → c , ((b , (r , s)) , t) })

------------------------------------------------------------------------
-- Step 2 — converse (flip the fiber); the three dagger laws up to ≈.
------------------------------------------------------------------------

infix 8 _†
_† : {A B : Set} → Rel A B → B → A → Set
(R †) b a = R a b

†-id : (A : Set) → ((idR A) †) ≈ idR A
†-id A = (λ a a' eq → sym eq) , (λ a a' eq → sym eq)

†-comp : {A B C : Set} (R : Rel A B) (S : Rel B C)
       → ((R ⨾ S) †) ≈ ((S †) ⨾ (R †))
†-comp R S = (λ { c a (b , (r , s)) → b , (s , r) })
           , (λ { c a (b , (s , r)) → b , (r , s) })

†-invol : {A B : Set} (R : Rel A B) → ((R †) †) ≈ R
†-invol R = ⊆-refl , ⊆-refl   -- (R †) † a b ≡ R a b definitionally

------------------------------------------------------------------------
-- Step 3 — meets (pointwise product of fibers); the GLB universal property.
------------------------------------------------------------------------

infixr 7 _∧_
_∧_ : {A B : Set} → Rel A B → Rel A B → A → B → Set
(R ∧ S) a b = (R a b) × (S a b)

∧-⊆ˡ : {A B : Set} (R S : Rel A B) → (R ∧ S) ⊆ R
∧-⊆ˡ R S a b (r , s) = r

∧-⊆ʳ : {A B : Set} (R S : Rel A B) → (R ∧ S) ⊆ S
∧-⊆ʳ R S a b (r , s) = s

∧-greatest : {A B : Set} {R S T : Rel A B} → T ⊆ R → T ⊆ S → T ⊆ (R ∧ S)
∧-greatest p q a b t = (p a b t , q a b t)

------------------------------------------------------------------------
-- Step 4 — the modular law (the gate that earns "allegory").
--   (R⨾S) ∧ T  ⊆  (R ∧ (T ⨾ S†)) ⨾ S
-- Constructive Σ/×-rearrangement: Rel is the tabular allegory.
------------------------------------------------------------------------

modular : {A B C : Set} (R : Rel A B) (S : Rel B C) (T : Rel A C)
        → ((R ⨾ S) ∧ T) ⊆ ((R ∧ (T ⨾ (S †))) ⨾ S)
modular R S T a c ((b , (r , s)) , t) = b , ((r , (c , (t , s))) , s)

------------------------------------------------------------------------
-- Step 1 deliverable (REUSE) — Rel is a TwoCategory with TwoCell = ⊆.
------------------------------------------------------------------------

Rel-TwoCategory : TwoCategory {lsuc 0ℓ} {lsuc 0ℓ} {0ℓ}
Rel-TwoCategory = record
  { Obj             = Set
  ; Mor             = Rel
  ; TwoCell         = _⊆_
  ; id-1            = idR
  ; comp-1          = λ S R → R ⨾ S          -- comp-1 g f = f ⨾ g
  ; id-2            = λ f → ⊆-refl
  ; comp-2-vertical = λ gh fg → ⊆-trans fg gh
  }

------------------------------------------------------------------------
-- Step 4 deliverable — the generic Allegory record, inhabited by Rel.
------------------------------------------------------------------------

record Allegory (ℓo ℓh ℓc : Level) : Set (lsuc (ℓo ⊔ ℓh ⊔ ℓc)) where
  field
    Obj      : Set ℓo
    Hom      : Obj → Obj → Set ℓh
    _⊑_      : {A B : Obj} → Hom A B → Hom A B → Set ℓc
    ⊑-refl′  : {A B : Obj} {f : Hom A B} → f ⊑ f
    ⊑-trans′ : {A B : Obj} {f g h : Hom A B} → f ⊑ g → g ⊑ h → f ⊑ h
    Id       : (A : Obj) → Hom A A
    _⨟_      : {A B C : Obj} → Hom A B → Hom B C → Hom A C
    inv      : {A B : Obj} → Hom A B → Hom B A
    _⊓_      : {A B : Obj} → Hom A B → Hom A B → Hom A B
    -- identity + associativity (both ⊑ directions = up to ≈)
    idˡ      : {A B : Obj} {f : Hom A B} → (Id A ⨟ f) ⊑ f
    idˡ⁻     : {A B : Obj} {f : Hom A B} → f ⊑ (Id A ⨟ f)
    idʳ      : {A B : Obj} {f : Hom A B} → (f ⨟ Id B) ⊑ f
    idʳ⁻     : {A B : Obj} {f : Hom A B} → f ⊑ (f ⨟ Id B)
    assoc    : {A B C D : Obj} {f : Hom A B} {g : Hom B C} {h : Hom C D}
             → ((f ⨟ g) ⨟ h) ⊑ (f ⨟ (g ⨟ h))
    assoc⁻   : {A B C D : Obj} {f : Hom A B} {g : Hom B C} {h : Hom C D}
             → (f ⨟ (g ⨟ h)) ⊑ ((f ⨟ g) ⨟ h)
    -- dagger
    inv-id    : {A : Obj} → (inv (Id A)) ⊑ Id A
    inv-id⁻   : {A : Obj} → (Id A) ⊑ inv (Id A)
    inv-comp  : {A B C : Obj} {f : Hom A B} {g : Hom B C}
              → (inv (f ⨟ g)) ⊑ (inv g ⨟ inv f)
    inv-comp⁻ : {A B C : Obj} {f : Hom A B} {g : Hom B C}
              → (inv g ⨟ inv f) ⊑ inv (f ⨟ g)
    inv-invol : {A B : Obj} {f : Hom A B} → (inv (inv f)) ⊑ f
    -- meet GLB
    meet-l        : {A B : Obj} {f g : Hom A B} → (f ⊓ g) ⊑ f
    meet-r        : {A B : Obj} {f g : Hom A B} → (f ⊓ g) ⊑ g
    meet-greatest : {A B : Obj} {f g h : Hom A B} → h ⊑ f → h ⊑ g → h ⊑ (f ⊓ g)
    -- modular law
    modular-law : {A B C : Obj} {R : Hom A B} {S : Hom B C} {T : Hom A C}
                → ((R ⨟ S) ⊓ T) ⊑ ((R ⊓ (T ⨟ inv S)) ⨟ S)

Rel-Allegory : Allegory (lsuc 0ℓ) (lsuc 0ℓ) 0ℓ
Rel-Allegory = record
  { Obj = Set ; Hom = Rel ; _⊑_ = _⊆_
  ; ⊑-refl′ = ⊆-refl ; ⊑-trans′ = ⊆-trans
  ; Id = idR ; _⨟_ = _⨾_ ; inv = _† ; _⊓_ = _∧_
  ; idˡ  = λ {A}{B}{f} → proj₁ (⨾-identityˡ f)
  ; idˡ⁻ = λ {A}{B}{f} → proj₂ (⨾-identityˡ f)
  ; idʳ  = λ {A}{B}{f} → proj₁ (⨾-identityʳ f)
  ; idʳ⁻ = λ {A}{B}{f} → proj₂ (⨾-identityʳ f)
  ; assoc  = λ {A}{B}{C}{D}{f}{g}{h} → proj₁ (⨾-assoc f g h)
  ; assoc⁻ = λ {A}{B}{C}{D}{f}{g}{h} → proj₂ (⨾-assoc f g h)
  ; inv-id  = λ {A} → proj₁ (†-id A)
  ; inv-id⁻ = λ {A} → proj₂ (†-id A)
  ; inv-comp  = λ {A}{B}{C}{f}{g} → proj₁ (†-comp f g)
  ; inv-comp⁻ = λ {A}{B}{C}{f}{g} → proj₂ (†-comp f g)
  ; inv-invol = λ {A}{B}{f} → proj₁ (†-invol f)
  ; meet-l = λ {A}{B}{f}{g} → ∧-⊆ˡ f g
  ; meet-r = λ {A}{B}{f}{g} → ∧-⊆ʳ f g
  ; meet-greatest = ∧-greatest
  ; modular-law = λ {A}{B}{C}{R}{S}{T} → modular R S T
  }
