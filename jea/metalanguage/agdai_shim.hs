{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE TemplateHaskell #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- agdai_shim.hs — Φ4: Agda-2.8.0 .agdai -> JSON-lines core-node schema for jea_agdai.intern_signature.
-- Decodes an interface with Agda's OWN version-matched deserialiser (no hand-decoded tag table), walks
-- each definition's elaborated TYPE (Agda's types ARE the segmentation), emits one node per core term:
--   {"id":int,"constructor":str,"qname":str|null,"index":int|null,"children":[int,...]}
-- Lit/PLit nodes additionally carry the literal VALUE:
--   {"id":int,"constructor":"Lit"|"PLit","qname":null,"index":null,"lit":str,"children":[]}
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
--
-- ⚑⚑ THAT RECIPE IS UNDER-SPECIFIED, AND THE GAP WAS MEASURED (2026-08-14). Bare
-- `-package Agda` takes WHATEVER Agda is registered, which on this box was the Debian
-- `Agda-2.8.0-DJrTbcOFazJDzri4fKrI2F` (built by ghc-9.10.3) while the `agda` BINARY on PATH
-- is a cabal-store build under ghc-9.6.6. Pin the package explicitly (`-package-id` /
-- `-package-db` naming the store the binary embeds) rather than letting resolution choose.
--
-- ⚑ BUT THE MISLINK WAS NOT WHAT BROKE DECODING, AND ASSUMING IT WAS COSTS A REBUILD THAT
-- FIXES NOTHING. Cross-build decode WORKS: `currentInterfaceVersion` is a SOURCE constant of
-- Agda 2.8.0, identical in both builds, so a 9.10.3-linked reader reads a 9.6.6-written
-- interface. Verified on a trivial standalone module, and on the corpus (~93% of cores
-- decoded under exactly that pairing).
--
-- ⚑ WHAT DOES BREAK IS THE DATA DIR, and it is a RUNTIME concern, not a link one. GHC bakes
-- `Paths_Agda.getDataDir` in as a LITERAL (here `/usr/share/libghc-agda-dev`); removing that
-- package left this statically-linked binary intact but dying at
-- `Agda.Interaction.Library:116` for every core. `jea_agdai.agda_datadir` now supplies
-- `Agda_datadir` from `agda --print-agda-data-dir` — so the SHIPPED binary keeps working
-- with no GHC on the machine at all, which is the state this box is in as of 2026-08-14.
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
  ( runTCMTop, iSignature, _sigDefinitions, defType, theDef, defCopy, Defn(..), funClauses
  , dataCons, recConHead, recFields, Interface )
import Agda.TypeChecking.Monad.Options (setCommandLineOptions)
import Agda.Interaction.Options (defaultOptions)
import Agda.Syntax.Common.Pretty (prettyShow)
import Agda.Syntax.Common (unArg, namedArg)
import Agda.Syntax.Internal
  ( Term(..), Type, Elim, Elim'(..), Abs, unAbs, unEl, unDom, ConHead(..), QName, Clause
  , clauseBody, namedClausePats, DeBruijnPattern, Pattern'(..), dbPatVarName, dbPatVarIndex
  , Sort, Sort'(..), Level'(..), getSort )
import AgdaiReflect (genWalkers)

