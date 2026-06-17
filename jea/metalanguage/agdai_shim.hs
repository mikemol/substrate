{-# LANGUAGE OverloadedStrings #-}
-- agdai_shim.hs — Φ4: Agda-2.8.0 .agdai -> JSON-lines core-node schema for jea_agdai.intern_signature.
-- Decodes an interface with Agda's OWN version-matched deserialiser (no hand-decoded tag table), walks
-- each definition's elaborated TYPE (Agda's types ARE the segmentation), emits one node per core term:
--   {"id":int,"constructor":str,"qname":str|null,"index":int|null,"children":[int,...]}
-- Trees here; cross-term sharing is recovered by jea_pyalg's hash-cons in intern_signature.
--
-- BUILD (needs the Agda-2.8.0 library in the GHC package db -- `ghc-pkg list Agda`):
--   ghc -package Agda -O0 -o agdai_shim agdai_shim.hs
-- RUN:  ./agdai_shim Foo.agdai > foo_core.jsonl     (then jea_agdai.intern_signature / core_intern_agdai)
-- The .agdai MUST be current-toolchain (same Agda that links here); a stale/older-version interface
-- decodes to Nothing -> rebuild it (`agda --safe Foo.agda`). VALIDATED: Emit.agdai -> 18 defs, 62 core
-- nodes -> interned 20 (3.1x sharing) with full parent->child edges (the typeholer's segmentation).
module Main where

import System.Environment (getArgs)
import System.IO (hPutStrLn, stderr)
import Data.IORef
import Data.List (intercalate)
import qualified Data.ByteString.Lazy as BL
import qualified Data.HashMap.Strict as HMap

import Agda.TypeChecking.Serialise (decodeInterface)
import Agda.TypeChecking.Monad.Base (runTCMTop, iSignature, _sigDefinitions, defType, Interface)
import Agda.TypeChecking.Monad.Options (setCommandLineOptions)
import Agda.Interaction.Options (defaultOptions)
import Agda.Syntax.Common.Pretty (prettyShow)
import Agda.Syntax.Common (unArg)
import Agda.Syntax.Internal
  ( Term(..), Type, Elim, Elim'(..), Abs, unAbs, unEl, unDom, ConHead(..), QName )

fresh :: IORef Int -> IO Int
fresh r = atomicModifyIORef' r (\n -> (n+1, n))

-- emit one node record; return its id. children already emitted (post-order).
emit :: IORef Int -> String -> Maybe String -> Maybe Int -> [Int] -> IO Int
emit r ctor mq mi kids = do
  i <- fresh r
  let q  = maybe "null" (\s -> "\"" ++ esc s ++ "\"") mq
      ix = maybe "null" show mi
      cs = "[" ++ intercalate "," (map show kids) ++ "]"
  putStrLn $ "{\"id\":" ++ show i ++ ",\"constructor\":\"" ++ ctor
           ++ "\",\"qname\":" ++ q ++ ",\"index\":" ++ ix ++ ",\"children\":" ++ cs ++ "}"
  return i

esc :: String -> String
esc = concatMap (\c -> case c of '"' -> "\\\""; '\\' -> "\\\\"; _ -> [c])

walkType :: IORef Int -> Type -> IO Int
walkType r = walkTerm r . unEl

walkElim :: IORef Int -> Elim -> IO [Int]
walkElim r (Apply a)    = (:[]) <$> walkTerm r (unArg a)
walkElim r (IApply x y z) = mapM (walkTerm r) [x,y,z]
walkElim r (Proj _ qn)  = (:[]) <$> emit r "Proj" (Just (prettyShow qn)) Nothing []

walkTerm :: IORef Int -> Term -> IO Int
walkTerm r t = case t of
  Var i es     -> do ks <- concat <$> mapM (walkElim r) es; emit r "Var" Nothing (Just i) ks
  Lam _ b      -> do k <- walkTerm r (unAbs b); emit r "Lam" Nothing Nothing [k]
  Lit _        -> emit r "Lit" Nothing Nothing []
  Def qn es    -> do ks <- concat <$> mapM (walkElim r) es; emit r "Def" (Just (prettyShow qn)) Nothing ks
  Con ch _ es  -> do ks <- concat <$> mapM (walkElim r) es; emit r "Con" (Just (prettyShow (conName ch))) Nothing ks
  Pi d b       -> do kd <- walkType r (unDom d); kc <- walkType r (unAbs b); emit r "Pi" Nothing Nothing [kd,kc]
  Sort _       -> emit r "Sort" Nothing Nothing []
  Level _      -> emit r "Level" Nothing Nothing []
  MetaV _ es   -> do ks <- concat <$> mapM (walkElim r) es; emit r "MetaV" Nothing Nothing ks
  DontCare u   -> do k <- walkTerm r u; emit r "DontCare" Nothing Nothing [k]
  Dummy _ es   -> do ks <- concat <$> mapM (walkElim r) es; emit r "Dummy" Nothing Nothing ks

main :: IO ()
main = do
  [path] <- getArgs
  bs <- BL.readFile path
  res <- runTCMTop (setCommandLineOptions defaultOptions >> decodeInterface bs)
  case res of
    Left _          -> hPutStrLn stderr "agdai_shim: decode TCErr" >> ioError (userError "TCErr")
    Right Nothing   -> hPutStrLn stderr "agdai_shim: decode Nothing (stale/wrong-version .agdai; rebuild it)" >> ioError (userError "Nothing")
    Right (Just i)  -> do
      r <- newIORef 0
      let defs = HMap.toList (_sigDefinitions (iSignature i))
      mapM_ (\(_, d) -> walkType r (defType d)) defs
      n <- readIORef r
      hPutStrLn stderr ("agdai_shim: " ++ show (length defs) ++ " definitions -> " ++ show n ++ " core nodes")
