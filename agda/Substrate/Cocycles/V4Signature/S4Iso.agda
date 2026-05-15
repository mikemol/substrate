------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso
--
-- S10 of slice 3: the bijection TotalSpace ≃ S_4 — the catalog's
-- "the 24 ARE S_4" identification (M41 v19) made constructive.
--
-- TotalSpace of the CY-5 cocycle = Σ OrbitKey (λ _ → V_4) — pairs of
-- (orbit-key, V_4 fiber-position). Under the V_4 ⋊ S_3 ≅ S_4
-- factorisation (proved in Substrate.Groups.SemidirectProduct), each
-- such pair corresponds bijectively to a permutation in S_4.
--
-- This file establishes the bijection in full:
--
--   total-to-s4 : TotalSpace → Permutation
--     total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok
--
--   s4-to-total : Permutation → TotalSpace
--     s4-to-total σ = (stab-d-to-orbit-key (s-for σ) _ , v-for σ)
--
--   σ-round-trip      : total-to-s4 (s4-to-total σ) ≈ σ          (pointwise)
--   total-round-trip  : s4-to-total (total-to-s4 tot) ≡ tot      (propositional)
--
-- The OrbitKey ↔ Stab(D) correspondence (with the convention chosen
-- here) is:
--
--     (α-pair, even) ↔ identity     (D fixed, C fixed, S↔S, W↔W)
--     (α-pair, odd)  ↔ (SW)         (D fixed, C fixed, S↔W)
--     (β-pair, even) ↔ (CSW)        (D fixed, C→S→W→C)
--     (β-pair, odd)  ↔ (CS)         (D fixed, W fixed, C↔S)
--     (γ-pair, even) ↔ (CWS)        (D fixed, C→W→S→C)
--     (γ-pair, odd)  ↔ (CW)         (D fixed, S fixed, C↔W)
--
-- The bijection is packaged at the end as TotalSpace≃S₄-bijection
-- (a small custom record — stdlib's _↔_ requires propositional
-- equality on both sides, which Permutation lacks without funext).
--
-- See: catalog/cocycles.md § CY-5 — "The 24 ARE S_4".
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso where

open import Level using (0ℓ)
open import Data.Empty using (⊥; ⊥-elim)
open import Data.Product using (_,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; _⁻¹; ε; ≈-refl; ≈-trans; inv-l; inv-r)
  renaming (apply to applyₛ; invₐ to invₐₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; act-axis-involutive; V₄-image)
open import Substrate.Groups.SemidirectProduct
  using (Stab-D; v-of-axis; v-of-axis-unique; v-for; s-for;
         s-for-fixes-D; factorisation)
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd;
         OrbitKey;
         CY5-V4Signature)
open import Substrate.Cocycle using (IsomorphicCocycleStructure)

------------------------------------------------------------------------
-- S12 — Bijection helper lemmas.
--
-- Permutation's bijection-certificate (apply/invₐ + inv-l + inv-r)
-- gives us injectivity. Combined with Axis-constructor distinctness,
-- it rules out the 10 "impossible" (apply σ C, apply σ S) cases when
-- σ ∈ Stab(D).
------------------------------------------------------------------------

-- apply σ is injective.
σ-injective :
  (σ : Permutation) (x y : Axis) →
  applyₛ σ x ≡ applyₛ σ y → x ≡ y
σ-injective σ x y eq =
  let
    p₁ : x ≡ invₐₛ σ (applyₛ σ x)
    p₁ = sym (inv-l σ x)
    p₂ : invₐₛ σ (applyₛ σ x) ≡ invₐₛ σ (applyₛ σ y)
    p₂ = cong (invₐₛ σ) eq
    p₃ : invₐₛ σ (applyₛ σ y) ≡ y
    p₃ = inv-l σ y
  in trans p₁ (trans p₂ p₃)

-- Axis-constructor distinctness (four obvious lemmas).
C≢D : C ≡ D → ⊥
C≢D ()
S≢D : S ≡ D → ⊥
S≢D ()
W≢D : W ≡ D → ⊥
W≢D ()
C≢S : C ≡ S → ⊥
C≢S ()
C≢W : C ≡ W → ⊥
C≢W ()
S≢W : S ≡ W → ⊥
S≢W ()
S≢C : S ≡ C → ⊥
S≢C ()
W≢C : W ≡ C → ⊥
W≢C ()
W≢S : W ≡ S → ⊥
W≢S ()

