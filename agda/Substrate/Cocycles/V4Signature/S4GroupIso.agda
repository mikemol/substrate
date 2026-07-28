------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4GroupIso
--
-- The catalog's primary claim about CY-5 — "the 24 ARE S_4"
-- (M41 v19) — lifted from set-level bijection (S4Iso, slice 4) to
-- the GROUP level: TotalSpace and S_4 are isomorphic as groups.
--
-- The set-bijection from S4Iso provides:
--   total-to-s4    : TotalSpace → Permutation
--   s4-to-total    : Permutation → TotalSpace
--   σ-round-trip   : total-to-s4 ∘ s4-to-total ≈ id  (pointwise)
--   total-round-trip : s4-to-total ∘ total-to-s4 ≡ id  (propositional)
--
-- This module transfers the S_4 group operations through the
-- bijection to give TotalSpace a group structure, then bundles
-- it as a Group with TotalSpace ≅ S_4 as IsGroupIsomorphism.
--
-- The ≈ vs ≡ asymmetry needs care:
--   * Permutation's equivalence is pointwise (_≈_), coarser than
--     propositional equality (which would require funext or UIP on
--     the bijection-certificate fields).
--   * TotalSpace = OrbitKey × V₄ — a finite product of decidable
--     types, propositional equality is fine.
--   * Lemma `≈-respects-s4-to-total`: s4-to-total is well-defined
--     under ≈ because it only inspects apply at three axes.
--
-- See:
--   * catalog/cocycles.md § CY-5 — "the 24 ARE S_4"
--   * Substrate.Cocycles.V4Signature.S4Iso — the underlying bijection
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4GroupIso where

open import Substrate.Foundation.Product using (_,_; proj₁; proj₂; ∃; -,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)
import Substrate.Algebra.Magma     as SM
import Substrate.Algebra.Semigroup as SS
import Substrate.Algebra.Monoid    as SMo
import Substrate.Algebra.Group     as SG

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Delooping  using (deloop)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis

open import Substrate.Groups.V4-Embedding
  using (embed; act-axis-involutive)
open import Substrate.Groups.SemidirectProduct
  using (Stab; v-for; s-for; s-for-fixes-anchor; v-of-axis; v-of-axis-unique; factorisation)
open import Substrate.Cocycles.V4Signature.S4Iso
  using (TotalSpace; total-to-s4; s4-to-total; σ-round-trip; total-round-trip; classify-CS)
open import Substrate.Groups.S4
open import Substrate.Groups.Symmetric.Permutation.Compose Axis
open import Substrate.Groups.Symmetric.EqRefl Axis
open import Substrate.Groups.Symmetric.Identity Axis
open import Substrate.Groups.Symmetric.Permutation.Inverse Axis
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.OrbitKey.Type
open import Substrate.Cocycles.V4Signature.S4Iso.Classify
open import Substrate.Groups.SemidirectProduct.V
open import Substrate.Axes.VOfAxis
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Cocycles.V4Signature.S4Iso.Roundtrips

------------------------------------------------------------------------
-- Helper: propositional equality implies pointwise equivalence.
------------------------------------------------------------------------

≡-to-≈ : {σ τ : Permutation} → σ ≡ τ → σ ≈ τ
≡-to-≈ refl x = refl

------------------------------------------------------------------------
-- s4-to-total respects pointwise equivalence.
--
-- Proof: s4-to-total σ is built from
--   v-for σ              = v-of-axis (apply σ D)
--   stab-d-to-orbit-key  = classify-CS (apply (s-for σ) C)
--                                       (apply (s-for σ) S)
-- and `s-for σ`'s apply at z is `act-axis (v-for σ) (apply σ z)`.
-- All three uses of σ are through its `apply` projection, so any two
-- pointwise-equivalent permutations produce equal s4-to-total values.
------------------------------------------------------------------------

≈-respects-s4-to-total :
  (σ τ : Permutation) → σ ≈ τ → s4-to-total σ ≡ s4-to-total τ
≈-respects-s4-to-total σ τ σ≈τ = cong₂ _,_ ok-eq v-eq
  where
    v-eq : v-for σ ≡ v-for τ
    v-eq = cong v-of-axis (σ≈τ D)

    s-for-eq-at :
      (z : Axis) → apply (s-for σ) z ≡ apply (s-for τ) z
    s-for-eq-at z =
      trans (cong (act-axis (v-for σ)) (σ≈τ z))
            (cong (λ v → act-axis v (apply τ z)) v-eq)

    ok-eq :
      classify-CS (apply (s-for σ) C) (apply (s-for σ) S)
      ≡ classify-CS (apply (s-for τ) C) (apply (s-for τ) S)
    ok-eq = cong₂ classify-CS (s-for-eq-at C) (s-for-eq-at S)

------------------------------------------------------------------------
-- TotalSpace group operations: transfer through the bijection.
--
-- a ∙ₜ b := s4-to-total (total-to-s4 a · total-to-s4 b)
-- εₜ    := s4-to-total ε
-- a ⁻¹ₜ := s4-to-total ((total-to-s4 a) ⁻¹)
------------------------------------------------------------------------

