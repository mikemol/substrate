{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepConvSharpen — ⟡FU-sep-conv-sharpen: the bare-nf vs extensional sig IS the
-- ℚ (intensional/finite) vs ≋ (observational/applied) split (ADD 100-101, 117),
-- with η on the boundary. Sharpens ⟡FU-sep-conv into three theorems over the
-- observation stream (the ≋ carrier, ObsBisim's head-obs + coinductive-tail shape):
--
--   BARE (intensional / ℚ / depth-0): the head observation (bare nf) agrees.
--   EXT  (observational / ≋ / depth-1+): the tail (all further observations) bisimilar.
--
-- THE DISSOLUTION ("which is THE equality, bare or extensional?"): neither — ≋
-- DECOMPOSES as bare × ext (Thm 1). η lives STRICTLY on the ext-not-bare boundary
-- (Thm 2, the arity gap: B M I vs M agree applied, differ bare). On the FINITE
-- IMAGE the two COINCIDE (Thm 3, the ℚ⊣R unit / bt-reflect, ADD 101-102): where
-- the observation is settled, bare determines ≋.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepConvSharpen where

open import Substrate.Foundation.Eq    using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.FUSep.FUSepQCyc using (Stream; hd; tl; _~ₛ_; hd~; tl~;
                             ~-refl; ~-sym; ~-trans; const;
                             AllHeads; ah-hd; ah-tl; allHeads~const)

record _×_ (A B : Set) : Set where
  constructor _,_
  field π₁ : A ; π₂ : B
open _×_ public

-- the two equalities, as relations on the observation stream.
BareEq : {A : Set} → Stream A → Stream A → Set
BareEq s t = hd s ≡ hd t            -- depth-0: intensional / ℚ (the bare nf)

ExtEq : {A : Set} → Stream A → Stream A → Set
ExtEq s t = tl s ~ₛ tl t             -- depth-1+: observational / ≋ (all applications)

------------------------------------------------------------------------
-- THEOREM 1 — ≋ DECOMPOSES as bare × ext. The full observational equality (_~_,
-- the ObsBisim ≋) is EXACTLY depth-0 (bare/ℚ) agreement AND depth-1+ (ext/≋)
-- agreement. The bare and extensional sigs are the two projections of ≋.
------------------------------------------------------------------------
split→ : {A : Set}{s t : Stream A} → s ~ₛ t → BareEq s t × ExtEq s t
split→ p = hd~ p , tl~ p

split← : {A : Set}{s t : Stream A} → BareEq s t → ExtEq s t → s ~ₛ t
hd~ (split← b e) = b
tl~ (split← b e) = e

------------------------------------------------------------------------
-- THEOREM 2 — η lives STRICTLY on the ext-not-bare boundary. A witness with ExtEq
-- (tails bisimilar — agree under every application) but ¬ BareEq (heads differ) —
-- the ARITY GAP: B M I vs M agree applied but differ bare (B M I is a stuck value).
-- So the observational (≋/R) quotient STRICTLY EXTENDS the intensional (bare/ℚ) one.
------------------------------------------------------------------------
data Bit2 : Set where t0 t1 : Bit2
t0≢t1 : t0 ≡ t1 → ⊥
t0≢t1 ()

cons : {A : Set} → A → Stream A → Stream A
hd (cons a s) = a
tl (cons a s) = s

sL sR : Stream Bit2
sL = cons t0 (const t1)      -- head t0, tail (const t1)  — the "B M I" side
sR = cons t1 (const t1)      -- head t1, tail (const t1)  — the "M" side

-- extensionally equal: tails agree (both const t1) — agreement under application.
eta-ext : ExtEq sL sR
eta-ext = ~-refl (const t1)

-- NOT bare equal: heads differ (t0 ≢ t1) — the depth-0 arity-gap distinction.
eta-not-bare : BareEq sL sR → ⊥
eta-not-bare b = t0≢t1 b

------------------------------------------------------------------------
-- THEOREM 3 — on the FINITE IMAGE the equalities COINCIDE (the ℚ⊣R unit). Where
-- the observation is SETTLED (constant — the finite Böhm tree, bt-reflect ADD 102),
-- bare DETERMINES ≋: two streams with the same settled head are fully bisimilar.
-- This is unit-id-on-finite (ADD 101): finite ⟹ ≋ collapses to the bare ≡.
------------------------------------------------------------------------
finite-coincidence : {A : Set}{x : A}{s t : Stream A}
                   → AllHeads x s → AllHeads x t → s ~ₛ t
finite-coincidence {s = s}{t} as at =
  ~-trans (allHeads~const _ s as) (~-sym (allHeads~const _ t at))

-- and on the finite image, bare holds definitionally (both heads = x): so bare,
-- ext, and ≋ all coincide there — the boundary CLOSES on the finite side.
finite-bare : {A : Set}{x : A}{s t : Stream A}
            → AllHeads x s → AllHeads x t → BareEq s t
finite-bare as at = trEq (ah-hd as) (symEq (ah-hd at))
  where symEq : {X : Set}{a b : X} → a ≡ b → b ≡ a
        symEq refl = refl
        trEq : {X : Set}{a b c : X} → a ≡ b → b ≡ c → a ≡ c
        trEq refl r = r
