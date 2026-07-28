{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.NOf where

-- The Z₃ word of a row. SINGLE carrier (index 2).

import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.Row

n-of : Row → Word Z₃-Base.Gen
n-of id  = []
n-of r   = Z₃-Base.a ∷ []
n-of r²  = Z₃-Base.a ∷ Z₃-Base.a ∷ []
n-of s   = []
n-of sr  = Z₃-Base.a ∷ []
n-of sr² = Z₃-Base.a ∷ Z₃-Base.a ∷ []
