{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentLogMFinLaws — ⟡nf-logM-fin-laws: the monoid-
-- with-zero laws for mulF (the junk-free carrier LogF, ADD 139), TRANSFERRED from
-- mulM (ADD 137/138) along the homomorphism ι. Absorption is direct on mulF;
-- comm/assoc transfer because ι is INJECTIVE (toℕ is injective on Fin), so
-- ι (mulF x y) ≡ ι (mulF y x) [via ι-hom + mulM-comm] ⟹ mulF x y ≡ mulF y x.
--
-- Together with mulF-identityˡ (ADD 139, UNCONDITIONAL) this makes (LogF, mulF,
-- just fz₀, nothing) a genuine commutative monoid-with-zero — the faithful carrier
-- law-complete WITHOUT the canonical caveat mulM needed.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentLogMFinLaws where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Algebra.Wedge.NilpotentFaithfulLogChart using (LogM; mulM)
open import Substrate.Algebra.Wedge.NilpotentLogMMonoid using (mulM-comm)
open import Substrate.Algebra.Wedge.NilpotentLogMAssoc  using (mulM-assoc)
open import Substrate.Algebra.Wedge.NilpotentLogMFin using (LogF; mulF; ι; ι-hom)

------------------------------------------------------------------------
-- toℕ injective on Fin (not in Foundation.Fin — derived inline), then ι injective.
------------------------------------------------------------------------
toℕ-injective : {n : ℕ} {i j : Fin n} → toℕ i ≡ toℕ j → i ≡ j
toℕ-injective {i = fz}   {fz}   _  = refl
toℕ-injective {i = fs i} {fs j} e  = cong fs (toℕ-injective (suc-inj e))
  where suc-inj : {a b : ℕ} → suc a ≡ suc b → a ≡ b
        suc-inj refl = refl

-- ι = mapMaybe toℕ; injective because toℕ is (nothing/just don't mix).
ι-injective : {x y : LogF} → ι x ≡ ι y → x ≡ y
ι-injective {nothing} {nothing} _ = refl
ι-injective {just i}  {just j}  e = cong just (toℕ-injective (just-inj e))
  where just-inj : {a b : ℕ} → (just a) ≡ just b → a ≡ b
        just-inj refl = refl

------------------------------------------------------------------------
-- ① ABSORPTION — direct on mulF (nothing is the zero), no transfer needed.
------------------------------------------------------------------------
mulF-zeroˡ : (x : LogF) → mulF nothing x ≡ nothing
mulF-zeroˡ x = refl

mulF-zeroʳ : (x : LogF) → mulF x nothing ≡ nothing
mulF-zeroʳ nothing  = refl
mulF-zeroʳ (just _) = refl

------------------------------------------------------------------------
-- ② COMMUTATIVITY — transferred: ι (mulF x y) ≡ ι (mulF y x) via ι-hom + mulM-comm,
-- then ι-injective. (No re-analysis of the cap; the mulM proof is reused wholesale.)
------------------------------------------------------------------------
mulF-comm : (x y : LogF) → mulF x y ≡ mulF y x
mulF-comm x y = ι-injective
  (trans (ι-hom x y)
  (trans (mulM-comm (ι x) (ι y))
         (sym (ι-hom y x))))

------------------------------------------------------------------------
-- ③ ASSOCIATIVITY — transferred: push ι-hom through both nested mulF, apply
-- mulM-assoc in the middle, then ι-injective.
------------------------------------------------------------------------
mulF-assoc : (x y z : LogF) → mulF (mulF x y) z ≡ mulF x (mulF y z)
mulF-assoc x y z = ι-injective
  (trans (ι-hom (mulF x y) z)
  (trans (cong (λ w → mulM w (ι z)) (ι-hom x y))
  (trans (mulM-assoc (ι x) (ι y) (ι z))
  (trans (cong (mulM (ι x)) (sym (ι-hom y z)))
         (sym (ι-hom x (mulF y z)))))))

------------------------------------------------------------------------
-- So (LogF, mulF, just fz₀ [ADD 139 identity], nothing) is a commutative
-- monoid-with-zero: comm + assoc + absorb (here) + identity (ADD 139, unconditional)
-- — the faithful carrier law-complete, the mulM laws reused via ι, not re-proved.
------------------------------------------------------------------------
