------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.Proofs
--
-- THE proof tier of el-atlas's structured edition — as a Π.
--
-- `proof-tier : (c : Claim) → Statement c` is a TOTAL dependent function. It
-- compiles iff EVERY claim in `Claim` is discharged by a real witness: there is
-- no escape constructor, so a claim cannot sit in the domain undischarged. This
-- is the el-atlas structured edition's reserved "Agda rung" filled — not a
-- markdown cell asserting "proved", but a compiled function the typechecker
-- stands behind. Adding a claim to `Claim`/`Statement` forces a new witness here
-- or the build breaks (the forcing function the prose ledger lacked).
--
-- Each witness is the real theorem from the evidence tier — the SAME proof, now
-- indexed by its el-atlas claim id:
--   CRS = Verdict.Properties.intertwine            (the crossbar)
--   PRO = NoCollapse.no-single-rail-quotient       (the prohibition)
--   JOI = Verdict.Properties.deMorgan-∧∨           (the joiners' De Morgan)
--   WAR = Warrant.Properties.⊓w-assoc              (the warrant semilattice)
--   TWN = Phase.N₊-S-noncommute                    (the H² separation)
--   NGL = NedgeShadow.bias-cannot-carry-verdict    (the G-value lift)
--
-- Separated from the def module (`ElAtlas`) per the def/proof policy: that
-- module's `Claim`/`Statement` closure stays proof-free; the `.Properties`
-- imports are confined here.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.Proofs where

open import Substrate.Foundation.Eq      using (_≡_; cong)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Logic.Evidence.Verdict using (Evidence; verdict; swapE; swapV)
open import Substrate.Logic.Evidence.ElAtlas
  using (Claim; CRS; PRO; JOI; WAR; TWN; NGL; ADJ; GCX; NOE; IDC; SWP; Statement)
open import Substrate.Logic.Evidence.Atlas using (nedge-atlas; exp-log; log-exp)
open import Substrate.Algebra.CayleyDickson
  using (xZD; yZD; xZD≢0; yZD≢0; zd-value-0; zd-residue-nonzero)
open import Substrate.Algebra.Z.Bezout using (bezout-ℤ)
open import Substrate.Logic.Evidence.SWP using (posR-section)

open import Substrate.Logic.Evidence.Verdict.Properties  using (intertwine; deMorgan-∧∨)
open import Substrate.Logic.Evidence.Verdict.NoCollapse  using (no-single-rail-quotient; faithful-refines-verdict)
open import Substrate.Logic.Evidence.Verdict.NedgeShadow using (bias-cannot-carry-verdict; recode; unrecode)
open import Substrate.Logic.Evidence.Verdict.Phase       using (N₊-S-noncommute)
open import Substrate.Logic.Evidence.Warrant.Properties  using (⊓w-assoc)

------------------------------------------------------------------------
-- The Π. Total over `Claim`; every case is a typechecked witness.
------------------------------------------------------------------------

proof-tier : (c : Claim) → Statement c
proof-tier CRS = intertwine
proof-tier PRO = no-single-rail-quotient
proof-tier JOI = deMorgan-∧∨
proof-tier WAR = ⊓w-assoc
proof-tier TWN = N₊-S-noncommute
proof-tier NGL = bias-cannot-carry-verdict
proof-tier ADJ = log-exp nedge-atlas , exp-log nedge-atlas
proof-tier GCX = xZD , yZD , xZD≢0 , yZD≢0 , zd-value-0 , zd-residue-nonzero
proof-tier NOE = bezout-ℤ
-- IDC: the recode codec is faithful-for-verdict — collapsing under recode forces verdict
-- agreement. Decoder = verdict ∘ unrecode; its obligation is the ADJ round-trip.
proof-tier IDC = faithful-refines-verdict recode (λ m → verdict (unrecode m))
                                          (λ e → cong verdict (log-exp nedge-atlas e))
proof-tier SWP = λ add mul oneℕ v t → posR-section add mul oneℕ v t

------------------------------------------------------------------------
-- Using the registry: extract a registered claim's proof by EVALUATING the Π.
-- A markdown row cannot hand you a proof; this does — the proof tier is live.
------------------------------------------------------------------------

crossbar : (e : Evidence) → verdict (swapE e) ≡ swapV (verdict e)
crossbar = proof-tier CRS