-- ⚑ THE WALKERS ARE GENERATED FROM AGDA'S OWN TYPE DECLARATIONS. `$(genWalkers ''Term)`
-- reifies the transitive closure from `Term` (86 types, 73 recursed) and emits one walker
-- per type — one equation per CONSTRUCTOR, with the constructor set taken from the type, so
-- a constructor added in a later Agda is covered on the next rebuild rather than swallowed
-- by a catch-all.
--
-- ⚑ EACH WALKER TAKES A SUB-WALKER PER TYPE PARAMETER, and it needs an explicit SIGNATURE
-- to do so. The ~73 walkers form ONE mutually-recursive binding group, and inside such a
-- group GHC types recursive uses MONOMORPHICALLY — so `Ranged` used at `Ranged String`,
-- `Ranged Int` and `Ranged BoundVariablePosition` (all three inside `NotationPart` alone)
-- unified its element variable into one ambiguous type. The errors then surfaced wherever a
-- dictionary was first demanded (`show`), never at the cause: four errors, one root.
--
-- ⚑ AND A SMALL FIXTURE CANNOT CATCH THAT. A 2-3 type test compiles green even with two
-- instantiations, because GHC's dependency analysis splits the parameterized walkers into
-- their own SCC and generalizes them. Agda's closure has real cycles through parameterized
-- types, so it does not split. The cycle is load-bearing to the bug.
--
-- ⚑ ROOTED AT `Clause`, NOT `Term` — MEASURED AS A STRICT SUPERSET (99 types vs 86, with
-- `Term` itself inside it). Generating BOTH roots would emit duplicate definitions for the
-- ~86 shared types; one root covers everything.
--
-- ⚑ AND `Clause` HAS ELEVEN FIELDS WHERE THE HAND-WRITTEN `walkClause` READ TWO. Rooting
-- here recovers `clauseTel` (the TELESCOPE — every binder's type and modality),
-- `clauseType`, `clauseCatchall`, `clauseRecursive`, `clauseUnreachable`, `clauseEllipsis`,
-- `clauseWhereModule`, and both `Range`s (packed as residue). Plus `PatOrigin`'s 10
-- constructors against `walkPat`'s `_ -> "PVarOther"` catch-all, and `Pattern'`'s 7.
$(genWalkers ''Clause)

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
--
-- ⚑⚑⚑ ⟡locals-are-emission-order — THIS COUNTER IS THE SOURCE OF A PROPERTY THE PYTHON SIDE
-- RECORDS ONLY AS A MEASUREMENT. `fresh` is a monotonic counter and children are emitted
-- before their parent, so every emitted id satisfies child < parent BY CONSTRUCTION. Downstream
-- (`sppf_db.pack_core_sql`) that is stored as `edge(clid < plid)` and verified empirically —
-- 130,915,197 / 130,915,197 corpus-wide — as though it were a regularity that might not hold.
-- It holds because of this line, on any corpus this shim emits.
--
-- ⚑⚑ AND THE ID MEANS NOTHING IN AGDA. It is not a de Bruijn index, not a name, not a position
-- in a telescope — it is "the Nth node this walk printed, in this file, in this run". Two files
-- containing the SAME subterm number it differently purely because the walk reached it at a
-- different point. Everything downstream that dedups (the interner, the packing fold, the 57×
-- collapse from 25.4M events to 443k nodes) is recovering structure this numbering obscured.
-- A consumer must therefore never read semantics INTO the id; it is a stream address.
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

-- | The GENERIC emit: `(constructor, children) -> id`. The whole contract the reflected
-- walkers need — no qname/index/lit FIELDS, because under a generic walk those are
-- CHILDREN. A `QName` is a subtree, a de Bruijn index is a `#Int:7` leaf, a literal is
-- `#Integer:61`. The schema gets SIMPLER: the hand-written `emit` carries four optional
-- fields only because a flat record was the sole way to reach what its branches could not
-- recurse into.
emitG :: IORef Int -> String -> [Int] -> IO Int
emitG r ctor kids = do
  i <- fresh r
  putStrLn $ "{\"id\":" ++ show i ++ ",\"constructor\":\"" ++ esc ctor
           ++ "\",\"children\":[" ++ intercalate "," (map show kids) ++ "]}"
  return i

-- emit one LITERAL node record carrying its VALUE (the "lit" field). Same shape as `emit`
-- (qname/index null, no children) plus  "lit":"<prettyShow value>"  — additive, so a consumer
-- that does not read "lit" is unaffected. A Lit/PLit node without this drops exactly the numeral
-- (num 61, num 78, …) a body carries; interners key it into `lit` (jea_agdai.intern_signature).
emitL :: IORef Int -> String -> String -> IO Int
emitL r ctor litval = do
  i <- fresh r
  putStrLn $ "{\"id\":" ++ show i ++ ",\"constructor\":\"" ++ ctor
           ++ "\",\"qname\":null,\"index\":null,\"lit\":\"" ++ esc litval ++ "\",\"children\":[]}"
  return i

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
  LitP _ l     ->                                                 emitL r "PLit" (prettyShow l)
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
  Lit l        -> emitL r "Lit" (prettyShow l)
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
               -- ⚑ THE TYPE IS NOW WALKED GENERICALLY. `Type'' t a` needs a sub-walker per
               -- parameter, both instantiated at `Term` here (`Type = Type'' Term Term`);
               -- the call site is where the instantiation is concrete, so this is where the
               -- sub-walkers are built. `walkType` (hand-written) is retained below for the
               -- CLAUSE path, which reaches `Term` but is not reached BY it and so is not in
               -- the generated closure.
               tr  <- walk_Agda_Syntax_Internal_Type__
                        (emitG r)
                        (walk_Agda_Syntax_Internal_Term (emitG r))
                        (walk_Agda_Syntax_Internal_Term (emitG r))
                        (defType d)
               -- ⚑ CLAUSES NOW WALK GENERICALLY TOO. `clauseNodes`/`walkClause`/`walkPat`
               -- read 2 of `Clause`'s 11 fields and bucketed unmatched patterns into
               -- `PVarOther`; the generated walker covers all 11 and all 7 `Pattern'`
               -- constructors with no catch-all.
               -- `funClauses` is PARTIAL (Function only); other Defns have no clauses, so
               -- the guard stays exactly as `clauseNodes` had it.
               cls <- case theDef d of
                        dd@FunctionDefn{} ->
                          mapM (walk_Agda_Syntax_Internal_Clause (emitG r)) (funClauses dd)
                        _ -> return []
               sid <- emit r "Defn" Nothing Nothing (tr : cls)
               let mems = defMembers (theDef d)                -- Φ7b: datatype->constructors / record->fields
                   memJSON = "[" ++ intercalate "," (map (\m -> "\"" ++ esc m ++ "\"") mems) ++ "]"
               putStrLn $ "{\"unit\":\"" ++ esc (prettyShow qn) ++ "\",\"root\":" ++ show sid
                        ++ ",\"kind\":\"" ++ defnKind (theDef d) ++ "\",\"members\":" ++ memJSON
                          ++ ",\"copy\":" ++ (if defCopy d then "true" else "false")   -- provenance: module-instantiation copy?
                          ++ sortJSON (defType d) ++ "}"
            ) defs
      n <- readIORef r
      hPutStrLn stderr ("agdai_shim: " ++ show (length defs) ++ " definitions -> " ++ show n ++ " core nodes")
