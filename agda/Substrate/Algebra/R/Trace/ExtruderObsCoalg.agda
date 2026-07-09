{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderObsCoalg — ⟡FU-eta-obscoalg: the OBSERVATION
-- COALGEBRA of a combinator algebra, as an INSTANCE of the existing generics —
-- NOT a hand-rolled stream. The obs-stream is `Final.ana` over a `Coalg` built
-- from the algebra's observation; reduction-invariance is `ana-unique`.
--
-- This is the idiomatic (CLAUDE.md reuse-search) replacement for the hand-rolled
-- Tm/Stream/spine of the ad-hoc FUSepConvEtaWitness: the carrier is
-- ExtruderFix.CombinatorAlgebra, the trace is RealTrace, the equality is Bisim._~_,
-- the unfold is Final.ana. The η-boundary (bare-distinct / applied-equal) is then
-- expressed against the GENUINE terminal-coalgebra machinery.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderObsCoalg where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

open import Substrate.Algebra.R.Trace         using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim   using (_~_; head~; tail~; ~-refl)
open import Substrate.Algebra.R.Trace.Final   using (Coalg; ana; ana-head; ana-tail; ana-unique; out; self-unfold)
open import Substrate.Algebra.R.Trace.ExtruderFix using (CombinatorAlgebra)

------------------------------------------------------------------------
-- An OBSERVED combinator algebra: a CombinatorAlgebra with a one-step observation
-- obs : C → ℕ (the "head digit" of a term) and a NEXT map (apply a fixed probe,
-- the Gauss-map step). Together they ARE a Coalg C — the observation coalgebra.
------------------------------------------------------------------------
-- ⟡set1-paydown: parameterize the carrier C : Set out of the record (substrate
-- stance: carriers are module params, never fields). With CombinatorAlgebra now
-- carrier-parameterized (in Set), C was the only Set₁ source, so the record drops
-- from Set₁ to Set; consumers write `ObservedAlgebra C`.
module _ (C : Set) where
  record ObservedAlgebra : Set where
    field
      A     : CombinatorAlgebra C
    open CombinatorAlgebra A public
    field
      obs   : C → ℕ                 -- the bare head observation (the CF digit)
      probe : C                     -- the fixed probe (the applied step)

    -- the observation coalgebra: state c ↦ (obs c , c · probe). EXACTLY Final.Coalg.
    obsCoalg : Coalg C
    obsCoalg c = obs c , (c · probe)

    -- the OBSERVATION STREAM = ana (the unfold) — NOT a hand-rolled stream. Every
    -- combinator's behaviour is the ana of its observation coalgebra.
    obsStream : C → RealTrace
    obsStream = ana obsCoalg

    -- the coalgebra laws come FREE from Final: head = obs, tail = obsStream ∘ (·probe).
    obs-head : (c : C) → head (obsStream c) ≡ obs c
    obs-head = ana-head obsCoalg

    obs-tail : (c : C) → tail (obsStream c) ≡ obsStream (c · probe)
    obs-tail = ana-tail obsCoalg

    ----------------------------------------------------------------------
    -- REDUCTION-INVARIANCE, for free from ana-unique: if two terms have the SAME
    -- observation coalgebra behaviour (same obs, and their ·probe successors relate),
    -- their obsStreams are ~. Concretely: applied-equal terms (a·probe ≡ b·probe for
    -- all further probes) have bisimilar tails — the η tail-agreement, generically.
    --
    -- The cleanest instance: if a · probe ≡ b (a REDUCES to b under the probe), then
    -- the tail of a's stream IS b's stream (obs-tail), so a and b agree from depth 1.
    ----------------------------------------------------------------------
    tail-after-step : (a : C) → tail (obsStream a) ≡ obsStream (a · probe)
    tail-after-step = obs-tail

    -- so if a·probe and b agree observationally (b ≡ a·probe), their streams' TAILS
    -- coincide — the applied/ext side. This is the reduction-invariance the ad-hoc
    -- witness proved by hand (bmi-reduces): here it is ana's computation law.
    step-tail-agree : (a b : C) → b ≡ (a · probe)
                    → tail (obsStream a) ≡ obsStream b
    step-tail-agree a b refl = obs-tail a

------------------------------------------------------------------------
-- ⟡FU-sep-conv-eta-witness, REALIGNED as an INSTANCE (was the hand-rolled
-- Tm/spine of FUSepConvEtaWitness, ADD 121). The η-boundary over the GENUINE
-- observation coalgebra: given an ObservedAlgebra where two terms `bmi` and `m`
-- are BARE-DISTINCT (obs bmi ≢ obs m) but APPLIED-EQUAL (bmi · probe ≡ m · probe),
-- their obsStreams have DIFFERENT heads but ~ tails — η's boundary, expressed
-- against ana / RealTrace / Bisim, not a bespoke stream.
------------------------------------------------------------------------
-- ⟡set1-paydown: ObservedAlgebra now parameterizes its carrier, so this module
-- threads C as a param (`ObservedAlgebra C`).
module EtaBoundary (C : Set) (O : ObservedAlgebra C) where
  open ObservedAlgebra O

  data ⊥ : Set where

  -- the two projections on obsStreams, from the genuine coalgebra:
  --   BareEq — heads agree (the obs digit, the ℚ/intensional side).
  --   ExtEq  — tails ~ (the applied behaviour, the ≋/observational side).
  BareEq : C → C → Set
  BareEq a b = head (obsStream a) ≡ head (obsStream b)

  ExtEq : C → C → Set
  ExtEq a b = tail (obsStream a) ~ tail (obsStream b)

  -- THE η-BOUNDARY, generic: bmi and m APPLIED-EQUAL (bmi·probe ≡ m·probe) ⟹ their
  -- tails ~ (ExtEq) — the ext/≋ side, via ana's tail law. This is the ADD-121
  -- bmi-reduces tail-agreement, now = obs-tail (ana's computation law).
  -- transport ~ along the ≡ chain: tail(obsStream bmi) ≡ obsStream(bmi·probe)
  -- ≡ obsStream(m·probe) ≡ tail(obsStream m). ~-refl on the common middle, moved
  -- to the endpoints by ≡-substitution (no chained rewrite, --without-K clean).
  eta-ext : (bmi m : C) → (bmi · probe) ≡ (m · probe) → ExtEq bmi m
  eta-ext bmi m step =
    transp (λ z → z ~ tail (obsStream m)) (symOB (obs-tail bmi))
      (transp (λ z → obsStream (bmi · probe) ~ z) (symOB (obs-tail m))
        (transpL (λ z → obsStream (bmi · probe) ~ obsStream z) step
          (~-refl (obsStream (bmi · probe)))))
    where
      transp : (P : RealTrace → Set) {a b : RealTrace} → a ≡ b → P a → P b
      transp P refl pa = pa
      transpL : (P : C → Set) {a b : C} → a ≡ b → P a → P b
      transpL P refl pa = pa
      symOB : {a b : RealTrace} → a ≡ b → b ≡ a
      symOB refl = refl

  -- and BARE-DISTINCT (obs bmi ≢ obs m) ⟹ ¬ BareEq — the ℚ side. (obs is the head
  -- by obs-head, so a head-disequality is an obs-disequality.)
  eta-not-bare : (bmi m : C) → (obs bmi ≡ obs m → ⊥) → BareEq bmi m → ⊥
  eta-not-bare bmi m ne be = ne (bare→obs be)
    where -- head(obsStream ·) ≡ obs · (obs-head), so transport the head-eq to an obs-eq.
          transpN : (P : ℕ → Set) {a b : ℕ} → a ≡ b → P a → P b
          transpN P refl pa = pa
          symN : {a b : ℕ} → a ≡ b → b ≡ a
          symN refl = refl
          bare→obs : head (obsStream bmi) ≡ head (obsStream m) → obs bmi ≡ obs m
          bare→obs h =
            transpN (λ z → z ≡ obs m) (obs-head bmi)
              (transpN (λ z → head (obsStream bmi) ≡ z) (obs-head m) h)