------------------------------------------------------------------------
-- Builder for Stab(D) elements.
--
-- Each non-identity element of Stab(D) permutes {C, S, W} while
-- fixing D. We define each as an explicit Permutation record.
------------------------------------------------------------------------

-- Identity in Stab(D): the S_4 identity (already defined as ε).
stab-id : Permutation
stab-id = ε

-- (SW): D↔D, C↔C, S↔W. Self-inverse (involution).
stab-sw : Permutation
stab-sw = record
  { apply = ap
  ; invₐ  = ap
  ; inv-l = invo
  ; inv-r = invo
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = C
    ap S = W
    ap W = S
    invo : (x : Axis) → ap (ap x) ≡ x
    invo D = refl
    invo C = refl
    invo S = refl
    invo W = refl

-- (CS): D↔D, S↔S? — wait, (CS) swaps C and S; W is fixed.
-- D↔D, W↔W, C↔S. Self-inverse.
stab-cs : Permutation
stab-cs = record
  { apply = ap
  ; invₐ  = ap
  ; inv-l = invo
  ; inv-r = invo
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = S
    ap S = C
    ap W = W
    invo : (x : Axis) → ap (ap x) ≡ x
    invo D = refl
    invo C = refl
    invo S = refl
    invo W = refl

-- (CW): D↔D, S↔S, C↔W. Self-inverse.
stab-cw : Permutation
stab-cw = record
  { apply = ap
  ; invₐ  = ap
  ; inv-l = invo
  ; inv-r = invo
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = W
    ap S = S
    ap W = C
    invo : (x : Axis) → ap (ap x) ≡ x
    invo D = refl
    invo C = refl
    invo S = refl
    invo W = refl

-- (CSW): the 3-cycle C→S→W→C, with D fixed.
-- apply: C→S, S→W, W→C, D→D.
-- invₐ:  (CWS) = C→W, W→S, S→C, D→D.
stab-csw : Permutation
stab-csw = record
  { apply = ap
  ; invₐ  = inv-ap
  ; inv-l = il
  ; inv-r = ir
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = S
    ap S = W
    ap W = C
    inv-ap : Axis → Axis
    inv-ap D = D
    inv-ap C = W
    inv-ap S = C
    inv-ap W = S
    il : (x : Axis) → inv-ap (ap x) ≡ x
    il D = refl
    il C = refl
    il S = refl
    il W = refl
    ir : (x : Axis) → ap (inv-ap x) ≡ x
    ir D = refl
    ir C = refl
    ir S = refl
    ir W = refl

-- (CWS): the 3-cycle C→W→S→C, with D fixed. Inverse of (CSW).
stab-cws : Permutation
stab-cws = record
  { apply = ap
  ; invₐ  = inv-ap
  ; inv-l = il
  ; inv-r = ir
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = W
    ap S = C
    ap W = S
    inv-ap : Axis → Axis
    inv-ap D = D
    inv-ap C = S
    inv-ap S = W
    inv-ap W = C
    il : (x : Axis) → inv-ap (ap x) ≡ x
    il D = refl
    il C = refl
    il S = refl
    il W = refl
    ir : (x : Axis) → ap (inv-ap x) ≡ x
    ir D = refl
    ir C = refl
    ir S = refl
    ir W = refl

------------------------------------------------------------------------
-- Verification that each constructed element is in Stab(D).
------------------------------------------------------------------------

stab-id-fixes-D : Stab-D stab-id
stab-id-fixes-D = refl

stab-sw-fixes-D : Stab-D stab-sw
stab-sw-fixes-D = refl

stab-cs-fixes-D : Stab-D stab-cs
stab-cs-fixes-D = refl

stab-cw-fixes-D : Stab-D stab-cw
stab-cw-fixes-D = refl

stab-csw-fixes-D : Stab-D stab-csw
stab-csw-fixes-D = refl

stab-cws-fixes-D : Stab-D stab-cws
stab-cws-fixes-D = refl

------------------------------------------------------------------------
-- The OrbitKey → Stab(D) map.
--
-- This embodies a SPECIFIC bijection between the 6 orbit-keys and
-- the 6 elements of Stab(D). Per the catalog's isomorphic-storage
-- discipline, the choice of WHICH Stab(D) element each orbit-key
-- maps to is a CONVENTION — not a structural commitment. A future
-- session may parametrise the choice; here we encode one explicit
-- convention.
--
-- Convention: pairing-of-(D, σ(C)) determines the V_4 partition;
-- chirality is the parity of the underlying S_3 permutation.
--
--   (α, even): D & C fixed → identity
--   (α, odd):  D & C fixed, S↔W → (SW)
--   (β, even): D fixed, C→S, S→W, W→C (3-cycle, even) → (CSW)
--   (β, odd):  D & W fixed, C↔S → (CS)
--   (γ, even): D fixed, C→W, W→S, S→C (3-cycle, even) → (CWS)
--   (γ, odd):  D & S fixed, C↔W → (CW)
------------------------------------------------------------------------

orbit-key-to-stab-d : OrbitKey → Permutation
orbit-key-to-stab-d (α-pair , even) = stab-id
orbit-key-to-stab-d (α-pair , odd)  = stab-sw
orbit-key-to-stab-d (β-pair , even) = stab-csw
orbit-key-to-stab-d (β-pair , odd)  = stab-cs
orbit-key-to-stab-d (γ-pair , even) = stab-cws
orbit-key-to-stab-d (γ-pair , odd)  = stab-cw

-- Each constructed Stab(D) element fixes D (trivially).
orbit-key-to-stab-d-fixes-D :
  (ok : OrbitKey) → Stab-D (orbit-key-to-stab-d ok)
orbit-key-to-stab-d-fixes-D (α-pair , even) = stab-id-fixes-D
orbit-key-to-stab-d-fixes-D (α-pair , odd)  = stab-sw-fixes-D
orbit-key-to-stab-d-fixes-D (β-pair , even) = stab-csw-fixes-D
orbit-key-to-stab-d-fixes-D (β-pair , odd)  = stab-cs-fixes-D
orbit-key-to-stab-d-fixes-D (γ-pair , even) = stab-cws-fixes-D
orbit-key-to-stab-d-fixes-D (γ-pair , odd)  = stab-cw-fixes-D

------------------------------------------------------------------------
-- TotalSpace of the CY-5 cocycle (re-exposed from V4Signature).
--
-- TotalSpace = Σ OrbitKey (λ _ → V_4). Each element is (orbit-key,
-- V_4-fiber-position).
------------------------------------------------------------------------

TotalSpace : Set
TotalSpace = IsomorphicCocycleStructure.TotalSpace CY5-V4Signature

------------------------------------------------------------------------
-- The forward map: TotalSpace → S_4.
--
-- Constructed via the semidirect product structure: given (ok, v),
-- the permutation is (embed v) · (orbit-key-to-stab-d ok), which is
-- a V_4-element · Stab(D)-element.
------------------------------------------------------------------------

total-to-s4 : TotalSpace → Permutation
total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok

------------------------------------------------------------------------
-- S13 — stab-d-to-orbit-key: the reverse map.
--
-- Given σ ∈ Stab(D), case-analyse on (applyₛ σ C, applyₛ σ S) to
-- determine the corresponding OrbitKey. Of the 4 × 4 = 16 cases:
--   - 6 are valid (form the bijection with the 6 Stab(D) elements);
--   - 10 are impossible (ruled out via σ-injective + σ-stab + Axis
--     distinctness).
------------------------------------------------------------------------

-- Totally-defined classifier from (σ(C), σ(S)) values to OrbitKey.
-- The 6 valid cases produce the expected orbit-key; the 10 impossible
-- (σ(C) = D, σ(S) = D, σ(C) = σ(S)) cases are caught by the wildcard
-- which produces an arbitrary value never observed in valid input.
classify-CS : Axis → Axis → OrbitKey
classify-CS C S = α-pair , even
classify-CS C W = α-pair , odd
classify-CS S W = β-pair , even
classify-CS S C = β-pair , odd
classify-CS W C = γ-pair , even
classify-CS W S = γ-pair , odd
classify-CS _ _ = α-pair , even   -- impossible for σ ∈ Stab(D)

stab-d-to-orbit-key : (σ : Permutation) → Stab-D σ → OrbitKey
stab-d-to-orbit-key σ _ = classify-CS (applyₛ σ C) (applyₛ σ S)

------------------------------------------------------------------------
-- S14 — s4-to-total: the inverse map.
------------------------------------------------------------------------

s4-to-total : Permutation → IsomorphicCocycleStructure.TotalSpace CY5-V4Signature
s4-to-total σ =
  stab-d-to-orbit-key (s-for σ) (s-for-fixes-D σ) , v-for σ

------------------------------------------------------------------------
-- S15a — Round trip on the OrbitKey side.
--
-- For each ok, stab-d-to-orbit-key (orbit-key-to-stab-d ok) ≡ ok.
-- Each case reduces by computation: orbit-key-to-stab-d produces a
-- known Permutation whose apply on C and S are constants, so the
-- aux helper of stab-d-to-orbit-key selects a specific clause.
------------------------------------------------------------------------

ok-round-trip :
  (ok : OrbitKey) →
  stab-d-to-orbit-key (orbit-key-to-stab-d ok)
                      (orbit-key-to-stab-d-fixes-D ok) ≡ ok
ok-round-trip (α-pair , even) = refl
ok-round-trip (α-pair , odd)  = refl
ok-round-trip (β-pair , even) = refl
ok-round-trip (β-pair , odd)  = refl
ok-round-trip (γ-pair , even) = refl
ok-round-trip (γ-pair , odd)  = refl

------------------------------------------------------------------------
-- S15b — Round trip on the Stab(D) side.
--
-- For σ ∈ Stab(D), orbit-key-to-stab-d (stab-d-to-orbit-key σ ...) ≈ σ.
--
-- Approach: 6 per-case lemmas, one per valid (σ(C), σ(S)) config,
-- each proving σ ≈ corresponding stab-{X}. Then stab-round-trip
-- case-analyses on (applyₛ σ C, applyₛ σ S) and dispatches.
--
-- Each per-case lemma handles all 4 axes:
--   - D: from σ-stab
--   - C: from pC
--   - S: from pS
--   - W: forced by σ being a bijection (sub-case-analysis on σ(W))
------------------------------------------------------------------------

-- For (α-pair, even): σ(D)=D, σ(C)=C, σ(S)=S ⇒ σ ≈ stab-id
case-α-even :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  applyₛ σ C ≡ C → applyₛ σ S ≡ S →
  σ ≈ stab-id
case-α-even σ σ-stab pC pS D = σ-stab
case-α-even σ σ-stab pC pS C = pC
case-α-even σ σ-stab pC pS S = pS
case-α-even σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans pW (sym σ-stab))))
... | C = ⊥-elim (W≢C (σ-injective σ W C (trans pW (sym pC))))
... | S = ⊥-elim (W≢S (σ-injective σ W S (trans pW (sym pS))))
... | W = refl

-- For (α-pair, odd): σ(D)=D, σ(C)=C, σ(S)=W ⇒ σ ≈ stab-sw
case-α-odd :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  applyₛ σ C ≡ C → applyₛ σ S ≡ W →
  σ ≈ stab-sw
case-α-odd σ σ-stab pC pS D = σ-stab
case-α-odd σ σ-stab pC pS C = pC
case-α-odd σ σ-stab pC pS S = pS
case-α-odd σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans pW (sym σ-stab))))
... | C = ⊥-elim (W≢C (σ-injective σ W C (trans pW (sym pC))))
... | S = refl
... | W = ⊥-elim (S≢W (σ-injective σ S W (trans pS (sym pW))))

