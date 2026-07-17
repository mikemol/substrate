------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Charter
--
-- Slice 3a of the shadow-architecture arc (Shadow F). The
-- realizability charter as a 4+1 gate record:
--
--   If a distinction is real, it must be constructible; if
--   constructible, it must be behaviorally reachable; if reachable,
--   it must be observable; if observable, it must be coverable; if
--   not, it is not a valid runtime distinction.
--
-- Per Increment 9, each row of the 6-distinction audit table also
-- carries a `persists-via` column — the mechanism by which the gate's
-- satisfaction extends across sessions. The fifth field captures this
-- time-extension; without it, the architecture's distinctions would
-- be only momentarily charter-valid.
--
-- A `Realizability` value is a record-of-five-cells. Each cell is
-- INDEXED by an evidence type (the formal Set whose inhabitation
-- witnesses the gate's pass) and fields the witness (a concrete
-- element of that type). ⟡set1-rp-charter: the evidence types are
-- record PARAMETERS, not fields — a Set-valued field pins the record
-- at Set₁, while a Set parameter never raises the record's sort
-- (set1-carrier-always-parameterize), so both `Cell` and
-- `Realizability` live at Set with the evidence visible in the type.
--
-- For operational gates whose claim doesn't reduce to an Agda-checkable
-- proposition (e.g., "tagged at Step B" is a process step, not a
-- type), the evidence type is `⊤` and the witness is `tt`. The
-- substantive structural gates (e.g., "L₁ uniquely decomp" from
-- `Substrate.ShadowArchitecture.Mode`) provide real Sets and witnesses
-- — see `Substrate.ShadowArchitecture.Distinction` for the 6-row
-- table where they're attached.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Charter where

open import Substrate.Foundation.Unit using (⊤; tt) public
open import Substrate.Foundation.Product using (_,_; _×_)

------------------------------------------------------------------------
-- A charter cell: evidence type + witness.
------------------------------------------------------------------------

record Cell (evidence : Set) : Set where
  constructor cell
  field
    witness  : evidence

-- Operational cell: evidence is ⊤, used when the gate's content is
-- a process / convention / external dependency rather than an Agda
-- proposition.
op-cell : Cell ⊤
op-cell = cell tt

------------------------------------------------------------------------
-- The realizability record.
------------------------------------------------------------------------

record Realizability (Ec Er Eo Ecov Ep : Set) : Set where
  constructor realizable
  field
    constructible : Cell Ec
    reachable     : Cell Er
    observable    : Cell Eo
    coverable     : Cell Ecov
    persists-via  : Cell Ep

------------------------------------------------------------------------
-- The four-gate check is the conjunction of the first four cells'
-- evidence; the time-extended check additionally requires
-- `persists-via`. We expose the existence-of-witnesses as a Set
-- so downstream users can demand "the distinction passes the charter"
-- as a proof obligation.
------------------------------------------------------------------------

-- A distinction passes the four gates: the conjunction of evidence
-- types (the record's own parameters — evidence is in the TYPE now).
PassesFourGates : {Ec Er Eo Ecov Ep : Set} → Realizability Ec Er Eo Ecov Ep → Set
PassesFourGates {Ec} {Er} {Eo} {Ecov} _ = Ec × Er × Eo × Ecov

-- The same with the time-extension column.
PassesFourPlusOne : {Ec Er Eo Ecov Ep : Set} → Realizability Ec Er Eo Ecov Ep → Set
PassesFourPlusOne {Ec} {Er} {Eo} {Ecov} {Ep} _ = Ec × Er × Eo × Ecov × Ep

------------------------------------------------------------------------
-- The witnesses-bundled-from-cells form the canonical proof of the
-- conjunction. Each Realizability instance gives one for free.
------------------------------------------------------------------------

four-gate-proof : {Ec Er Eo Ecov Ep : Set}
                  (r : Realizability Ec Er Eo Ecov Ep) → PassesFourGates r
four-gate-proof r =
    Cell.witness (Realizability.constructible r)
  , Cell.witness (Realizability.reachable r)
  , Cell.witness (Realizability.observable r)
  , Cell.witness (Realizability.coverable r)

four-plus-one-proof : {Ec Er Eo Ecov Ep : Set}
                      (r : Realizability Ec Er Eo Ecov Ep) → PassesFourPlusOne r
four-plus-one-proof r =
    Cell.witness (Realizability.constructible r)
  , Cell.witness (Realizability.reachable r)
  , Cell.witness (Realizability.observable r)
  , Cell.witness (Realizability.coverable r)
  , Cell.witness (Realizability.persists-via r)
