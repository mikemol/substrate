------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Distinction
--
-- Slice 3b of the shadow-architecture arc. The six rows of Increment
-- 9's charter audit table, each as a `Realizability` instance:
--
--   1. 7 axis-signatures      (Increments 2, 3)
--   2. 7 Fano-lines            (Increment 3)
--   3. guard response          (Increment 6, star of 001)
--   4. e₁ adjunction           (Increments 1, 6)
--   5. e₂ symmetric lens       (Increments 1, 6)
--   6. L₆ reconstitution       (Increment 3, 001+110→111)
--
-- Each distinction provides a 5-cell `Realizability` record. Where
-- the gate's content is Agda-substantive (a structural fact our
-- previous slices already established), the cell carries that fact's
-- evidence type with a `refl`/etc. witness. Where the gate's content
-- is operational (a process step, file-write convention, drift-log
-- mechanism), the cell uses `op-cell` (evidence = ⊤).
--
-- The closing theorem `all-distinctions-pass` records the audit's
-- conclusion: all six distinctions pass the four gates, and (with
-- time-extension) pass the 4+1 gates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Distinction where

open import Substrate.Foundation.Bool using (true)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_)

open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.ShadowArchitecture.Duality using (normal-vector; dual-line)
open import Substrate.ShadowArchitecture.Weight
  using (point-orbit; line-orbit; Orbit)
open import Substrate.ShadowArchitecture.Mode
  using (Mode; in-mode; decomp; snap; regroup; guard;
         star-of-001; guard-territory-is-star-001;
         L₄-decomp; L₄-snap; L₅-snap; L₅-regroup)
open import Substrate.ShadowArchitecture.Charter
  using (Cell; cell; op-cell; Realizability; realizable;
         PassesFourGates; PassesFourPlusOne;
         four-gate-proof; four-plus-one-proof)

------------------------------------------------------------------------
-- Names for the six audited distinctions.
------------------------------------------------------------------------

data Distinction-Name : Set where
  D-axis-sigs          : Distinction-Name
  D-fano-lines         : Distinction-Name
  D-guard-response     : Distinction-Name
  D-e1-adjunction      : Distinction-Name
  D-e2-symmetric-lens  : Distinction-Name
  D-L6-reconstitution  : Distinction-Name

------------------------------------------------------------------------
-- Row 1: 7 axis-signatures.
--
-- constructible: Point type (read/write set on F₂³)
-- reachable:     every move classifies to one Point  (point-orbit)
-- observable:    tagged at Step B                     (operational)
-- coverable:     Point synthesisable from 3 bits      (point-to-vec)
-- persists-via:  axis-tags in cotype                  (operational)
------------------------------------------------------------------------

charter-axis-sigs : Realizability Point (Point → Orbit) ⊤ (Point → Vector 3) ⊤
charter-axis-sigs = realizable
    (cell p₁₀₀)                                   -- a Point witness
    (cell point-orbit)                            -- the orbit classifier
    op-cell                                       -- operational
    (cell point-to-vec)                           -- the embedding
    op-cell                                       -- operational

------------------------------------------------------------------------
-- Row 2: 7 Fano-lines.
--
-- constructible: FanoLine type (triple-check on 3-tuples of points)
-- reachable:     line-points (every FanoLine has a definite triple)
-- observable:    completion/gap via incidence       (operational)
-- coverable:     line-orbit synthesis from F₂³      (line-orbit)
-- persists-via:  probe-state section                 (operational)
------------------------------------------------------------------------

charter-fano-lines :
  Realizability FanoLine (FanoLine → Point × Point × Point) ⊤ (FanoLine → Orbit) ⊤
charter-fano-lines = realizable
    (cell L₁)                                          -- a FanoLine witness
    (cell line-points)                                 -- triple-lookup
    op-cell
    (cell line-orbit)                                  -- orbit classifier
    op-cell

------------------------------------------------------------------------
-- Row 3: guard response.
--
-- constructible: {L₂, L₃, L₆} = star of 001        (guard-territory-is-star-001)
-- reachable:     on e₃-bit moves                    (operational)
-- observable:    reject + redirect to 110/111      (operational)
-- coverable:     constructed 001                    (p₀₀₁ : Point)
-- persists-via:  drift events section               (operational)
------------------------------------------------------------------------

charter-guard-response :
  Realizability (∀ (ℓ : FanoLine) → in-mode guard ℓ ≡ star-of-001 ℓ) ⊤ ⊤ Point ⊤
charter-guard-response = realizable
    (cell guard-territory-is-star-001)
    op-cell
    op-cell
    (cell p₀₀₁)
    op-cell

------------------------------------------------------------------------
-- Row 4: e₁ adjunction (decomp/snap).
--
-- The unit-of-the-adjunction lives at L₄, which decomp writes and
-- snap reads. Operational gates dominate; the L₄-incidence facts
-- from `Mode` provide the structural anchor.
------------------------------------------------------------------------

charter-e1-adjunction : Realizability ⊤ ⊤ (in-mode decomp L₄ ≡ true) ⊤ ⊤
charter-e1-adjunction = realizable
    op-cell                                            -- "lift / contract" labels
    op-cell                                            -- "both instantiated"
    (cell L₄-decomp)                                   -- L₄ unit-of-adj.
    op-cell                                            -- round-trip
    op-cell                                            -- shadow-list completeness