-- For (β-pair, odd): σ(D)=D, σ(C)=S, σ(S)=C ⇒ σ ≈ stab-cs
case-β-odd :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  applyₛ σ C ≡ S → applyₛ σ S ≡ C →
  σ ≈ stab-cs
case-β-odd σ σ-stab pC pS D = σ-stab
case-β-odd σ σ-stab pC pS C = pC
case-β-odd σ σ-stab pC pS S = pS
case-β-odd σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans pW (sym σ-stab))))
... | C = ⊥-elim (S≢W (σ-injective σ S W (trans pS (sym pW))))
... | S = ⊥-elim (C≢W (σ-injective σ C W (trans pC (sym pW))))
... | W = refl

-- For (β-pair, even): σ(D)=D, σ(C)=S, σ(S)=W ⇒ σ ≈ stab-csw
case-β-even :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  applyₛ σ C ≡ S → applyₛ σ S ≡ W →
  σ ≈ stab-csw
case-β-even σ σ-stab pC pS D = σ-stab
case-β-even σ σ-stab pC pS C = pC
case-β-even σ σ-stab pC pS S = pS
case-β-even σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans pW (sym σ-stab))))
... | C = refl
... | S = ⊥-elim (C≢W (σ-injective σ C W (trans pC (sym pW))))
... | W = ⊥-elim (S≢W (σ-injective σ S W (trans pS (sym pW))))

