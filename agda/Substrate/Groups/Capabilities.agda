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

-- ⟡witness-orbit-collapse: each capability's five Zₙ witnesses are ONE type-orbit whose
-- graded points are separated by the cyclic index, so each Zₙ is an APPLICATION of the
-- orbit at its index (Z₂↦1 … Z₇↦6) — not a per-Zₙ copy.

open import Substrate.Groups.Capabilities.CoxeterFin using (CoxeterFinCapability)
import Substrate.Groups.Capabilities.CoxeterFin.Witness as CoxeterFinW
open import Substrate.Groups.Capabilities.xFreeCyclic using (xFreeCyclicCapability)
import Substrate.Groups.Capabilities.xFreeCyclic.Witness as xFreeCyclicW
open import Substrate.Groups.Capabilities.PhaseProjection using (PhaseProjectionCapability)
import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjectionW
open import Substrate.Groups.Capabilities.Strict2Monoid using (Strict2MonoidCapability)
import Substrate.Groups.Capabilities.Strict2Monoid.Witness as Strict2MonoidW
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Groups.Coxeter.Word using (Word)
import Substrate.Groups.Coxeter.Cyclic.Base as B
import Substrate.Groups.Coxeter.Cyclic.Existential as E
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.Z7-Coxeter as Z₇
import Substrate.Groups.FreeCyclic-Coxeter as F
coxeterFin-Z₂ = CoxeterFinW.cap 1
coxeterFin-Z₃ = CoxeterFinW.cap 2
coxeterFin-Z₄ = CoxeterFinW.cap 3
coxeterFin-Z₅ = CoxeterFinW.cap 4
coxeterFin-Z₇ = CoxeterFinW.cap 6

xFreeCyclic-Z₂ = xFreeCyclicW.cap 1
xFreeCyclic-Z₃ = xFreeCyclicW.cap 2
xFreeCyclic-Z₄ = xFreeCyclicW.cap 3
xFreeCyclic-Z₅ = xFreeCyclicW.cap 4
xFreeCyclic-Z₇ = xFreeCyclicW.cap 6

phaseProj-Z₂ = PhaseProjectionW.cap 1
phaseProj-Z₃ = PhaseProjectionW.cap 2
phaseProj-Z₄ = PhaseProjectionW.cap 3
phaseProj-Z₅ = PhaseProjectionW.cap 4
phaseProj-Z₇ = PhaseProjectionW.cap 6

strict2Monoid-Z₂ = Strict2MonoidW.cap 1
strict2Monoid-Z₃ = Strict2MonoidW.cap 2
strict2Monoid-Z₄ = Strict2MonoidW.cap 3
strict2Monoid-Z₅ = Strict2MonoidW.cap 4
strict2Monoid-Z₇ = Strict2MonoidW.cap 6

------------------------------------------------------------------------
-- The cone indices: ZnInstance × CapabilityTag.
------------------------------------------------------------------------

-- ⟡rc-provides (⟡rc-closeout): the four capability records are Set₀ (Gen/Canonical-Free
-- parameterized); the outer `Σ Set` was the SOLE Set₁ source. De-existentialized to the
-- CONCRETE per-Zₙ carriers, `Provides`/`complete` drop to Set.

-- ⟡rc-deletes (⟡rerank2-floor-dissolve): the bespoke `⊤₁ : Set₁` gap-cell
-- placeholder is DELETED — every Provides cell is now filled (no gap cells).

data ZnInstance : Set where
  Z₂ Z₃ Z₄ Z₅ Z₇ : ZnInstance

data CapabilityTag : Set where
  coxeterFin    : CapabilityTag
  xFreeCyclic   : CapabilityTag
  phaseProj     : CapabilityTag
  strict2Monoid : CapabilityTag

------------------------------------------------------------------------
-- Provides : ZnInstance → CapabilityTag → Set.
--
-- The cell type at (n, c) = the corresponding capability record's
-- CONCRETE type, at the per-Zₙ carriers. (⟡rc-provides: the Σ-existential
-- form was the sole Set₁ source; every cell is filled — no gap/⊤ cells —
-- so the de-existentialized cells land in Set.)
------------------------------------------------------------------------

Provides : ZnInstance → CapabilityTag → Set

