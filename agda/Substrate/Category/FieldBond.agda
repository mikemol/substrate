------------------------------------------------------------------------
-- Substrate.Category.FieldBond
--
-- A bond between two fields, with explicit orientation.
--
-- Per [[project-3plus1-is-cone-instance]] bond extension: when the
-- M:N cone's total M+N doesn't equal a single prime power, the
-- structure decomposes via the prime-power factorization of M+N
-- into multiple host fields, with BONDS connecting them.
--
-- A FieldBond is the categorical handle for one such inter-field
-- connection. It has:
--   * A from-field and a to-field.
--   * A bond morphism from-field → to-field (representing the
--     structural connection).
--   * Orientation IS the direction (from→to is not symmetric).
--
-- Substrate examples (deferred to slice 9):
--   * F₂ → F₃ in Z/6 = Z/2 × Z/3 (CRT bond).
--   * F₂³ → F₃, F₃ → F₇ in 168-gauge of |PSL(2, 7)| = 2³ · 3 · 7
--     (multi-field tower per project-reserved-selfdual-bijection-gauge).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FieldBond where

open import Level using (Level; _⊔_)

private
  variable
    ℓ ℓ′ : Level

------------------------------------------------------------------------
-- The FieldBond record.
--
-- At the Set level, a bond is just an oriented morphism between two
-- Sets. The "field" naming reflects intended use: from and to are
-- carriers of finite fields F_p, F_q.
--
-- The structural content (orientation as forced by which field has
-- the (M+N-1) interpretation hosted) lives at the use site; this
-- primitive records only the bond direction.
------------------------------------------------------------------------

record FieldBond (From : Set ℓ) (To : Set ℓ′) : Set (ℓ ⊔ ℓ′) where
  field
    bond : From → To

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: FieldBond is the substrate's primitive for
-- inter-field structural connections. The orientation (which field
-- is From, which is To) is forced by which side hosts (M+N-1)
-- interpretations in the cone's filling.
--
-- A "reversible" bond (one with an inverse morphism in both
-- directions) would be a separate enhancement, capturing the
-- bijective inter-field iso case (e.g., CRT iso Z/(pq) ≅ Z/p × Z/q
-- is reversible).
--
-- Substrate use: slice 9 instantiates with Z/6 = F₂ × F₃, providing
-- both the bond morphism and the inverse.
--
-- Per [[project-composite-torsion-euler-substrate]]: composite
-- torsion via Euler-Fermat connects to the bond structure when the
-- composite order factors across coprime primes.
------------------------------------------------------------------------
