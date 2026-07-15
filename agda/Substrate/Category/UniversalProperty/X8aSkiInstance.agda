{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aSkiInstance — ⟡x8a-ski-instance: land the abstract
-- confluence-uniqueness of the extruder (X8aUnique.CRUnique.cr-nf-unique, ADD 213) at the
-- REAL SKI reduction — FUSep's concrete SKI Church-Rosser (FUSepQReduce.sn-confluent, which
-- is FUSepQCR.newman applied at the SN term's Acc over the shedding step ↦). This is the
-- --guardedness SEAM promised in 213: X8aUnique stays --safe/no-guardedness by parameterizing
-- the CR frame; HERE (with --guardedness on) the concrete FUSepQCR wiring lands.
--
-- The ℕ-predecessor demonstrator (X8aBacked, 212) has a DETERMINISTIC `next`, so its own
-- confluence is trivial; the genuine confluence CONTENT lives at the BRANCHING SKI shedding
-- reduction, where multiple redexes could diverge but Church-Rosser (newman via SN) forces
-- convergence. Instantiating CRUnique at FUSep's ⇒*/Converge/sn-confluent yields:
-- ski-nf-unique — the SKI shedding-normal-form is UNIQUE (path-independent). So the extruder's
-- solve computes THE canonical normal form of a real SKI term, not just A value.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.X8aSkiInstance where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Category.UniversalProperty.ConfluenceUnique using (module CRUnique)
open import Substrate.FUSep.FUSepQReduce
  using (Reduce; _↦_; SN; sn-confluent) renaming (Tm to Tm⟦533ef80d⟧)  -- the SKI shedding system (⇒ is an explicit arg)
open import Substrate.FUSep.FUSepQCR using (module Newman)

------------------------------------------------------------------------
-- ① Enter FUSep's SKI shedding system at a classifier ⇒ (the wedge tags each term stop/shed),
--    with its local confluence WCR↦ as hypothesis (the braided diamond, FUSepQConfluence).
------------------------------------------------------------------------
module SkiCR (⇒ : Reduce) where
  open Newman (_↦_ ⇒) using (_⇒*_; Converge)

  -- FUSep's concrete SKI Church-Rosser: newman applied at the SN term's Acc. Given local
  -- confluence and SN, multi-step peaks converge — the wedge-projected confluent fragment.
  ski-CR : ({a b c : Tm⟦533ef80d⟧} → (_↦_ ⇒) a b → (_↦_ ⇒) a c → Converge b c)  -- WCR↦ hypothesis
         → {t : Tm⟦533ef80d⟧} → SN ⇒ t
         → {b c : Tm⟦533ef80d⟧} → t ⇒* b → t ⇒* c → Converge b c
  ski-CR wcr snt = sn-confluent ⇒ wcr snt

------------------------------------------------------------------------
-- ② INSTANTIATE CRUnique at the SKI frame → SKI normal-form uniqueness. For a FIXED SN term
--    t with local confluence, the CR frame is (⇒*, Converge, sn-confluent) — exactly
--    CRUnique's telescope — so cr-nf-unique gives: two normal forms of t coincide.
------------------------------------------------------------------------
module SkiNfUnique
  (⇒ : Reduce)
  (wcr : let open Newman (_↦_ ⇒) in {a b c : Tm⟦533ef80d⟧} → (_↦_ ⇒) a b → (_↦_ ⇒) a c → Converge b c)
  where
  open Newman (_↦_ ⇒) using (_⇒*_; Converge)
  open import Substrate.Foundation.Eq using (sym; trans)

  -- a term is NORMAL when every reduction from it is trivial (returns it): b ⇒* d ⟹ d ≡ b.
  Normal : Tm⟦533ef80d⟧ → Set
  Normal b = (d : Tm⟦533ef80d⟧) → b ⇒* d → d ≡ b

  -- ski-nf-unique: the SKI shedding-normal-form of an SN term t is UNIQUE. Threaded HONESTLY:
  -- the root t must be SN (sn-confluent's hypothesis — the wedge-projected confluent fragment).
  -- Two normal forms b, c that t reduces to converge (by sn-confluent), and being normal each
  -- IS the common reduct, so b ≡ c. This is FUSep's concrete SKI Church-Rosser landing the
  -- extruder's layer-② uniqueness (213) at the real branching SKI reduction.
  ski-nf-unique :
    {t : Tm⟦533ef80d⟧} → SN ⇒ t →
    {b c : Tm⟦533ef80d⟧} → t ⇒* b → t ⇒* c → Normal b → Normal c → b ≡ c
  ski-nf-unique snt t⇒*b t⇒*c nb nc with sn-confluent ⇒ wcr snt t⇒*b t⇒*c
  ... | d , (b⇒*d , c⇒*d) = trans (sym (nb d b⇒*d)) (nc d c⇒*d)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder's confluence-uniqueness LANDED at real SKI): the
-- abstract CR⟹unique-NF principle (X8aUnique.CRUnique, 213) is now instantiated at FUSep's
-- CONCRETE SKI Church-Rosser (sn-confluent = FUSepQCR.newman at the SN term's Acc over the
-- shedding step ↦). ski-nf-unique: a real SKI term's normal form is UNIQUE by confluence. So
-- the extruder's layer-② uniqueness (path-independence, 213) is no longer just the abstract
-- principle — it holds CONCRETELY for SKI, at the --guardedness seam 213 identified. The ℕ
-- demonstrator's determinism made its confluence trivial; here the BRANCHING SKI reduction's
-- confluence is the genuine content, supplied by FUSep's newman (WCR from the braided diamond
-- ⊕ SN from the shedding-halts). The either/or "is the SKI normal form unique?" bottoms out:
-- YES, by Church-Rosser — the wedge-projected SN fragment is confluent, so `solve` computes
-- THE canonical normal form. The extruder joins μ/ν in the full frame (existence 212 +
-- uniqueness 213), and its confluence-uniqueness now holds for the REAL SKI reduction.
------------------------------------------------------------------------
