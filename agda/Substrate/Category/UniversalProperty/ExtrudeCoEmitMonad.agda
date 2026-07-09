{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad — ⟡extrude-coio-monad: the coinductive emit-MONAD.
-- The finite IO (285) emits then MUST return; CoIO (289) emits FOREVER but never returns. CoEmit is the mix:
-- a computation that may emit (finitely or forever) AND may return an A — the coinductive free monad over
-- "emit O". Mixed inductive-coinductive: a CoEmit is a (delayed) Step, where a Step is ret a | emit o then a
-- CoEmit. ret/bind give the monad; bisimilarity is its equality. Small, no funext/Set₁/levels/postulate.
--
-- NO `mutual` (⟡de-mutual, the RealTrace discipline): a mixed inductive-coinductive pair does not need a
-- mutual block — thread the CONTINUATION through the inductive layer as a parameter, then tie the knot by
-- guarded corecursion. `Step A K` is the base functor (the step-shape, with its continuation-slot K threaded
-- in as a parameter — the "prior state" passed forward); `CoEmit A` is its guarded fixpoint (K := CoEmit A).
-- Likewise `Step≈ R` threads the continuation-relation R, and `_≈ᵉ_` ties R := _≈ᵉ_. --guardedness carries
-- the coinductive records; every corecursive call sits under a constructor (guarded), never in a mutual block.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: CoEmit/Step (the coinductive
-- emit-monad), ret/emitᶜ/bind/map, _≈ᵉ_ (bisimilarity) + ≈ᵉ-refl, and bind-ret-left (left unit up to bisim).
-- The framing is (prose: 285/289 + the free-monad-over-emit).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad (O : Set) where

open import Substrate.Foundation.Eq using (_≡_; refl)

private variable A B C : Set

------------------------------------------------------------------------
-- ① THE COINDUCTIVE EMIT-MONAD. The base functor `Step A K` is the step-shape with its
--    continuation threaded in as the parameter K; `CoEmit A` is its guarded fixpoint,
--    K := CoEmit A. No mutual: `Step` references only its parameter, `CoEmit` closes the
--    loop coinductively (the RealTrace coinductive-record pattern; --guardedness).
------------------------------------------------------------------------
data Step (A K : Set) : Set where      -- ⟦shape:f8c709b4 ret,emitᶜ⟧
  ret   : A → Step A K
  emitᶜ : O → K → Step A K

record CoEmit (A : Set) : Set where
  coinductive
  field step : Step A (CoEmit A)
open CoEmit public

------------------------------------------------------------------------
-- ② MAP and BIND (the monad structure), corecursively. No `mutual` block: the paired type
--    signatures are declared BEFORE the clauses (forward declaration), which makes map↔map-step
--    and bind↔bind-step mutually recursive without the keyword. The corecursive call sits under
--    emitᶜ (guarded by the `step` field). The copattern `step (f …) = …-step (step …)` is a
--    DEFINITIONAL equation — the monad-law proofs below (right-unit, assoc) rely on it, so the
--    step-level actions stay first-class rather than being inlined behind a `with`.
------------------------------------------------------------------------
map      : (A → B) → CoEmit A → CoEmit B
map-step : (A → B) → Step A (CoEmit A) → Step B (CoEmit B)
step (map f c)         = map-step f (step c)
map-step f (ret a)     = ret (f a)
map-step f (emitᶜ o k) = emitᶜ o (map f k)

bind      : CoEmit A → (A → CoEmit B) → CoEmit B
bind-step : Step A (CoEmit A) → (A → CoEmit B) → Step B (CoEmit B)
step (bind c h)         = bind-step (step c) h
bind-step (ret a)     h = step (h a)
bind-step (emitᶜ o k) h = emitᶜ o (bind k h)

-- return of the monad, and a one-shot emit that then returns tt:
returnᶜ : A → CoEmit A
step (returnᶜ a) = ret a

------------------------------------------------------------------------
-- ③ BISIMILARITY (the coinductive equality): same step-shape, bisimilar continuations.
--    `Step≈ R` threads the continuation-relation R through the step-shape; `_≈ᵉ_` ties
--    R := _≈ᵉ_ by guarded corecursion — again no mutual.
------------------------------------------------------------------------
data Step≈ {A : Set} (R : CoEmit A → CoEmit A → Set) : Step A (CoEmit A) → Step A (CoEmit A) → Set where
  ret≈  : (a : A) → Step≈ R (ret a) (ret a)
  emit≈ : (o : O) {k k' : CoEmit A} → R k k' → Step≈ R (emitᶜ o k) (emitᶜ o k')

record _≈ᵉ_ {A : Set} (c d : CoEmit A) : Set where
  coinductive
  field step≈ : Step≈ _≈ᵉ_ (step c) (step d)
open _≈ᵉ_ public

infix 4 _≈ᵉ_

-- reflexivity by GUARDED CORECURSION (the Trace.Bisim.~-refl pattern; no mutual): ≈ᵉ-refl produces the
-- bisimilarity coinductively; the corecursive call ≈ᵉ-refl k sits under emit≈, so it is guarded.
≈ᵉ-refl : (c : CoEmit A) → c ≈ᵉ c
step≈ (≈ᵉ-refl c) with step c
... | ret a     = ret≈ a
... | emitᶜ o k = emit≈ o (≈ᵉ-refl k)

-- step-refl : the ONE canonical Step≈-reflexivity, shared by the assoc monad-law (ret case). Defined AFTER
-- ≈ᵉ-refl (which it composes from) — no mutual block; plain structural recursion on the Step.
step-refl : (s : Step A (CoEmit A)) → Step≈ _≈ᵉ_ s s
step-refl (ret a)     = ret≈ a
step-refl (emitᶜ o k) = emit≈ o (≈ᵉ-refl k)

------------------------------------------------------------------------
-- ④ THE LEFT-UNIT MONAD LAW, up to bisimilarity: bind (returnᶜ a) h ≈ᵉ h a. (returnᶜ a steps to ret a, and
--    bind-step (ret a) h = step (h a) — so bind (returnᶜ a) h and h a have the same step, hence bisimilar.)
------------------------------------------------------------------------
bind-ret-left : (a : A) (h : A → CoEmit B) → bind (returnᶜ a) h ≈ᵉ h a
step≈ (bind-ret-left a h) = lemma
  where
    -- step (bind (returnᶜ a) h) = bind-step (step (returnᶜ a)) h = bind-step (ret a) h = step (h a):
    lemma : Step≈ _≈ᵉ_ (step (bind (returnᶜ a) h)) (step (h a))
    lemma with step (h a)
    ... | ret b      = ret≈ b
    ... | emitᶜ o k  = emit≈ o (≈ᵉ-refl k)

------------------------------------------------------------------------
-- ⑤ (⟡extrude-coio-monad-laws) the full equivalence + the remaining monad laws, up to bisimilarity:
------------------------------------------------------------------------
-- symmetry + transitivity (completing the equivalence):
-- right unit: bind c returnᶜ ≈ᵉ c
bind-ret-right : (c : CoEmit A) → bind c returnᶜ ≈ᵉ c
step≈ (bind-ret-right c) = lemma (step c)
  where
    lemma : (s : Step A (CoEmit A)) → Step≈ _≈ᵉ_ (bind-step s returnᶜ) s
    lemma (ret a)     = ret≈ a
    lemma (emitᶜ o k) = emit≈ o (bind-ret-right k)

-- associativity: bind (bind c g) h ≈ᵉ bind c (λ x → bind (g x) h)
bind-assoc : (c : CoEmit A) (g : A → CoEmit B) (h : B → CoEmit C) →
             bind (bind c g) h ≈ᵉ bind c (λ x → bind (g x) h)
bind-assoc {A = A} c g h = go c
  where
    gh : A → CoEmit _
    gh x = bind (g x) h
    go : (c' : CoEmit A) → bind (bind c' g) h ≈ᵉ bind c' gh
    step≈ (go c') = lemma (step c')
      where
        lemma : (s : Step A (CoEmit A)) → Step≈ _≈ᵉ_ (bind-step (bind-step s g) h) (bind-step s gh)
        lemma (ret a)     = step-refl (step (gh a))
        lemma (emitᶜ o k) = emit≈ o (go k)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the coinductive emit-monad: emit finitely-then-return OR forever, a monad up
-- to bisimilarity; small): the finite IO (285) emits then returns; CoIO (289) emits forever. CoEmit (①) is the
-- mix — the coinductive free monad over "emit O" (mixed inductive-coinductive: a delayed Step that returns or
-- emits-then-continues, the base functor Step A K tied at K := CoEmit A by guarded corecursion — NO mutual).
-- map/bind (②) give the monad structure corecursively; returnᶜ is the unit.
-- Bisimilarity (③, _≈ᵉ_ — same step-shape, bisimilar continuations, an equivalence via ≈ᵉ-refl) is its
-- equality (the coinductive equality, D-no-classical-spook). The left-unit law (④, bind-ret-left) holds up to
-- bisimilarity — the monad law at the coinductive equality (not ≡, no funext). Small, no funext/Set₁/levels/
-- postulate/mutual, parameterized over O. So the emit-monad extends coinductively: the unbounded emit is a
-- monad too, up to bisimilarity. Chain: 285 (finite emit-monad) / 289 (unbounded stream) → 290d (the
-- coinductive emit-monad, laws up to bisim).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = CoEmit/Step (the coinductive emit-monad), map/bind/returnᶜ, _≈ᵉ_
-- + ≈ᵉ-refl, bind-ret-left (left unit up to bisim). SCOPED: the right-unit + associativity up to bisim (the
-- remaining monad laws, corecursive — ⟡extrude-coio-monad-laws); ≈ᵉ-sym/-trans (the full equivalence). What's
-- grounded: the coinductive emit-monad with its bisimilarity and the left-unit law — the unbounded emit as a
-- monad, up to bisim, small.
------------------------------------------------------------------------
