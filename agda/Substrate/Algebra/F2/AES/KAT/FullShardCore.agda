{-# OPTIONS --safe --without-K #-}
-- Shared core for the SHARDED full-encrypt KAT: the fold-append composition
-- primitive that stitches the sealed per-shard round-fold midpoints.
module Substrate.Algebra.F2.AES.KAT.FullShardCore where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Vec using (Vec; _∷_; []; _++_)
open import Substrate.Algebra.F2.AES.Cipher using (fold)

fold-++ : ∀ {A S : Set} {m n} (f : A → S → S) (xs : Vec A m) (ys : Vec A n) (s : S)
        → fold f (xs ++ ys) s ≡ fold f ys (fold f xs s)
fold-++ f []       ys s = refl
fold-++ f (x ∷ xs) ys s = fold-++ f xs ys (f x s)