------------------------------------------------------------------------
-- Row 5: e₂ symmetric lens (regroup).
--
-- Behaviour preservation lives at L₅, which snap reads and regroup
-- writes. Same shape as Row 4.
------------------------------------------------------------------------

charter-e2-symmetric-lens : Realizability ⊤ ⊤ (in-mode snap L₅ ≡ true) ⊤ ⊤
charter-e2-symmetric-lens = realizable
    op-cell                                            -- "extract / rebuild"
    op-cell                                            -- "on refactor/dup"
    (cell L₅-snap)                                     -- L₅ behaviour-pres.
    op-cell                                            -- tests re-run
    op-cell                                            -- original test resources

------------------------------------------------------------------------
-- Row 6: L₆ reconstitution (001 + 110 → 111).
--
-- The composition fact is Agda-provable: the F₂³ sum of point-to-vec
-- p₀₀₁ and point-to-vec p₁₁₀ equals point-to-vec p₁₁₁. By construction
-- both sides reduce to the F₂³ vector 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ [].
------------------------------------------------------------------------

L₆-composition-fact :
  point-to-vec p₀₀₁ +ⱽ point-to-vec p₁₁₀ ≡ point-to-vec p₁₁₁
L₆-composition-fact = refl

charter-L6-reconstitution :
  Realizability (point-to-vec p₀₀₁ +ⱽ point-to-vec p₁₁₀ ≡ point-to-vec p₁₁₁) ⊤ ⊤ ⊤ ⊤
charter-L6-reconstitution = realizable
    (cell L₆-composition-fact)                         -- 001 + 110 → 111
    op-cell                                            -- both populated
    op-cell                                            -- log distinguish
    op-cell                                            -- cotype synthesis
    op-cell                                            -- 001+110 stay populated

------------------------------------------------------------------------
-- The full audit table.
--
-- ⟡set1-rp-charter: `Realizability` is indexed by its five evidence
-- types, so the table's return type varies per row. Five computed
-- index families (one per gate column) carry that variation; each
-- clause reduces definitionally to the row's instance type above.
------------------------------------------------------------------------

con-ev rea-ev obs-ev cov-ev per-ev : Distinction-Name → Set

con-ev D-axis-sigs         = Point
con-ev D-fano-lines        = FanoLine
con-ev D-guard-response    = ∀ (ℓ : FanoLine) → in-mode guard ℓ ≡ star-of-001 ℓ
con-ev D-e1-adjunction     = ⊤
con-ev D-e2-symmetric-lens = ⊤
con-ev D-L6-reconstitution =
  point-to-vec p₀₀₁ +ⱽ point-to-vec p₁₁₀ ≡ point-to-vec p₁₁₁

rea-ev D-axis-sigs         = Point → Orbit
rea-ev D-fano-lines        = FanoLine → Point × Point × Point
rea-ev D-guard-response    = ⊤
rea-ev D-e1-adjunction     = ⊤
rea-ev D-e2-symmetric-lens = ⊤
rea-ev D-L6-reconstitution = ⊤

obs-ev D-axis-sigs         = ⊤
obs-ev D-fano-lines        = ⊤
obs-ev D-guard-response    = ⊤
obs-ev D-e1-adjunction     = in-mode decomp L₄ ≡ true
obs-ev D-e2-symmetric-lens = in-mode snap L₅ ≡ true
obs-ev D-L6-reconstitution = ⊤

cov-ev D-axis-sigs         = Point → Vector 3
cov-ev D-fano-lines        = FanoLine → Orbit
cov-ev D-guard-response    = Point
cov-ev D-e1-adjunction     = ⊤
cov-ev D-e2-symmetric-lens = ⊤
cov-ev D-L6-reconstitution = ⊤

per-ev D-axis-sigs         = ⊤
per-ev D-fano-lines        = ⊤
per-ev D-guard-response    = ⊤
per-ev D-e1-adjunction     = ⊤
per-ev D-e2-symmetric-lens = ⊤
per-ev D-L6-reconstitution = ⊤

charter-of : (D : Distinction-Name)
           → Realizability (con-ev D) (rea-ev D) (obs-ev D) (cov-ev D) (per-ev D)
charter-of D-axis-sigs         = charter-axis-sigs
charter-of D-fano-lines        = charter-fano-lines
charter-of D-guard-response    = charter-guard-response
charter-of D-e1-adjunction     = charter-e1-adjunction
charter-of D-e2-symmetric-lens = charter-e2-symmetric-lens
charter-of D-L6-reconstitution = charter-L6-reconstitution

------------------------------------------------------------------------
-- Audit conclusion: all six distinctions pass.
--
-- The bundled witnesses follow from `four-gate-proof` /
-- `four-plus-one-proof` of `Charter`, which extract the witnesses from
-- each cell directly.
------------------------------------------------------------------------

all-distinctions-pass :
  ∀ (D : Distinction-Name) → PassesFourGates (charter-of D)
all-distinctions-pass D = four-gate-proof (charter-of D)

all-distinctions-pass-time-extended :
  ∀ (D : Distinction-Name) → PassesFourPlusOne (charter-of D)
all-distinctions-pass-time-extended D = four-plus-one-proof (charter-of D)
