------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOFFI — ACTUAL emission: the extruder's reduction trace RUN as
-- real Haskell output. Everything up to 289 PROVES emission (--safe, small); this PERFORMS it, via Agda's GHC
-- backend (FFI). --safe FORBIDS FFI, so this module drops --safe and is ISOLATED from the proven core — it
-- imports the proven emit-programs and runs them through Haskell's real IO + putStr.
--
-- The bridge: interpret the finite emit-monad IO (285) into Haskell's IO by walking the ret/emit tree,
-- putStr-ing each emitted output. run-emit (286a) already turns a bounded run into an IO HeadShape ⊤; here we
-- render each HeadShape to a String and putStr it — so the reduction trace ACTUALLY PRINTS.
--
-- NOTE (non-safe by necessity): FFI/COMPILE-GHC cannot be --safe. This is the ONE impure module; the entire
-- proven emit-side (285-289) stays --safe and small. This module is the performance boundary.
------------------------------------------------------------------------

{-# OPTIONS --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOFFI where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Agda.Builtin.List using (List; []; _∷_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape; isS; isK; isI; isApp)
open import Substrate.Category.UniversalProperty.ExtrudeIO HeadShape using (IO; ret; emit)
open import Substrate.Category.UniversalProperty.ExtrudeIORunEmit using (run-emit)
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream using (CoIO; run-coio; take-coio)
import Substrate.Foundation.List as SL

------------------------------------------------------------------------
-- ① HASKELL PRIMITIVES via FFI: String, Haskell's IO, putStr, and sequencing. Mapped to real GHC.
------------------------------------------------------------------------
open import Agda.Builtin.IO renaming (IO to HIO)
data HUnit : Set where hunit : HUnit
{-# COMPILE GHC HUnit = data () (()) #-}

postulate
  HString  : Set
  hputStrs : List HString → HIO HUnit    -- print a whole list of chunks in one Haskell action

{-# FOREIGN GHC import qualified Data.Text as T #-}
{-# FOREIGN GHC import qualified Data.Text.IO as TIO #-}
{-# COMPILE GHC HString = type T.Text #-}
{-# COMPILE GHC hputStrs = \xs -> mapM_ TIO.putStr xs #-}

------------------------------------------------------------------------
-- ② RENDER a HeadShape to a Haskell String (a short tag per observation).
------------------------------------------------------------------------
postulate
  hS hK hI hApp hVar hOther : HString
  hnl : HString

-- map each HeadShape constructor to a tag. (HeadShape's constructors from ExtrudeStepDecidable.)
render : HeadShape → HString
render isS   = hS
render isK   = hK
render isI   = hI
render isApp = hApp

{-# COMPILE GHC hS     = T.pack "S "  #-}
{-# COMPILE GHC hK     = T.pack "K "  #-}
{-# COMPILE GHC hI     = T.pack "I "  #-}
{-# COMPILE GHC hApp   = T.pack "@ "  #-}
{-# COMPILE GHC hVar   = T.pack "v "  #-}
{-# COMPILE GHC hOther = T.pack ". "  #-}
{-# COMPILE GHC hnl    = T.pack "\n"  #-}

------------------------------------------------------------------------
-- ③ INTERPRET the finite emit-monad IO into Haskell's IO: walk ret/emit, putStr each rendered output.
------------------------------------------------------------------------
collect-str : {A : Set} → IO A → List HString
collect-str (ret a)    = []
collect-str (emit o k) = render o ∷ collect-str k

interp : {A : Set} → IO A → HIO HUnit
interp m = hputStrs (collect-str m)

------------------------------------------------------------------------
-- ④ ACTUAL EMISSION: run a term's bounded reduction and PRINT its observation trace.
------------------------------------------------------------------------
emit-run : ℕ → Tm⟦533ef80d⟧ → HIO HUnit
emit-run fuel t = interp (run-emit fuel t)

-- a concrete demo term + a main that ACTUALLY emits its trace (filled at the instantiation site):
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_)

-- ④' a LITERAL emit program (sanity — prints "S K I "):
literal : IO HUnit
literal = emit isS (emit isK (emit isI (ret hunit)))

-- ⑤ the RUN emits (finite IO): a real term's bounded reduction trace via run-emit:
demo : Tm⟦533ef80d⟧
demo = I ∙ K                         -- I ∙ K → K

-- ⑥ (⟡extrude-io-ffi-stream) stream the UNBOUNDED costream (run-coio, 289) — take a prefix of the infinite
--    emit and print it. Distinct from ⑤: this walks the COINDUCTIVE costream (CoIO), not the finite IO.
-- render a Substrate.List of HeadShapes into a builtin List of HStrings (the FFI boundary):
render-all : SL.List HeadShape → List HString
render-all SL.[]        = []
render-all (o SL.∷ os)  = render o ∷ render-all os

stream-coio : ℕ → Tm⟦533ef80d⟧ → HIO HUnit
stream-coio n t = hputStrs (render-all (take-coio n (run-coio t)))

main : HIO HUnit
main = stream-coio 8 demo            -- stream the first 8 emissions of the UNBOUNDED reduction costream
