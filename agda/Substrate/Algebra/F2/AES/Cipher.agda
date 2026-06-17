------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.Cipher  (AI-12c: the full AES round-trip)
--
-- THE STRUCTURAL ROUND-TRIP `decrypt ks (encrypt ks s) ≡ s` for AES-128 — R2
-- of the reversible-composition spine, lifting the per-round round-trip (AI-11)
-- over the 11 round keys.  Key-PARAMETRIC: it holds for ANY round keys (forward
-- and inverse use the same keys), so it needs no key schedule (AI-12k).
--
-- The reusable costructure is `fold-rt` — the cipher-level twin of `map-rt`:
-- fold a per-step forward map, undo it with the reverse-order inverse fold; if
-- each step's inverse undoes it pointwise, the backward fold undoes the forward.
-- Fully --safe --without-K, 0 postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.Cipher where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Algebra.F2.AES.Round
  using (State; round; inv-round; final-round; inv-final-round; addKey;
         round-rt; final-round-rt; add-rt)

------------------------------------------------------------------------
-- generic reversible fold (the cipher-level reversibility combinator).
------------------------------------------------------------------------
fold : {A S : Set} {n : ℕ} (f : A → S → S) → Vec A n → S → S
fold f []       s = s
fold f (k ∷ ks) s = fold f ks (f k s)

rfold : {A S : Set} {n : ℕ} (g : A → S → S) → Vec A n → S → S
rfold g []       t = t
rfold g (k ∷ ks) t = g k (rfold g ks t)

fold-rt : {A S : Set} {n : ℕ} (f g : A → S → S)
        → ((a : A) (s : S) → g a (f a s) ≡ s)
        → (ks : Vec A n) (s : S) → rfold g ks (fold f ks s) ≡ s
fold-rt f g rt []       s = refl
fold-rt f g rt (k ∷ ks) s = trans (cong (g k) (fold-rt f g rt ks (f k s))) (rt k s)

------------------------------------------------------------------------
-- AES-128: k₀ pre-whiten · 9 middle rounds · k₁₀ final round (FIPS-197 §5.1).
------------------------------------------------------------------------
encrypt : State → Vec State 9 → State → State → State
encrypt k0 mid k10 s = final-round k10 (fold round mid (addKey k0 s))

decrypt : State → Vec State 9 → State → State → State
decrypt k0 mid k10 t = addKey k0 (rfold inv-round mid (inv-final-round k10 t))

-- THE FULL STRUCTURAL ROUND-TRIP.
cipher-rt : (k0 : State) (mid : Vec State 9) (k10 s : State)
          → decrypt k0 mid k10 (encrypt k0 mid k10 s) ≡ s
cipher-rt k0 mid k10 s =
  trans (cong (λ y → addKey k0 (rfold inv-round mid y))
              (final-round-rt k10 (fold round mid (addKey k0 s))))
  (trans (cong (addKey k0) (fold-rt round inv-round round-rt mid (addKey k0 s)))
         (add-rt k0 s))
