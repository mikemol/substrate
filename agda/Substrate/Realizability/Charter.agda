------------------------------------------------------------------------
-- Substrate.Realizability.Charter
--
-- Mechanically-checked backbone for the paper
--   "Grounding the Realizability Charter"
-- covering §4 in full and a CORRECTED, parametric §5.
--
-- DESIGN (common substructure, found recursively).  The four gates are
-- one structure — a typed cons-list of flag-gates (`Chain`, the same
-- shape as the substrate term-algebra `UPTerm`) — instantiated as nested
-- prefixes.  `⟦_⟧?` evaluates a chain to its cumulative Bool test; `Wit`
-- is the cumulative realiser (an INDUCTIVE family, so its index is
-- inferable); `sound` bridges them.  §4 is generic in the carrier `D`.
--
-- §5 PARAMETRISATION + VARIANCE FIX.  The carrier is the Boolean cube
-- `Cube n = Fin n → Bool`, generic in the arity `n`; `Distinction` is
-- `Cube 4`.  A gate is a MASK of required coordinates; it passes `d` iff
-- `mask ⊑ d` (pointwise).  The earlier draft sought a RIGHT adjoint /
-- interior operator ("largest passing sub-distinction"), which is
-- refutable at ⊥ (⊥ is always interior-closed but passes nothing).  The
-- correct structure is the DUAL: a LEFT adjoint / CLOSURE operator
-- ("smallest passing super-distinction" = declare the missing
-- resources) = join with the mask, `rmask mask d = d ∨ mask`.  This
-- closes — for EVERY gate — `closed ⟺ passes` in BOTH directions, with
-- no `Fin` decidable-equality (only two `∨`-lemmas).
--
-- DISCHARGED (refl / () / induction, ZERO postulates):
--   §4.1 Lemma 4.1 (ordering forced)        `drop`
--   §4.1 Lemma 4.2 (witness composition)    `_++ᵖ_` + thin-category laws
--   §4.1 Lemma 4.3 (determinism⇒replay)     module `Replay`
--   §4.2 Theorem 4.4 (filter soundness)     `sound` + `intersection` +
--                                           `reject`
--   §5   GateReflection (CLOSURE, generic)  `mkReflection`; the four
--                                           gates `refl-{con,rea,obs,cov}`
--                                           closed; `mask ⊑ d ⟺ gate? d`
--                                           via `·⇒mask` / `mask⇒·`.
--
-- The only residue is an ASYMMETRY, not a hole: `coverable` has a left
-- adjoint (closure to ⊤) but no right adjoint (its passer-set is {⊤}, so
-- for d ≠ ⊤ there is no coverable sub-distinction ⊑ d).  Stated in prose,
-- not proven as a universal non-existence (no negation-overclaim).
--
-- Truth ≠ validity (§1/§8): passing establishes ADMISSIBILITY, not truth.
-- Substrate Foundation only; --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Realizability.Charter where

open import Substrate.Foundation.Bool    using (Bool; true; false; _∧_; _∨_)
open import Substrate.Foundation.Eq      using (_≡_; refl; cong; trans)
open import Substrate.Foundation.Product using (_,_; _×_)
open import Substrate.Foundation.Sum     using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Fin     using (Fin; zero; suc)

------------------------------------------------------------------------
-- 0.  The atomic substructure: Bool reflection (∧ for §4, ∨ for §5).
------------------------------------------------------------------------

∧-elimˡ : ∀ {a b} → a ∧ b ≡ true → a ≡ true
∧-elimˡ {true}  p = refl
∧-elimˡ {false} ()

∧-elimʳ : ∀ {a b} → a ∧ b ≡ true → b ≡ true
∧-elimʳ {true}  p = p
∧-elimʳ {false} ()

∧-intro : ∀ {a b} → a ≡ true → b ≡ true → a ∧ b ≡ true
∧-intro {true}  pa pb = pb
∧-intro {false} () pb

∧-false→⊎ : ∀ {a b} → a ∧ b ≡ false → (a ≡ false) ⊎ (b ≡ false)
∧-false→⊎ {true}  p = inj₂ p
∧-false→⊎ {false} p = inj₁ refl

