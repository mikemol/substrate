{-# OPTIONS --safe --without-K --guardedness #-}
------------------------------------------------------------------------
-- ExtrudeCoEmitIffIso — the STRONGEST proven-equivalent: the iff ≈ᵉ→~ / ≈ᵉ←~ is not just a logical
-- equivalence but (toward) an ISO. Coinductive records are proof-relevant, so "equal proofs" means a
-- proof-bisimilarity _≈~_ on _~_ (heads agree — ℕ is a set — tails recurse). ⟡iff-iso.
------------------------------------------------------------------------
module Substrate.Category.UniversalProperty.ExtrudeCoEmitIffIso where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace using (RealTrace; head)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~)

-- proof-bisimilarity on _~_ : two bisimilarity-proofs agree if their head-equalities coincide and their
-- tail-proofs are proof-bisimilar. (head~ p, head~ q : head x ≡ head y in ℕ — a set — so they're equal.)
record _≈~_ {x y : RealTrace} (p q : x ~ y) : Set where
  coinductive
  field
    head≈~ : head~ p ≡ head~ q
    tail≈~ : tail~ p ≈~ tail~ q
open _≈~_ public

------------------------------------------------------------------------
-- The round-trip is CLEANEST on CoIO (identity encoding, 305): ≈ᶜ→~/≈ᶜ←~ are pure copattern swaps, so
-- ≈ᶜ→~ (≈ᶜ←~ q) reduces DEFINITIONALLY to q at every observation — the round-trip is ~-proof-reflexivity,
-- NO UIP needed. This is the iso for the CoIO family; the CoEmit (parity) round-trip needs ℕ-UIP (labeled).
------------------------------------------------------------------------
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream using (CoIO)
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim using (_≈ᶜ_)
open import Substrate.Category.UniversalProperty.ExtrudeCostreamViaTrace using (coio-trace; ≈ᶜ→~; ≈ᶜ←~)

-- proof-bisim reflexivity (any _~_ proof is proof-bisimilar to itself):
≈~-refl : {x y : RealTrace} (p : x ~ y) → p ≈~ p
head≈~ (≈~-refl p) = refl
tail≈~ (≈~-refl p) = ≈~-refl (tail~ p)

-- the round-trip on CoIO: ≈ᶜ→~ ∘ ≈ᶜ←~ is the identity up to proof-bisimilarity (definitional — no UIP):
iso-CoIO : {c d : CoIO ℕ} (q : coio-trace c ~ coio-trace d) → (≈ᶜ→~ (≈ᶜ←~ q)) ≈~ q
head≈~ (iso-CoIO q) = refl
tail≈~ (iso-CoIO q) = iso-CoIO (tail~ q)

------------------------------------------------------------------------
-- The CoEmit (parity) iso: unlike CoIO's identity encoding, the parity round-trip's head is NOT definitionally
-- refl — but ℕ is a SET (Hedberg: decidable equality ⇒ UIP), so ANY two head-equalities coincide. Composed
-- from Foundation.Hedberg (Decidable⇒UIP) + Foundation.Nat (_≟_). This closes ⟡iff-iso-coemit-uip.
------------------------------------------------------------------------
open import Substrate.Foundation.Nat using (_≟_)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace; ≈ᵉ→~; ≈ᵉ←~)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ using (CoEmit; _≈ᵉ_; ret; emitᶜ; step)

