------------------------------------------------------------------------
-- Substrate.Groups.Capabilities
--
-- Tier 2 + Tier 3 cross-Zₙ feature-completeness infrastructure.
--
-- Tier 2: capability records, one per genericized capability,
-- bundling the parametric generic's parameter list. Each Zₙ supplies
-- a record value for every capability it has.
--
-- Tier 3: the reflective completeness theorem `complete`. Indexed
-- over `ZnInstance × CapabilityTag`, returns the corresponding
-- capability record (or ⊤ for gap cells). The function being TOTAL
-- across the product type is the substrate's static check that
-- every Zₙ has every capability the cone exposes.
--
-- Adding a new Zₙ requires:
--   * a new ZnInstance constructor,
--   * a clause in each capability's per-Zₙ witness (one record value),
--   * a clause in `complete` per capability — the typechecker drives
--     coverage.
--
-- Adding a new capability requires:
--   * a new Capabilities/<Name>.agda with the record + Z₃/Z₄/Z₅
--     witnesses,
--   * a new constructor in `CapabilityTag`,
--   * a new clause in `complete` per Zₙ.
--
-- Adding either kind of cell expansion makes `complete` partial
-- until the new clauses land — coverage IS the cross-check.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Capabilities where

------------------------------------------------------------------------
-- Re-export the four capability modules.
------------------------------------------------------------------------

open import Substrate.Groups.Capabilities.CoxeterFin       public
  using (CoxeterFinCapability)
  renaming ( cap-Z₂ to coxeterFin-Z₂; cap-Z₃ to coxeterFin-Z₃
           ; cap-Z₄ to coxeterFin-Z₄; cap-Z₅ to coxeterFin-Z₅
           ; cap-Z₇ to coxeterFin-Z₇)

open import Substrate.Groups.Capabilities.xFreeCyclic      public
  using (xFreeCyclicCapability)
  renaming ( cap-Z₂ to xFreeCyclic-Z₂; cap-Z₃ to xFreeCyclic-Z₃
           ; cap-Z₄ to xFreeCyclic-Z₄; cap-Z₅ to xFreeCyclic-Z₅
           ; cap-Z₇ to xFreeCyclic-Z₇)

open import Substrate.Groups.Capabilities.PhaseProjection  public
  using (PhaseProjectionCapability)
  renaming ( cap-Z₂ to phaseProj-Z₂; cap-Z₃ to phaseProj-Z₃
           ; cap-Z₄ to phaseProj-Z₄; cap-Z₅ to phaseProj-Z₅
           ; cap-Z₇ to phaseProj-Z₇)

open import Substrate.Groups.Capabilities.Strict2Monoid    public
  using (Strict2MonoidCapability)
  renaming ( cap-Z₂ to strict2Monoid-Z₂; cap-Z₃ to strict2Monoid-Z₃
           ; cap-Z₄ to strict2Monoid-Z₄; cap-Z₅ to strict2Monoid-Z₅
           ; cap-Z₇ to strict2Monoid-Z₇)

------------------------------------------------------------------------
-- The cone indices: ZnInstance × CapabilityTag.
------------------------------------------------------------------------

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_)
-- ⟡set1-paydown: CoxeterFinCapability now takes (Gen : Set)(Canonical : Word Gen → Set)
-- as parameters; the `Provides` cell existentializes BOTH (Σ Set / Σ (Word Gen → Set)),
-- exactly as the strict2Monoid cell already existentializes its Set carrier.
open import Substrate.Groups.Coxeter.Word using (Word)

------------------------------------------------------------------------
-- Lifted ⊤ at Set₁ for gap cells (capability records live at Set₁).
------------------------------------------------------------------------

record ⊤₁ : Set₁ where
  constructor tt₁

data ZnInstance : Set where
  Z₂ Z₃ Z₄ Z₅ Z₇ : ZnInstance

data CapabilityTag : Set where
  coxeterFin    : CapabilityTag
  xFreeCyclic   : CapabilityTag
  phaseProj     : CapabilityTag
  strict2Monoid : CapabilityTag

------------------------------------------------------------------------
-- Provides : ZnInstance → CapabilityTag → Set₁.
--
-- The cell type at (n, c) in the cone. Filled cells return the
-- corresponding capability record's type; gap cells return ⊤.
--
-- The gap layout (⊤ cells) documents which cells are NOT currently
-- filled — they typecheck trivially but Tier 3's `complete` returns
-- `tt` for them, marking the gap explicitly.
------------------------------------------------------------------------

Provides : ZnInstance → CapabilityTag → Set₁

-- Z₂: all four genericized capabilities filled (Slice 6).
Provides Z₂ coxeterFin    = Σ Set (λ Gen → Σ (Word Gen → Set) (λ Canonical → CoxeterFinCapability Gen Canonical 2))
Provides Z₂ xFreeCyclic   = Σ Set (λ Zn-Word → Σ (Zn-Word → Set) (λ Zn-Canonical → xFreeCyclicCapability Zn-Word Zn-Canonical))
Provides Z₂ phaseProj     = Σ Set (λ Zn-Word → Σ Set (λ F-Word → PhaseProjectionCapability Zn-Word F-Word))
Provides Z₂ strict2Monoid = Σ Set Strict2MonoidCapability

