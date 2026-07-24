------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.Cipher.RoundTrip  (AI-12c: the full AES round-trip)
--
-- THE STRUCTURAL ROUND-TRIP `decrypt ks (encrypt ks s) ≡ s` for AES-128 — R2
-- of the reversible-composition spine, lifting the per-round round-trip
-- (Round.RoundTrip) over the 11 round keys.  Key-PARAMETRIC: it holds for ANY
-- round keys (forward and inverse use the same keys), so it needs no key
-- schedule (AI-12k).
--
-- The reusable costructure is `fold-rt` — the cipher-level twin of `map-rt`:
-- fold a per-step forward map, undo it with the reverse-order inverse fold.
-- Forcing THIS module deserializes the per-round inverses (→ GF inverse); the
-- forward cipher (Cipher) does not.  Fully --safe --without-K, 0 postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.Cipher.RoundTrip where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Algebra.F2.AES.Round using (State; round; final-round; addKey)
open import Substrate.Algebra.F2.AES.Round.RoundTrip
  using (inv-round; inv-final-round; round-rt; final-round-rt; add-rt)
open import Substrate.Algebra.F2.AES.Cipher using (fold; encrypt)

------------------------------------------------------------------------
-- generic reverse-order fold + its round-trip (the cipher-level combinator).
------------------------------------------------------------------------
rfold : {A S : Set} {n : ℕ} (g : A → S → S) → Vec A n → S → S
rfold g []       t = t
rfold g (k ∷ ks) t = g k (rfold g ks t)

fold-rt : {A S : Set} {n : ℕ} (f g : A → S → S)
        → ((a : A) (s : S) → g a (f a s) ≡ s)
        → (ks : Vec A n) (s : S) → rfold g ks (fold f ks s) ≡ s
fold-rt f g rt []       s = refl
fold-rt f g rt (k ∷ ks) s = trans (cong (g k) (fold-rt f g rt ks (f k s))) (rt k s)

------------------------------------------------------------------------
-- AES-128 decryption + the full structural round-trip.
------------------------------------------------------------------------
decrypt : State → Vec State 9 → State → State → State
decrypt k0 mid k10 t = addKey k0 (rfold inv-round mid (inv-final-round k10 t))

cipher-rt : (k0 : State) (mid : Vec State 9) (k10 s : State)
          → decrypt k0 mid k10 (encrypt k0 mid k10 s) ≡ s
cipher-rt k0 mid k10 s =
  trans (cong (λ y → addKey k0 (rfold inv-round mid y))
              (final-round-rt k10 (fold round mid (addKey k0 s))))
  (trans (cong (addKey k0) (fold-rt round inv-round round-rt mid (addKey k0 s)))
         (add-rt k0 s))