∨-elim : ∀ {a b} → a ∨ b ≡ true → (a ≡ true) ⊎ (b ≡ true)
∨-elim {true}  p = inj₁ refl
∨-elim {false} p = inj₂ p

∨-trueʳ : ∀ b → b ∨ true ≡ true
∨-trueʳ true  = refl
∨-trueʳ false = refl

------------------------------------------------------------------------
-- 1.  The common substructure (generic in the carrier D).
------------------------------------------------------------------------

module _ {D : Set} where

  data Chain : Set where
    ε   : Chain
    _▷_ : Chain → (D → Bool) → Chain
  infixl 5 _▷_

  ⟦_⟧? : Chain → D → Bool
  ⟦ ε ⟧?     d = true
  ⟦ c ▷ f ⟧? d = ⟦ c ⟧? d ∧ f d

  data Wit : Chain → D → Set where
    wε  : ∀ {d}     → Wit ε d
    w▷  : ∀ {c f d} → Wit c d → f d ≡ true → Wit (c ▷ f) d

  -- THE BRIDGE: Theorem 4.4 soundness + every per-gate soundness, once.
  sound : (c : Chain) {d : D} → ⟦ c ⟧? d ≡ true → Wit c d
  sound ε       p = wε
  sound (c ▷ f) p = w▷ (sound c (∧-elimˡ p)) (∧-elimʳ p)

  -- Lemma 4.1 (ordering forced): one peel of the cons.
  drop : ∀ {c f d} → Wit (c ▷ f) d → Wit c d
  drop (w▷ w _) = w

  -- typed rejection located at a specific flag (§3.2 / §4.4).
  data Rejected : Chain → D → Set where
    here  : ∀ {c f d} → f d ≡ false   → Rejected (c ▷ f) d
    there : ∀ {c f d} → Rejected c d  → Rejected (c ▷ f) d

  reject : (c : Chain) {d : D} → ⟦ c ⟧? d ≡ false → Rejected c d
  reject ε       ()
  reject (c ▷ f) p with ∧-false→⊎ p
  ... | inj₁ cf = there (reject c cf)
  ... | inj₂ ff = here ff

------------------------------------------------------------------------
-- 2.  The Boolean cube (generic in the arity n) — the §5 carrier.
--
-- A gate is a MASK of required coordinates; it passes d iff mask ⊑ d.
-- Its reflection (left adjoint / closure) is join-with-the-mask.
------------------------------------------------------------------------

module Cube (n : ℕ) where

  C : Set
  C = Fin n → Bool

  -- pointwise admissibility order (a Π-type ⇒ index-inferable).
  _⊑_ : C → C → Set
  d ⊑ e = (j : Fin n) → d j ≡ true → e j ≡ true
  infix 4 _⊑_

  ⊑-refl : ∀ {d} → d ⊑ d
  ⊑-refl _ p = p

  ⊑-trans : ∀ {d e f} → d ⊑ e → e ⊑ f → d ⊑ f
  ⊑-trans h k j p = k j (h j p)

  -- r₃ generalised: the closure that DECLARES the mask's coordinates.
  rmask : C → C → C
  rmask mask d j = d j ∨ mask j

  -- closure laws (extensive / monotone / idempotent), all from ∨.
  rmask-ext : (mask : C) {d : C} → d ⊑ rmask mask d
  rmask-ext mask {d} j p = cong (_∨ mask j) p

  rmask-mono : (mask : C) {d e : C} → d ⊑ e → rmask mask d ⊑ rmask mask e
  rmask-mono mask {d} {e} h j q with ∨-elim q
  ... | inj₁ dj = cong (_∨ mask j) (h j dj)
  ... | inj₂ mj = trans (cong (e j ∨_) mj) (∨-trueʳ (e j))

  rmask-idem : (mask : C) {d : C} → rmask mask (rmask mask d) ⊑ rmask mask d
  rmask-idem mask {d} j q with ∨-elim q
  ... | inj₁ r  = r
  ... | inj₂ mj = trans (cong (d j ∨_) mj) (∨-trueʳ (d j))

  -- THE COREFLECTION FIX: closed ⟺ passes, BOTH directions, every mask.
  rmask-closed→passes : (mask : C) {d : C} → rmask mask d ⊑ d → mask ⊑ d
  rmask-closed→passes mask {d} h j mj =
    h j (trans (cong (d j ∨_) mj) (∨-trueʳ (d j)))

  rmask-passes→closed : (mask : C) {d : C} → mask ⊑ d → rmask mask d ⊑ d
  rmask-passes→closed mask {d} h j q with ∨-elim q
  ... | inj₁ dj = dj
  ... | inj₂ mj = h j mj

  -- A gate's right adjoint, corrected to a left adjoint (reflection):
  -- an interior… no, a CLOSURE operator whose fixed objects are exactly
  -- the mask's passers.
  record GateReflection (mask : C) : Set where
    field
      r       : C → C
      ext     : {d : C} → d ⊑ r d
      mono    : {d e : C} → d ⊑ e → r d ⊑ r e
      idem    : {d : C} → r (r d) ⊑ r d
      closed→ : {d : C} → r d ⊑ d → mask ⊑ d
      passes→ : {d : C} → mask ⊑ d → r d ⊑ d

  -- Conjecture 5.1 (corrected variance): DISCHARGED for every gate-mask.
  mkReflection : (mask : C) → GateReflection mask
  mkReflection mask = record
    { r       = rmask mask
    ; ext     = rmask-ext mask
    ; mono    = rmask-mono mask
    ; idem    = rmask-idem mask
    ; closed→ = rmask-closed→passes mask
    ; passes→ = rmask-passes→closed mask
    }

