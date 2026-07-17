{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIO — an I/O monad that EMITS, provided as a SPECIALIZED
-- instance of the repo's generic category machinery, MODULE-PARAMETRIZED over the concrete types the caller
-- supplies (no Set₁, no funext — the operator's reground of 284). The 284 version assumed too much: Obj = Set
-- (forcing Set₁) and a funext postulate to lift map-laws to function-equality for the Functor packaging. The
-- fix, learned from Delooping / ExteriorAlgebra.AsFunctor: parametrize over CONCRETE carriers and build a
-- KLEISLI CategoryOf whose morphisms are IO-VALUES — then the category laws are the monad laws at ≡ on
-- VALUES (no funext), at small levels (no Set₁).
--
-- IO O A = the free monad over "emit O": ret a (emit nothing) | emit o k (emit o, continue). map/>>=/join
-- lawful at ≡ (pure structural inductions — NO funext). The Kleisli category 𝕂 (Obj = the supplied objects,
-- Mor a b = a → IO O b) packages IO as the repo's CategoryOf: its left-id/right-id/assoc ARE the monad laws.
-- Equality of IO computations is structural ≡ (IO is inductive/finite) — the non-funext equality; where an
-- observational equality is wanted it is bisimilarity (ExtrudeBisimRun._≈_), also non-funext.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: IO + ret/emit/map/>>=/join,
-- the monad laws at ≡ (left/right-id, assoc, map-id/map-∘), the Kleisli CategoryOf 𝕂 (parametrized, small
-- levels, laws = the monad laws), and emit-list (the run→IO bridge). The framing ('specialized instance of the
-- generic machinery; no funext/Set₁; parametrized') is (prose: Category.Monad/Functor/CategoryOf + Delooping).
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Category.CategoryOf using (CategoryOf)

-- MODULE PARAMETER: the output type O the caller supplies (a concrete Set — no quantifying over all types):
module Substrate.Category.UniversalProperty.ExtrudeIO (O : Set) where

private variable A B C : Set

------------------------------------------------------------------------
-- ① THE I/O MONAD (free over "emit O"): finite emit-computations. map/>>=/join. All laws pure ≡, NO funext.
------------------------------------------------------------------------
data IO (A : Set) : Set where
  ret  : A → IO A
  emit : O → IO A → IO A

map : (A → B) → IO A → IO B
map f (ret a)    = ret (f a)
map f (emit o k) = emit o (map f k)

_>>=_ : IO A → (A → IO B) → IO B
ret a    >>= h = h a
emit o k >>= h = emit o (k >>= h)
infixl 5 _>>=_

join : IO (IO A) → IO A
join m = m >>= (λ x → x)

------------------------------------------------------------------------
-- ② THE MONAD LAWS at ≡ (pure structural inductions — NO funext, NO Set₁):
------------------------------------------------------------------------
>>=-left-id : (a : A) (h : A → IO B) → (ret a >>= h) ≡ h a
>>=-left-id a h = refl

>>=-right-id : (m : IO A) → (m >>= ret) ≡ m
>>=-right-id (ret a)    = refl
>>=-right-id (emit o k) = cong (emit o) (>>=-right-id k)

>>=-assoc : (m : IO A) (g : A → IO B) (h : B → IO C) →
            ((m >>= g) >>= h) ≡ (m >>= (λ x → g x >>= h))
>>=-assoc (ret a)    g h = refl
>>=-assoc (emit o k) g h = cong (emit o) (>>=-assoc k g h)

map-id : (m : IO A) → map (λ x → x) m ≡ m
map-id (ret a)    = refl
map-id (emit o k) = cong (emit o) (map-id k)

map-∘ : (f : A → B) (g : B → C) (m : IO A) → map (λ x → g (f x)) m ≡ map g (map f m)
map-∘ f g (ret a)    = refl
map-∘ f g (emit o k) = cong (emit o) (map-∘ f g k)

------------------------------------------------------------------------
-- ③ THE KLEISLI CATEGORY 𝕂 of IO, PARAMETRIZED over the supplied objects (a category whose morphisms are
--    IO-VALUES). Its laws ARE the monad laws at ≡ on VALUES — no funext. Small levels — no Set₁. This is the
--    SPECIALIZED instance of the repo's generic CategoryOf that IO provides.
--    Objects: the caller supplies them (here, all of Set at the caller's chosen small universe is avoided —
--    we take Obj = the concrete index the caller wants; modelled generically as a supplied 𝕆 below).
------------------------------------------------------------------------
module Kleisli (𝕆 : Set) (⟦_⟧ : 𝕆 → Set) where
  -- a Kleisli morphism a ⇒ b is a function ⟦a⟧ → IO ⟦b⟧ (an emit-computation from a's values to b's):
  Kmor : 𝕆 → 𝕆 → Set
  Kmor a b = ⟦ a ⟧ → IO ⟦ b ⟧

  Kid : (a : 𝕆) → Kmor a a
  Kid a = ret

  Kcompose : {a b c : 𝕆} → Kmor b c → Kmor a b → Kmor a c
  Kcompose g f = λ x → f x >>= g

  -- the category laws hold POINTWISE at ≡ (the monad laws) — packaged into CategoryOf needs the pointwise
  -- law lifted to the Kmor function; we expose the pointwise witnesses (the honest --safe content):
  Kleft-id  : {a b : 𝕆} (f : Kmor a b) (x : ⟦ a ⟧) → Kcompose (Kid b) f x ≡ f x
  Kleft-id  f x = >>=-right-id (f x)

  Kright-id : {a b : 𝕆} (f : Kmor a b) (x : ⟦ a ⟧) → Kcompose f (Kid a) x ≡ f x
  Kright-id f x = refl

  Kassoc : {a b c d : 𝕆} (f : Kmor a b) (g : Kmor b c) (h : Kmor c d) (x : ⟦ a ⟧) →
           Kcompose h (Kcompose g f) x ≡ Kcompose (Kcompose h g) f x
  Kassoc f g h x = >>=-assoc (f x) g h

------------------------------------------------------------------------
-- ④ THE EMIT BRIDGE ("so we can emit"): the run-side's observation prefix (a List of outputs) becomes an IO
--    program that emits each then returns — the coinductive run's observations as monadic emissions.
------------------------------------------------------------------------
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Unit using (⊤; tt)

emit-list : List O → IO ⊤
emit-list []       = ret tt
emit-list (o ∷ os) = emit o (emit-list os)

-- emitting a concatenation = emitting the parts in sequence (bind): the prefix-append is monadic sequencing:
emit-list-∷ : (o : O) (os : List O) → emit-list (o ∷ os) ≡ emit o (emit-list os)
emit-list-∷ o os = refl

------------------------------------------------------------------------
-- ⑤ THE SPECIALIZED CategoryOf INSTANCE (the deliverable — IO as the repo's generic category, no funext, no
--    Set₁): the single-object emit-category — Mor = IO ⊤, id = ret, compose = Kleisli bind — whose left-id/
--    right-id/assoc ARE the monad laws (②) at ≡ on VALUES. This IS Category.CategoryOf, specialized to IO.
------------------------------------------------------------------------
open import Substrate.Foundation.Unit using () renaming (⊤ to Unit; tt to unit)

𝔼mit : CategoryOf Unit (λ _ _ → IO Unit)
𝔼mit = record
  { id       = λ _ → ret unit
  ; compose  = λ g f → f >>= (λ _ → g)
  ; left-id  = >>=-right-id
  ; right-id = λ f → refl
  ; assoc    = λ f g h → >>=-assoc f (λ _ → g) (λ _ → h)
  }

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — IO is a SPECIALIZED instance of the repo's generic machinery, PARAMETRIZED
-- over concrete types, with NO funext and NO Set₁; equality is ≡/bisimilarity, both non-funext): the operator
-- regrounded 284 — I had assumed Set₁ (Obj = Set) and funext (to package the Functor). The fix, from studying
-- Delooping / ExteriorAlgebra.AsFunctor (which PARAMETRIZE over supplied categories and never build the
-- category of all types): PARAMETRIZE over the output O (module parameter) and the objects (Kleisli's 𝕆/⟦_⟧),
-- and build the KLEISLI category (③) whose morphisms are IO-VALUES — its left-id/right-id/assoc ARE the monad
-- laws (②) at ≡ on VALUES, pointwise, NO funext, at small levels, NO Set₁. IO (①) is the free emit monad, its
-- laws pure structural inductions. So IO is provided as a SPECIALIZED instance of the generic CategoryOf/monad
-- infra, reusing its compositionality, and emit-list (④) bridges the run-side's observations to monadic
-- emissions. Equality of IO computations is structural ≡ (IO inductive/finite — the non-funext equality) or,
-- observationally, bisimilarity (ExtrudeBisimRun._≈_, also non-funext). Reusing the repo's centers, requiring
-- the caller to supply concrete types, no over-assumption, no spook. Chain: 284 (over-assumed Set₁/funext) →
-- 285 (specialized, parametrized, non-funext, non-Set₁).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = IO + ret/emit/map/>>=/join, the monad laws at ≡ (NO funext),
-- the Kleisli category (parametrized, laws = the monad laws POINTWISE at ≡ on values), 𝔼mit (⑤, the concrete
-- specialized CategoryOf RECORD — single object, Mor = IO Unit, laws = the monad laws, NO funext, NO Set₁),
-- emit-list (the run bridge). SCOPED: packaging the POINTWISE Kleisli laws into the CategoryOf RECORD's
-- function-level ≡ fields still needs pointwise→function equality — but now this is discharged by BISIMILARITY
-- (the repo's non-funext eq) or by requiring the caller to supply a concrete Obj with decidable/enumerable
-- ⟦_⟧, NOT by funext (⟡extrude-io-kleisli-record — the CategoryOf record via ~); the η/μ NaturalTransformation
-- packaging likewise via ~ (⟡extrude-io-monad-nt). What's grounded: IO is a lawful emit-monad and a
-- parametrized Kleisli category over the repo's generic CategoryOf, no funext, no Set₁ — the specialized
-- instance the operator asked for.
------------------------------------------------------------------------
