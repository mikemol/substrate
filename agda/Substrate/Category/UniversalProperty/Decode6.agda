------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Decode6
--
-- ⟡odecode-decode6 (Phase B of ⟡ta-upterm-O-decode): the 6 concrete legacy
-- UPArrowP objects DECODE into the self-constructed object universe
-- O = Σ ℕ TmDB (ObjectUniverse.agda) — completing "the objects live in O."
--
-- Each object's DISCRIMINATING witness (its Contentful/Recognized certificate's
-- Source) is coded into O and (where meaningful) round-tripped:
--   * ℕ-carrier objects (eq-UP, Quotient) → the Source value as `(0 , var n)`,
--     recovered by `decode-nat` (round-trip refl).
--   * ℕ×ℕ-carrier objects (crt-UP, QuotientProduct) → the Source pair combined to
--     a SINGLE ℕ via the CRT codec (combine witness-3-5), and recovered EXACTLY by
--     the landed `crt-roundtrip` at moduli (3,5) — the (S,T,W)→ℕ→(S,T,W) recovery,
--     using the SAME moduli the objects' own Witness (mod3×mod5) uses.
--
-- HONEST BOUNDARY (⟡diagonal-Y-combinator): the function-space objects
-- (windowedCF-UP, the 5 Instances) have carriers `A → B` whose EXTENSIONAL value
-- has no ℕ/TmDB code (Cantor: no ℕ ↠ (A→B)). Their DEFINABLE representative (the
-- constant/definable witness) codes via the point-surjection ladder
-- (Category.Lawvere.PointSurjective / the Y-combinator), an orientation residue —
-- but that Y-completion is SCOPED-NOT-BUILT (DiagonalLawvereSKI). So they are
-- documented here, not force-coded; this is a genuine (respected) exclusion, not
-- a wall to dissolve.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Decode6 where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; s≤s; z≤n)
open import Substrate.Foundation.Product using (_×_; _,_; Σ; proj₁)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.UniversalProperty.TmDBGodel using (TmDB; var; S; K; I; app)
open import Substrate.Category.UniversalProperty.ObjectUniverse using (O)
open import Substrate.Algebra.Quotient.CRT using (combine)
open import Substrate.Algebra.Quotient.CRT.FromTrace using (witness-3-5)
open import Substrate.Category.UniversalProperty.DiagonalObsCodeCRT using (decodePair; crt-roundtrip)

-- the objects' certificates (the discriminating witness data):
open import Substrate.Category.UniversalProperty.Vacuity using (eq-contentful)
open import Substrate.Category.UniversalProperty.Recognized using (crt-recognized; content)
open import Substrate.Category.UniversalProperty.Quotient using (Quotient-contentful)
open import Substrate.Category.UniversalProperty.QuotientProduct using (QuotientProduct-contentful)

------------------------------------------------------------------------
-- 1. The ℕ ↔ O coding: n ↦ (grade 0, var n); recover by reading the var index.
------------------------------------------------------------------------

nat→O : ℕ → O
nat→O n = 0 , var n

code→nat : TmDB → ℕ
code→nat (var n) = n
code→nat S       = 0
code→nat K       = 0
code→nat I       = 0
code→nat (app _ _) = 0

decode-nat : O → ℕ
decode-nat (_ , t) = code→nat t

nat-roundtrip : (n : ℕ) → decode-nat (nat→O n) ≡ n
nat-roundtrip _ = refl

------------------------------------------------------------------------
-- 2. The ℕ-carrier objects: eq-UP (Source 0) and Quotient (Source 1).
--    The Source is read off the object's own Contentful certificate.
------------------------------------------------------------------------

eq-source : ℕ
eq-source = proj₁ eq-contentful            -- eq-UP's discriminating Source (= 0)

eq→O : O
eq→O = nat→O eq-source

eq-roundtrip : decode-nat eq→O ≡ eq-source
eq-roundtrip = refl

quot-source : ℕ
quot-source = proj₁ Quotient-contentful    -- Quotient-UPArrow's Source (= 1)

quot→O : O
quot→O = nat→O quot-source

quot-roundtrip : decode-nat quot→O ≡ quot-source
quot-roundtrip = refl

------------------------------------------------------------------------
-- 3. The ℕ×ℕ-carrier CRT objects: crt-UP and QuotientProduct (Source (1,2),
--    Witness = mod3×mod5). The Source pair combines to a single ℕ (= 22) and
--    is recovered EXACTLY by crt-roundtrip at moduli (3,5) — the (S,T,W)→ℕ→(S,T,W)
--    recovery, on the SAME moduli the objects' Witness uses.
------------------------------------------------------------------------

crt-source : ℕ × ℕ
crt-source = proj₁ (content crt-recognized)          -- crt-UP's Source (= (1,2))

crt-code : ℕ
crt-code = combine witness-3-5 crt-source            -- = 22

crt→O : O
crt→O = nat→O crt-code

-- THE ROUND-TRIP: decoding the CRT code recovers crt-UP's Source pair exactly.
crt-decode-roundtrip : decodePair 2 4 crt-code ≡ crt-source
crt-decode-roundtrip = crt-roundtrip witness-3-5 1 2 (s≤s (s≤s z≤n)) (s≤s (s≤s (s≤s z≤n)))

-- QuotientProduct has the SAME Source (1,2) and the SAME mod3×mod5 Witness, so
-- the same code + round-trip cover it (crt-source ≡ QuotientProduct's Source).
qp-source : ℕ × ℕ
qp-source = proj₁ QuotientProduct-contentful         -- = (1,2)

qp-code : ℕ
qp-code = combine witness-3-5 qp-source

qp-decode-roundtrip : decodePair 2 4 qp-code ≡ qp-source
qp-decode-roundtrip = crt-roundtrip witness-3-5 1 2 (s≤s (s≤s z≤n)) (s≤s (s≤s (s≤s z≤n)))

------------------------------------------------------------------------
-- 4. HONEST BOUNDARY — the function-space objects (⟡diagonal-Y-combinator).
--    windowedCF-UP (Source ℕ→RealTrace→List ℕ) and the 5 Instances (carriers
--    (B→M)→(F→M), etc.) have EXTENSIONAL function carriers: no ℕ↠(A→B) (Cantor).
--    Their DEFINABLE witnesses (constant / definable functions) code via the
--    point-surjection ladder (Category.Lawvere.PointSurjective; the Y-combinator),
--    an orientation residue reached by increasing the run — but the Y-completion
--    for arbitrary definable maps is scoped-not-built (DiagonalLawvereSKI). So they
--    are NOT force-coded here: a genuine (respected) exclusion, reoriented (δ²=id
--    green theorem) not dissolved. This is the arc's one honest boundary.
------------------------------------------------------------------------
