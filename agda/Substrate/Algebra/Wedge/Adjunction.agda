------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Adjunction
--
-- Free ⊣ Forgetful, UNIFORM over every carrier, falling out of the wedge —
-- and its triangle law IS the witness `a = recon q b r`.
--
-- Forgetful = `eval = recon`: evaluate a term (q, b, r) to its value.
-- Free      = package an element-with-decomposition as that term.
-- The adjunction's defining hom-set bijection
--      Wedge D a b   ≅   Term D a b        (uniform in D : DivStr)
-- is here DEFINITIONAL — `Term D a b = Σ q, r. a ≡ recon q b r` is the same
-- data as a wedge, so the round-trips are `refl` (record/Σ eta). That is the
-- strongest possible form of the hom-iso: not merely a bijection, an identity
-- of data.
--
-- The "witness read twice" lives where it actually is: the FORGETFUL
-- orientation `eval q b r ≡ a` is the Free orientation `a ≡ eval q b r` read
-- backward (`sym`), and reading it twice cancels (`sym-sym`). `eval-eq` is
-- the counit/triangle (Forgetful ∘ Free = id on the value) = the witness.
--
-- HONEST SCOPE: this is the unit/counit/triangle CORE that falls out of the
-- wedge — the hom-iso and triangle-as-witness. Functoriality / the
-- naturality square (the genuine 2-categorical content) is NOT spelled out.
-- What is claimed is exactly what compiles.
--
-- At D = ℕ-div: "a wedge of a against b IS a pair (q, r) with q·b + r ≡ a" —
-- the division theorem, as the adjunction's hom-set.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Adjunction where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge
  using (DivStr; C; recon; Wedge; quot; rem; wedge-eq; forget; forget-correct)

------------------------------------------------------------------------
-- 0. The witness read twice cancels.
------------------------------------------------------------------------

sym-sym : {A : Set} {x y : A} (p : x ≡ y) → sym (sym p) ≡ p
sym-sym refl = refl

------------------------------------------------------------------------
-- 1. Forgetful (eval) and the term type it evaluates.
------------------------------------------------------------------------

eval : (D : DivStr) → ℕ → C D → C D → C D
eval = recon

-- the FREE term for a against b: a (q, r) decomposing a. (Same orientation
-- as the wedge — so the hom-iso below is definitional.)
Term : (D : DivStr) → C D → C D → Set
Term D a b = Σ ℕ (λ q → Σ (C D) (λ r → a ≡ recon D q b r))

------------------------------------------------------------------------
-- 2. The hom-set bijection Wedge ≅ Term, uniform in D — DEFINITIONAL.
------------------------------------------------------------------------

to : {D : DivStr} {a b : C D} → Wedge D a b → Term D a b
to w = quot w , rem w , wedge-eq w

from : {D : DivStr} {a b : C D} → Term D a b → Wedge D a b
from (q , r , e) = record { quot = q ; rem = r ; wedge-eq = e }

-- One round-trip is definitional: re-packaging a wedge as a term and back
-- is the identity (Σ/record eta), b flowing straight from w's type.
from∘to : {D : DivStr} {a b : C D} (w : Wedge D a b) → from (to w) ≡ w
from∘to _ = refl

-- The other direction (`to (from t) ≡ t`) is ALSO definitional, but cannot
-- be STATED on an abstract term `t`: the wedge's divisor `b` appears only
-- under `recon` (a carrier-supplied, non-injective function), so `from t`
-- leaves `b` an unsolved meta. It is recoverable once `b` is concrete — i.e.
-- exactly the non-injective-divisor quirk the substrate already meets in
-- BezoutMod (where `g` only occurs as `g mod-suc m`). So: bijection, with one
-- side needing the divisor pinned.

------------------------------------------------------------------------
-- 3. The triangle law = the witness. The counit (eval) after the unit
--    (package) returns the element: `eval q b r ≡ a`, i.e. `forget w ≡ a`.
--    This is the Free orientation read backward; reading it twice is id.
------------------------------------------------------------------------

eval-eq : {D : DivStr} {a b : C D} (w : Wedge D a b) →
          eval D (quot w) b (rem w) ≡ a
eval-eq w = sym (wedge-eq w)

triangle : {D : DivStr} {a b : C D} (w : Wedge D a b) → forget w ≡ a
triangle = forget-correct

-- re-orienting the witness twice is the identity (the adjunction is the
-- witness read twice — here, literally).
reorient : {D : DivStr} {a b : C D} (w : Wedge D a b) →
           sym (eval-eq w) ≡ wedge-eq w
reorient w = sym-sym (wedge-eq w)
