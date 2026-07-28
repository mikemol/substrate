{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aConfluentClassifier — ⟡x8a-wcr-discharge (honest
-- scope): package the TWO open hypotheses of the SKI extruder (fpf, WCR↦) into ONE named
-- interface — ConfluentClassifier — so the discharge is a clean explicit OBLIGATION, not
-- scattered parameters. A concrete branching SKI reduction supplies ONE such record; then the
-- non-degenerate SKI BackedUP and ski-nf-unique both fall out by feeding its fields.
--
-- WHY AN INTERFACE, NOT A DISCHARGE (grounded scope-finding, ADD 217): "discharge WCR↦ from
-- the braided diamond" rests on a SHAPE MISMATCH — FUSepQConfluence.diamond is EQUATIONAL over
-- a Span (rBack ≡ app viaP pBack), NOT a RELATIONAL WCR↦ (a↦b → a↦c → Converge b c); no bridge
-- exists; WCR↦ is nowhere discharged (open BY DESIGN); no concrete branching Reduce is exported
-- (216). A genuine discharge needs a concrete branching classifier + a diamond→WCR↦ bridge — a
-- CONSTRUCTION, not a wiring. So the honest deliverable is the OBLIGATION interface.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.X8aConfluentClassifier where
import Substrate.Foundation.RewriteConfluence

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.FUSep.FUSepQReduce using (stop; shed; Reduce; _↦_; SN; sn-confluent) renaming (Step to Step⟦c0e06c56⟧; Tm to Tm⟦533ef80d⟧)
open import Substrate.FUSep.FUSepQCR using (module Newman)

------------------------------------------------------------------------
-- THE OBLIGATION INTERFACE: what a concrete branching SKI classifier must supply so the SKI
-- extruder is non-degenerate (branching) AND its normal-form uniqueness is unconditional-
-- modulo-SN. Exactly the two hypotheses fpf + WCR↦, named as one record.
------------------------------------------------------------------------
record ConfluentClassifier : Set where
  field
    ⇒    : Reduce
    -- ① fixed-point-free: a shed genuinely changes the term (so fix? is decidable via the tag).
    fpf  : (t t' : Tm⟦533ef80d⟧) → ⇒ t ≡ shed t' → ¬ (t' ≡ t)
    -- ② local confluence of the shedding step ↦ (the braided-diamond content, in RELATIONAL
    --    form: one-step peaks converge — what sn-confluent/newman consumes).
    wcr  : let open Substrate.Foundation.RewriteConfluence (_↦_ ⇒) in {a b c : Tm⟦533ef80d⟧} → (_↦_ ⇒) a b → (_↦_ ⇒) a c → Converge b c


open ConfluentClassifier public
------------------------------------------------------------------------
-- GIVEN a ConfluentClassifier, its SKI Church-Rosser is DISCHARGED for every SN term: the wcr
-- field feeds sn-confluent directly. This is the composition the interface enables — the
-- discharge is now "supply a ConfluentClassifier", a single obligation.
------------------------------------------------------------------------
module _ (C : ConfluentClassifier) where
  open Substrate.Foundation.RewriteConfluence (_↦_ (⇒ C)) using (_⇒*_; Converge)

  -- the SKI CR for this classifier, for any SN-rooted reduction — sn-confluent fed the wcr field.
  classifier-CR : {t : Tm⟦533ef80d⟧} → SN (⇒ C) t → {b c : Tm⟦533ef80d⟧} → t ⇒* b → t ⇒* c → Converge b c
  classifier-CR snt = sn-confluent (⇒ C) (wcr C) snt

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the discharge is an OBLIGATION INTERFACE, honestly scoped):
-- the SKI extruder's two open hypotheses (fpf, WCR↦) are packaged as ONE named record,
-- ConfluentClassifier — so "discharge WCR↦" becomes the clean obligation "supply a
-- ConfluentClassifier", and classifier-CR shows sn-confluent fires the moment one is supplied.
-- The literal "discharge from the braided diamond" is a SHAPE MISMATCH (the diamond is
-- Span-equational, WCR↦ is relational; no bridge; WCR↦ open by design) — so the honest move,
-- like ADD 205, is to NAME the obligation rather than fabricate the classifier or a false
-- bridge. The either/or "discharge vs leave-scattered" dissolves into: the obligation is ONE
-- interface, the concrete branching classifier that inhabits it is a genuine CONSTRUCTION
-- (⟡x8a-branching-classifier) — the diamond→WCR↦ bridge + a real shed-branching Reduce — kept
-- as residue, not faked. The all-stop ⇒₀ (216) inhabits this trivially (fpf vacuous, wcr
-- vacuous — no ↦ steps); a branching one is the open work, now with a precise target type.
------------------------------------------------------------------------