-- For (γ-pair, even): σ(D)=D, σ(C)=W, σ(S)=C ⇒ σ ≈ stab-cws
case-γ-even :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  applyₛ σ C ≡ W → applyₛ σ S ≡ C →
  σ ≈ stab-cws
case-γ-even σ σ-stab pC pS D = σ-stab
case-γ-even σ σ-stab pC pS C = pC
case-γ-even σ σ-stab pC pS S = pS
case-γ-even σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans pW (sym σ-stab))))
... | C = ⊥-elim (S≢W (σ-injective σ S W (trans pS (sym pW))))
... | S = refl
... | W = ⊥-elim (C≢W (σ-injective σ C W (trans pC (sym pW))))

-- For (γ-pair, odd): σ(D)=D, σ(C)=W, σ(S)=S ⇒ σ ≈ stab-cw
case-γ-odd :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  applyₛ σ C ≡ W → applyₛ σ S ≡ S →
  σ ≈ stab-cw
case-γ-odd σ σ-stab pC pS D = σ-stab
case-γ-odd σ σ-stab pC pS C = pC
case-γ-odd σ σ-stab pC pS S = pS
case-γ-odd σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans pW (sym σ-stab))))
... | C = refl
... | S = ⊥-elim (S≢W (σ-injective σ S W (trans pS (sym pW))))
... | W = ⊥-elim (C≢W (σ-injective σ C W (trans pC (sym pW))))

