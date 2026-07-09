-- Contract tests for the Data.Peano reimplementation. Each corresponds to a call
-- site in Agda-2.8.0. Run: ghc -O0 -o spec test/Spec.hs -i. && ./spec
module Main (main) where
import Data.Peano
import System.Exit (exitFailure, exitSuccess)
import System.Timeout (timeout)

p :: Int -> Peano
p = toEnum

-- the LOAD-BEARING property: comparison against an infinite Peano must terminate
infinite :: Peano
infinite = foldr (const Succ) Zero [(1::Int)..]

check :: String -> Bool -> IO Bool
check name b = do putStrLn ((if b then "  ok   " else "  FAIL ") ++ name); return b

main :: IO ()
main = do
  -- Agda: Utils/String.hs   natSize xs == 1
  r1 <- check "Eq + Num literal:  p 1 == 1"            (p 1 == 1)
  -- Agda: SanityCheck.hs    natSize d >= toEnum n
  r2 <- check "Ord + Enum:        p 5 >= toEnum 3"     (p 5 >= toEnum (3::Int))
  -- Agda: Utils/Size.hs     natSize = foldr (const Succ) Zero
  r3 <- check "constructors:      foldr Succ Zero [1,2] == p 2"
              (foldr (const Succ) Zero [(1::Int),2] == p 2)
  -- laziness: MUST terminate on an infinite Peano
  r4 <- timeout 2000000 (return $! (infinite == 1))    >>= check "lazy Eq  on infinite" . (== Just False)
  r5 <- timeout 2000000 (return $! (infinite >= p 3))  >>= check "lazy Ord on infinite" . (== Just True)
  -- arithmetic sanity (not used by Agda, but the Num instance must be coherent)
  r6 <- check "arith:             2+3=5, 2*3=6, 5-2=3, 2-5=0"
              (p 2 + p 3 == p 5 && p 2 * p 3 == p 6 && p 5 - p 2 == p 3 && p 2 - p 5 == p 0)
  r7 <- check "Enum roundtrip:    fromEnum . toEnum == id"
              (all (\n -> fromEnum (p n) == n) [0..5])
  if and [r1,r2,r3,r4,r5,r6,r7] then exitSuccess else exitFailure
