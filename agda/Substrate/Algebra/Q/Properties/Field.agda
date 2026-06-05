------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Field
--
-- The ℚ field laws, discharged over the SEMANTIC equality `_≈ℚ_`
-- (cross-multiplication; Substrate.Algebra.Q.Equiv). Over `≈ℚ` the inverse
-- laws are TRUE (they are syntactically false on the unreduced `_≡_`: 0/b² ≢
-- 0/1). The numerator arithmetic uses the canonical ℤ ring laws
-- (Z.Properties.{Mul,MulFull}); denominators are products of `suc _`, whose
-- `(_ ∸ 1)` un-truncates by refl. Carriers matched as `mkℚ` so num/den-1 are
-- concrete (no record-eta stalls).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Field where

open import Substrate.Foundation.Nat using (suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-comm; *-assoc; *-identityˡ; *-identityʳ; quad)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left; *ℤ-comm)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-identityˡ; *ℤ-identityʳ; *ℤ-zeroˡ; *ℤ-zeroʳ;
         *ℤ-distribˡ-+; *ℤ-distribʳ-+; quadℤ)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-comm; +ℤ-assoc; +ℤ-identityˡ; +ℤ-identityʳ; +ℤ-inverseˡ; +ℤ-inverseʳ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Arithmetic using (_+ℚ_; _*ℚ_; -ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- Commutativity.
------------------------------------------------------------------------

+ℚ-comm : (a b : ℚ) → (a +ℚ b) ≈ℚ (b +ℚ a)
+ℚ-comm (mkℚ na da₋) (mkℚ nb db₋) =
  cong₂ _*ℤ_
    (+ℤ-comm (na *ℤ (+ suc db₋)) (nb *ℤ (+ suc da₋)))
    (cong +_ (*-comm (suc db₋) (suc da₋)))

*ℚ-comm : (a b : ℚ) → (a *ℚ b) ≈ℚ (b *ℚ a)
*ℚ-comm (mkℚ na da₋) (mkℚ nb db₋) =
  cong₂ _*ℤ_ (*ℤ-comm na nb) (cong +_ (*-comm (suc db₋) (suc da₋)))

------------------------------------------------------------------------
-- Multiplicative associativity.
------------------------------------------------------------------------

*ℚ-assoc : (a b c : ℚ) → ((a *ℚ b) *ℚ c) ≈ℚ (a *ℚ (b *ℚ c))
*ℚ-assoc (mkℚ na da₋) (mkℚ nb db₋) (mkℚ nc dc₋) =
  cong₂ _*ℤ_
    (*ℤ-assoc na nb nc)
    (cong +_ (sym (*-assoc (suc da₋) (suc db₋) (suc dc₋))))

------------------------------------------------------------------------
-- Identity.
------------------------------------------------------------------------

+ℚ-identityˡ : (a : ℚ) → (0ℚ +ℚ a) ≈ℚ a
+ℚ-identityˡ (mkℚ na da₋) =
  cong₂ _*ℤ_
    (trans (+ℤ-identityˡ (na *ℤ (+ 1))) (*ℤ-identityʳ na))
    (cong +_ (sym (*-identityˡ (suc da₋))))

+ℚ-identityʳ : (a : ℚ) → (a +ℚ 0ℚ) ≈ℚ a
+ℚ-identityʳ (mkℚ na da₋) =
  cong₂ _*ℤ_
    (trans (+ℤ-identityʳ (na *ℤ (+ 1))) (*ℤ-identityʳ na))
    (cong +_ (sym (*-identityʳ (suc da₋))))

*ℚ-identityˡ : (a : ℚ) → (1ℚ *ℚ a) ≈ℚ a
*ℚ-identityˡ (mkℚ na da₋) =
  cong₂ _*ℤ_ (*ℤ-identityˡ na) (cong +_ (sym (*-identityˡ (suc da₋))))

*ℚ-identityʳ : (a : ℚ) → (a *ℚ 1ℚ) ≈ℚ a
*ℚ-identityʳ (mkℚ na da₋) =
  cong₂ _*ℤ_ (*ℤ-identityʳ na) (cong +_ (sym (*-identityʳ (suc da₋))))

------------------------------------------------------------------------
-- Zero absorption.
------------------------------------------------------------------------

zero-absorbˡ : (a : ℚ) → (0ℚ *ℚ a) ≈ℚ 0ℚ
zero-absorbˡ (mkℚ na da₋) = cong (_*ℤ (+ 1)) (*ℤ-zeroˡ na)

zero-absorbʳ : (a : ℚ) → (a *ℚ 0ℚ) ≈ℚ 0ℚ
zero-absorbʳ (mkℚ na da₋) = cong (_*ℤ (+ 1)) (*ℤ-zeroʳ na)

------------------------------------------------------------------------
-- Additive inverses (TRUE over ≈ℚ; syntactically false over ≡).
------------------------------------------------------------------------

+ℚ-inverseˡ : (a : ℚ) → ((-ℚ a) +ℚ a) ≈ℚ 0ℚ
+ℚ-inverseˡ (mkℚ na da₋) =
  cong (_*ℤ (+ 1))
    (trans (cong (_+ℤ (na *ℤ (+ suc da₋))) (neg-*-left na (+ suc da₋)))
           (+ℤ-inverseˡ (na *ℤ (+ suc da₋))))

+ℚ-inverseʳ : (a : ℚ) → (a +ℚ (-ℚ a)) ≈ℚ 0ℚ
+ℚ-inverseʳ (mkℚ na da₋) =
  cong (_*ℤ (+ 1))
    (trans (cong ((na *ℤ (+ suc da₋)) +ℤ_) (neg-*-left na (+ suc da₋)))
           (+ℤ-inverseʳ (na *ℤ (+ suc da₋))))

------------------------------------------------------------------------
-- Additive associativity (the nested cross-multiplication identity).
-- Numerators expand (via *ℤ-distribʳ-+ + *ℤ-assoc) to a common 3-term sum;
-- the two groupings reconcile by +ℤ-assoc + ℕ *-comm on the cross denominators;
-- the outer denominators differ by ℕ *-assoc.
------------------------------------------------------------------------

+ℚ-assoc : (a b c : ℚ) → ((a +ℚ b) +ℚ c) ≈ℚ (a +ℚ (b +ℚ c))
+ℚ-assoc (mkℚ na da₋) (mkℚ nb db₋) (mkℚ nc dc₋) =
  trans (cong (_*ℤ DR) nL≡nR) (cong (nR *ℤ_) (sym deq))
  where
    sa = suc da₋
    sb = suc db₋
    sc = suc dc₋
    X  = na *ℤ (+ (sb * sc))
    Y1 = nb *ℤ (+ (sa * sc))
    Z1 = nc *ℤ (+ (sa * sb))
    DL = + ((sa * sb) * sc)
    DR = + (sa * (sb * sc))
    nL = (((na *ℤ (+ sb)) +ℤ (nb *ℤ (+ sa))) *ℤ (+ sc)) +ℤ (nc *ℤ (+ (sa * sb)))
    nR = (na *ℤ (+ (sb * sc))) +ℤ (((nb *ℤ (+ sc)) +ℤ (nc *ℤ (+ sb))) *ℤ (+ sa))
    deq : DL ≡ DR
    deq = cong +_ (*-assoc sa sb sc)
    innerL : ((na *ℤ (+ sb)) +ℤ (nb *ℤ (+ sa))) *ℤ (+ sc) ≡ X +ℤ Y1
    innerL = trans (*ℤ-distribʳ-+ (na *ℤ (+ sb)) (nb *ℤ (+ sa)) (+ sc))
                   (cong₂ _+ℤ_ (*ℤ-assoc na (+ sb) (+ sc)) (*ℤ-assoc nb (+ sa) (+ sc)))
    innerR : ((nb *ℤ (+ sc)) +ℤ (nc *ℤ (+ sb))) *ℤ (+ sa)
           ≡ (nb *ℤ (+ (sc * sa))) +ℤ (nc *ℤ (+ (sb * sa)))
    innerR = trans (*ℤ-distribʳ-+ (nb *ℤ (+ sc)) (nc *ℤ (+ sb)) (+ sa))
                   (cong₂ _+ℤ_ (*ℤ-assoc nb (+ sc) (+ sa)) (*ℤ-assoc nc (+ sb) (+ sa)))
    nL≡nR : nL ≡ nR
    nL≡nR =
      trans (cong (_+ℤ Z1) innerL)
      (trans (+ℤ-assoc X Y1 Z1)
      (trans (cong (X +ℤ_) (cong₂ _+ℤ_ (cong (nb *ℤ_) (cong +_ (*-comm sa sc)))
                                       (cong (nc *ℤ_) (cong +_ (*-comm sa sb)))))
             (cong (X +ℤ_) (sym innerR))))

------------------------------------------------------------------------
-- Left distributivity (the deepest cross-multiplication identity).
-- Both numerators expand (via *ℤ-distribˡ/ʳ-+) to a 2-term sum; each term
-- normalizes to na *ℤ (n? *ℤ (+ K)); the two K's match by a 4-factor product
-- reorder (Nat.Properties.Mul.quad + *-comm/*-assoc).
------------------------------------------------------------------------

distribˡ : (a b c : ℚ) → (a *ℚ (b +ℚ c)) ≈ℚ ((a *ℚ b) +ℚ (a *ℚ c))
distribˡ (mkℚ na da₋) (mkℚ nb db₋) (mkℚ nc dc₋) =
  trans lhs-exp (trans (cong₂ _+ℤ_ term-nb term-nc) (sym rhs-exp))
  where
    sa = suc da₋
    sb = suc db₋
    sc = suc dc₋
    L = sa * (sb * sc)
    R = (sa * sb) * (sa * sc)
    S = (nb *ℤ (+ sc)) +ℤ (nc *ℤ (+ sb))
    Knb : sc * R ≡ (sa * sc) * L
    Knb = trans (*-comm sc R)
          (trans (cong (_* sc) (quad sa sb sa sc))
          (trans (*-assoc (sa * sa) (sb * sc) sc)
          (trans (cong ((sa * sa) *_) (*-comm (sb * sc) sc))
                 (sym (quad sa sc sa (sb * sc))))))
    Knc : sb * R ≡ (sa * sb) * L
    Knc = trans (*-comm sb R)
          (trans (cong (_* sb) (quad sa sb sa sc))
          (trans (*-assoc (sa * sa) (sb * sc) sb)
          (trans (cong ((sa * sa) *_) (*-comm (sb * sc) sb))
                 (sym (quad sa sb sa (sb * sc))))))
    lhs-exp : (na *ℤ S) *ℤ (+ R)
            ≡ (na *ℤ ((nb *ℤ (+ sc)) *ℤ (+ R))) +ℤ (na *ℤ ((nc *ℤ (+ sb)) *ℤ (+ R)))
    lhs-exp = trans (*ℤ-assoc na S (+ R))
              (trans (cong (na *ℤ_) (*ℤ-distribʳ-+ (nb *ℤ (+ sc)) (nc *ℤ (+ sb)) (+ R)))
                     (*ℤ-distribˡ-+ na ((nb *ℤ (+ sc)) *ℤ (+ R)) ((nc *ℤ (+ sb)) *ℤ (+ R))))
    rhs-exp : (((na *ℤ nb) *ℤ (+ (sa * sc))) +ℤ ((na *ℤ nc) *ℤ (+ (sa * sb)))) *ℤ (+ L)
            ≡ (((na *ℤ nb) *ℤ (+ (sa * sc))) *ℤ (+ L)) +ℤ (((na *ℤ nc) *ℤ (+ (sa * sb))) *ℤ (+ L))
    rhs-exp = *ℤ-distribʳ-+ ((na *ℤ nb) *ℤ (+ (sa * sc))) ((na *ℤ nc) *ℤ (+ (sa * sb))) (+ L)
    term-nb : na *ℤ ((nb *ℤ (+ sc)) *ℤ (+ R)) ≡ ((na *ℤ nb) *ℤ (+ (sa * sc))) *ℤ (+ L)
    term-nb = trans (cong (na *ℤ_) (*ℤ-assoc nb (+ sc) (+ R)))
              (trans (cong (λ t → na *ℤ (nb *ℤ (+ t))) Knb)
              (trans (sym (*ℤ-assoc na nb (+ ((sa * sc) * L))))
                     (sym (*ℤ-assoc (na *ℤ nb) (+ (sa * sc)) (+ L)))))
    term-nc : na *ℤ ((nc *ℤ (+ sb)) *ℤ (+ R)) ≡ ((na *ℤ nc) *ℤ (+ (sa * sb))) *ℤ (+ L)
    term-nc = trans (cong (na *ℤ_) (*ℤ-assoc nc (+ sb) (+ R)))
              (trans (cong (λ t → na *ℤ (nc *ℤ (+ t))) Knc)
              (trans (sym (*ℤ-assoc na nc (+ ((sa * sb) * L))))
                     (sym (*ℤ-assoc (na *ℤ nc) (+ (sa * sb)) (+ L)))))

------------------------------------------------------------------------
-- Right distributivity. Same recipe, mirrored: the ℤ-level quadℤ interchange
-- pulls each numerator term into nᵢ *ℤ (nc *ℤ (+ K)) form; the K's match by
-- the ℕ quad reorder.
------------------------------------------------------------------------

distribʳ : (a b c : ℚ) → ((a +ℚ b) *ℚ c) ≈ℚ ((a *ℚ c) +ℚ (b *ℚ c))
distribʳ (mkℚ na da₋) (mkℚ nb db₋) (mkℚ nc dc₋) =
  trans lhs-exp (trans (cong₂ _+ℤ_ term-a term-b) (sym rhs-exp))
  where
    sa = suc da₋
    sb = suc db₋
    sc = suc dc₋
    LDen = (sa * sb) * sc
    RDen = (sa * sc) * (sb * sc)
    P = (na *ℤ (+ sb)) +ℤ (nb *ℤ (+ sa))
    Ka : sb * RDen ≡ (sb * sc) * LDen
    Ka = trans (*-comm sb RDen)
         (trans (cong (_* sb) (quad sa sc sb sc))
         (trans (*-assoc (sa * sb) (sc * sc) sb)
         (trans (cong ((sa * sb) *_) (trans (*-assoc sc sc sb) (cong (sc *_) (*-comm sc sb))))
                (sym (trans (*-comm (sb * sc) ((sa * sb) * sc)) (*-assoc (sa * sb) sc (sb * sc)))))))
    Kb : sa * RDen ≡ (sa * sc) * LDen
    Kb = trans (*-comm sa RDen)
         (trans (cong (_* sa) (quad sa sc sb sc))
         (trans (*-assoc (sa * sb) (sc * sc) sa)
         (trans (cong ((sa * sb) *_) (trans (*-assoc sc sc sa) (cong (sc *_) (*-comm sc sa))))
                (sym (trans (*-comm (sa * sc) ((sa * sb) * sc)) (*-assoc (sa * sb) sc (sa * sc)))))))
    lhs-exp : (P *ℤ nc) *ℤ (+ RDen)
            ≡ ((na *ℤ (+ sb)) *ℤ (nc *ℤ (+ RDen))) +ℤ ((nb *ℤ (+ sa)) *ℤ (nc *ℤ (+ RDen)))
    lhs-exp = trans (*ℤ-assoc P nc (+ RDen))
                    (*ℤ-distribʳ-+ (na *ℤ (+ sb)) (nb *ℤ (+ sa)) (nc *ℤ (+ RDen)))
    rhs-exp : (((na *ℤ nc) *ℤ (+ (sb * sc))) +ℤ ((nb *ℤ nc) *ℤ (+ (sa * sc)))) *ℤ (+ LDen)
            ≡ (((na *ℤ nc) *ℤ (+ (sb * sc))) *ℤ (+ LDen)) +ℤ (((nb *ℤ nc) *ℤ (+ (sa * sc))) *ℤ (+ LDen))
    rhs-exp = *ℤ-distribʳ-+ ((na *ℤ nc) *ℤ (+ (sb * sc))) ((nb *ℤ nc) *ℤ (+ (sa * sc))) (+ LDen)
    term-a : (na *ℤ (+ sb)) *ℤ (nc *ℤ (+ RDen)) ≡ ((na *ℤ nc) *ℤ (+ (sb * sc))) *ℤ (+ LDen)
    term-a = trans (quadℤ na (+ sb) nc (+ RDen))
             (trans (cong (λ t → (na *ℤ nc) *ℤ (+ t)) Ka)
                    (sym (*ℤ-assoc (na *ℤ nc) (+ (sb * sc)) (+ LDen))))
    term-b : (nb *ℤ (+ sa)) *ℤ (nc *ℤ (+ RDen)) ≡ ((nb *ℤ nc) *ℤ (+ (sa * sc))) *ℤ (+ LDen)
    term-b = trans (quadℤ nb (+ sa) nc (+ RDen))
             (trans (cong (λ t → (nb *ℤ nc) *ℤ (+ t)) Kb)
                    (sym (*ℤ-assoc (nb *ℤ nc) (+ (sa * sc)) (+ LDen))))

------------------------------------------------------------------------
-- COMPLETE: all 14 ℚ field laws over ≈ℚ are the exports above
--   +ℚ-{assoc,comm,identityˡ,identityʳ,inverseˡ,inverseʳ}
--   *ℚ-{assoc,comm,identityˡ,identityʳ}  zero-absorb{ˡ,ʳ}  distrib{ˡ,ʳ}
-- This module is THE canonical, fully-discharged target that
-- Q.AsField.ℚ-Field-Obligation aspired to but could not be (its ≡-typed
-- inverse fields are syntactically false: (-ℚ a) +ℚ a = 0/b² ≢ 0/1 = 0ℚ AS
-- RECORDS). No bundling record: a record declaring these proof-typed fields
-- would make this module a def-provider importing proof modules, violating the
-- def/proof separation policy — the flat lemma exports are the bundle.
------------------------------------------------------------------------