infixl 7 _∙ₜ_

_∙ₜ_ : TotalSpace → TotalSpace → TotalSpace
a ∙ₜ b = s4-to-total (total-to-s4 a · total-to-s4 b)

εₜ : TotalSpace
εₜ = s4-to-total ε

_⁻¹ₜ : TotalSpace → TotalSpace
a ⁻¹ₜ = s4-to-total ((total-to-s4 a) ⁻¹)

------------------------------------------------------------------------
-- Group axioms.
--
-- Each axiom is proved by:
--   1. Stating the corresponding S_4 axiom (which holds up to ≈).
--   2. Using ≈-respects-s4-to-total to transfer to ≡ on TotalSpace.
--   3. Where round trips appear, σ-round-trip and total-round-trip
--      close the chain.
------------------------------------------------------------------------

-- Associativity.
∙ₜ-assoc : (a b c : TotalSpace) → (a ∙ₜ b) ∙ₜ c ≡ a ∙ₜ (b ∙ₜ c)
∙ₜ-assoc a b c = ≈-respects-s4-to-total σL σR chain
  where
    φa = total-to-s4 a
    φb = total-to-s4 b
    φc = total-to-s4 c
    σL = total-to-s4 (s4-to-total (φa · φb)) · φc
    σR = φa · total-to-s4 (s4-to-total (φb · φc))
    -- Key step: apply σL z = apply φa (φb (φc z)) = apply σR z
    chain : σL ≈ σR
    chain z =
      trans (σ-round-trip (φa · φb) (apply φc z))
            (sym (cong (apply φa) (σ-round-trip (φb · φc) z)))

-- Left identity.
∙ₜ-identityˡ : (a : TotalSpace) → εₜ ∙ₜ a ≡ a
∙ₜ-identityˡ a =
  trans (≈-respects-s4-to-total σL (total-to-s4 a) chain)
        (total-round-trip a)
  where
    σL = total-to-s4 (s4-to-total ε) · total-to-s4 a
    chain : σL ≈ total-to-s4 a
    chain z = σ-round-trip ε (apply (total-to-s4 a) z)

-- Right identity.
∙ₜ-identityʳ : (a : TotalSpace) → a ∙ₜ εₜ ≡ a
∙ₜ-identityʳ a =
  trans (≈-respects-s4-to-total σL (total-to-s4 a) chain)
        (total-round-trip a)
  where
    σL = total-to-s4 a · total-to-s4 (s4-to-total ε)
    chain : σL ≈ total-to-s4 a
    chain z = cong (apply (total-to-s4 a)) (σ-round-trip ε z)

-- Left inverse.
∙ₜ-inverseˡ : (a : TotalSpace) → (a ⁻¹ₜ) ∙ₜ a ≡ εₜ
∙ₜ-inverseˡ a = ≈-respects-s4-to-total σL ε chain
  where
    φa = total-to-s4 a
    σL = total-to-s4 (s4-to-total (φa ⁻¹)) · φa
    chain : σL ≈ ε
    chain z =
      trans (σ-round-trip (φa ⁻¹) (apply φa z))
            (inv-l φa z)

-- Right inverse.
∙ₜ-inverseʳ : (a : TotalSpace) → a ∙ₜ (a ⁻¹ₜ) ≡ εₜ
∙ₜ-inverseʳ a = ≈-respects-s4-to-total σL ε chain
  where
    φa = total-to-s4 a
    σL = φa · total-to-s4 (s4-to-total (φa ⁻¹))
    chain : σL ≈ ε
    chain z =
      trans (cong (apply φa) (σ-round-trip (φa ⁻¹) z))
            (inv-r φa z)

-- Congruence of _∙ₜ_ wrt ≡ (trivial since TotalSpace uses propositional
-- equality).
∙ₜ-cong : {a₁ a₂ b₁ b₂ : TotalSpace} →
         a₁ ≡ a₂ → b₁ ≡ b₂ → (a₁ ∙ₜ b₁) ≡ (a₂ ∙ₜ b₂)
∙ₜ-cong refl refl = refl

-- Congruence of _⁻¹ₜ wrt ≡.
⁻¹ₜ-cong : {a₁ a₂ : TotalSpace} → a₁ ≡ a₂ → (a₁ ⁻¹ₜ) ≡ (a₂ ⁻¹ₜ)
⁻¹ₜ-cong refl = refl

------------------------------------------------------------------------
-- Bundle TotalSpace as a substrate-native Group.
------------------------------------------------------------------------

TotalSpace-Magma : SM.Magma TotalSpace
TotalSpace-Magma = record { _·_ = _∙ₜ_ }

TotalSpace-Semigroup : SS.Semigroup TotalSpace
TotalSpace-Semigroup = record
  { magma   = TotalSpace-Magma
  ; ·-assoc = ∙ₜ-assoc
  }

