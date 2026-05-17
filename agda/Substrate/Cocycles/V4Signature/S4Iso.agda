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
open import Data.Product using (_,_; proj₁; proj₂; Σ; Σ-syntax)
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
  using (Stab-D; Stab-C; Stab-S; Stab-W;
         v-of-axis; v-of-axis-unique; v-for; s-for;
         s-for-fixes-D; factorisation)
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd;
         OrbitKey;
         CY5-V4Signature)
open import Substrate.Cocycle using (IsomorphicCocycleStructure)
open import Data.Fin using (Fin; zero; suc)
open import Substrate.Groups.Stab-S3 using (Stab; fin3-to-non-anchor)
open import Substrate.Groups.Stab-S3-Extend
  using (extend; extend-apply-pointwise-cong)
open import Substrate.Groups.Stab-S3-Restrict using (restrict)
open import Substrate.Groups.Stab-S3-Iso using (extend-restrict)
import Substrate.Groups.SFin as SFin
open import Substrate.Cocycles.V4Signature.OrbitKey-S3
  using (transposition; transposition-fixes-third; orbit-key-to-s3;
         s3-id; s3-csw; s3-cws;
         s3-to-orbit-key; orbit-key-to-s3-of-s3-to-orbit-key)

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

-- Identity in Stab(D): now also expressed as extend D of the SFin
-- identity (s3-id = SFin.ε), uniform with the other 5 stab-X. This
-- makes every stab-X a `proj₁ (extend D <SFin element>)` and lets
-- orbit-key-to-stab-d delegate to orbit-key-to-stab-anchor D
-- definitionally: each clause of the OLD orbit-key-to-stab-d body
-- becomes `proj₁ (extend D (orbit-key-to-s3 ok))` already.
stab-id : Permutation
stab-id = proj₁ (extend D s3-id)

-- (SW): D↔D, C↔C, S↔W. Self-inverse.
-- Expressed as extend D of the Fin-3 transposition swapping (1, 2),
-- which corresponds to S↔W under the D-anchor convention 0↔C, 1↔S, 2↔W.
stab-sw : Permutation
stab-sw = proj₁ (extend D (transposition (suc zero) (suc (suc zero))))

-- (CS): D↔D, W↔W, C↔S. Self-inverse.
-- Fin-3 transposition (0, 1) = C↔S under D-anchor convention.
stab-cs : Permutation
stab-cs = proj₁ (extend D (transposition zero (suc zero)))

-- (CW): D↔D, S↔S, C↔W. Self-inverse.
-- Fin-3 transposition (0, 2) = C↔W under D-anchor convention.
stab-cw : Permutation
stab-cw = proj₁ (extend D (transposition zero (suc (suc zero))))

-- (CSW): the 3-cycle C→S→W→C, with D fixed.
-- Constructed parametrically: extend D applied to the (0 1 2) 3-cycle
-- in SFin.Permutation 3. Uniform with stab-{sw,cs,cw} (all four are
-- now `proj₁ (extend D (some s3 element))`); the level-0 stab-X
-- family is parametric over the SFin generator.
stab-csw : Permutation
stab-csw = proj₁ (extend D s3-csw)

-- (CWS): the 3-cycle C→W→S→C, with D fixed. Inverse of (CSW),
-- parametrically constructed via the same template.
stab-cws : Permutation
stab-cws = proj₁ (extend D s3-cws)

------------------------------------------------------------------------
-- Verification that each constructed element is in Stab(D).
------------------------------------------------------------------------

stab-id-fixes-D : Stab-D stab-id
stab-id-fixes-D = refl

-- stab-id is the S₄ identity; fixes every axis.
stab-id-fixes-C : Stab-C stab-id
stab-id-fixes-C = refl

stab-id-fixes-S : Stab-S stab-id
stab-id-fixes-S = refl

stab-id-fixes-W : Stab-W stab-id
stab-id-fixes-W = refl

stab-sw-fixes-D : Stab-D stab-sw
stab-sw-fixes-D = refl

-- stab-sw swaps S↔W (Fin-3 swap 1↔2); fixes C (Fin-3 index 0) by
-- transposition-fixes-third. Structural relationship visible:
-- transposition (1, 2) fixes index 0, lifted by extend-D to C.
stab-sw-fixes-C : Stab-C stab-sw
stab-sw-fixes-C = cong (fin3-to-non-anchor D) (transposition-fixes-third (suc zero) (suc (suc zero)) zero (λ ()) (λ ()))

stab-cs-fixes-D : Stab-D stab-cs
stab-cs-fixes-D = refl

-- stab-cs swaps C↔S (Fin-3 swap 0↔1); fixes W (index 2).
stab-cs-fixes-W : Stab-W stab-cs
stab-cs-fixes-W = cong (fin3-to-non-anchor D) (transposition-fixes-third zero (suc zero) (suc (suc zero)) (λ ()) (λ ()))

stab-cw-fixes-D : Stab-D stab-cw
stab-cw-fixes-D = refl

-- stab-cw swaps C↔W (Fin-3 swap 0↔2); fixes S (index 1).
stab-cw-fixes-S : Stab-S stab-cw
stab-cw-fixes-S = cong (fin3-to-non-anchor D) (transposition-fixes-third zero (suc (suc zero)) (suc zero) (λ ()) (λ ()))

-- stab-csw, stab-cws are 3-cycles; fix only D.
-- No -C, -S, or -W siblings to add (those propositions are false).
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

