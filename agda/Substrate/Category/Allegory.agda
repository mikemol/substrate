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

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)

------------------------------------------------------------------------
-- Step 0 — relations as fiber families, with the inclusion order.
------------------------------------------------------------------------

infix 4 _⊆_
_⊆_ : {A B : Set} → (A → B → Set) → (A → B → Set) → Set
_⊆_ {A} {B} R S = (a : A) (b : B) → R a b → S a b

⊆-refl : {A B : Set} {R : A → B → Set} → R ⊆ R
⊆-refl _ _ r = r

⊆-trans : {A B : Set} {R S T : A → B → Set} → R ⊆ S → S ⊆ T → R ⊆ T
⊆-trans p q a b r = q a b (p a b r)

-- hom-equivalence = mutual inclusion (the ≈ the laws hold up to).
_≈_ : {A B : Set} → (A → B → Set) → (A → B → Set) → Set
R ≈ S = (R ⊆ S) × (S ⊆ R)

------------------------------------------------------------------------
-- Step 1 — identity + composition (relational comp = Σ over the middle = Poly ◁).
------------------------------------------------------------------------

idR : (A : Set) → A → A → Set
idR A a a' = a ≡ a'

infixr 9 _⨾_
_⨾_ : {A B C : Set} → (A → B → Set) → (B → C → Set) → A → C → Set
_⨾_ {A} {B} {C} R S a c = Σ B (λ b → (R a b) × (S b c))

⨾-identityˡ : {A B : Set} (R : A → B → Set) → (idR A ⨾ R) ≈ R
⨾-identityˡ R = (λ { a b (_ , (refl , r)) → r })
              , (λ a b r → a , (refl , r))

⨾-assoc : {A B C D : Set} (R : A → B → Set) (S : B → C → Set) (T : C → D → Set)
        → ((R ⨾ S) ⨾ T) ≈ (R ⨾ (S ⨾ T))
⨾-assoc R S T = (λ { a d (c , ((b , (r , s)) , t)) → b , (r , (c , (s , t))) })
              , (λ { a d (b , (r , (c , (s , t)))) → c , ((b , (r , s)) , t) })

------------------------------------------------------------------------
-- Step 2 — converse (flip the fiber); the three dagger laws up to ≈.
------------------------------------------------------------------------

infix 8 _†
_† : {A B : Set} → (A → B → Set) → B → A → Set
(R †) b a = R a b

†-comp : {A B C : Set} (R : A → B → Set) (S : B → C → Set)
       → ((R ⨾ S) †) ≈ ((S †) ⨾ (R †))
†-comp R S = (λ { c a (b , (r , s)) → b , (s , r) })
           , (λ { c a (b , (s , r)) → b , (r , s) })

†-invol : {A B : Set} (R : A → B → Set) → ((R †) †) ≈ R
†-invol R = ⊆-refl , ⊆-refl   -- (R †) † a b ≡ R a b definitionally

------------------------------------------------------------------------
-- Step 3 — meets (pointwise product of fibers); the GLB universal property.
------------------------------------------------------------------------

infixr 7 _∧_
_∧_ : {A B : Set} → (A → B → Set) → (A → B → Set) → A → B → Set
(R ∧ S) a b = (R a b) × (S a b)

∧-⊆ˡ : {A B : Set} (R S : A → B → Set) → (R ∧ S) ⊆ R
∧-⊆ˡ R S a b (r , s) = r

∧-⊆ʳ : {A B : Set} (R S : A → B → Set) → (R ∧ S) ⊆ S
∧-⊆ʳ R S a b (r , s) = s

∧-greatest : {A B : Set} {R S T : A → B → Set} → T ⊆ R → T ⊆ S → T ⊆ (R ∧ S)
∧-greatest p q a b t = (p a b t , q a b t)

------------------------------------------------------------------------
-- Step 4 — the modular law (the gate that earns "allegory").
--   (R⨾S) ∧ T  ⊆  (R ∧ (T ⨾ S†)) ⨾ S
-- Constructive Σ/×-rearrangement: Rel is the tabular allegory.
------------------------------------------------------------------------

modular : {A B C : Set} (R : A → B → Set) (S : B → C → Set) (T : A → C → Set)
        → ((R ⨾ S) ∧ T) ⊆ ((R ∧ (T ⨾ (S †))) ⨾ S)
modular R S T a c ((b , (r , s)) , t) = b , ((r , (c , (t , s))) , s)

------------------------------------------------------------------------
-- ⟡rc-closeout (⟡rc-rel-allegory): the terminal Set₁ deliverables
-- `Rel-TwoCategory`, the generic `Allegory` record + `Rel-Allegory`
-- (and `Allegory/Division.agda`'s `Rel-DivisionAllegory`) were DEAD
-- surface — no value consumers (the Stencil/Maps/Mono modules use the
-- Set-valued ops above directly). Deleted as dead Set₁ surface. The
-- faithful re-valuation — relations valued in an extended
-- `Foundation.Universe` (`⌜≡⌝`/`⌜Σ⌝`/`⌜Π⌝` codes; `Rel a b = El a →
-- El b → U`), landing the allegory at Set₀ (⟡pyrig-object-carrier's
-- next rung) — is the documented re-engineering residue, rebuilt when
-- wanted.
------------------------------------------------------------------------
