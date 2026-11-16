------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division.Backslash
--
-- Defines: _∖_
-- The LEFT RESIDUAL of composition: (R ∖ T) is the greatest S with
-- R⨾S ⊆ T.  A universally-quantified fiber, so Set₀ under --without-K.
--
-- ⟡alg6-restore: recovered from efe21483^ (Substrate.Category.Allegory.
-- Division, ALG-6).  The generic `DivisionAllegory` record and its `Rel-`
-- instance were deleted as dead surface; these Set₀ operators went with
-- them as COLLATERAL and depend on nothing that was removed.  One lemma,
-- one elaboration unit; no barrel re-exports these siblings.
--
-- ⚑ THE RECORD WAS NEVER THE Set₁ SOURCE, and reading it as one gets the
-- paydown backwards.  `DivisionAllegory` and `Allegory` BOTH already
-- parameterized their carriers and were level-polymorphic
-- (⟡set1-rp-divisionallegory).  The Set₁ lived in the INSTANTIATION —
-- `Rel-Allegory : Allegory {lsuc 0ℓ} {lsuc 0ℓ} {0ℓ} Set (λ A B → A → B →
-- Set) _⊆_` — where `Obj := Set` AND `Hom := A → B → Set` are each at
-- `lsuc 0ℓ`.  set1-carrier-always-parameterize does not ERASE level debt;
-- it RELOCATES it to the instantiation site, which is where it becomes
-- visible.  Two independent sources: the object universe (dissolvable
-- today — `Obj := U`, precedent Category/Allegory/Power.agda:47) and the
-- proof-relevant hom-valuation (`Rel a b = El a → El b → U`), which needs
-- `⌜≡⌝`/`⌜Σ⌝` codes that Foundation/Universe.agda does not yet carry
-- (`⌜⊤⌝ ⌜bool⌝ ⌜×⌝ ⌜⇒⌝` are all it has).
--
-- ⚑ SO THE GENERIC RECORD IS WORK, NOT RESIDUE, AND NOT "pending a Set₁
-- rebuild" — there is no Set₁ layer coming back.  It is the Set₀
-- re-valuation (⟡rc-rel-allegory / ⟡rc-tarski-universe), blocked only on
-- those two codes, with the payload — these six operators — already here.
-- Do NOT rebuild the record before the codes exist: every obligation is
-- independent, so the vestigial-record move (Topos.agda:25-33) would
-- typecheck today, buy ZERO paydown (the record was never the source),
-- and re-create the dead surface that got it deleted.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division.Backslash where


infixr 5 _∖_
_∖_ : {A B C : Set} → (A → B → Set) → (A → C → Set) → B → C → Set
_∖_ {A} R T b c = (a : A) → R a b → T a c
