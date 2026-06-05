------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Contextuality.General
--
-- The contextuality detector for an ARBITRARY F₂ scenario (a finite cover of
-- parity contexts), generalising the worked triangle in
-- Substrate.Algebra.Wedge.Contextuality.
--
--   * `combine sc sel` folds the connecting map `_⊕ᶜ_` over a SELECTION of
--     contexts (sel : Vector m, an F₂ coefficient per context) — the F₂-linear
--     combination of the cover. This is the Čech 1-cochain.
--   * `combine-sat` : any global section satisfies any combination — the
--     connecting map is sound on the whole cover (the cocycle composes).
--   * an `Obstruction` is a selection whose combination is the unsatisfiable
--     `(𝟎ⱽ, 𝟙)` ("0 = 1") — the nonzero H¹ class as DATA (a kept witness).
--   * `obstruction-refutes` : the kept obstruction CONSTRUCTS a refutation of
--     any global section (a genuine P ⊢ ⊥, no LEM, no `subst` — the equalities
--     are composed as wedge-generated patches via trans/cong).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Contextuality.General where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; 𝟘≢𝟙)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)
open import Substrate.Algebra.Wedge.Contextuality
  using (Constraint; con; lhs; rhs; satisfies; _⊕ᶜ_; ⊕ᶜ-satisfies;
         ⟨_,_⟩; inner-zero)

------------------------------------------------------------------------
-- 1. Scenarios, all-satisfaction, global sections.
------------------------------------------------------------------------

-- A scenario is a finite cover: m parity contexts over n measurements.
-- (Vec rather than List so the selection is index-aligned.)

AllSat : ∀ {n m} → Vector n → Vec (Constraint n) m → Set
AllSat s []       = ⊤
AllSat s (c ∷ cs) = satisfies s c × AllSat s cs

GlobalSection : ∀ {n m} → Vec (Constraint n) m → Set
GlobalSection {n} sc = Σ (Vector n) (λ s → AllSat s sc)

------------------------------------------------------------------------
-- 2. The connecting map folded over a selection (the F₂-linear combination
--    of contexts), and its soundness on any global section.
------------------------------------------------------------------------

-- scale a context by an F₂ coefficient: 𝟘 drops it (to the neutral context
-- (𝟎ⱽ, 𝟘), satisfied by everything), 𝟙 keeps it.
scaleᶜ : ∀ {n} → F₂ → Constraint n → Constraint n
scaleᶜ 𝟘 c = con 𝟎ⱽ 𝟘
scaleᶜ 𝟙 c = c

scaleᶜ-sat : ∀ {n} {s : Vector n} (b : F₂) (c : Constraint n) →
             satisfies s c → satisfies s (scaleᶜ b c)
scaleᶜ-sat {s = s} 𝟘 c _ = inner-zero s
scaleᶜ-sat        𝟙 c e = e

-- the F₂-linear combination of the selected contexts.
combine : ∀ {n m} → Vec (Constraint n) m → Vector m → Constraint n
combine []       []        = con 𝟎ⱽ 𝟘
combine (c ∷ cs) (b ∷ sel) = scaleᶜ b c ⊕ᶜ combine cs sel

-- SOUNDNESS: a global section satisfies every combination (the cocycle composes).
combine-sat : ∀ {n m} {s : Vector n}
              (sc : Vec (Constraint n) m) (sel : Vector m) →
              AllSat s sc → satisfies s (combine sc sel)
combine-sat {s = s} []       []        _        = inner-zero s
combine-sat {s = s} (c ∷ cs) (b ∷ sel) (e , es) =
  ⊕ᶜ-satisfies {s = s} (scaleᶜ b c) (combine cs sel)
               (scaleᶜ-sat b c e) (combine-sat cs sel es)

------------------------------------------------------------------------
-- 3. The obstruction (kept as data) and the constructive carry theorem.
------------------------------------------------------------------------

-- a selection whose combination is the "0 = 1" context — the nonzero
-- cohomology class, computed and retained.
Obstruction : ∀ {n m} → Vec (Constraint n) m → Set
Obstruction {n} {m} sc = Σ (Vector m) (λ sel → combine sc sel ≡ con (𝟎ⱽ {n}) 𝟙)

-- THE CARRY: a kept obstruction constructs a refutation of any global section.
-- No subst — the obstruction equality is split by `cong lhs / cong rhs` and
-- composed with the soundness proof as wedge-generated patches.
obstruction-refutes : ∀ {n m} (sc : Vec (Constraint n) m) →
                      Obstruction sc → ¬ GlobalSection sc
obstruction-refutes sc (sel , eq) (s , allsat) =
  𝟘≢𝟙 (trans (sym (inner-zero s))
             (trans (trans (cong (λ v → ⟨ v , s ⟩) (sym (cong lhs eq)))
                           (combine-sat sc sel allsat))
                    (cong rhs eq)))
