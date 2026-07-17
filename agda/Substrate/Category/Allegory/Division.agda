------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division  (ALG-6)
--
-- The DIVISION ALLEGORY of relations: the two residuals of composition,
-- with their defining adjunctions.  This is the conceptual destination of
-- the allegory walk — where root and log unify.
--
--   (R ∖ T) = greatest S with R⨾S ⊆ T   (left residual / "right division")
--   (S ／ T) = greatest R with R⨾S ⊆ T   (right residual / "left division")
--
-- characterized by the two adjunctions
--   R⨾S ⊆ T  ⇔  S ⊆ R∖T        (∖-adjˡ / ∖-adjˡ⁻)
--   R⨾S ⊆ T  ⇔  R ⊆ S／T        (／-adjʳ / ／-adjʳ⁻)
--
-- THE GEM — root and log without the either/or.  Left and right division
-- are ONE operation conjugated by the converse †:
--     (R ∖ T) †  ≡  (R † ／ T †)        (DEFINITIONALLY; `residual-duality`).
-- "Divide on the left" and "divide on the right" are not two choices but
-- the same residual seen through †.  Root and log are the two residuals of
-- the exponentiation arrow `pow` (given power+exponent ⇒ base = root; given
-- power+base ⇒ exponent = log); this duality says they are †-conjugate, a
-- single structure, not an either/or.  `pow` itself is greenfield — the
-- concrete root/log instance lands once pow is presented in `Rel`; the
-- STRUCTURE that unifies them (the residual pair + the † duality) is here.
--
-- All up to `--safe --without-K`: the residuals are universally-quantified
-- fibers, the adjunctions are currying/uncurrying, the duality is `refl`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division where

open import Substrate.Foundation.Level using (Level; _⊔_; 0ℓ) renaming (suc to lsuc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Category.Allegory
  using (_⨾_; _†; _⊆_; ⊆-refl; _≈_; Allegory; Rel-Allegory)

------------------------------------------------------------------------
-- the two residuals of composition.
------------------------------------------------------------------------

infixr 5 _∖_
_∖_ : {A B C : Set} → (A → B → Set) → (A → C → Set) → B → C → Set
_∖_ {A} R T b c = (a : A) → R a b → T a c

infixr 5 _／_
_／_ : {A B C : Set} → (B → C → Set) → (A → C → Set) → A → B → Set
_／_ {A} {B} {C} S T a b = (c : C) → S b c → T a c

------------------------------------------------------------------------
-- the two adjunctions (R⨾S ⊆ T ⇔ S ⊆ R∖T ⇔ R ⊆ S／T).
------------------------------------------------------------------------

∖-adjˡ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
       → (R ⨾ S) ⊆ T → S ⊆ (R ∖ T)
∖-adjˡ h b c s a r = h a c (b , (r , s))

∖-adjˡ⁻ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
        → S ⊆ (R ∖ T) → (R ⨾ S) ⊆ T
∖-adjˡ⁻ k a c (b , (r , s)) = k b c s a r

／-adjʳ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
        → (R ⨾ S) ⊆ T → R ⊆ (S ／ T)
／-adjʳ h a b r c s = h a c (b , (r , s))

／-adjʳ⁻ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} {T : A → C → Set}
         → R ⊆ (S ／ T) → (R ⨾ S) ⊆ T
／-adjʳ⁻ k a c (b , (r , s)) = k a b r c s

------------------------------------------------------------------------
-- THE GEM — left division = right division of the converses.
------------------------------------------------------------------------

residual-duality : {A B C : Set} (R : A → B → Set) (T : A → C → Set)
                 → ((R ∖ T) †) ≈ ((R †) ／ (T †))
residual-duality R T = ⊆-refl , ⊆-refl

------------------------------------------------------------------------
-- the generic Division Allegory, inhabited by Rel.
------------------------------------------------------------------------

-- ⟡set1-rp-divisionallegory: Al's carriers thread through as implicit
-- binders (Obj/Hom/_⊑_ are now Allegory's params, not its fields) —
-- carriers as params never raise the sort (set1-carrier-always-parameterize).
record DivisionAllegory
  {ℓo ℓh ℓc : Level}
  {Obj : Set ℓo} {Hom : Obj → Obj → Set ℓh}
  {_⊑_ : {A B : Obj} → Hom A B → Hom A B → Set ℓc}
  (Al : Allegory Obj Hom _⊑_)
       : Set (ℓo ⊔ ℓh ⊔ ℓc) where
  open Allegory Al
  field
    _∖∖_   : {X Y Z : Obj} → Hom X Y → Hom X Z → Hom Y Z
    _//_   : {X Y Z : Obj} → Hom Y Z → Hom X Z → Hom X Y
    ∖-adj  : {X Y Z : Obj} {R : Hom X Y} {S : Hom Y Z} {T : Hom X Z}
           → (R ⨟ S) ⊑ T → S ⊑ (R ∖∖ T)
    ∖-adj⁻ : {X Y Z : Obj} {R : Hom X Y} {S : Hom Y Z} {T : Hom X Z}
           → S ⊑ (R ∖∖ T) → (R ⨟ S) ⊑ T
    /-adj  : {X Y Z : Obj} {R : Hom X Y} {S : Hom Y Z} {T : Hom X Z}
           → (R ⨟ S) ⊑ T → R ⊑ (S // T)
    /-adj⁻ : {X Y Z : Obj} {R : Hom X Y} {S : Hom Y Z} {T : Hom X Z}
           → R ⊑ (S // T) → (R ⨟ S) ⊑ T

Rel-DivisionAllegory : DivisionAllegory Rel-Allegory
Rel-DivisionAllegory = record
  { _∖∖_   = _∖_
  ; _//_   = _／_
  ; ∖-adj  = ∖-adjˡ
  ; ∖-adj⁻ = ∖-adjˡ⁻
  ; /-adj  = ／-adjʳ
  ; /-adj⁻ = ／-adjʳ⁻
  }
