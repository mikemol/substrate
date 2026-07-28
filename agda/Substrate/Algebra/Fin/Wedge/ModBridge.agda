------------------------------------------------------------------------
-- Substrate.Algebra.Fin.Wedge.ModBridge
--
-- THE WEDGE CONSTRUCTS THE GENERAL-N CYCLIC BRIDGE. `ℕ-div ↠ Cyc-div n`,
-- the modular reduction (mod (suc n)) as a `Bridge` — the general-modulus
-- generalization of `ParityBridge` (which is the n=1 case, modulus 2). A
-- `Bridge` is a carrier translation that RESPECTS `recon`, and modular
-- reduction does (it is the ℕ → Z/(suc n) ring homomorphism). So this is
-- a bridge the wedge CONSTRUCTS, not one bolted on, completing the
-- "arithmetic" family of roots (ℕ-div, ℤ-div, F₂-div, and now the whole
-- Z/(suc n) tower).
--
-- The translate is `_mod-suc n` landed into Fin (suc n) via `fromℕ<`.
-- `respects` is the ring-hom fact, but — crucially — we do NOT re-prove
-- it: the substrate already carries modular reduction as a ring
-- homomorphism in Algebra.Nat.Mod.Homomorphism (mod-add-hom /
-- mod-*-right / mod-+-left). The ENTIRE content of `respects` is the
-- ℕ-level identity
--     (q·b + r) mod n  ≡  (q·(b mod n) + (r mod n)) mod n
-- assembled from those, then lifted into Fin (suc n) equality by
-- `toℕ-injective` (carrier elements are distinguished by `toℕ`) using the
-- round-trip `toℕ-fromℕ<`. No new mod ring-hom lemmas were needed.
--
-- Because a Bridge transports the whole Euclidean apparatus
-- (Bridge.transport-trace), `modn-bridge n` carries gcd / Bézout / mod
-- from ℕ onto Z/(suc n): the number theory flows along the geodesic.
--
-- AGREEMENT WITH PARITY (n=1, modulus 2): `parity` in spirit is this
-- bridge at n=1 — `parity (suc m) = 𝟙 +₂ parity m` is the 2-element wrap,
-- and `_mod-suc 1` on ℕ is the same alternation 0,1,0,1,…. We do not prove
-- F₂ ≅ Cyc-div 1 here (it would need the F₂ ≅ Fin 2 carrier iso); the two
-- are the same construction at different moduli, as the docstrings record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Fin.Wedge.ModBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties using (toℕ-fromℕ<; toℕ-injective)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)
open import Substrate.Algebra.Nat.Mod.Homomorphism
  using (mod-add-hom; mod-mult-hom; mod-+-left)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div; Trace)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; transport-trace)
open import Substrate.Algebra.Fin.Wedge using (Cyc-div; recon-cyc)

------------------------------------------------------------------------
-- 1. The translation: modular reduction ℕ → Z/(suc n) = Fin (suc n).
------------------------------------------------------------------------

reduce : (n : ℕ) → ℕ → Fin (suc n)
reduce n a = fromℕ< (mod-suc-bound a n)

-- `toℕ` reads the translation as the ℕ-level residue (the round-trip).
toℕ-reduce : (n a : ℕ) → toℕ (reduce n a) ≡ a mod-suc n
toℕ-reduce n a = toℕ-fromℕ< (mod-suc-bound a n)

------------------------------------------------------------------------
-- 2. The ℕ-level ring-hom identity that IS the content of `respects`.
--
--   (q·b + r) mod n ≡ (q·(b mod n) + (r mod n)) mod n
--
-- Assembled from the existing modular ring-homomorphism lemmas; no new
-- mod arithmetic is introduced here.
------------------------------------------------------------------------

respects-ℕ : (n q b r : ℕ) →
             (q * b + r) mod-suc n
               ≡ ((q mod-suc n) * (b mod-suc n) + (r mod-suc n)) mod-suc n
respects-ℕ n q b r =
  trans (mod-add-hom (q * b) r n)
        (trans (cong (λ z → (z + (r mod-suc n)) mod-suc n)
                     (mod-mult-hom q b n))
               (mod-+-left ((q mod-suc n) * (b mod-suc n)) (r mod-suc n) n))

------------------------------------------------------------------------
-- 3. Reading the two recon-sides through `toℕ`.
--
--   LHS = translate (recon ℕ-div q b r) = reduce n (q·b + r)
--   RHS = recon (Cyc-div n) q (reduce b) (reduce r)
-- The bridge equation is their equality in Fin (suc n); both read through
-- `toℕ` into the two sides of `respects-ℕ`.
------------------------------------------------------------------------

toℕ-RHS : (n q b r : ℕ) →
          toℕ (recon-cyc n (reduce n q) (reduce n b) (reduce n r))
            ≡ ((q mod-suc n) * (b mod-suc n) + (r mod-suc n)) mod-suc n
toℕ-RHS n q b r =
  trans (toℕ-reduce n (toℕ (reduce n q) * toℕ (reduce n b) + toℕ (reduce n r)))
  (trans (cong (λ z → (z * toℕ (reduce n b) + toℕ (reduce n r)) mod-suc n)
               (toℕ-reduce n q))
  (trans (cong (λ z → ((q mod-suc n) * z + toℕ (reduce n r)) mod-suc n)
               (toℕ-reduce n b))
         (cong (λ z → ((q mod-suc n) * (b mod-suc n) + z) mod-suc n)
               (toℕ-reduce n r))))

------------------------------------------------------------------------
-- 4. The bridge.
------------------------------------------------------------------------

respects-cyc : (n q b r : ℕ) →
               reduce n (q * b + r) ≡ recon-cyc n (reduce n q) (reduce n b) (reduce n r)
respects-cyc n q b r = toℕ-injective
  (trans (toℕ-reduce n (q * b + r))
         (trans (respects-ℕ n q b r) (sym (toℕ-RHS n q b r))))

modn-bridge : (n : ℕ) → Bridge ℕ-div (Cyc-div n)
modn-bridge n = record
  { translate = reduce n
  ; respects  = respects-cyc n
  ; z-pres    = toℕ-injective (toℕ-reduce n zero)
  }

------------------------------------------------------------------------
-- 5. The payoff: the bridge transports the whole Euclidean apparatus
--    (hence gcd / Bézout / mod) from ℕ onto Z/(suc n).
------------------------------------------------------------------------

modn-transport-trace : (n : ℕ) {a b g : ℕ} →
  Trace ℕ-div a b g →
  Trace (Cyc-div n) (reduce n a) (reduce n b) (reduce n g)
modn-transport-trace n = transport-trace (modn-bridge n)
