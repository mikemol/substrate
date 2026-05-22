------------------------------------------------------------------------
-- Substrate.Algebra.Z6-FieldBond
--
-- Z/6 ≅ F₂ × F₃ via the CRT bond — substrate's first FieldBond
-- instance.
--
-- Z/6 = ℤ/6ℤ has order 6 = 2 · 3 with gcd(2, 3) = 1, so by the
-- Chinese Remainder Theorem Z/6 decomposes as Z/2 × Z/3 = F₂ × F₃.
-- The CRT iso IS the bond's structural content; it provides BOTH
-- the forward bond Z/6 → F₂ × F₃ (mod 2, mod 3 simultaneously) AND
-- the reverse bond F₂ × F₃ → Z/6 (the unique element with the given
-- residues).
--
-- Both bonds are oriented (forward and backward); the orientation
-- distinguishes the source-field from the target. Substrate's
-- FieldBond primitive records each direction explicitly.
--
-- Per [[project-3plus1-is-cone-instance]] bond extension: Z/6 is the
-- simplest non-prime-power case where the structure CANNOT live in
-- a single F_q. It requires two host fields (F₂ and F₃) connected
-- by the CRT bond.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z6-FieldBond where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FieldBond

------------------------------------------------------------------------
-- N-1: The carriers.
------------------------------------------------------------------------

Z6 : Set
Z6 = Fin 6

F₂×F₃ : Set
F₂×F₃ = Fin 2 × Fin 3

------------------------------------------------------------------------
-- N-2: The CRT forward map Z/6 → F₂ × F₃.
--
--   n ↦ (n mod 2, n mod 3)
------------------------------------------------------------------------

crt-forward : Z6 → F₂×F₃
crt-forward zero                                                = zero , zero
crt-forward (suc zero)                                          = suc zero , suc zero
crt-forward (suc (suc zero))                                    = zero , suc (suc zero)
crt-forward (suc (suc (suc zero)))                              = suc zero , zero
crt-forward (suc (suc (suc (suc zero))))                        = zero , suc zero
crt-forward (suc (suc (suc (suc (suc zero)))))                  = suc zero , suc (suc zero)

------------------------------------------------------------------------
-- N-3: The CRT reverse map F₂ × F₃ → Z/6.
--
-- The inverse of crt-forward, by direct case-enumeration.
------------------------------------------------------------------------

crt-backward : F₂×F₃ → Z6
crt-backward (zero , zero)                          = zero
crt-backward (suc zero , suc zero)                  = suc zero
crt-backward (zero , suc (suc zero))                = suc (suc zero)
crt-backward (suc zero , zero)                      = suc (suc (suc zero))
crt-backward (zero , suc zero)                      = suc (suc (suc (suc zero)))
crt-backward (suc zero , suc (suc zero))            = suc (suc (suc (suc (suc zero))))

------------------------------------------------------------------------
-- N-4: The roundtrip — crt-backward ∘ crt-forward ≡ id on Z/6.
--
-- Six refl cases (one per Z/6 element).
------------------------------------------------------------------------

crt-roundtrip : (n : Z6) → crt-backward (crt-forward n) ≡ n
crt-roundtrip zero                                                = refl
crt-roundtrip (suc zero)                                          = refl
crt-roundtrip (suc (suc zero))                                    = refl
crt-roundtrip (suc (suc (suc zero)))                              = refl
crt-roundtrip (suc (suc (suc (suc zero))))                        = refl
crt-roundtrip (suc (suc (suc (suc (suc zero)))))                  = refl

------------------------------------------------------------------------
-- N-5: The two FieldBond instances.
------------------------------------------------------------------------

Z6→F₂×F₃-bond : FieldBond Z6 F₂×F₃
Z6→F₂×F₃-bond = record { bond = crt-forward }

F₂×F₃→Z6-bond : FieldBond F₂×F₃ Z6
F₂×F₃→Z6-bond = record { bond = crt-backward }

------------------------------------------------------------------------
-- N-6: Capstone.
--
-- After this slice: Z/6 = F₂ × F₃ via the CRT bond IS the substrate's
-- first non-trivial FieldBond instance. The forward and backward
-- bonds together realize the CRT iso.
--
-- Per [[project-3plus1-is-cone-instance]] bond extension:
-- 6 = 2 · 3 is the simplest non-prime-power total. The structure
-- requires TWO host fields (F₂, F₃) with bonds in both directions
-- to fully capture the CRT iso.
--
-- Per [[project-composite-torsion-euler-substrate]]: Z/6's
-- decomposition is the substrate's worked example of composite
-- torsion via CRT. Euler-Fermat applied to Z/6 reduces to applying
-- it independently to each prime-power factor (F₂ and F₃), with the
-- bond combining the results.
--
-- Deferred follow-ons:
--
--   * **Roundtrip in the other direction**: forward ∘ backward ≡ id
--     on F₂ × F₃ (6 refl cases on the 6 elements of F₂ × F₃).
--
--   * **Generic CRT for any coprime pair (m, n)**: parametric module
--     `crt-iso : (gcd m n ≡ 1) → Z/(m·n) ≅ Z/m × Z/n`. Substantial;
--     needs gcd machinery.
--
--   * **Multi-field tower for 168 = 2³·3·7**: bonds across F₂³, F₃,
--     F₇, realizing the substrate's |PSL(2,7)|-gauge structure per
--     project_reserved_selfdual_bijection_gauge.
------------------------------------------------------------------------
