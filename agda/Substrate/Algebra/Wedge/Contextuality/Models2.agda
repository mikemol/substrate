------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Contextuality.Models2
--
-- More models, including a NON-contextual one — so the detector is shown to
-- DISCRIMINATE, not merely always fire:
--
--   * the PENTAGON (5-cycle, odd parity) — contextual: obstruction (𝟙×5),
--     no global section, yet every context individually satisfiable.
--   * a CONSISTENT triangle (even parity) — NON-contextual: it HAS a global
--     section (all-zero), and is locally satisfiable too. No obstruction.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Contextuality.Models2 where

open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.Wedge.Contextuality using (Constraint; con; satisfies)
open import Substrate.Algebra.Wedge.Contextuality.General
  using (GlobalSection; Obstruction; obstruction-refutes)
open import Substrate.Algebra.Wedge.Contextuality.Models using (LocallySat; Contextual)

------------------------------------------------------------------------
-- 21–25. The pentagon (5-cycle, odd parity) — contextual.
------------------------------------------------------------------------

pent-c₁ pent-c₂ pent-c₃ pent-c₄ pent-c₅ : Constraint 5
pent-c₁ = con (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) 𝟘
pent-c₂ = con (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) 𝟘
pent-c₃ = con (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) 𝟘
pent-c₄ = con (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) 𝟘
pent-c₅ = con (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) 𝟙

pent-scenario : Vec (Constraint 5) 5
pent-scenario = pent-c₁ ∷ pent-c₂ ∷ pent-c₃ ∷ pent-c₄ ∷ pent-c₅ ∷ []

pent-obstruction : Obstruction pent-scenario
pent-obstruction = (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) , refl

pent-no-global : ¬ GlobalSection pent-scenario
pent-no-global = obstruction-refutes pent-scenario pent-obstruction

pent-locally-sat : LocallySat pent-scenario
pent-locally-sat zero                         = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
pent-locally-sat (suc zero)                   = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
pent-locally-sat (suc (suc zero))             = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
pent-locally-sat (suc (suc (suc zero)))       = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
pent-locally-sat (suc (suc (suc (suc zero)))) = (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl

pent-contextual : Contextual pent-scenario
pent-contextual = pent-locally-sat , pent-no-global

------------------------------------------------------------------------
-- 26–28. A consistent triangle (even parity) — NON-contextual: it has a
--         global section, so no obstruction exists.
------------------------------------------------------------------------

ok-c₁ ok-c₂ ok-c₃ : Constraint 3
ok-c₁ = con (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) 𝟘
ok-c₂ = con (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) 𝟘
ok-c₃ = con (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) 𝟘

ok-scenario : Vec (Constraint 3) 3
ok-scenario = ok-c₁ ∷ ok-c₂ ∷ ok-c₃ ∷ []

-- all-zero is a global section: every context has even (𝟘) parity.
ok-global : GlobalSection ok-scenario
ok-global = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl , refl , refl , tt

ok-locally-sat : LocallySat ok-scenario
ok-locally-sat zero             = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
ok-locally-sat (suc zero)       = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
ok-locally-sat (suc (suc zero)) = (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , refl
