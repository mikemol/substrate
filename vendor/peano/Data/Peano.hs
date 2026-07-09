-- | Data.Peano — a lazy unary natural, sufficient for Agda's @Agda.Utils.Size@.
--
-- WHY THIS EXISTS (read before changing)
--   Agda 2.8.0 build-depends on the Hackage package @peano >= 0.1.0.1 && < 0.2@.
--   Hackage is unreachable from this container (403) and the package has no
--   discoverable GitHub mirror. This module is a REIMPLEMENTATION, not a vendored
--   copy: it provides exactly the surface Agda consumes, and nothing else.
--
-- THE SURFACE AGDA ACTUALLY USES (verified against Agda-2.8.0 source, not guessed)
--   The sole import in all of Agda is:
--       src/full/Agda/Utils/Size.hs:14   import Data.Peano as X ( Peano(Zero,Succ) )
--   and the sole consumers of the resulting values are:
--       Utils/Size.hs      natSize = foldr (const Succ) Zero    -- constructors
--       Utils/Size.hs      natSize = toEnum . size              -- Enum
--       Utils/String.hs    natSize xs == 1                      -- Eq + Num literal
--       Syntax/Internal/SanityCheck.hs  natSize d >= toEnum n   -- Ord + Enum
--   Hence the required instances are exactly: Eq, Ord, Enum, Num.
--   Upstream also exports PeanoOrd and friends; Agda imports none of them, so they
--   are deliberately absent (a reimplementation should not invent surface).
--
-- THE LAZINESS CONTRACT (the load-bearing property)
--   natSize is documented as "Lazily compute a (possibly infinite) size. Use when
--   comparing a size against a fixed number." So foldr (const Succ) Zero is applied
--   to possibly-infinite structures and the comparison must short-circuit at the
--   first constructor difference rather than forcing the spine.
--   Derived Eq/Ord on `data Peano = Zero | Succ Peano` have exactly this property.
--   Asserted by the test-suite (vendor/peano/test/Spec.hs), not assumed.
--
-- WHAT IS DELIBERATELY PARTIAL
--   negate has no meaning on a unary natural; it errors, as upstream does.
--   (-) is TRUNCATED subtraction (monus): 2 - 5 == 0. Agda calls neither.
module Data.Peano ( Peano(Zero, Succ) ) where

-- | A unary natural. Lazy in its tail: @Succ undefined@ is a legitimate value whose
--   Eq/Ord comparison against a finite Peano terminates.
data Peano = Zero | Succ Peano
  deriving (Eq, Ord, Show, Read)
  -- NB: derived Eq/Ord ARE the laziness contract. Do not replace them with
  -- fromEnum-based instances: that forces the (possibly infinite) spine.

instance Enum Peano where
  toEnum n
    | n <= 0    = Zero
    | otherwise = Succ (toEnum (n - 1))
  fromEnum Zero     = 0
  fromEnum (Succ n) = 1 + fromEnum n

instance Num Peano where
  fromInteger n
    | n <= 0    = Zero
    | otherwise = Succ (fromInteger (n - 1))

  Zero   + m = m
  Succ n + m = Succ (n + m)

  Zero   * _ = Zero
  Succ n * m = m + n * m

  -- truncated (monus) subtraction; total on naturals
  Zero   - _      = Zero
  n      - Zero   = n
  Succ n - Succ m = n - m

  abs = id

  signum Zero     = Zero
  signum (Succ _) = Succ Zero

  negate = error "Data.Peano.negate: a unary natural has no additive inverse"