-- Z₂: all four genericized capabilities filled (Slice 6).
Provides Z₂ coxeterFin    = CoxeterFinCapability (B.Gen 1) (E.Canonical-ex 1) 2
Provides Z₂ xFreeCyclic   = xFreeCyclicCapability (Word (B.Gen 1)) (E.Canonical-ex 1)
Provides Z₂ phaseProj     = PhaseProjectionCapability (Word (B.Gen 1)) (Word F.Gen)
Provides Z₂ strict2Monoid = Strict2MonoidCapability (Word (B.Gen 1))

-- Z₃: all four genericized capabilities filled.
Provides Z₃ coxeterFin    = CoxeterFinCapability (B.Gen 2) (E.Canonical-ex 2) 3
Provides Z₃ xFreeCyclic   = xFreeCyclicCapability (Word (B.Gen 2)) (E.Canonical-ex 2)
Provides Z₃ phaseProj     = PhaseProjectionCapability (Word (B.Gen 2)) (Word F.Gen)
Provides Z₃ strict2Monoid = Strict2MonoidCapability (Word (B.Gen 2))

-- Z₄: all four genericized capabilities filled.
Provides Z₄ coxeterFin    = CoxeterFinCapability (B.Gen 3) (E.Canonical-ex 3) 4
Provides Z₄ xFreeCyclic   = xFreeCyclicCapability (Word (B.Gen 3)) (E.Canonical-ex 3)
Provides Z₄ phaseProj     = PhaseProjectionCapability (Word (B.Gen 3)) (Word F.Gen)
Provides Z₄ strict2Monoid = Strict2MonoidCapability (Word (B.Gen 3))

-- Z₅: all four genericized capabilities filled.
Provides Z₅ coxeterFin    = CoxeterFinCapability (B.Gen 4) (E.Canonical-ex 4) 5
Provides Z₅ xFreeCyclic   = xFreeCyclicCapability (Word (B.Gen 4)) (E.Canonical-ex 4)
Provides Z₅ phaseProj     = PhaseProjectionCapability (Word (B.Gen 4)) (Word F.Gen)
Provides Z₅ strict2Monoid = Strict2MonoidCapability (Word (B.Gen 4))

-- Z₇: all four genericized capabilities filled (Slice 5).
Provides Z₇ coxeterFin    = CoxeterFinCapability (B.Gen 6) (E.Canonical-ex 6) 7
Provides Z₇ xFreeCyclic   = xFreeCyclicCapability (Word (B.Gen 6)) (E.Canonical-ex 6)
Provides Z₇ phaseProj     = PhaseProjectionCapability (Word (B.Gen 6)) (Word F.Gen)
Provides Z₇ strict2Monoid = Strict2MonoidCapability (Word (B.Gen 6))

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
complete Z₂ coxeterFin    = coxeterFin-Z₂
complete Z₂ xFreeCyclic   = xFreeCyclic-Z₂
complete Z₂ phaseProj     = phaseProj-Z₂
complete Z₂ strict2Monoid = strict2Monoid-Z₂
-- Z₃ row (filled)
complete Z₃ coxeterFin    = coxeterFin-Z₃
complete Z₃ xFreeCyclic   = xFreeCyclic-Z₃
complete Z₃ phaseProj     = phaseProj-Z₃
complete Z₃ strict2Monoid = strict2Monoid-Z₃
-- Z₄ row (filled)
complete Z₄ coxeterFin    = coxeterFin-Z₄
complete Z₄ xFreeCyclic   = xFreeCyclic-Z₄
complete Z₄ phaseProj     = phaseProj-Z₄
complete Z₄ strict2Monoid = strict2Monoid-Z₄
-- Z₅ row (filled)
complete Z₅ coxeterFin    = coxeterFin-Z₅
complete Z₅ xFreeCyclic   = xFreeCyclic-Z₅
complete Z₅ phaseProj     = phaseProj-Z₅
complete Z₅ strict2Monoid = strict2Monoid-Z₅
-- Z₇ row (filled)
complete Z₇ coxeterFin    = coxeterFin-Z₇
complete Z₇ xFreeCyclic   = xFreeCyclic-Z₇
complete Z₇ phaseProj     = phaseProj-Z₇
complete Z₇ strict2Monoid = strict2Monoid-Z₇
