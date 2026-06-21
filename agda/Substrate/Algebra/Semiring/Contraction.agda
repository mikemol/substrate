------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.Contraction
--
-- ⊙ C6: the wedge/tensor engine takes the Semiring as a REAL PARAMETER — ONE
-- tensor `contract` (the semiring inner product ⊕ᵢ aᵢ⊗bᵢ, GraphBLAS-style)
-- that PLACES ITSELF via the chosen gauge: Bool routes (reachability), ℕ counts
-- (paths), ℕ∞ tropical costs (min-plus / shortest), F₂ computes parity. One
-- definition, four jobs — instances, not three builds.
--
-- This is the CONSUMER that "measures the dormant Semiring" the conjecture
-- asked for (a second one beside `Semiring.SPPF.inside`, the inside-fold). The
-- four gauges already live in `Semiring.Instances`; here a single tensor reads
-- them all, exhibited by `refl` at each gauge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring.Contraction where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Magma     using (Magma)
open import Substrate.Algebra.Semigroup using (magma)
open import Substrate.Algebra.Monoid    using (semigroup; ε)
open import Substrate.Algebra.Semiring  using (Semiring; +-monoid; *-monoid)
open import Substrate.Algebra.Semiring.Instances
  using (ℕ-semiring; Bool-semiring; tropical-semiring; F₂-semiring)
open import Substrate.Algebra.Semiring.NatInf using (ℕ∞; fin)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)

------------------------------------------------------------------------
-- The tensor, parametric over the semiring: ⟨a,b⟩ = ⊕ᵢ (aᵢ ⊗ bᵢ).
------------------------------------------------------------------------

module _ {A : Set} (S : Semiring A) where
  private
    infixr 6 _⊕_
    infixr 7 _⊗_
    _⊕_ : A → A → A
    a ⊕ b = Magma._·_ (magma (semigroup (+-monoid S))) a b
    _⊗_ : A → A → A
    a ⊗ b = Magma._·_ (magma (semigroup (*-monoid S))) a b

  contract : List A → List A → A
  contract []       _        = ε (+-monoid S)
  contract (_ ∷ _)  []       = ε (+-monoid S)
  contract (a ∷ as) (b ∷ bs) = (a ⊗ b) ⊕ contract as bs

------------------------------------------------------------------------
-- THE PLACEMENT: one tensor, four gauges — each reading by `refl`.
------------------------------------------------------------------------

-- ℕ count:  1·3 + 2·4 = 11  (number of weighted paths).
_ : contract ℕ-semiring (1 ∷ 2 ∷ []) (3 ∷ 4 ∷ []) ≡ 11
_ = refl

-- Bool route:  (⊤∧⊤) ∨ (⊥∧⊤) = ⊤  (is there a live channel?).
_ : contract Bool-semiring (true ∷ false ∷ []) (true ∷ true ∷ []) ≡ true
_ = refl

-- ℕ∞ tropical cost:  min(1+3, 2+4) = min(4,6) = 4  (cheapest composite).
_ : contract tropical-semiring (fin 1 ∷ fin 2 ∷ []) (fin 3 ∷ fin 4 ∷ []) ≡ fin 4
_ = refl

-- F₂ parity:  (𝟙∧𝟙) ⊕ (𝟙∧𝟙) = 𝟙 ⊕ 𝟙 = 𝟘  (XOR-cancelling compute).
_ : contract F₂-semiring (𝟙 ∷ 𝟙 ∷ []) (𝟙 ∷ 𝟙 ∷ []) ≡ 𝟘
_ = refl
