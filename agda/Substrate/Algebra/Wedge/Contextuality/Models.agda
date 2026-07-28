------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Contextuality.Models
--
-- Concrete contextual models as instances of the general detector
-- (Substrate.Algebra.Wedge.Contextuality.General):
--
--   * the parity TRIANGLE (3 contexts) re-derived through the general
--     machinery — its obstruction is the selection (𝟙,𝟙,𝟙), refl;
--   * the parity SQUARE / 4-cycle (4 contexts) — a larger AvN/GHZ-family
--     witness, obstruction (𝟙,𝟙,𝟙,𝟙), refl;
--   * `Contextual` = locally satisfiable AND no global section — the honest
--     definition of contextuality; the triangle is shown contextual.
--
-- Each obstruction is proved by `refl` (the combination of concrete contexts
-- reduces to the "0 = 1" context), so contextuality is fully computed.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Contextuality.Models where

open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.Wedge.Contextuality
  using (Constraint; con; satisfies; tri-c₁; tri-c₂; tri-c₃)
open import Substrate.Algebra.Wedge.Contextuality.General
  using (GlobalSection; Obstruction; obstruction-refutes)

------------------------------------------------------------------------
-- Slice 4. The triangle as a general scenario.
------------------------------------------------------------------------

tri-scenario : Vec (Constraint 3) 3
tri-scenario = tri-c₁ ∷ tri-c₂ ∷ tri-c₃ ∷ []

tri-obstruction′ : Obstruction tri-scenario
tri-obstruction′ = (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) , refl

tri-no-global : ¬ GlobalSection tri-scenario
tri-no-global = obstruction-refutes tri-scenario tri-obstruction′

------------------------------------------------------------------------
-- Slice 5. The parity square (4-cycle): x₁+x₂=0, x₂+x₃=0, x₃+x₄=0, x₄+x₁=1.
------------------------------------------------------------------------

sq-c₁ sq-c₂ sq-c₃ sq-c₄ : Constraint 4
sq-c₁ = con (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) 𝟘
sq-c₂ = con (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) 𝟘
sq-c₃ = con (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) 𝟘
sq-c₄ = con (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) 𝟙

sq-scenario : Vec (Constraint 4) 4
sq-scenario = sq-c₁ ∷ sq-c₂ ∷ sq-c₃ ∷ sq-c₄ ∷ []

sq-obstruction : Obstruction sq-scenario
sq-obstruction = (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) , refl

sq-no-global : ¬ GlobalSection sq-scenario
sq-no-global = obstruction-refutes sq-scenario sq-obstruction

------------------------------------------------------------------------
-- Slice 6. Local consistency and the honest definition of contextuality.
------------------------------------------------------------------------

LocallySat : ∀ {n m} → Vec (Constraint n) m → Set
LocallySat {n} {m} sc = (i : Fin m) → Σ (Vector n) (λ s → satisfies s (lookup sc i))

-- A model is CONTEXTUAL iff every context is individually satisfiable yet no
-- global section exists.
Contextual : ∀ {n m} → Vec (Constraint n) m → Set
Contextual sc = LocallySat sc × ¬ GlobalSection sc

tri-locally-sat : LocallySat tri-scenario
tri-locally-sat zero             = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
tri-locally-sat (suc zero)       = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
tri-locally-sat (suc (suc zero)) = (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl

tri-contextual′ : Contextual tri-scenario
tri-contextual′ = tri-locally-sat , tri-no-global
