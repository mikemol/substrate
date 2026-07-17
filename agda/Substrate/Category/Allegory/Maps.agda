------------------------------------------------------------------------
-- Substrate.Category.Allegory.Maps  (ALG-5)
--
-- MAPS in the allegory of relations: a map is a relation that is ENTIRE
-- (every a relates to something) and DETERMINISTIC (every fiber is a
-- subsingleton).  This is the allegory's derived predicate that cuts
-- "function" out of "relation" — same fiber family `R : A → B → Set`,
-- with the fibers constrained to singletons.
--
--   * `idR` is a map; maps are closed under `_⨾_` (the sub-category).
--   * `graph f = (f a ≡ b)` is a map — FUNCTIONS ARE MAPS, the canonical
--     inhabitant (map ≃ function); `idR = graph id` is the degenerate case.
--   * `map-value-unique` : a map's witnessed value is unique — the
--     singleton-fiber READOUT.
--
-- Φ-FLOOR connection (the recursion's bottom): `deterministic R` says the
-- fiber over each `a` is a singleton — i.e. the fiber-refinement operator
-- Φ has landed on `μΦ[a]` = a singleton.  "Map vs relation" is exactly
-- this singleton-vs-not readout, not a chosen structure.  The wedge's own
-- arrows (quotient, recon) become map-instances here at ALG-7, once the
-- wedge is presented in `Rel`; `recon-bounded-unique` is then precisely
-- the proof that those fibers are singletons (Φ converges).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Maps where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; subst)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Category.Allegory using (idR; _⨾_)

------------------------------------------------------------------------
-- map = entire + deterministic relation = every fiber a singleton.
------------------------------------------------------------------------

entire : {A B : Set} → (A → B → Set) → Set
entire {A} {B} R = (a : A) → Σ B (λ b → R a b)

deterministic : {A B : Set} → (A → B → Set) → Set
deterministic {A} {B} R = (a : A) (b b' : B) → R a b → R a b' → b ≡ b'

isMap : {A B : Set} → (A → B → Set) → Set
isMap R = entire R × deterministic R

------------------------------------------------------------------------
-- identity is a map; maps closed under composition (the sub-category).
------------------------------------------------------------------------

idR-entire : (A : Set) → entire (idR A)
idR-entire A a = a , refl

idR-det : (A : Set) → deterministic (idR A)
idR-det A a b b' eq eq' = trans (sym eq) eq'

idR-map : (A : Set) → isMap (idR A)
idR-map A = idR-entire A , idR-det A

⨾-entire : {A B C : Set} {R : A → B → Set} {S : B → C → Set}
         → entire R → entire S → entire (R ⨾ S)
⨾-entire {R = R} {S} eR eS a with eR a
... | b , r with eS b
... | c , s = c , (b , (r , s))

⨾-det : {A B C : Set} {R : A → B → Set} {S : B → C → Set}
      → deterministic R → deterministic S → deterministic (R ⨾ S)
⨾-det {R = R} {S} dR dS a c c' (b , (r , s)) (b' , (r' , s')) =
  dS b c c' s (subst (λ z → S z c') (sym (dR a b b' r r')) s')

⨾-map : {A B C : Set} {R : A → B → Set} {S : B → C → Set}
      → isMap R → isMap S → isMap (R ⨾ S)
⨾-map (eR , dR) (eS , dS) = ⨾-entire eR eS , ⨾-det dR dS

------------------------------------------------------------------------
-- functions are maps: graph f = (f a ≡ b). The canonical inhabitant
-- (map ≃ function); subsumes idR = graph id.
------------------------------------------------------------------------

graph : {A B : Set} → (A → B) → A → B → Set
graph f a b = f a ≡ b

graph-entire : {A B : Set} (f : A → B) → entire (graph f)
graph-entire f a = f a , refl

graph-det : {A B : Set} (f : A → B) → deterministic (graph f)
graph-det f a b b' eq eq' = trans (sym eq) eq'

graph-map : {A B : Set} (f : A → B) → isMap (graph f)
graph-map f = graph-entire f , graph-det f

------------------------------------------------------------------------
-- the singleton-fiber readout (Φ-floor): a map's witnessed value is
-- unique — deterministic = μΦ landed on a singleton.
------------------------------------------------------------------------

map-value-unique : {A B : Set} {R : A → B → Set} → isMap R
                 → (a : A) (p q : Σ B (λ b → R a b)) → proj₁ p ≡ proj₁ q
map-value-unique (_ , d) a (b , r) (b' , r') = d a b b' r r'

------------------------------------------------------------------------
-- maps as a bundled sub-category.
------------------------------------------------------------------------

-- ⟡rc-cheap (⟡set1-rerank2): the ex-Σ-holder `Map A B = Σ (Rel A B) isMap : Set₁` held the
-- relation as DATA; with the relation as a PARAMETER the bundle drops to Set (the family-as-
-- param move — the "genuine Σ-holder" label was the wall-reflex).
record Map (A B : Set) (R : A → B → Set) : Set where
  constructor mkMap
  field
    is-map : isMap R

idMap : (A : Set) → Map A A (idR A)
idMap A = mkMap (idR-map A)

infixr 9 _⨾M_
_⨾M_ : {A B C : Set} {R : A → B → Set} {S : B → C → Set} → Map A B R → Map B C S → Map A C (R ⨾ S)
mkMap mR ⨾M mkMap mS = mkMap (⨾-map mR mS)
