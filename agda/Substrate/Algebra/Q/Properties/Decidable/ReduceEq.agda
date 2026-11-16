------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable.ReduceEq
--
-- reduce-eq?: compare reduced shape keys (Register's `_≟ˢ_`, short-circuit
-- on shape mismatch) and numerators (`_≟ℤ_`).
--
-- This de-orphans Register: `_≟ˢ_` is a load-bearing decision step proven to
-- agree with `reduce-respects-≈` (≈ℚ ⟺ reduce a ≡ reduce b).  Two views — the
-- propositional uniqueness proof and the operational shape comparison — decide
-- the same relation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable.ReduceEq where

open import Substrate.Foundation.Nat.Properties.Cancel using (suc-injective)
open import Substrate.Foundation.Product using (proj₂)
open import Substrate.Foundation.Negation.Dec
open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Reduce using (reduce)
open import Substrate.Algebra.Q.Properties.Canonical.ReduceIsReduced
open import Substrate.Algebra.Wedge.Shape.Register using (_≟ˢ_)
open import Substrate.Algebra.Q.Properties.Decidable.Key
open import Substrate.Algebra.Q.Properties.Decidable.Faithful
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Nat.SucInjective

reduce-eq? : (a b : ℚ) → Dec (reduce a ≡ reduce b)
reduce-eq? a b with q-key (reduce a) ≟ˢ q-key (reduce b)
... | no  key≢ = no (λ re → key≢ (cong q-key re))
... | yes key≡ with num (reduce a) ≟ℤ num (reduce b)
...   | no  num≢ = no (λ re → num≢ (cong num re))
...   | yes num≡ =
          yes (cong₂ mkℚ num≡
                 (suc-injective
                   (proj₂ (key-faithful (reduce a) (reduce b)
                            (reduce-is-reduced a) (reduce-is-reduced b) key≡))))
