------------------------------------------------------------------------
-- Substrate.Algebra.List.Wedge
--
-- THE FREE MONOID FOUNDED ON THE WEDGE — `List A` as a `DivStr`, a fourth
-- (parametric) foundational root. This is the root where the wedge's defining
-- phrase and the carrier's own structure COINCIDE exactly: `recon q b r =
-- (q copies of b) ++ r` is, verbatim, "q copies of b, then the remainder r"
-- — the description of the generic wedge (Wedge.agda) made definitional. The
-- terminal divisor `z` is the empty word `[]`.
--
-- So the free monoid is not just *a* wedge-carrier; it is the wedge's NATIVE
-- carrier — the one whose `recon` is the wedge's intension rather than a ring
-- arithmetic encoding of it. (Connects to the center: the free monoid is the
-- free construction; here it sits on the wedge basis as a root of the sphere.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.List.Wedge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _++_)
open import Substrate.Algebra.Wedge using (DivStr)

-- q copies of b, concatenated (the quotient's free-monoid scale).
lrepeat : {A : Set} → ℕ → List A → List A
lrepeat zero    _ = []
lrepeat (suc n) b = b ++ lrepeat n b

List-div : Set → DivStr
List-div A = record { C = List A ; z = [] ; recon = λ q b r → lrepeat q b ++ r }