------------------------------------------------------------------------
-- 3.  The instance: Distinction = Cube 4, with named coordinates.
------------------------------------------------------------------------

open Cube 4

Distinction : Set
Distinction = C

recipe manifest measure bounded : Distinction → Bool
recipe   d = d zero
manifest d = d (suc zero)
measure  d = d (suc (suc zero))
bounded  d = d (suc (suc (suc zero)))

-- the charter chain and its prefixes (the four named gates).
chain-con chain-rea chain-obs charter : Chain {Distinction}
chain-con = ε ▷ recipe
chain-rea = ε ▷ recipe ▷ manifest
chain-obs = ε ▷ recipe ▷ manifest ▷ measure
charter   = ε ▷ recipe ▷ manifest ▷ measure ▷ bounded

Constructible Reachable Observable Coverable Accepted : Distinction → Set
Constructible d = Wit chain-con d
Reachable     d = Wit chain-rea d
Observable    d = Wit chain-obs d
Coverable     d = Wit charter   d
Accepted        = Coverable

constructible? reachable? observable? coverable? audit? : Distinction → Bool
constructible? d = ⟦ chain-con ⟧? d
reachable?     d = ⟦ chain-rea ⟧? d
observable?    d = ⟦ chain-obs ⟧? d
coverable?     d = ⟦ charter   ⟧? d
audit?           = coverable?

------------------------------------------------------------------------
-- 4.  Lemma 4.1 (ordering is forced) — named projections (= `drop`).
------------------------------------------------------------------------

forces-cov⇒obs : ∀ {d} → Coverable d → Observable d
forces-cov⇒obs = drop

forces-obs⇒rea : ∀ {d} → Observable d → Reachable d
forces-obs⇒rea = drop

forces-rea⇒con : ∀ {d} → Reachable d → Constructible d
forces-rea⇒con = drop

forces-cov⇒con : ∀ {d} → Coverable d → Constructible d
forces-cov⇒con w = drop (drop (drop w))

------------------------------------------------------------------------
-- 5.  Theorem 4.4 (soundness as a necessary-condition filter).
------------------------------------------------------------------------

audit-sound : ∀ {d} → audit? d ≡ true → Accepted d
audit-sound = sound charter

intersection : ∀ {d} → Accepted d
             → Constructible d × Reachable d × Observable d × Coverable d
intersection w = drop (drop (drop w)) , drop (drop w) , drop w , w

intersection-conv : ∀ {d}
  → Constructible d × Reachable d × Observable d × Coverable d → Accepted d
intersection-conv (_ , _ , _ , cov) = cov

audit-reject : ∀ {d} → audit? d ≡ false → Rejected charter d
audit-reject = reject charter

