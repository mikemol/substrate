{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQReduce — ⟡FU-sep-Q-reduce: full SKI reduction, where SN FAILS globally
-- (Ω = SII(SII) diverges). The wedge PROJECTS the missing piece; the split is the
-- TARSKI/fixed-point pattern the system applies to all continued fractions, and
-- extracting the residue is ONE EEA STEP (operator).
--
-- THE ANSWER (operator + ⟡H0-read ResidueAtom / Trace.Residues): reduction is
-- RESIDUE-SHEDDING (EEA). Each step sheds a residue, tagged PROVE-OR-CORRECT:
--   residue = z (the unit / base)  → STOP: a value/nf reached (the gcd) — CLEAN.
--   residue ≢ z                    → a FIXED-POINT-FREE correction → RECURSE.
-- "The residue refuses to vanish — which is exactly why the prove-or-correct
-- engine never dead-ends." So the SN-vs-Diverges dichotomy is the LEAST vs
-- GREATEST fixed point of the residue-shedding functor (Tarski):
--   SN       = LEAST fixed point (inductive): shedding TERMINATES (residue → z),
--              the finite CF / rational / ℚ side — Newman/CR applies (ADD 109).
--   Diverges = GREATEST fixed point (coinductive): shedding is PRODUCTIVE-forever,
--              the infinite CF / irrational / R side — bisimilarity (ADD 100).
-- The boundary is NOT "undecidable unresolved residue" — the prove-or-correct tag
-- is decidable PER STEP (z or not); the WHOLE-term SN is whether the shedding
-- reaches base, which is exactly the least ⊆ greatest containment (the halting
-- boundary as a fixed-point structure, not a gap). The wedge extraction at each
-- step IS the single EEA step.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQReduce where

open import Substrate.Foundation.Eq using (_≡_; refl)

data Tm : Set where      -- ⟦shape:533ef80d atom,app⟧
  atom : Tm
  app  : Tm → Tm → Tm

-- one reduction step (abstract carrier of the residue-shedding), with the
-- prove-or-correct TAG: a step either STOPS (value, clean, residue = z) or SHEDS
-- a residue and CONTINUES to a successor. This is Trace.Residues' done | more.
data Step (t : Tm) : Set where      -- ⟦shape:c0e06c56 stop,shed⟧
  stop : Step t                        -- residue = z: a value/nf (the gcd, base)
  shed : (t' : Tm) → Step t            -- residue ≢ z: a fixed-point-free correction

-- the reduction system: a classifier (the wedge) tags each term.
Reduce : Set
Reduce = (t : Tm) → Step t

module _ (⇒ : Reduce) where

  -- the forward step relation extracted from the classifier.
  data _↦_ : Tm → Tm → Set where
    mk : ∀ {t t'} → ⇒ t ≡ shed t' → t ↦ t'

  ----------------------------------------------------------------------
  -- SN = the LEAST fixed point (inductive Acc): the shedding TERMINATES — every
  -- ↦-path reaches `stop` (a value). Finite CF / rational / ℚ side.
  ----------------------------------------------------------------------
  data SN (t : Tm) : Set where
    sn : (∀ t' → t ↦ t' → SN t') → SN t

  ----------------------------------------------------------------------
  -- Diverges = the GREATEST fixed point (coinductive): the shedding is
  -- PRODUCTIVE forever — always another residue to shed, never `stop`. Infinite
  -- CF / irrational / R side. THIS is the residue the wedge projects out.
  ----------------------------------------------------------------------
  record Diverges (t : Tm) : Set where
    coinductive
    field
      next   : Tm
      steps  : t ↦ next
      onward : Diverges next
  open Diverges public

  ----------------------------------------------------------------------
  -- THE PROVE-OR-CORRECT DICHOTOMY at ONE step (the single EEA step, decidable):
  -- a term either STOPS (value — contributes to the SN least-fixed-point) or
  -- SHEDS (a correction — recurse; may reach base (SN) or never (Diverges)).
  -- This is the wedge tag, decidable per step; whole-term SN/Diverges is the
  -- least/greatest closure of it (Tarski) — the halting boundary as structure.
  ----------------------------------------------------------------------
  data Tag : Set where cleanStop : Tag ; correct : Tag

  classify : (t : Tm) → Tag
  classify t with ⇒ t
  ... | stop    = cleanStop      -- residue z: the gcd/base — STOP
  ... | shed _  = correct        -- residue ≢ z: fixed-point-free correction

  -- the tag is FAITHFUL: cleanStop ⟺ the term is a value (⇒ t ≡ stop). One EEA
  -- step never dead-ends — it either stops clean or hands back a correction.
  tag-stops : (t : Tm) → ⇒ t ≡ stop → classify t ≡ cleanStop
  tag-stops t eq with ⇒ t
  ... | stop   = refl
  tag-corrects : ∀ (t t' : Tm) → ⇒ t ≡ shed t' → classify t ≡ correct
  tag-corrects t t' eq with ⇒ t
  ... | shed _ = refl

  ----------------------------------------------------------------------
  -- THE TARSKI BOUNDARY: least (SN) ⊆ greatest — an SN term is NOT Diverges.
  -- If the shedding terminates (SN), it cannot also be productive-forever
  -- (Diverges): the two fixed points are DISJOINT, and their boundary is the
  -- halting line. Proof: induct on the SN witness; Diverges hands a step, SN's
  -- IH applies to the successor, but Diverges is inherited — contradiction bottoms
  -- out when SN reaches a value with no ↦-successor. This is least ⊆ greatest made
  -- into DISJOINTNESS (the CF terminates XOR runs forever — rational XOR irrational).
  ----------------------------------------------------------------------
  data ⊥ : Set where

  sn-not-diverges : ∀ {t} → SN t → Diverges t → ⊥
  sn-not-diverges (sn f) d = sn-not-diverges (f (next d) (steps d)) (onward d)

  ----------------------------------------------------------------------
  -- WIRING SN INTO NEWMAN (ADD 109): SN t is exactly the Acc on the forward step
  -- ↦ that FUSepQCR.Newman.SN needs. So the ℚ (SN) side feeds church-rosser: with
  -- local confluence (WCR, the braided diamond ADD 107), SN terms are CONFLUENT.
  -- The wedge has PROJECTED the confluent fragment; the residue (Diverges) is
  -- handed to bisimilarity (ADD 100) — the R side where SN fails and Newman cannot
  -- reach, exactly as the ℚ⊣R = SN boundary (ADD 109 insight).
  ----------------------------------------------------------------------
  open import Substrate.FUSep.FUSepQCR using (module Newman)
  open Newman _↦_ using () renaming (SN to SN-Acc; WCR to WCR↦; CR to CR↦; newman to newman↦)

  -- SN (this module's least-fixed-point) coincides with Newman's Acc-SN.
  SN⟹Acc : ∀ {t} → SN t → SN-Acc t
  SN⟹Acc {t} (sn f) = acc′ (λ t' t'↦t → SN⟹Acc (f t' t'↦t))
    where open import Substrate.Foundation.WellFounded renaming (acc to acc′)

  -- THE ℚ-SIDE CONFLUENCE, assembled: given local confluence, every SN term is
  -- Church-Rosser (newman↦ applied at the SN term's Acc) — the wedge-projected
  -- confluent fragment. This is the REAL wire: SN feeds Newman, out comes CR.
  open Newman _↦_ using (_⇒*_; Converge)
  sn-confluent : WCR↦ → ∀ {t} → SN t → ∀ {b c} → t ⇒* b → t ⇒* c → Converge b c
  sn-confluent wcr snt = newman↦ wcr (SN⟹Acc snt)
