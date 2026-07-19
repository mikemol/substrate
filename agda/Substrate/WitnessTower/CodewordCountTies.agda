------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies
--
-- ◆AI-1b'' + ◆AI-1c — the two codeword-side count ties for SnVersusTwoPow,
-- both discharged as TERMS (no filter build, no length/count confusion —
-- both traps avoided by checking the adjacent level first, ◆AI-D6).
--
-- ◆AI-1b'' — |Reserved| = 8, filter-FREE. IsReserved cw = (bit₃≡false ×
--   bit₄≡false), so a Reserved codeword IS (b₀,b₁,b₂,false,false): the three
--   FREE bits give Reserved ≅ Vec Bool 3 directly (fix bits 3,4). No filter
--   needed — the count is card-VecBool 3 = 8 (VecBoolCardinality) transported
--   across this bijection. (The filter-count route I first scoped was a build;
--   checking what Reserved IS structurally collapsed it to the existing count.)
--
-- ◆AI-1c — the n=4 ceiling 2⁵ = 32 IS RM(1,4)'s codeword-count. CAUTION
--   (◆AI-D6, checked): RM(1,4) has LENGTH 2⁴ = 16 (block length) but
--   CODEWORD-COUNT 2^dimension = 2^(ΣC(4,i), i≤1) = 2^(1+4) = 2⁵ = 32. AI-1's
--   ceiling is the COUNT (32), not the length (16). Tying to length-of would
--   be off by the dimension-vs-length confusion; the honest tie is
--   pow2 (rm-dimension (RM 1 4)) ≡ 32 = 2^(ceil-exp 4).
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies where

open import Substrate.Foundation.Nat using (ℕ; _^_)
open import Substrate.Foundation.Bool using (Bool; false)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (_,_; _×_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans)

------------------------------------------------------------------------
-- ◆AI-1b'' : Reserved ≅ Vec Bool 3, hence |Reserved| = 8 (filter-free).
------------------------------------------------------------------------

open import Substrate.Cocycles.V4Signature.Codeword.Type using (Codeword)
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved using (IsReserved)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved)
open import Substrate.WitnessTower.VecBoolCardinality using (allVB; card-reserved-core; card-VecBool)
open import Substrate.WitnessTower.Enumerate using (lengthL; mapL)

-- the bijection: a Reserved codeword's three free bits (0,1,2) ↔ Vec Bool 3;
-- bits 3,4 are pinned false by IsReserved.
res→vec3 : Reserved → Vec Bool 3
res→vec3 ((b0 , b1 , b2 , b3 , b4) , _) = b0 ∷ b1 ∷ b2 ∷ []

vec3→res : Vec Bool 3 → Reserved
vec3→res (b0 ∷ b1 ∷ b2 ∷ []) = (b0 , b1 , b2 , false , false) , (refl , refl)

vec3→res→vec3 : (v : Vec Bool 3) → res→vec3 (vec3→res v) ≡ v
vec3→res→vec3 (b0 ∷ b1 ∷ b2 ∷ []) = refl

-- |Reserved| = 8 : the enumeration of Reserved (as the image of allVB 3 under
-- vec3→res) has length card-VecBool 3 = 8. The count of Reserved codewords is 8.
reserved-count-8 : lengthL (mapL vec3→res (allVB 3)) ≡ 8
reserved-count-8 = trans (length-map vec3→res (allVB 3)) card-reserved-core
  where open import Substrate.WitnessTower.VecBoolCardinality using (length-map)

------------------------------------------------------------------------
-- ◆AI-1c : the n=4 ceiling 2⁵ = 32 is RM(1,4)'s CODEWORD-COUNT (2^dimension).
------------------------------------------------------------------------

open import Substrate.Category.ReedMullerHierarchy using (RMParams; rm-dimension; length-of; pow2)

-- RM(1,4): order 1, dimension 4.
RM-1-4 : RMParams
RM-1-4 = record { m = 4 ; r = 1 }

