{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepConvObsBisimWire — ⟡FU-sep-conv-obsbisim-wire: wire the Stream-level
-- bare × ext split (FUSepConvSharpen, ADD 118) to the REAL ObsBisim.≋ over ARS
-- carriers. The Stream was the SHAPE of ≋; this proves the SAME split holds for
-- the genuine observational bisimilarity — "the re-presentation" (same coalgebra,
-- different carrier).
--
-- THE DISSOLUTION ("is the Stream ~ a DIFFERENT equality from ObsBisim.≋, or the
-- same one re-presented?"): SAME coalgebra. ObsBisim.≋ has obs-eq (the head, BARE
-- / ℚ / intensional) + tail≋ (∀ probe, the tails — EXT / ≋ / observational). So
-- the genuine ≋ ALSO decomposes as bare × ext, with the SAME three theorems.
-- Here ExtEq is RICHER: tail≋ quantifies over EVERY probe p (a branching tree),
-- vs the Stream's single tail — the applied/observational side over all arguments.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepConvObsBisimWire where

open import Substrate.Foundation.Eq    using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
import Substrate.FUSep.ConversionCongruence as ConversionCongruence
open ConversionCongruence using (ARS)
import Substrate.FUSep.ObsBisim as ObsBisim

record _×_ (A B : Set) : Set where
  constructor _,_
  field π₁ : A ; π₂ : B
open _×_ public

-- work over an arbitrary observation coalgebra (an ARS + observation), exactly
-- ObsBisim's parameters.
module _ (R : ARS) (Obs : Set) (obs : ARS.Carrier R → Obs)
         (obs-resp : ∀ {a b} → ConversionCongruence._≈_ R a b → obs a ≡ obs b) where
  open ARS R
  -- ObsBisim's ≋ lives in an anonymous module; access via the qualified name with
  -- the params prepended, and its fields via record projection.
  _≋_ : Carrier → Carrier → Set
  a ≋ b = ObsBisim._≋_ R Obs obs obs-resp a b
  obs-eq : ∀ {a b} → a ≋ b → obs a ≡ obs b
  obs-eq r = ObsBisim._≋_.obs-eq r
  tail≋ : ∀ {a b} → a ≋ b → ∀ (p : Carrier) → (a · p) ≋ (b · p)
  tail≋ r = ObsBisim._≋_.tail≋ r

  ----------------------------------------------------------------------
  -- the two projections of the GENUINE ≋ (not the Stream stand-in):
  --   BareEq — the head observation agrees (depth-0, intensional / ℚ).
  --   ExtEq  — for EVERY probe p, the tails are ≋ (depth-1+, observational / ≋).
  ----------------------------------------------------------------------
  BareEq : Carrier → Carrier → Set
  BareEq a b = obs a ≡ obs b

  ExtEq : Carrier → Carrier → Set
  ExtEq a b = ∀ (p : Carrier) → (a · p) ≋ (b · p)

  ----------------------------------------------------------------------
  -- THEOREM 1 (the wire): the GENUINE ObsBisim.≋ DECOMPOSES as bare × ext, exactly
  -- as the Stream ~ did (ADD 118). obs-eq and tail≋ ARE the two projections.
  ----------------------------------------------------------------------
  obsplit→ : ∀ {a b} → a ≋ b → BareEq a b × ExtEq a b
  obsplit→ r = obs-eq r , tail≋ r

  obsplit← : ∀ {a b} → BareEq a b → ExtEq a b → a ≋ b
  ObsBisim._≋_.obs-eq (obsplit← ba ex)   = ba
  ObsBisim._≋_.tail≋  (obsplit← ba ex) p = ex p

  ----------------------------------------------------------------------
  -- THEOREM 3 (finite-image coincidence, the ℚ⊣R unit): where CONVERSION already
  -- holds (a ≈ b — the finite/settled image, ADD 101-102), BareEq holds (obs is a
  -- ≈-invariant, obs-resp) AND full ≋ holds (≈⟹≋) — the two equalities COINCIDE.
  -- On the finite image, bare determines ≋, exactly as ADD 118's finite-coincidence.
  ----------------------------------------------------------------------
  _≈_ : Carrier → Carrier → Set
  a ≈ b = ConversionCongruence._≈_ R a b

  finite-bare : ∀ {a b} → a ≈ b → BareEq a b
  finite-bare ab = obs-resp ab

  finite-coincidence : ∀ {a b} → a ≈ b → a ≋ b
  finite-coincidence ab = ObsBisim.≈⟹≋ R Obs obs obs-resp ab
