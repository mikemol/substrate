{-# OPTIONS --safe --without-K #-}
-- GF(2⁸) is a CommutativeRing — Ring (AI-6f) + gmul-comm. Validates the record
-- and the (F₂,m)/(GF(2⁸),f) instantiation path for the R[y]/(f) tower (AI-17 B4).
module Substrate.Algebra.F2.GF256.CommRing where
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
open import Substrate.Algebra.F2.GF256.Mul using (gmul-comm)
open import Substrate.Algebra.F2.GF256.Ring using (GF256-Ring)
GF256-CommRing : CommutativeRing _
GF256-CommRing = record { ring = GF256-Ring ; *-comm = gmul-comm }