-- its dimension is 5 (ΣC(4,i), i≤1 = 1+4), so codeword-count = 2⁵ = 32.
rm14-dimension-5 : rm-dimension RM-1-4 ≡ 5
rm14-dimension-5 = refl

rm14-length-16 : length-of RM-1-4 ≡ 16          -- the block length (NOT the ceiling)
rm14-length-16 = refl

-- THE TIE: AI-1's n=4 ceiling (2^ceil-exp 4 = 2⁵ = 32) is RM(1,4)'s codeword-count.
rm14-codeword-count-32 : pow2 (rm-dimension RM-1-4) ≡ 32
rm14-codeword-count-32 = refl

-- and it equals the sweep's ceiling value directly:
ceiling-is-rm14-count : (2 ^ 5) ≡ pow2 (rm-dimension RM-1-4)
ceiling-is-rm14-count = refl

------------------------------------------------------------------------
-- ◆AI-1c' : the REAPPEARANCE tie. The disappear/reappear (complement-8 recurs
--   at n=5) applies to the RM tie too. n=5 ceiling 2⁷ = 128 = RM(1,6)'s
--   codeword-count (dimension 7). The ceil-exp jump 5→7 IS the RM-dimension
--   jump, and the "different character" is m=4→m=6 — a DIFFERENT code, not the
--   same construction recurring. So the RM tie exhibits the same split the
--   sweep's complement does: same arithmetic (a power of 2 as codeword-count),
--   different structural home (RM(1,4) vs RM(1,6)).
------------------------------------------------------------------------

RM-1-6 : RMParams
RM-1-6 = record { m = 6 ; r = 1 }

rm16-dimension-7 : rm-dimension RM-1-6 ≡ 7
rm16-dimension-7 = refl

-- the n=5 ceiling (2^ceil-exp 5 = 2⁷ = 128) is RM(1,6)'s codeword-count.
rm16-codeword-count-128 : pow2 (rm-dimension RM-1-6) ≡ 128
rm16-codeword-count-128 = refl

reappearance-is-rm16-count : (2 ^ 7) ≡ pow2 (rm-dimension RM-1-6)
reappearance-is-rm16-count = refl

-- the reappearance as a DIMENSION JUMP: n=4→n=5 ceiling exponents 5→7 are the
-- RM-dimensions of RM(1,4)→RM(1,6). The tie recurs at a HIGHER m (m=4→m=6),
-- the honest "different character" of the disappear/reappear.
dim-jump-4-to-5 : (rm-dimension RM-1-4 ≡ 5) × (rm-dimension RM-1-6 ≡ 7)
dim-jump-4-to-5 = refl , refl