reject-at-constructible : ∀ {d} → recipe   d ≡ false → Rejected charter d
reject-at-constructible ff = there (there (there (here ff)))

reject-at-reachable : ∀ {d} → manifest d ≡ false → Rejected charter d
reject-at-reachable ff = there (there (here ff))

reject-at-observable : ∀ {d} → measure  d ≡ false → Rejected charter d
reject-at-observable ff = there (here ff)

reject-at-coverable : ∀ {d} → bounded  d ≡ false → Rejected charter d
reject-at-coverable ff = here ff

------------------------------------------------------------------------
-- 6.  Worked verdicts (computed, not asserted) — §1 / §7.4 self-audit.
------------------------------------------------------------------------

good : Distinction
good _ = true

good-accepted : Accepted good
good-accepted = audit-sound refl

-- "dedup skills by semantic similarity" with NO declared equivalence
-- relation (coordinate 0 = recipe is false) — fails at CONSTRUCTIBLE.
dedup-no-eqrel : Distinction
dedup-no-eqrel zero    = false
dedup-no-eqrel (suc _) = true

dedup-rejected : Rejected charter dedup-no-eqrel
dedup-rejected = audit-reject refl

------------------------------------------------------------------------
-- 7.  Lemma 4.2 (witness composition) — the same cons-list, with audited
-- steps and ℕ boundary tags (a free category; the gate chain is the
-- one-object specialisation).
------------------------------------------------------------------------

record Step (s t : ℕ) : Set where
  constructor step
  field
    carries : Distinction
    audited : Accepted carries

data Pipe : ℕ → ℕ → Set where
  []  : ∀ {s} → Pipe s s
  _∷_ : ∀ {s m t} → Step s m → Pipe m t → Pipe s t
infixr 5 _∷_

_++ᵖ_ : ∀ {s m t} → Pipe s m → Pipe m t → Pipe s t
[]      ++ᵖ q = q
(x ∷ p) ++ᵖ q = x ∷ (p ++ᵖ q)
infixr 5 _++ᵖ_

++ᵖ-idˡ : ∀ {s t} (p : Pipe s t) → ([] ++ᵖ p) ≡ p
++ᵖ-idˡ p = refl

++ᵖ-idʳ : ∀ {s t} (p : Pipe s t) → (p ++ᵖ []) ≡ p
++ᵖ-idʳ []      = refl
++ᵖ-idʳ (x ∷ p) = cong (x ∷_) (++ᵖ-idʳ p)

++ᵖ-assoc : ∀ {s m n′ t} (p : Pipe s m) (q : Pipe m n′) (r : Pipe n′ t)
          → ((p ++ᵖ q) ++ᵖ r) ≡ (p ++ᵖ (q ++ᵖ r))
++ᵖ-assoc []      q r = refl
++ᵖ-assoc (x ∷ p) q r = cong (x ∷_) (++ᵖ-assoc p q r)

------------------------------------------------------------------------
-- 8.  Lemma 4.3 (determinism ⇒ replayability).
------------------------------------------------------------------------

data Verdict : Set where
  accept reject′ : Verdict

module Replay
  {Input Canon : Set}
  (canon  : Input → Canon)
  (decide : Canon → Verdict)
  where

  run : Input → Verdict
  run i = decide (canon i)

  replay : ∀ {i j} → canon i ≡ canon j → run i ≡ run j
  replay e = cong decide e

  replay-self : ∀ i → run i ≡ run i
  replay-self i = refl

------------------------------------------------------------------------
-- 9.  §5  The gate reflections (variance-corrected, DISCHARGED).
--
-- Each gate is a coordinate MASK; its reflection is `mkReflection mask`.
-- The connecting lemmas show `mask ⊑ d ⟺ gate? d ≡ true`, so the
-- reflection's `closed ⟺ passes` is closed/passes the ACTUAL gate.
------------------------------------------------------------------------

conMask reaMask obsMask covMask : Distinction
conMask zero          = true
conMask (suc _)       = false
reaMask zero          = true
reaMask (suc zero)    = true
reaMask (suc (suc _)) = false
obsMask zero                = true
obsMask (suc zero)          = true
obsMask (suc (suc zero))    = true
obsMask (suc (suc (suc _))) = false
covMask _ = true