TotalSpace-Monoid : SMo.Monoid TotalSpace
TotalSpace-Monoid = record
  { semigroup = TotalSpace-Semigroup
  ; ε         = εₜ
  ; ε-left    = ∙ₜ-identityˡ
  ; ε-right   = ∙ₜ-identityʳ
  }

TotalSpace-Group : SG.Group TotalSpace
TotalSpace-Group = record
  { monoid    = TotalSpace-Monoid
  ; inv       = _⁻¹ₜ
  ; inv-left  = ∙ₜ-inverseˡ
  ; inv-right = ∙ₜ-inverseʳ
  }

------------------------------------------------------------------------
-- GROUNDED on the categorical spine via DELOOPING. TotalSpace's monoid
-- reduct IS the one-object category BG (Substrate.Category.Delooping) —
-- one object ⋆, hom(⋆,⋆) = TotalSpace, identity = εₜ, composition = ∙ₜ.
-- The ∙ₜ-assoc / ∙ₜ-identityˡ/ʳ laws above ARE its category laws. This is
-- the Algebra→Category bridge closing the parallel-hierarchy gap
-- ([[project-bridge-indexes-algebra-category]]): a structure bundled in
-- Algebra.Monoid is now a substrate-named Category.CategoryOf, ON the spine.
------------------------------------------------------------------------

TotalSpace-Category : CategoryOf ⊤ (λ _ _ → TotalSpace)
TotalSpace-Category = deloop TotalSpace-Monoid

------------------------------------------------------------------------
-- The group homomorphism / isomorphism TotalSpace ≅ S_4.
--
-- Substrate-honest scope: the FULL group-morphism record machinery
-- (stdlib's Algebra.Morphism.Structures.IsGroupHomomorphism /
-- IsGroupIsomorphism) is REMOVED. The homomorphism witnesses + the
-- injectivity / surjectivity proofs are KEPT as standalone functions
-- — a downstream substrate-native GroupHomomorphism record can
-- consume them mechanically.
------------------------------------------------------------------------

-- Homomorphism witnesses.
total-to-s4-homo :
  (a b : TotalSpace) → total-to-s4 (a ∙ₜ b) ≈ (total-to-s4 a · total-to-s4 b)
total-to-s4-homo a b = σ-round-trip (total-to-s4 a · total-to-s4 b)

total-to-s4-ε-homo : total-to-s4 εₜ ≈ ε
total-to-s4-ε-homo = σ-round-trip ε

total-to-s4-⁻¹-homo :
  (a : TotalSpace) → total-to-s4 (a ⁻¹ₜ) ≈ (total-to-s4 a) ⁻¹
total-to-s4-⁻¹-homo a = σ-round-trip ((total-to-s4 a) ⁻¹)

-- Injectivity.
total-to-s4-injective : ∀ {a b} → total-to-s4 a ≈ total-to-s4 b → a ≡ b
total-to-s4-injective {a} {b} eq =
  trans (sym (total-round-trip a))
        (trans (≈-respects-s4-to-total (total-to-s4 a) (total-to-s4 b) eq)
               (total-round-trip b))

-- Surjectivity.
total-to-s4-surjective :
  ∀ σ → ∃ λ a → ∀ {z} → z ≡ a → total-to-s4 z ≈ σ
total-to-s4-surjective σ = s4-to-total σ , λ {z} z≡ x →
  trans (cong (λ w → apply (total-to-s4 w) x) z≡)
        (σ-round-trip σ x)

------------------------------------------------------------------------
-- Notes
--
-- 1. This module closes the catalog's "24 ARE S_4" claim at the
--    deepest level the catalog asserts. The 24 elements of the CY-5
--    TotalSpace ARE the elements of S_4 — as groups, not just as
--    bijection-related sets. The cocycle's gauge group V_4 sits
--    inside S_4 as a normal subgroup; the cosets are the 6 OrbitKeys.
--
-- 2. The asymmetry in equivalence relations (_≡_ on TotalSpace,
--    _≈_ on Permutation) is real and load-bearing. Without ≈-respects-
--    s4-to-total, the transfer wouldn't be well-defined. The lemma's
--    proof exploits that s4-to-total inspects σ.apply at only three
--    axes — finite information.
--
-- 3. The Group structure on TotalSpace is NOT the structure CY-5's
--    cocycle gauge produces. CY-5's V_4-action on TotalSpace acts
--    only on the fiber (the second component); it never moves
--    between OrbitKeys. The Group structure here is the LIFTED
--    S_4-action, which moves freely across the whole TotalSpace
--    via the bijection. The two are distinct: the cocycle's V_4-
--    action is the *fibre-preserving* action, the S_4-action is the
--    *whole-of-TotalSpace* action.
--
-- 4. Cross-references:
--    - Substrate.Cocycles.V4Signature.S4Iso for the underlying
--      set-bijection.
--    - Substrate.Cocycle.IsomorphicCocycleStructure for the cocycle
--      abstraction CY-5 inhabits.
--    - catalog/cocycles.md § CY-5 — "the 24 ARE S_4".
------------------------------------------------------------------------
