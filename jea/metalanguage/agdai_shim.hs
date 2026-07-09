{-# LANGUAGE OverloadedStrings #-}
-- agdai_shim.hs — Φ4: Agda-2.8.0 .agdai -> JSON-lines core-node schema for jea_agdai.intern_signature.
-- Decodes an interface with Agda's OWN version-matched deserialiser (no hand-decoded tag table), walks
-- each definition's elaborated TYPE (Agda's types ARE the segmentation), emits one node per core term:
--   {"id":int,"constructor":str,"qname":str|null,"index":int|null,"children":[int,...]}
-- and one DEFMARK per definition, now carrying its ELABORATED SORT:
--   {"unit":qname,"root":int,"kind":str,"members":[str],"sort":"Type"|…,"level":int|null}
-- `level` is the universe the definition INHABITS (Πs peeled; if the codomain is itself
-- `Sort s`, that s — a record former's type is `… → Set₁`, whose own sort is Set₂, so
-- taking getSort (defType d) directly is off by one). Set₁ debt is a SORT, not a token:
-- grepping `Set₁` in source counts declarations (1 token ↦ ~4 core definitions: record,
-- constructor, transp-, hcomp-) and misses Set₁-TYPED FUNCTIONS entirely.
-- Trees here; cross-term sharing is recovered by jea_pyalg's hash-cons in intern_signature.
--
-- VERIFIED against Agda-2.8.0 (2026-07-09). Two 2.6.3-era facts had rotted here:
--   * Agda.Utils.Pretty was removed in 2.6.4 -> Agda.Syntax.Common.Pretty.
--   * Agda 2.7 unified Type/Prop/SSet into `Univ :: Univ -> Level -> Sort'`,
--     so a closed sort matches `Univ _ (Max n [])`, not `Type (Max n [])`.
-- The previous header claimed 2.8.0 while the source only compiled against 2.6.3.
-- A header states intent at writing time, not the artifact's truth (D-header-is-not-a-fact).
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
import Agda.TypeChecking.Monad.Base
  ( runTCMTop, iSignature, _sigDefinitions, defType, theDef, Defn(..), funClauses
  , dataCons, recConHead, recFields, Interface )
import Agda.TypeChecking.Monad.Options (setCommandLineOptions)
import Agda.Interaction.Options (defaultOptions)
import Agda.Syntax.Common.Pretty (prettyShow)
import Agda.Syntax.Common (unArg, namedArg)
import Agda.Syntax.Internal
  ( Term(..), Type, Elim, Elim'(..), Abs, unAbs, unEl, unDom, ConHead(..), QName, Clause
  , clauseBody, namedClausePats, DeBruijnPattern, Pattern'(..), dbPatVarName, dbPatVarIndex
  , Sort, Sort'(..), Level'(..), getSort )

-- | The universe level of a closed sort, if it has one. `Type (Max 0 []) -> Just 0`,
--   `Type (Max 1 []) -> Just 1`. Level-polymorphic / Prop / Inf -> Nothing.
-- | The universe level of a closed sort, if it has one.
--   Agda 2.7 unified Type/Prop/SSet into `Univ :: Univ -> Level -> Sort'`.
--   Verified against Agda-2.8.0 by asking GHC to enumerate Sort's constructors.
levelOf :: Sort -> Maybe Integer
levelOf (Univ _ (Max n [])) = Just n
levelOf _                   = Nothing

sortKind :: Sort -> String
sortKind s = case s of
  Univ u _ -> show u
  Inf _ _  -> "Inf"
  SizeUniv -> "SizeUniv"
  _        -> "other"