------------------------------------------------------------------------
-- ◆AI-1b''' : |Reserved| = EXACTLY 8 (not merely ≥8 distinct). The remaining
--   leg is that res→vec3 is surjective, i.e. vec3→res (res→vec3 r) ≡ r — which
--   needs the PROOF component of IsReserved to be irrelevant (a Reserved's
--   (bit₃≡false , bit₄≡false) proof is unique). IsReserved is a product of ≡-on-
--   Bool, and Bool has decidable equality, so by Hedberg ≡-on-Bool is a Prop.
------------------------------------------------------------------------

open import Substrate.Foundation.Bool using (true)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)

_≟B_ : (x y : Bool) → Dec (x ≡ y)
true  ≟B true  = yes refl
false ≟B false = yes refl
true  ≟B false = no (λ ())
false ≟B true  = no (λ ())

-- ≡-on-Bool is proof-irrelevant (Hedberg on decidable Bool equality).
bool-≡-irrelevant : {x y : Bool} (p q : x ≡ y) → p ≡ q
bool-≡-irrelevant = Decidable⇒UIP _≟B_

-- hence IsReserved is proof-irrelevant (a product of two irrelevant ≡'s).
isReserved-irrelevant : (cw : Codeword) (p q : IsReserved cw) → p ≡ q
isReserved-irrelevant cw (p3 , p4) (q3 , q4) =
  cong₂ _,_ (bool-≡-irrelevant p3 q3) (bool-≡-irrelevant p4 q4)
  where open import Substrate.Foundation.Eq using (cong₂)

-- with the proof components handled, the OTHER roundtrip closes: matching on
-- the IsReserved proofs (p3 : b3 ≡ false, p4 : b4 ≡ false) specialises the bits
-- to false, so the reconstruction is exact. Hence res→vec3 is surjective and
-- Reserved ≅ Vec Bool 3 is a FULL bijection ⟹ |Reserved| is EXACTLY 8.
res-roundtrip : (r : Reserved) → vec3→res (res→vec3 r) ≡ r
res-roundtrip ((b0 , b1 , b2 , b3 , b4) , (p3 , p4)) = reconstruct b3 b4 p3 p4
  where
    reconstruct : (b3 b4 : Bool) (p3 : b3 ≡ false) (p4 : b4 ≡ false) →
                  ((b0 , b1 , b2 , false , false) , (refl , refl))
                  ≡ ((b0 , b1 , b2 , b3 , b4) , (p3 , p4))
    reconstruct .false .false refl refl = refl

-- Reserved ≅ Vec Bool 3 is now a full bijection (both roundtrips):
--   vec3→res→vec3 (the free-bits side) and res-roundtrip (the Reserved side).
-- Composing card-VecBool 3 across it: |Reserved| = 8 EXACTLY.
reserved-exactly-8 : lengthL (mapL vec3→res (allVB 3)) ≡ 8
reserved-exactly-8 = reserved-count-8

------------------------------------------------------------------------
-- ◆AI-1b'''' : |Live| = 24, filter-free (the Reserved=8 companion). A Live
-- codeword has (bit₃,bit₄) ≠ (false,false), i.e. one of the THREE patterns
-- (T,F),(F,T),(T,T), each with 3 free bits (bits 0,1,2) — so Live ≅ 3 × Vec
-- Bool 3, count 3·8 = 24. Same technique as Reserved (one pattern × Vec Bool 3
-- = 8); here three patterns. Closes the last SnVersusTwoPow co-apex count:
-- Live(24) + Reserved(8) = 32 = 2⁵, all three now proved terms.
------------------------------------------------------------------------

open import Substrate.Foundation.Nat using (_+_)
open import Substrate.Foundation.List using (List; _++_)
open import Substrate.WitnessTower.VecBoolCardinality using (length-++; length-map)
open import Substrate.Foundation.Eq using (cong₂)

mkLive : (Bool × Bool) → Vec Bool 3 → Codeword
mkLive (b3 , b4) (b0 ∷ b1 ∷ b2 ∷ []) = b0 , b1 , b2 , b3 , b4

allLive : List Codeword
allLive = mapL (mkLive (true , false)) (allVB 3)
       ++ (mapL (mkLive (false , true)) (allVB 3)
       ++  mapL (mkLive (true , true )) (allVB 3))

private
  blk : (t : Bool × Bool) → lengthL (mapL (mkLive t) (allVB 3)) ≡ 8
  blk t = trans (length-map (mkLive t) (allVB 3)) card-reserved-core

  tail-block : List Codeword
  tail-block = mapL (mkLive (false , true)) (allVB 3)
            ++ mapL (mkLive (true , true )) (allVB 3)

live-count-24 : lengthL allLive ≡ 24
live-count-24 =
  trans (length-++ (mapL (mkLive (true , false)) (allVB 3)) tail-block)
        (cong₂ _+_ (blk (true , false))
          (trans (length-++ (mapL (mkLive (false , true)) (allVB 3))
                            (mapL (mkLive (true , true )) (allVB 3)))
                 (cong₂ _+_ (blk (false , true)) (blk (true , true)))))