------------------------------------------------------------------------
-- The dispatch: case-analysing on (applyₛ σ C, applyₛ σ S) and
-- routing to the per-case lemmas (for valid cases) or absurdity
-- (for impossible cases).
------------------------------------------------------------------------

stab-round-trip :
  (σ : Permutation) (σ-stab : Stab-D σ) →
  orbit-key-to-stab-d (stab-d-to-orbit-key σ σ-stab) ≈ σ
stab-round-trip σ σ-stab z
  with applyₛ σ C in pC | applyₛ σ S in pS
... | D | _ = ⊥-elim (C≢D (σ-injective σ C D (trans pC (sym σ-stab))))
... | C | D = ⊥-elim (S≢D (σ-injective σ S D (trans pS (sym σ-stab))))
... | S | D = ⊥-elim (S≢D (σ-injective σ S D (trans pS (sym σ-stab))))
... | W | D = ⊥-elim (S≢D (σ-injective σ S D (trans pS (sym σ-stab))))
... | C | C = ⊥-elim (S≢C (σ-injective σ S C (trans pS (sym pC))))
... | C | S = sym (case-α-even σ σ-stab pC pS z)
... | C | W = sym (case-α-odd  σ σ-stab pC pS z)
... | S | C = sym (case-β-odd  σ σ-stab pC pS z)
... | S | S = ⊥-elim (C≢S (σ-injective σ C S (trans pC (sym pS))))
... | S | W = sym (case-β-even σ σ-stab pC pS z)
... | W | C = sym (case-γ-even σ σ-stab pC pS z)
... | W | S = sym (case-γ-odd  σ σ-stab pC pS z)
... | W | W = ⊥-elim (C≢S (σ-injective σ C S (trans pC (sym pS))))

------------------------------------------------------------------------
-- S15c — Round trip on the S_4 side: total-to-s4 ∘ s4-to-total ≈ id.
--
-- Reading: starting from σ ∈ S_4, split via semidirect (v-for σ, s-for σ),
-- then reassemble through total-to-s4 — we recover σ pointwise.
--
-- Computation at z:
--   total-to-s4 (s4-to-total σ)
--     = embed (v-for σ) · orbit-key-to-stab-d (stab-d-to-orbit-key (s-for σ) _)
--   applyₛ ... z = act-axis (v-for σ) (applyₛ (orbit-key-to-stab-d ...) z)
--                = act-axis (v-for σ) (applyₛ (s-for σ) z)   (stab-round-trip)
--                = act-axis (v-for σ) (act-axis (v-for σ) (applyₛ σ z))  (def s-for)
--                = applyₛ σ z                                  (involutive)
------------------------------------------------------------------------