-- the four reflection obligations, CLOSED (Conjecture 5.1, left-adjoint).
refl-con : GateReflection conMask
refl-con = mkReflection conMask

refl-rea : GateReflection reaMask
refl-rea = mkReflection reaMask

refl-obs : GateReflection obsMask
refl-obs = mkReflection obsMask

refl-cov : GateReflection covMask
refl-cov = mkReflection covMask

-- mask ⊑ d ⟺ gate? d ≡ true (the mask really is the gate).
con⇒mask : ∀ {d} → recipe d ≡ true → conMask ⊑ d
con⇒mask rp zero    _ = rp
con⇒mask rp (suc _) ()
mask⇒con : ∀ {d} → conMask ⊑ d → recipe d ≡ true
mask⇒con h = h zero refl

rea⇒mask : ∀ {d} → reachable? d ≡ true → reaMask ⊑ d
rea⇒mask rp zero          _ = ∧-elimˡ rp
rea⇒mask rp (suc zero)    _ = ∧-elimʳ rp
rea⇒mask rp (suc (suc _)) ()
mask⇒rea : ∀ {d} → reaMask ⊑ d → reachable? d ≡ true
mask⇒rea h = ∧-intro (h zero refl) (h (suc zero) refl)

obs⇒mask : ∀ {d} → observable? d ≡ true → obsMask ⊑ d
obs⇒mask {d} rp with sound chain-obs {d} rp
... | w▷ (w▷ (w▷ wε rc) mn) me = go
  where
    go : obsMask ⊑ d
    go zero                _ = rc
    go (suc zero)          _ = mn
    go (suc (suc zero))    _ = me
    go (suc (suc (suc _))) ()
mask⇒obs : ∀ {d} → obsMask ⊑ d → observable? d ≡ true
mask⇒obs h = ∧-intro (∧-intro (h zero refl) (h (suc zero) refl))
                     (h (suc (suc zero)) refl)

cov⇒mask : ∀ {d} → coverable? d ≡ true → covMask ⊑ d
cov⇒mask {d} rp with sound charter {d} rp
... | w▷ (w▷ (w▷ (w▷ wε rc) mn) me) bd = go
  where
    go : covMask ⊑ d
    go zero                   _ = rc
    go (suc zero)             _ = mn
    go (suc (suc zero))       _ = me
    go (suc (suc (suc zero))) _ = bd
mask⇒cov : ∀ {d} → covMask ⊑ d → coverable? d ≡ true
mask⇒cov h = ∧-intro (∧-intro (∧-intro (h zero refl) (h (suc zero) refl))
                              (h (suc (suc zero)) refl))
                     (h (suc (suc (suc zero))) refl)

-- HEADLINE: the old refuted `Conj-closed⇒observable` is now PROVED — the
-- closure's fixed objects are EXACTLY the observable passers (both ways).
obs-closed⇒passes : ∀ {d} → rmask obsMask d ⊑ d → observable? d ≡ true
obs-closed⇒passes h = mask⇒obs (rmask-closed→passes obsMask h)

obs-passes⇒closed : ∀ {d} → observable? d ≡ true → rmask obsMask d ⊑ d
obs-passes⇒closed rp = rmask-passes→closed obsMask (obs⇒mask rp)

------------------------------------------------------------------------
-- 10.  The remaining ASYMMETRY (stated, not a hole, not a negation
-- proof).  `covMask ⊑ d ⟺ d ≡ const true`, so:
--   * coverable HAS a left adjoint: the closure `rmask covMask` (refl-cov)
--     — "remediate to the smallest coverable super-distinction" = ⊤.
--   * coverable lacks a RIGHT adjoint: a right adjoint would need, for
--     each d, the largest coverable e ⊑ d; but the only coverable point
--     is ⊤, and ⊤ ⊑ d forces d ≡ ⊤, so for d ≠ ⊤ no coverable e ⊑ d
--     exists.  (Per the no-negation-overclaim discipline this is a noted
--     asymmetry, NOT a proved universal non-existence.)
------------------------------------------------------------------------
