------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas
--
-- The substrate-side of el-atlas's STRUCTURED EDITION as a Π, not a document.
--
-- `scratch/el-atlas/el-atlas-repo/el-atlas-structured.md` is the instrument's
-- output: a claim lattice whose header reserves the integration target —
--   "Proof tier: EMPTY — reserved: the Agda rung. [W]-by-sample != [W]-by-proof."
-- That markdown is the FROZEN SNAPSHOT of a function: each el-atlas claim is
-- `C : S → {P,F,U,V}` over the model space. Re-registering the proof tier AS
-- markdown would re-freeze it — a hand-written "proved" cell a grep can read but
-- the machine cannot enforce (the exact failure the UP-Registry rejects:
-- conformance is a COMPILED witness, not the absence of a ⊤-stub).
--
-- So the proof tier is a DEPENDENT FUNCTION. This module holds the proof-free
-- half: the claim atoms (`Claim`), each claim's substrate STATEMENT as a type
-- (`Statement : Claim → Set`), and the open FRONTIER. The witnesses — the total
-- Π `proof-tier : (c : Claim) → Statement c` — live in `.Proofs` (def/proof
-- separation: this module imports no proof closure, so def-consumers of `Claim`
-- pay nothing). Querying a claim's status will mean EVALUATING the function,
-- with the typechecker standing behind every discharge.
--
-- Vantage extension (future): the structured edition's perspective-visibility
-- tables become `visibility : (c : Claim) → Vantage → Verdict`, computed, with
-- discharged claims P-at-their-proof-vantage by construction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas where

open import Substrate.Foundation.Bool    using (Bool)
open import Substrate.Foundation.Empty   using (⊥)
open import Substrate.Foundation.Eq      using (_≡_)
open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Product using (_×_; Σ)

open import Substrate.Logic.Evidence.Verdict
  using (Evidence; Verdict; verdict; swapE; swapV; notE; _∧E_; _∨E_; negPos)
open import Substrate.Logic.Evidence.Verdict.NedgeShadow
  using (Bias; bias; recode; unrecode)
open import Substrate.Logic.Evidence.Warrant using (Warrant; _⊓w_)
-- GCX (Cayley-Dickson zero-divisor schedule): the Statement references the tower's
-- def-level vocabulary only (the witnesses live in `.Proofs`).
open import Substrate.Algebra.CayleyDickson
  using (𝕊#; ≈#; mul; zero#; Prod; mulW)
-- NOE (Noether pairings = Bézout): the conserved charge g of the Euclidean reduction
-- flow, witnessed by the Bézout momenta. Statement = the type of `bezout-ℤ`.
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Z.Bezout         using (BezoutℤWitness)

------------------------------------------------------------------------
-- The structured-edition claim atoms currently ON the substrate's Agda rung
-- (the discharged cluster — el-atlas's opening move 3 + the move-2 bridge).
------------------------------------------------------------------------

-- CRS crossbar (De Morgan intertwine) · PRO sphere prohibition (no single-rail
-- quotient) · JOI joiners (dual-rail De Morgan) · WAR provenance warrants
-- (meet-semilattice) · TWN twist/phase (H² separation [N₊,S]) · NGL G-value
-- lift (scalar bias cannot carry the 4-valued verdict) · ADJ chart adjunction
-- (lossless two-chart exp ⊣ log adjoint equivalence on the evidence carrier).
data Claim : Set where
  CRS PRO JOI WAR TWN NGL ADJ GCX NOE : Claim

------------------------------------------------------------------------
-- Each claim's substrate STATEMENT, dependent on the claim. A type per claim;
-- the proof tier produces an inhabitant. (Stated in def-level vocabulary only,
-- so this module stays proof-free; `.Proofs` supplies the witnesses and the
-- typechecker verifies each inhabits its Statement.)
------------------------------------------------------------------------

Statement : Claim → Set
Statement CRS = (e : Evidence) → verdict (swapE e) ≡ swapV (verdict e)
Statement PRO = (q : Evidence → Bool) (d : Bool → Verdict) →
                ((e : Evidence) → d (q e) ≡ verdict e) → ⊥
Statement JOI = (a b : Evidence) → notE (a ∧E b) ≡ (notE a ∨E notE b)
Statement WAR = (a b c : Warrant) → ((a ⊓w b) ⊓w c) ≡ (a ⊓w (b ⊓w c))
Statement TWN = ((x : Evidence) → negPos (swapE x) ≡ swapE (negPos x)) → ⊥
Statement NGL = (d : Bias → Verdict) →
                ((e : Evidence) → d (bias e) ≡ verdict e) → ⊥
-- ADJ: the lossless adjoint equivalence (round-trips) of the evidence carrier's
-- two charts — the structural content of exp ⊣ log, realized by `nedge-atlas`.
Statement ADJ = ((e : Evidence)     → unrecode (recode e) ≡ e)
              × ((m : Bool × Bool)  → recode (unrecode m) ≡ m)
-- GCX: the Cayley-Dickson zero-divisor schedule, el-atlas-style — there exist nonzero
-- sedenions whose product VALUE collapses to 0, yet whose kept RESIDUE (the just-prior
-- octonion sub-product, acP) is nonzero. The "wall" is a discarded residue, not nothing.
Statement GCX =
  Σ 𝕊# λ x → Σ 𝕊# λ y →
       (≈# 4 x (zero# 4) → ⊥)                              -- x ≠ 0
     × (≈# 4 y (zero# 4) → ⊥)                              -- y ≠ 0
     × ≈# 4 (mul 4 x y) (zero# 4)                          -- product value = 0 (the collapse)
     × (≈# 3 (Prod.acP (mulW 3 x y)) (zero# 3) → ⊥)        -- but the kept residue ≠ 0
-- NOE: the Noether pairing IS Bézout (user, 2026-06-13). The Euclidean reduction is the
-- symmetry flow, the gcd g is the conserved charge, and the Bézout coefficients are the
-- conserved momenta: every EEA trace yields (s,t) with s·a + t·b ≡ g. Statement = the
-- type of `bezout-ℤ`; the conservation law of the EEA flow.
Statement NOE = {a b g : ℕ} → EEATrace a b g → BezoutℤWitness a b g

------------------------------------------------------------------------
-- The FRONTIER: structured-edition claims NOT yet on the Agda rung. Names
-- only — they deliberately carry NO Statement and NO witness, so nothing here
-- can masquerade as proved. A frontier claim graduates by moving into `Claim`
-- (with its Statement); the totality of `proof-tier` then FORCES a witness or
-- the build breaks. That forcing is the point — the open set is honest, the
-- discharged set cannot lie.
------------------------------------------------------------------------

-- SWP semiring-weighted parsing (the deeper SPPF / packed multiplicity — one chart,
-- pluggable carrier semiring) · IDC identity-collapse schedule (↔ twins). IDC's
-- substrate witness is `NoCollapse.faithful-refines-verdict` (identity unseparated-in-
-- probe-space), but its ∀-over-probe-carrier form is Set₁ — it needs the rung's
-- `Statement : Claim → Set` lifted to Set₁ (or a fixed faithful carrier), a universe
-- decision deferred. (ADJ → Atlas.nedge-atlas; GCX → CayleyDickson's sedenion zero
-- divisor with kept residue; NOE → bezout-ℤ, the conserved charge of the Euclidean flow.)
data Frontier : Set where
  SWP IDC : Frontier
