------------------------------------------------------------------------
-- Substrate.Cocycle
--
-- The IsomorphicCocycleStructure abstraction (per the catalog's strong
-- discipline) — substrate-native.
--
-- Phase-2 rewrite (revision): parametric over Substrate.Algebra.
-- SetoidGroup (so both Group instances (via to-setoid) and natively
-- setoid-shaped groups like Symmetric / SFin / Coxeter can plug in).
-- Action is Substrate.Algebra.SetoidGroup.Action (axioms use ≡ on the
-- action carrier).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycle where

open import Substrate.Foundation.Eq
  using (_≡_; refl; cong)
open import Substrate.Foundation.Product
  using (Σ; Σ-syntax; _×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Algebra.SetoidGroup.Action public
  using (Action; act; act-id; act-∙)

------------------------------------------------------------------------
-- IsTorsor — SetoidGroup-parametric.
------------------------------------------------------------------------

record IsTorsor (Carrier : Set) (_≈_ : Carrier → Carrier → Set)
                (G : SetoidGroup Carrier _≈_) (T : Set) : Set where      -- ⟦shape:8ffbc99a action,(g,(t₁ t₂⟧
  open SetoidGroup G
  field
    action     : Action Carrier _≈_ G T
    free       :
      (g : Carrier) (t : T) →
      act action g t ≡ t →
      g ≡ ε
    transitive :
      (t₁ t₂ : T) →
      Σ Carrier (λ g → act action g t₁ ≡ t₂)

open IsTorsor public

------------------------------------------------------------------------
-- IsomorphicCocycleStructure — primary abstraction.
------------------------------------------------------------------------

record IsomorphicCocycleStructure : Set₁ where      -- ⟦shape:ffdd236e Invariant,Gauge,Fiber⟧
  field
    Invariant    : Set
    GaugeCarrier : Set
    GaugeRel     : GaugeCarrier → GaugeCarrier → Set
    Gauge        : SetoidGroup GaugeCarrier GaugeRel
    Fiber        : Invariant → Set
    fiber-torsor : (i : Invariant) → IsTorsor GaugeCarrier GaugeRel Gauge (Fiber i)

  TotalSpace : Set
  TotalSpace = Σ Invariant Fiber

  project : TotalSpace → Invariant
  project = proj₁

------------------------------------------------------------------------
-- WeakCocycleStructure — compatibility shape.
------------------------------------------------------------------------

record WeakCocycleStructure : Set₁ where
  field
    Base         : Set
    GaugeCarrier : Set
    GaugeRel     : GaugeCarrier → GaugeCarrier → Set
    Gauge        : SetoidGroup GaugeCarrier GaugeRel
    action-w     : Action GaugeCarrier GaugeRel Gauge Base
    Invariant    : Set
    project      : Base → Invariant
    project-gauge-invariant :
      (g : GaugeCarrier) (b : Base) →
      project (act action-w g b) ≡ project b

------------------------------------------------------------------------
-- Downcast.
------------------------------------------------------------------------

module Downcast (𝒞 : IsomorphicCocycleStructure) where
  open IsomorphicCocycleStructure 𝒞
  open SetoidGroup Gauge using () renaming (ε to εG; _∙_ to _·G_)

  ∣G∣ : Set
  ∣G∣ = GaugeCarrier

  total-act : ∣G∣ → TotalSpace → TotalSpace
  total-act g (i , t) = i , act (action (fiber-torsor i)) g t

  total-act-id : (x : TotalSpace) → total-act εG x ≡ x
  total-act-id (i , t) =
    cong (i ,_) (act-id (action (fiber-torsor i)) t)

  total-act-∙ :
    (g h : ∣G∣) (x : TotalSpace) →
    total-act (g ·G h) x ≡ total-act g (total-act h x)
  total-act-∙ g h (i , t) =
    cong (i ,_) (act-∙ (action (fiber-torsor i)) g h t)

  total-action : Action GaugeCarrier GaugeRel Gauge TotalSpace
  total-action = record
    { act    = total-act
    ; act-id = total-act-id
    ; act-∙  = total-act-∙
    }

  proj-gauge-inv :
    (g : ∣G∣) (x : TotalSpace) →
    project (total-act g x) ≡ project x
  proj-gauge-inv _ _ = refl

  weak : WeakCocycleStructure
  weak = record
    { Base                    = TotalSpace
    ; GaugeCarrier            = GaugeCarrier
    ; GaugeRel                = GaugeRel
    ; Gauge                   = Gauge
    ; action-w                = total-action
    ; Invariant               = Invariant
    ; project                 = project
    ; project-gauge-invariant = proj-gauge-inv
    }