-- | Peel the type telescope's Pis and return the CODOMAIN's sort. When the codomain
--   is itself a universe (`Sort s`) the definition INHABITS s, so return s -- not
--   getSort s, which is one universe up. This off-by-one bites every parameterized
--   definition (a record former's type is `... -> Set1`, whose own sort is Set2).
codomainSort :: Type -> Sort
codomainSort t = case unEl t of
  Pi _ b -> codomainSort (unAbs b)
  Sort s -> s
  _      -> getSort t

sortJSON :: Type -> String
sortJSON t = let s = codomainSort t
             in ",\"sort\":\"" ++ sortKind s ++ "\",\"level\":" ++ maybe "null" show (levelOf s)

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

-- Φ7a: walk a clause's LHS argument patterns (namedClausePats). Agda core is de-Bruijn, so a pattern
-- VARIABLE carries the bound index (alpha-quotiented, like Var); a constructor/def pattern carries the
-- FREE referential qname. This is the segmentation the old shim dropped (it walked only the RHS body) --
-- the LHS is half of every clause and is exactly what tells two same-RHS functions apart by their
-- match structure. Catch-all covers IApplyP (cubical endpoints) etc. without guessing their arity.
walkPat :: IORef Int -> DeBruijnPattern -> IO Int
walkPat r p = case p of
  VarP _ x     -> emit r "PVar"  (Just (dbPatVarName x))         (Just (dbPatVarIndex x)) []
  DotP _ t     -> do k  <- walkTerm r t;                          emit r "PDot"  Nothing Nothing [k]
  ConP ch _ ps -> do ks <- mapM (walkPat r . namedArg) ps;        emit r "PCon"  (Just (prettyShow (conName ch))) Nothing ks
  LitP _ _     ->                                                 emit r "PLit"  Nothing Nothing []
  ProjP _ qn   ->                                                 emit r "PProj" (Just (prettyShow qn)) Nothing []
  DefP _ qn ps -> do ks <- mapM (walkPat r . namedArg) ps;        emit r "PDef"  (Just (prettyShow qn)) Nothing ks
  _            ->                                                 emit r "PVarOther" Nothing Nothing []

-- a clause node groups its LHS patterns + RHS body (the full clause, not just the body, Φ7a). An absurd
-- clause (no body) is patterns-only. funClauses is partial (Function only); other Defns yield no clauses.
walkClause :: IORef Int -> Clause -> IO Int
walkClause r c = do
  ps   <- mapM (walkPat r . namedArg) (namedClausePats c)
  body <- maybe (return []) (fmap (:[]) . walkTerm r) (clauseBody c)
  emit r "Clause" Nothing Nothing (ps ++ body)

clauseNodes :: IORef Int -> Defn -> IO [Int]
clauseNodes r d = case d of
  FunctionDefn{} -> mapM (walkClause r) (funClauses d)
  _              -> return []

-- Φ7b: the inter-definition member edges Agda's typed AST carries -- a datatype's constructors, and a
-- record's (constructor + fields). Each member is ALSO its own top-level Definition (walked in its own
-- right), so this records the PARENT->member link the flat per-def walk drops: a coverage/structure
-- readout can then connect a datatype to its constructors instead of seeing orphan units. Names only
-- (the member's own unit carries its core term); the link rides the parent's unit marker.
defMembers :: Defn -> [String]
defMembers d = case d of
  DatatypeDefn{} -> map prettyShow (dataCons d)
  RecordDefn{}   -> map prettyShow (conName (recConHead d) : map unDom (recFields d))
  _              -> []

-- Φ6: label each definition's Defn KIND. The non-Function kinds need no extra BODY walk -- their members
-- (a datatype's constructors, a record's fields) are themselves separate top-level Definitions, walked in
-- their own right (verified on mat260: every Op/Tm constructor + Transition field is its own unit). So
-- "handle the non-Function Defns" = RECOGNISE + label them (kind in the unit marker), powering a coverage
-- readout, not invent a body they don't have.
defnKind :: Defn -> String
defnKind d = case d of
  FunctionDefn{}      -> "Function"
  DatatypeDefn{}      -> "Datatype"
  RecordDefn{}        -> "Record"
  ConstructorDefn{}   -> "Constructor"
  PrimitiveDefn{}     -> "Primitive"
  PrimitiveSortDefn{} -> "PrimitiveSort"
  DataOrRecSigDefn{}  -> "DataOrRecSig"
  GeneralizableVar{}  -> "GeneralizableVar"
  AbstractDefn{}      -> "Abstract"
  _                   -> "Axiom"

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
      -- one UNIT per definition: a synthetic Defn root over [the elaborated TYPE, each clause BODY].
      -- Type + proof/program bodies = what agda_similarity's text comparison saw. The Defn node is keyed
      -- STRUCTURALLY (no qname in the node) so structurally-identical definitions still intern to ONE node
      -- (the duplicate signal); the qname rides the unit marker for display only. Emitted as
      -- {"unit":qname,"root":id} after the def's nodes, so jea_pysim builds per-def units.
      mapM_ (\(qn, d) -> do
               tr  <- walkType r (defType d)
               cls <- clauseNodes r (theDef d)                 -- Φ7a: full clauses (LHS patterns + RHS)
               sid <- emit r "Defn" Nothing Nothing (tr : cls)
               let mems = defMembers (theDef d)                -- Φ7b: datatype->constructors / record->fields
                   memJSON = "[" ++ intercalate "," (map (\m -> "\"" ++ esc m ++ "\"") mems) ++ "]"
               putStrLn $ "{\"unit\":\"" ++ esc (prettyShow qn) ++ "\",\"root\":" ++ show sid
                        ++ ",\"kind\":\"" ++ defnKind (theDef d) ++ "\",\"members\":" ++ memJSON
                          ++ sortJSON (defType d) ++ "}"
            ) defs
      n <- readIORef r
      hPutStrLn stderr ("agdai_shim: " ++ show (length defs) ++ " definitions -> " ++ show n ++ " core nodes")
