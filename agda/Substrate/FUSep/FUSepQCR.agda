{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQCR — ⟡FU-sep-Q-CR: the CAPSTONE. Newman's lemma — a TERMINATING and
-- LOCALLY-CONFLUENT rewrite system is CONFLUENT (Church-Rosser). Assembles the
-- three tower ingredients:
--   • TERMINATION  — Acc on the reduction step (halts→trace's driver, ADD 104).
--   • LOCAL DIAMOND — one-step peaks converge (the braided diamond, ADD 107).
--   • (the functorial/hexagon coherence, ADD 108, is what makes the local
--      diamonds TILE — it is why the induction below closes.)
--
-- ⟡H0 (EXHAUSTIVE search): the substrate has Acc + WellFounded but NO Newman, NO
-- Church-Rosser, NO reflexive-transitive closure, NO wf-recursor — a GENUINE gap
-- (not a re-derivation). So I build it honestly on Acc, consuming it by hand-
-- recursion exactly as compute-trace-acc does (ADD 104). Abstract over the step
-- `_⇒_` and its carrier, so the concrete SKI system slots in.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQCR where

open import Substrate.Foundation.Eq          using (_≡_; refl)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.Foundation.Product     using (Σ; _,_) renaming (proj₁ to fst; proj₂ to snd)

module Newman
  {Tm : Set}
  (_⇒_ : Tm → Tm → Set)                              -- the one-step reduction
  where

  -- reflexive-transitive closure: the multi-step reduction ⇒* (the SPPF path).
  data _⇒*_ : Tm → Tm → Set where
    done : ∀ {a}          → a ⇒* a
    _◅_  : ∀ {a b c} → a ⇒ b → b ⇒* c → a ⇒* c

  -- compose multi-step reductions (path concatenation).
  _++*_ : ∀ {a b c} → a ⇒* b → b ⇒* c → a ⇒* c
  done      ++* q = q
  (r ◅ rs)  ++* q = r ◅ (rs ++* q)

  -- a peak a⇒*b, a⇒*c CONVERGES: ∃ d with b⇒*d and c⇒*d (joinability).
  Converge : Tm → Tm → Set
  Converge b c = Σ Tm (λ d → (b ⇒* d) × (c ⇒* d))
    where _×_ : Set → Set → Set
          A × B = Σ A (λ _ → B)

  -- WEAK (local) confluence: one-step peaks converge. (The braided diamond, ADD 107.)
  WCR : Set
  WCR = ∀ {a b c} → a ⇒ b → a ⇒ c → Converge b c

  -- CONFLUENCE (Church-Rosser): multi-step peaks converge.
  CR : Set
  CR = ∀ {a b c} → a ⇒* b → a ⇒* c → Converge b c

  _×_ : Set → Set → Set
  A × B = Σ A (λ _ → B)

  -- reverse well-foundedness: Acc on the FORWARD step ⇒ (a is accessible when all
  -- its ⇒-successors are — this is termination/strong-normalization).
  SN : Tm → Set
  SN = Acc (λ x y → y ⇒ x)      -- x accessible below y iff y ⇒ x (forward step)

  ------------------------------------------------------------------
  -- NEWMAN'S LEMMA: WCR + SN ⟹ CR, by well-founded induction on the peak apex.
  -- The classic diamond-tiling proof: split each multistep into first-step +
  -- rest; local-confluence the two first steps; recurse (IH at the strictly-
  -- smaller successors) to close. This is where the local diamonds TILE (ADD 108
  -- coherence is the semantic content of the tiling closing).
  ------------------------------------------------------------------
  newman : WCR → ∀ {a} → SN a → ∀ {b c} → a ⇒* b → a ⇒* c → Converge b c
  newman wcr accA done              a⇒*c = _ , (a⇒*c , done)
  newman wcr accA (a⇒b ◅ b⇒*b')     done = _ , (done , (a⇒b ◅ b⇒*b'))
  newman wcr (acc rec) (_◅_ {b = b} a⇒b b⇒*x) (_◅_ {b = c} a⇒c c⇒*y) =
    -- local confluence on the two first steps a⇒b, a⇒c: common e.
    let e   = fst (wcr a⇒b a⇒c)
        b⇒*e = fst (snd (wcr a⇒b a⇒c))
        c⇒*e = snd (snd (wcr a⇒b a⇒c))
        -- IH at b (b < a via a⇒b): join x (from b⇒*x) and e (from b⇒*e).
        accB = rec b a⇒b
        jx  = newman wcr accB b⇒*x b⇒*e
        d₁  = fst jx
        x⇒*d₁ = fst (snd jx)
        e⇒*d₁ = snd (snd jx)
        -- IH at c (c < a via a⇒c): join (c⇒*e then e⇒*d₁) with c⇒*y.
        accC = rec c a⇒c
        jy  = newman wcr accC (c⇒*e ++* e⇒*d₁) c⇒*y
        d₂  = fst jy
        d₁⇒*d₂ = fst (snd jy)
        y⇒*d₂  = snd (snd jy)
    in d₂ , ((x⇒*d₁ ++* d₁⇒*d₂) , y⇒*d₂)