------------------------------------------------------------------------
-- Parametric anchor dispatcher (and its fixes proof). One template,
-- four anchor specialisations below. All four (including the cocycle's
-- chirality-choice anchor `-d`) delegate to the same parametric form;
-- the chirality choice lives in `orbit-key-to-s3`'s OrbitKey→s3
-- mapping (not in this per-anchor dispatcher).
--
-- The specialised C/S/W siblings are uppercase by convention; `-d` is
-- lowercase to mark the cocycle anchor under the use-vs-commit
-- convention (CY-5 USES D as anchor without committing to it).
------------------------------------------------------------------------

orbit-key-to-stab-anchor : (X : Axis) → OrbitKey → Permutation
orbit-key-to-stab-anchor X ok = proj₁ (extend X (orbit-key-to-s3 ok))

orbit-key-to-stab-anchor-fixes :
  (X : Axis) (ok : OrbitKey) → Stab X (orbit-key-to-stab-anchor X ok)
orbit-key-to-stab-anchor-fixes X ok = proj₂ (extend X (orbit-key-to-s3 ok))

-- D-anchor specialisation: delegates to orbit-key-to-stab-anchor D.
-- This is now definitionally valid because EVERY stab-X is parametric
-- (`proj₁ (extend D <s3-X>)`) and the orbit-key-to-s3 mapping picks
-- the matching s3-X for each ok. The 6 OLD clauses each reduced to
-- `proj₁ (extend D (orbit-key-to-s3 ok))` already — they were just
-- writing it out by hand.
--
-- The cocycle's chirality choice lives in orbit-key-to-s3's
-- OrbitKey→s3 mapping — that IS the chirality.
orbit-key-to-stab-d : OrbitKey → Permutation
orbit-key-to-stab-d = orbit-key-to-stab-anchor D

orbit-key-to-stab-d-fixes-D :
  (ok : OrbitKey) → Stab-D (orbit-key-to-stab-d ok)
orbit-key-to-stab-d-fixes-D = orbit-key-to-stab-anchor-fixes D

orbit-key-to-stab-C : OrbitKey → Permutation
orbit-key-to-stab-C = orbit-key-to-stab-anchor C

orbit-key-to-stab-C-fixes-C :
  (ok : OrbitKey) → Stab-C (orbit-key-to-stab-C ok)
orbit-key-to-stab-C-fixes-C = orbit-key-to-stab-anchor-fixes C

orbit-key-to-stab-S : OrbitKey → Permutation
orbit-key-to-stab-S = orbit-key-to-stab-anchor S

orbit-key-to-stab-S-fixes-S :
  (ok : OrbitKey) → Stab-S (orbit-key-to-stab-S ok)
orbit-key-to-stab-S-fixes-S = orbit-key-to-stab-anchor-fixes S

orbit-key-to-stab-W : OrbitKey → Permutation
orbit-key-to-stab-W = orbit-key-to-stab-anchor W

orbit-key-to-stab-W-fixes-W :
  (ok : OrbitKey) → Stab-W (orbit-key-to-stab-W ok)
orbit-key-to-stab-W-fixes-W = orbit-key-to-stab-anchor-fixes W

------------------------------------------------------------------------
-- Stop anchoring on D. For ANY axis X, any σ ∈ Stab X factors via
-- extend X: there exists an SFin.Permutation 3 element s such that
-- proj₁ (extend X s) ≈ σ. The witness s is exactly `restrict X σ`,
-- and the proof IS `extend-restrict`.
--
-- This is the parametric-over-anchor decomposition theorem. The
-- existing D-specific stab-d-to-orbit-key + stab-round-trip recover
-- as the X=D instance, composed with s3-to-orbit-key on the OrbitKey
-- side. The OrbitKey form (Σ[ ok ∈ OrbitKey ] (orbit-key-to-stab-
-- anchor X ok ≈ σ)) follows once the SFin.Permutation 3 pointwise
-- round-trip on orbit-key-to-s3 ∘ s3-to-orbit-key is proved (deferred;
-- ~27 sub-cases over Fin 3 trichotomy + bijection-injectivity).
------------------------------------------------------------------------

stab-anchor-decomposes :
  (X : Axis) (σ : Permutation) (σ-stab : Stab X σ) →
  Σ[ s ∈ SFin.Permutation 3 ]
    ((x : Axis) → applyₛ (proj₁ (extend X s)) x ≡ applyₛ σ x)
stab-anchor-decomposes X σ σ-stab =
  restrict X (σ , σ-stab) , extend-restrict X σ σ-stab

------------------------------------------------------------------------
-- OrbitKey-form of stab-anchor-decomposes: composes the SFin-form
-- (extend ∘ restrict ≈ id) with the SFin→OrbitKey round-trip (orbit-
-- key-to-s3 ∘ s3-to-orbit-key ≈sfin id) via extend-apply-pointwise-cong.
-- This is the full parametric round-trip — for any anchor X and any
-- σ ∈ Stab X, we recover the OrbitKey index ok such that orbit-key-
-- to-stab-anchor X ok ≈ σ.
------------------------------------------------------------------------

stab-anchor-decomposes-orbitkey :
  (X : Axis) (σ : Permutation) (σ-stab : Stab X σ) →
  Σ[ ok ∈ OrbitKey ]
    ((x : Axis) → applyₛ (proj₁ (extend X (orbit-key-to-s3 ok))) x
                ≡ applyₛ σ x)
stab-anchor-decomposes-orbitkey X σ σ-stab =
  s3-to-orbit-key s , λ x →
    trans
      (extend-apply-pointwise-cong X
         (orbit-key-to-s3 (s3-to-orbit-key s)) s
         (orbit-key-to-s3-of-s3-to-orbit-key s) x)
      (extend-restrict X σ σ-stab x)
  where
    s : SFin.Permutation 3
    s = restrict X (σ , σ-stab)

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