-- Z₃: all four genericized capabilities filled.
Provides Z₃ coxeterFin    = Σ Set (λ Gen → Σ (Word Gen → Set) (λ Canonical → CoxeterFinCapability Gen Canonical 3))
Provides Z₃ xFreeCyclic   = Σ Set (λ Zn-Word → Σ (Zn-Word → Set) (λ Zn-Canonical → xFreeCyclicCapability Zn-Word Zn-Canonical))
Provides Z₃ phaseProj     = Σ Set (λ Zn-Word → Σ Set (λ F-Word → PhaseProjectionCapability Zn-Word F-Word))
Provides Z₃ strict2Monoid = Σ Set Strict2MonoidCapability

-- Z₄: all four genericized capabilities filled.
Provides Z₄ coxeterFin    = Σ Set (λ Gen → Σ (Word Gen → Set) (λ Canonical → CoxeterFinCapability Gen Canonical 4))
Provides Z₄ xFreeCyclic   = Σ Set (λ Zn-Word → Σ (Zn-Word → Set) (λ Zn-Canonical → xFreeCyclicCapability Zn-Word Zn-Canonical))
Provides Z₄ phaseProj     = Σ Set (λ Zn-Word → Σ Set (λ F-Word → PhaseProjectionCapability Zn-Word F-Word))
Provides Z₄ strict2Monoid = Σ Set Strict2MonoidCapability

-- Z₅: all four genericized capabilities filled.
Provides Z₅ coxeterFin    = Σ Set (λ Gen → Σ (Word Gen → Set) (λ Canonical → CoxeterFinCapability Gen Canonical 5))
Provides Z₅ xFreeCyclic   = Σ Set (λ Zn-Word → Σ (Zn-Word → Set) (λ Zn-Canonical → xFreeCyclicCapability Zn-Word Zn-Canonical))
Provides Z₅ phaseProj     = Σ Set (λ Zn-Word → Σ Set (λ F-Word → PhaseProjectionCapability Zn-Word F-Word))
Provides Z₅ strict2Monoid = Σ Set Strict2MonoidCapability

-- Z₇: all four genericized capabilities filled (Slice 5).
Provides Z₇ coxeterFin    = Σ Set (λ Gen → Σ (Word Gen → Set) (λ Canonical → CoxeterFinCapability Gen Canonical 7))
Provides Z₇ xFreeCyclic   = Σ Set (λ Zn-Word → Σ (Zn-Word → Set) (λ Zn-Canonical → xFreeCyclicCapability Zn-Word Zn-Canonical))
Provides Z₇ phaseProj     = Σ Set (λ Zn-Word → Σ Set (λ F-Word → PhaseProjectionCapability Zn-Word F-Word))
Provides Z₇ strict2Monoid = Σ Set Strict2MonoidCapability

------------------------------------------------------------------------
-- The completeness theorem.
--
-- `complete` is a TOTAL function over ZnInstance × CapabilityTag.
-- If the function is not total, the typechecker flags the missing
-- cell. With the current gap-as-⊤ convention, gap cells are filled
-- with `tt`; filled cells dispatch to the per-Zₙ witness.
--
-- The shape of this function IS the (M, N) cone's covering theorem.
------------------------------------------------------------------------

complete : (n : ZnInstance) (c : CapabilityTag) → Provides n c
-- Z₂ row (filled)
complete Z₂ coxeterFin    = (_ , _ , coxeterFin-Z₂)
complete Z₂ xFreeCyclic   = (_ , _ , xFreeCyclic-Z₂)
complete Z₂ phaseProj     = (_ , _ , phaseProj-Z₂)
complete Z₂ strict2Monoid = (_ , strict2Monoid-Z₂)
-- Z₃ row (filled)
complete Z₃ coxeterFin    = (_ , _ , coxeterFin-Z₃)
complete Z₃ xFreeCyclic   = (_ , _ , xFreeCyclic-Z₃)
complete Z₃ phaseProj     = (_ , _ , phaseProj-Z₃)
complete Z₃ strict2Monoid = (_ , strict2Monoid-Z₃)
-- Z₄ row (filled)
complete Z₄ coxeterFin    = (_ , _ , coxeterFin-Z₄)
complete Z₄ xFreeCyclic   = (_ , _ , xFreeCyclic-Z₄)
complete Z₄ phaseProj     = (_ , _ , phaseProj-Z₄)
complete Z₄ strict2Monoid = (_ , strict2Monoid-Z₄)
-- Z₅ row (filled)
complete Z₅ coxeterFin    = (_ , _ , coxeterFin-Z₅)
complete Z₅ xFreeCyclic   = (_ , _ , xFreeCyclic-Z₅)
complete Z₅ phaseProj     = (_ , _ , phaseProj-Z₅)
complete Z₅ strict2Monoid = (_ , strict2Monoid-Z₅)
-- Z₇ row (filled)
complete Z₇ coxeterFin    = (_ , _ , coxeterFin-Z₇)
complete Z₇ xFreeCyclic   = (_ , _ , xFreeCyclic-Z₇)
complete Z₇ phaseProj     = (_ , _ , phaseProj-Z₇)
complete Z₇ strict2Monoid = (_ , strict2Monoid-Z₇)