-- ℕ is a set: any two proofs of m ≡ n in ℕ are equal (the head component's justification).
ℕ-UIP : {m n : ℕ} (p q : m ≡ n) → p ≡ q
ℕ-UIP = Decidable⇒UIP _≟_

-- the CoEmit round-trip's HEAD obstruction is now CLOSED: ℕ-UIP (Hedberg) makes the head-equalities coincide
-- (the parity encoding isn't definitionally invertible at the head, but ℕ-set repairs it). The TAIL needs a
-- commutation lemma (≈ᵉ→~/≈ᵉ←~, being `with`-based on step c|step d, don't commute with tail~ definitionally
-- against the coinductive ≈~ target) — LABELED ⟡iff-iso-coemit-tail. Contrast CoIO (identity encoding, 308):
-- head≈~=refl AND tail commutes definitionally, so iso-CoIO is complete. The GRADE gap is the encoding's doing.
iso-CoEmit-head : {c d : CoEmit ℕ} (q : coemit-trace c ~ coemit-trace d)
                → head~ (≈ᵉ→~ (≈ᵉ←~ q)) ≡ head~ q
iso-CoEmit-head q = ℕ-UIP _ _

------------------------------------------------------------------------
-- iff-iso-coemit-stencil: the stencil's notion of iso is FRAME-GROUPOID CONNECTEDNESS (StencilGroupoid) —
-- _≈ᵉ_ and _≈ᵗ_ are connected by ≈ᵉ→~/≈ᵉ←~ in the ~-groupoid (which is refl/sym/trans, an equivalence). This
-- is the μ/ν frame: μ = the code-level agreement (head, EXACT ≡ via ℕ-UIP, iso-CoEmit-head); ν = the ~-frame
-- groupoid (the coinductive carrier, up-to). The iff (304, both directions) IS the frame-groupoid iso — no
-- proof-bisimilarity round-trip needed (that is the STRONGER definitional iso, landed for CoIO at 308).
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Bisim using (~-sym; ~-trans)

record FrameIso {c d : CoEmit ℕ} : Set where   -- the stencil iso: connected in the ~-groupoid, both directions
  field
    fwd    : c ≈ᵉ d → coemit-trace c ~ coemit-trace d
    bwd    : coemit-trace c ~ coemit-trace d → c ≈ᵉ d
open FrameIso public

coemit-frame-iso : {c d : CoEmit ℕ} → FrameIso {c} {d}
coemit-frame-iso = record { fwd = ≈ᵉ→~ ; bwd = ≈ᵉ←~ }

-- the ~-frame is a groupoid (the ν-side of the stencil): every iso invertible + composable (StencilGroupoid ①).
frame-iso-sym   : {c d : CoEmit ℕ} → coemit-trace c ~ coemit-trace d → coemit-trace d ~ coemit-trace c
frame-iso-sym   = ~-sym
frame-iso-trans : {c d e : CoEmit ℕ} → coemit-trace c ~ coemit-trace d → coemit-trace d ~ coemit-trace e → coemit-trace c ~ coemit-trace e
frame-iso-trans = ~-trans

------------------------------------------------------------------------
-- coemit-trace-mu-nu: the CoEmit iso presented as a TwoFraming (the stencil's μ/ν record). μ-frame = the
-- code-level EXACT ≡ (head, via ℕ-UIP — on the nose, both directions); ν-frame = the ~-carrier groupoid (the
-- coinductive up-to, via the frame iso + ~-groupoid). The ≡/~ asymmetry is structural: μ is exact, ν is up-to.
------------------------------------------------------------------------

record CoEmitTwoFraming {c d : CoEmit ℕ} : Set where
  field
    -- μ-frame (finite/exact, ≡): the head codes agree on the nose (the parity coherence's exact core).
    μ-head-fwd : (p : c ≈ᵉ d) → head (coemit-trace c) ≡ head (coemit-trace d)
    -- ν-frame (coinductive/up-to, ~): the carrier agreement via the frame iso (both directions = the ~-groupoid iso).
    ν-fwd      : c ≈ᵉ d → coemit-trace c ~ coemit-trace d
    ν-bwd      : coemit-trace c ~ coemit-trace d → c ≈ᵉ d
open CoEmitTwoFraming public

coemit-two-framing : {c d : CoEmit ℕ} → CoEmitTwoFraming {c} {d}
coemit-two-framing = record
  { μ-head-fwd = λ p → head~ (≈ᵉ→~ p)   -- μ: exact head agreement (≡)
  ; ν-fwd      = ≈ᵉ→~                     -- ν: the coinductive carrier iso, forward
  ; ν-bwd      = ≈ᵉ←~                     -- ν: and backward (the ~-groupoid, up-to)
  }

------------------------------------------------------------------------
-- cover-the-cycle (the THIRD grading dimension, operator): a round-trip is a CYCLE; cover it → a POINT. The
-- ret/constant-stream is a PERIOD-1 cycle (next c (ret a) = c → coemit-trace c loops), FINITELY-GENERATED by
-- ONE point. So its round-trip ≈~ is GENERATED by the head (the point, via ℕ-UIP) and LIFTED self-similarly by
-- the cycle — it BOTTOMS OUT (the cover is the point, not a fresh obstruction each step). CofreeDual: the ~-cofree
-- obstruction shrinks to the NON-finitely-generated (aperiodic) tail; the periodic part collapses to ≡ (order-collapse).
------------------------------------------------------------------------
-- THE COVER, correctly typed: for ℕ-headed traces, ANY two ~-proofs of the same endpoints are ≈~ — the head
-- is ≡ (ℕ-UIP, the point), the tail recurses (the cover lifts self-similarly). This is the general statement
-- that _~_ is a PROP up to ≈~ for ℕ-streams (Hedberg at each head + coinduction) — the cover-the-cycle made
-- total: every ~-proof is ≈~-unique, so ANY round-trip ≈~ id (⟡iff-iso-coemit-tail discharged via the cover).
~-prop : {x y : RealTrace} (p q : x ~ y) → p ≈~ q
head≈~ (~-prop p q) = ℕ-UIP _ _
tail≈~ (~-prop p q) = ~-prop (tail~ p) (tail~ q)

------------------------------------------------------------------------
-- iff-iso-coemit-tail DISCHARGED via the cover: the CoEmit round-trip ≈ᵉ→~ (≈ᵉ←~ q) ≈~ q is now IMMEDIATE from
-- ~-prop (any two ~-proofs are ≈~). My cyclic re-casing was proving a SPECIFIC round-trip; the cover-the-cycle
-- shows ~ is a PROP up to ≈~, so EVERY round-trip is ≈~ id — no map-commutation needed. The CoEmit proof-iso
-- reaches the SAME grade as CoIO (308), via the point (ℕ-UIP) + the cover (coinduction), not definitional invertibility.
------------------------------------------------------------------------
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using () renaming (≈ᵉ→~ to E→; ≈ᵉ←~ to E←)

iso-CoEmit-tail : {c d : CoEmit ℕ} (q : coemit-trace c ~ coemit-trace d) → (E→ (E← q)) ≈~ q
iso-CoEmit-tail q = ~-prop (E→ (E← q)) q
