------------------------------------------------------------------------
-- Substrate.Category.ConjugationCoalgebra.CharacterOrthogonality
--
-- The character-table orthogonality predicates: row orthogonality
-- (rows = irreducible characters are orthonormal under the standard
-- inner product) and column orthogonality (columns = conjugacy
-- classes are dual-orthonormal under centralizer-size weighting).
--
-- U2 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
--
-- Parameterised over a value-type V + arithmetic operations + a
-- finite class-count n. No proofs in this slice — concrete instances
-- (U3 GL3F2, U4 Monster) specialize V to ℤ or ℚ and supply
-- per-instance orthogonality proofs.
--
-- Per [[continuous-via-discrete-inference-rules]]: orthogonality is
-- a DISCRETE constraint (finite sum over Fin n = number of conjugacy
-- classes); substrate-safe regardless of V's continuous structure.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- row + column orthogonality ARE the universal property of a
-- character table — they uniquely characterize it as the data of
-- an irreducible decomposition of the regular representation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ConjugationCoalgebra.CharacterOrthogonality where

open import Level using (Level; _⊔_)
open import Data.Fin using (Fin; zero; suc)
open import Data.Nat using (ℕ)

private
  variable
    ℓV : Level

------------------------------------------------------------------------
-- 1. Sum over Fin n (generic finite indexed sum).
--
-- Parameterised over a value-type V + addition + zero. Used for
-- character-table inner products.
------------------------------------------------------------------------

module _ {V : Set ℓV} (zero-V : V) (_+V_ : V → V → V) where

  sum-Fin : ∀ {n : ℕ} → (Fin n → V) → V
  sum-Fin {ℕ.zero}  f = zero-V
  sum-Fin {ℕ.suc n} f = f zero +V sum-Fin {n} (λ i → f (suc i))

------------------------------------------------------------------------
-- 2. Row inner product (= ⟨χᵢ, χⱼ⟩).
--
-- For an n×n character table Char : Fin n → Fin n → V, the inner
-- product of rows i and j is:
--   ⟨row-i, row-j⟩ = Σ_c χᵢ(c) · conj(χⱼ(c))
--
-- Parameterised over V's multiplication + conjugation. For ℤ-valued
-- characters, conjugation is identity (-V = id); for ℂ-valued
-- characters, it's complex conjugation.
------------------------------------------------------------------------

module _
  {V : Set ℓV}
  (zero-V : V)
  (_+V_ : V → V → V)
  (_*V_ : V → V → V)
  (conj-V : V → V)
  where

  row-inner :
    ∀ {n : ℕ} →
    (Char : Fin n → Fin n → V) →
    (i j : Fin n) →
    V
  row-inner Char i j =
    sum-Fin zero-V _+V_ (λ c → (Char i c) *V conj-V (Char j c))

  col-inner :
    ∀ {n : ℕ} →
    (Char : Fin n → Fin n → V) →
    (c c' : Fin n) →
    V
  col-inner Char c c' =
    sum-Fin zero-V _+V_ (λ i → (Char i c) *V conj-V (Char i c'))

------------------------------------------------------------------------
-- 3. The orthogonality predicates.
--
-- Row orthogonality: ⟨χᵢ, χⱼ⟩ = |G| · δᵢⱼ
--   (equivalently: (1/|G|) ⟨χᵢ, χⱼ⟩ = δᵢⱼ — normalised form)
--
-- Column orthogonality: Σ_i χᵢ(c) · conj(χᵢ(c')) = |Z_c| · δ_{cc'}
--   (where Z_c is the centralizer of the c-class representative)
--
-- Parameterised over V's equality predicate + the relevant "size"
-- values (group-order, centralizer-orders). User-supplied for
-- specific instances.
------------------------------------------------------------------------

module _
  {V : Set ℓV}
  (zero-V : V)
  (_+V_ : V → V → V)
  (_*V_ : V → V → V)
  (conj-V : V → V)
  (_≈V_ : V → V → Set ℓV)
  where

  -- Row orthogonality (specialized to "ranged value" — see comments).
  -- The "expected" form is:
  --   ⟨χᵢ, χⱼ⟩ ≈V (i ≡ j ? G : zero-V)
  -- Stated abstractly via an "expected" function the caller supplies
  -- (typically (λ i j → if i ≡ j then G else zero-V)). This sidesteps
  -- the need for decidable Fin equality in the substrate primitive.
  RowOrthogonal :
    ∀ {n : ℕ} →
    (Char : Fin n → Fin n → V) →
    (expected : Fin n → Fin n → V) →
    Set ℓV
  RowOrthogonal Char expected = ∀ i j →
    row-inner zero-V _+V_ _*V_ conj-V Char i j ≈V expected i j

  -- Column orthogonality: similar pattern with centralizer-weighted
  -- diagonal.
  ColOrthogonal :
    ∀ {n : ℕ} →
    (Char : Fin n → Fin n → V) →
    (expected : Fin n → Fin n → V) →
    Set ℓV
  ColOrthogonal Char expected = ∀ c c' →
    col-inner zero-V _+V_ _*V_ conj-V Char c c' ≈V expected c c'

------------------------------------------------------------------------
-- 4. Capstone — orthogonality framework in place.
--
-- U2 of the 20-slice arc. With U1 (WithCharacters) + U2 in place,
-- specific instances (U3 GL3F2, U4 Monster) supply:
--   * Specialization of V (= ℤ or ℚ)
--   * Specialization of arithmetic (+V, *V, conj-V, ≈V)
--   * Class sizes + centralizer orders + group order (as V-values)
--   * Per-(i,j) and per-(c,c') orthogonality proofs
--
-- The RowOrthogonal and ColOrthogonal predicates as defined here are
-- SIGNATURES; per-instance proof is downstream. For substrate
-- purposes, naming the predicates IS the structural target — it
-- exposes the universal property of character tables at the
-- categorical-primitive level.
--
-- Per [[anneal-don't-leap]]: the detailed Kronecker-δ specialization
-- (= "for i ≡ j the value equals G, otherwise zero") is deferred to
-- per-instance work. Substrate primitive provides the framework;
-- instances close the proof gap.
------------------------------------------------------------------------