σ-round-trip :
  (σ : Permutation) → total-to-s4 (s4-to-total σ) ≈ σ
σ-round-trip σ z =
  trans (cong (act-axis (v-for σ))
              (stab-round-trip (s-for σ) (s-for-fixes-D σ) z))
        (act-axis-involutive (v-for σ) (applyₛ σ z))

------------------------------------------------------------------------
-- S15d — Round trip on the TotalSpace side: s4-to-total ∘ total-to-s4 ≡ id.
--
-- This is propositional equality on TotalSpace = OrbitKey × V₄, since
-- both projections are decidable enumerations (no functions inside).
--
-- Decomposition: cong₂ _,_ ok-eq v-eq.
--
--   v-eq : v-for (total-to-s4 (ok, v)) ≡ v.
--     applyₛ σ D = act-axis v (applyₛ (orbit-key-to-stab-d ok) D)
--                = act-axis v D                                 (ok fixes D)
--     v-for σ = v-of-axis (applyₛ σ D) = v-of-axis (act-axis v D)
--     By v-of-axis-unique on v with refl, v ≡ v-of-axis (act-axis v D).
--
--   ok-eq : stab-d-to-orbit-key (s-for σ) _ ≡ ok.
--     applyₛ (s-for σ) z = act-axis (v-for σ) (act-axis v (...orbit-key-to-stab-d ok z))
--                        = act-axis v (act-axis v (...))         (v-eq)
--                        = applyₛ (orbit-key-to-stab-d ok) z     (involutive)
--     so classify-CS values agree, and ok-round-trip closes.
------------------------------------------------------------------------

total-round-trip :
  (tot : TotalSpace) → s4-to-total (total-to-s4 tot) ≡ tot
total-round-trip (ok , v) = cong₂ _,_ ok-eq v-eq
  where
    σ′ : Permutation
    σ′ = total-to-s4 (ok , v)

    σD : applyₛ σ′ D ≡ act-axis v D
    σD = cong (act-axis v) (orbit-key-to-stab-d-fixes-D ok)

    v-eq : v-for σ′ ≡ v
    v-eq = sym (v-of-axis-unique v (applyₛ σ′ D) (sym σD))

    s≈orb : (z : Axis) →
            applyₛ (s-for σ′) z ≡ applyₛ (orbit-key-to-stab-d ok) z
    s≈orb z =
      -- applyₛ (s-for σ′) z
      --   = act-axis (v-for σ′) (act-axis v (applyₛ (orbit-key-to-stab-d ok) z))
      --   = act-axis v (act-axis v (applyₛ (orbit-key-to-stab-d ok) z))  (v-eq)
      --   = applyₛ (orbit-key-to-stab-d ok) z                            (involutive)
      trans (cong (λ w → act-axis w (act-axis v
                          (applyₛ (orbit-key-to-stab-d ok) z))) v-eq)
            (act-axis-involutive v (applyₛ (orbit-key-to-stab-d ok) z))

    ok-eq : classify-CS (applyₛ (s-for σ′) C) (applyₛ (s-for σ′) S) ≡ ok
    ok-eq =
      trans (cong₂ classify-CS (s≈orb C) (s≈orb S))
            (ok-round-trip ok)

------------------------------------------------------------------------
-- S16 — TotalSpace ≃ S_4: the bijection packaged.
--
-- Cannot use stdlib's `_↔_` (= Inverse on propositional setoids), since
-- σ-round-trip is `_≈_` (pointwise) rather than `_≡_` (extensional —
-- would need funext for the bijection-certificate fields).
--
-- Instead, a small custom record bundling the four pieces. This is the
-- catalog's "24 ARE S_4" identification (M41 v19) made constructive:
-- the TotalSpace of CY-5 is in bijection with S_4, with the bijection's
-- to-from round trip up to pointwise equivalence and from-to up to
-- propositional equality.
------------------------------------------------------------------------

record TotalSpace≃S₄ : Set where
  field
    to       : TotalSpace → Permutation
    from     : Permutation → TotalSpace
    to-from  : (σ : Permutation) → to (from σ) ≈ σ
    from-to  : (tot : TotalSpace) → from (to tot) ≡ tot

TotalSpace≃S₄-bijection : TotalSpace≃S₄
TotalSpace≃S₄-bijection = record
  { to      = total-to-s4
  ; from    = s4-to-total
  ; to-from = σ-round-trip
  ; from-to = total-round-trip
  }
