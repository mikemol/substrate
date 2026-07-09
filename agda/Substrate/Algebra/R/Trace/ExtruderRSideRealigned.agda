{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderRSideRealigned — ⟡tower-realign-R: the FOUR
-- ad-hoc R-side modules (ObsBisim, FUSepQCyc, FUSepConvSharpen, FUSepConvObsBisimWire)
-- collapse to INSTANCES of ONE substrate cluster: RealTrace + Bisim._~_ + CycleWire.
--
-- Rosetta (ADD 123):
--   FUSepQCyc.cyc/cyc~const/selfSimilar~cyc  →  CycleWire.cycle/cycle2~twos (VERBATIM)
--   FUSepQCyc.Stream/_~_                      →  RealTrace / Bisim._~_
--   FUSepConvSharpen/Wire  bare × ext split   →  Bisim._~_'s TWO FIELDS (head~/tail~)
--   ObsBisim.≋                                →  Bisim._~_ over ana (ExtruderObsCoalg)
--
-- The four modules were the residue that made the R-side structure legible before
-- the centers were found; this is the load-bearing form. The contrast (this ~55
-- lines vs ~4×100 ad-hoc) is the regrounding measure.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderRSideRealigned where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Nat     using (ℕ)

open import Substrate.Algebra.R.Trace       using (RealTrace; head; tail; twos)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)
open import Substrate.Algebra.R.Trace.CycleWire using (cycle; cycle2; cycle2~twos)

------------------------------------------------------------------------
-- ① THE COUNIT (FUSepQCyc.cyc~const / selfSimilar~cyc): a periodic real ~ its
-- period. This IS CycleWire.cycle2~twos — cycle 2 [] ~ twos, by bisimulation.
-- The ad-hoc FUSepQCyc rebuilt cyc-go/cyc/const/cyc-loop~const/cyc~const; they
-- ARE cycle-go/cycle/twos/cyclego2~twos/cycle2~twos. One-line corollary:
------------------------------------------------------------------------
counit : cycle2 ~ twos
counit = cycle2~twos

------------------------------------------------------------------------
-- ② THE BARE × EXT SPLIT (FUSepConvSharpen Thm 1 / FUSepConvObsBisimWire): ≋
-- decomposes as bare × ext. Over the REAL Bisim._~_, this is NOT a theorem to
-- prove — head~ and tail~ ARE the two projections. The ad-hoc BareEq/ExtEq/
-- split→/split← are the record's own accessors.
------------------------------------------------------------------------
BareEq : RealTrace → RealTrace → Set
BareEq a b = head a ≡ head b            -- the ℚ / intensional projection

ExtEq : RealTrace → RealTrace → Set
ExtEq a b = tail a ~ tail b             -- the ≋ / observational projection

-- split→ / split← : ≋ = bare × ext, definitionally (head~/tail~ ARE the split).
splitBare : ∀ {a b} → a ~ b → BareEq a b
splitBare = head~
splitExt  : ∀ {a b} → a ~ b → ExtEq a b
splitExt  = tail~
splitBack : ∀ {a b} → BareEq a b → ExtEq a b → a ~ b
head~ (splitBack ba ex) = ba
tail~ (splitBack ba ex) = ex

------------------------------------------------------------------------
-- ③ FINITE-IMAGE COINCIDENCE (FUSepConvSharpen Thm 3, the ℚ⊣R unit): on the
-- settled image, bare determines ≋. For a constant real (twos), any two copies
-- coincide — bare, ext, ≋ all one. (~-refl is the settled coincidence.)
------------------------------------------------------------------------
settled-coincidence : twos ~ twos
settled-coincidence = ~-refl twos

-- and the split's two projections both hold there: bare (head 2 ≡ head 2) and
-- ext (tail twos ~ tail twos) — the equalities coincide on the finite image.
settled-bare : BareEq twos twos
settled-bare = refl
settled-ext : ExtEq twos twos
settled-ext = ~-refl (tail twos)

------------------------------------------------------------------------
-- ④ ObsBisim.≋ IS Bisim._~_ over the observation stream. The ad-hoc ObsBisim
-- built a coinductive ≋ (obs-eq + tail≋) over an ARS carrier; that IS Bisim._~_
-- pulled back along ana (the obs-coalgebra, ExtruderObsCoalg). Two terms with
-- the same obs-coalgebra behaviour have bisimilar obsStreams — which is exactly
-- Bisim._~_ on their ana images. So ObsBisim.≋ a b ≙ obsStream a ~ obsStream b.
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.ExtruderObsCoalg using (ObservedAlgebra)

-- ⟡set1-paydown: ObservedAlgebra now parameterizes its carrier C, so this module
-- threads C as a param (`ObservedAlgebra C`).
module ObsIsBisim (C : Set) (O : ObservedAlgebra C) where
  open ObservedAlgebra O

  -- the ad-hoc ObsBisim.≋ on carrier C = Bisim._~_ on the ana (obsStream) images.
  ObsBisim≋ : C → C → Set
  ObsBisim≋ a b = obsStream a ~ obsStream b

  -- its head/tail projections are Bisim's — obs-eq is head~ (via obs-head), tail≋
  -- is tail~. The ad-hoc ObsBisim's two fields ARE Bisim._~_'s two fields, pulled
  -- back along ana. (Reflexivity witnesses the shape.)
  obsbisim-refl : ∀ a → ObsBisim≋ a a
  obsbisim-refl a = ~-refl (obsStream a)
