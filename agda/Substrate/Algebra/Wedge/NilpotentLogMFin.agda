{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentLogMFin — ⟡nf-logM-fin: the JUNK-FREE faithful
-- carrier LogF = Maybe (Fin (suc d)), where the monoid-with-zero IDENTITY holds
-- UNCONDITIONALLY (no canonical caveat). This is the carrier the junk-residue of
-- ADD 137 pointed at: Maybe ℕ over-represents (just j, j ≥ cap, breaks identity);
-- Fin (suc d) is EXACTLY {0..d}, so `just j` for j ≥ cap simply cannot arise.
--
-- The invariant made structural: the bound `toℕ i < suc d` that Maybe ℕ had to
-- carry as a HYPOTHESIS (mulM-identityˡ-canonical's `j < suc d`) is now a THEOREM
-- of the carrier (toℕ-bound). The residue (the junk) is excluded by construction,
-- and ι = toℕ-map embeds LogF as the canonical subobject on which mulM restricts.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentLogMFin where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_; _<?_; z≤n; s≤s)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Wedge.NilpotentFaithfulLogChart using (d; LogM; mulM)

------------------------------------------------------------------------
-- Two small Fin facts (not in Foundation.Fin) — derived inline.
------------------------------------------------------------------------
-- every Fin (suc n) is below its bound.
toℕ-bound : {n : ℕ} (i : Fin n) → toℕ i < n
toℕ-bound fzero     = s≤s z≤n
toℕ-bound (fsuc i) = s≤s (toℕ-bound i)

-- fromℕ< recovers the Fin it came from (the round-trip), for ANY bound witness.
fromℕ<-toℕ : {n : ℕ} (i : Fin n) (p : toℕ i < n) → fromℕ< p ≡ i
fromℕ<-toℕ fzero     (s≤s q) = refl
fromℕ<-toℕ (fsuc i) (s≤s p) = cong fsuc (fromℕ<-toℕ i p)

------------------------------------------------------------------------
-- THE FAITHFUL CARRIER + its multiplication. LogF = Maybe (Fin (suc d)); mulF
-- adds the logs (as ℕ) and, below the cap, keeps the result AS A Fin (fromℕ<);
-- at/over the cap, the absorbing nothing.
------------------------------------------------------------------------
LogF : Set
LogF = Maybe (Fin (suc d))

mulF : LogF → LogF → LogF
mulF nothing  _        = nothing
mulF (just _) nothing  = nothing
mulF (just i) (just j) with (toℕ i + toℕ j) <? suc d
... | yes p = just (fromℕ< p)
... | no  _ = nothing

------------------------------------------------------------------------
-- ① THE WIN: IDENTITY holds UNCONDITIONALLY. just fzero (the Fin 0) is a two-sided
-- identity — for EVERY j : Fin (suc d), no `j < cap` hypothesis, because the
-- carrier's bound (toℕ-bound) supplies it. This is exactly what Maybe ℕ could not
-- do (ADD 137's identity-fails-on-junk); the junk is gone.
------------------------------------------------------------------------
fz₀ : Fin (suc d)
fz₀ = fzero

mulF-identityˡ : (x : LogF) → mulF (just fz₀) x ≡ x
mulF-identityˡ nothing  = refl
mulF-identityˡ (just j) with (toℕ fz₀ + toℕ j) <? suc d
-- toℕ fzero + toℕ j = 0 + toℕ j reduces to toℕ j, so p : toℕ j < suc d and fromℕ< p ≡ j.
... | yes p = cong just (fromℕ<-toℕ j p)
... | no ¬p = ⊥-elim (¬p (toℕ-bound j))

------------------------------------------------------------------------
-- ② ι = the canonical embedding LogF → LogM (Maybe (Fin) → Maybe ℕ via toℕ). It
-- is a HOMOMORPHISM ι (mulF x y) ≡ mulM (ι x) (ι y) — so comm/assoc/absorb (proved
-- for mulM on the full Maybe ℕ, ADD 137/138) TRANSFER to mulF, and ι exhibits LogF
-- as the canonical subobject on which mulM restricts to a genuine monoid-with-zero.
------------------------------------------------------------------------
ι : LogF → LogM
ι nothing  = nothing
ι (just i) = just (toℕ i)

ι-hom : (x y : LogF) → ι (mulF x y) ≡ mulM (ι x) (ι y)
ι-hom nothing  _        = refl
ι-hom (just _) nothing  = refl
ι-hom (just i) (just j) with (toℕ i + toℕ j) <? suc d
... | yes p = cong (λ z → just z) (toℕ-fromℕ< p)  -- ι (just (fromℕ< p)) = just (toℕ (fromℕ< p)) = just (toℕ i + toℕ j)
      where -- toℕ (fromℕ< p) ≡ (toℕ i + toℕ j): fromℕ< then toℕ is the identity on the ℕ.
            toℕ-fromℕ< : {n m : ℕ} (q : m < n) → toℕ (fromℕ< q) ≡ m
            toℕ-fromℕ< (s≤s z≤n)     = refl
            toℕ-fromℕ< (s≤s (s≤s q)) = cong suc (toℕ-fromℕ< (s≤s q))
... | no  _ = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the "identity needs a hypothesis" of Maybe ℕ
-- (ADD 137) dissolves — on Maybe (Fin (suc d)) the hypothesis IS the carrier's
-- bound (toℕ-bound), so identity is unconditional. Maybe ℕ was the free carrier
-- WITH junk; Maybe (Fin (suc d)) is the CANONICAL (junk-free) one, and ι is the
-- embedding realizing it as the subobject mulM restricts to. The residue (junk)
-- is not deleted but EXCLUDED BY CONSTRUCTION, its absence now a theorem.
------------------------------------------------------------------------
