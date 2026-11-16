{-# LANGUAGE TemplateHaskell #-}
-- AgdaiReflect — the GENERIC core dumper, generated from Agda's own type declarations.
--
-- ⚑ THIS REPLACES A HAND-WRITTEN ENUMERATION. `agdai_shim.hs` walks Agda core with ~30
-- manually-written branches (`walkTerm` 11, `walkPat` 7, `defnKind` 10, `defMembers` 3).
-- Every one is a person's mapping from an Agda constructor to a flat record, so:
--   * a constructor added in a later Agda is SILENTLY swallowed by a catch-all
--     (`_ -> emit "PVarOther"`), which is data loss reported as success; and
--   * whatever nobody wrote a branch for is dropped — `Sort _ -> []` and `Level _ -> []`
--     discard the sort and the level outright, and `Sort'` has TWELVE constructors where
--     the shim recognises four.
--
-- ⚑ AGDA DERIVES NEITHER `Data` NOR `Generic` on its internal syntax (measured: `Term`,
-- `QName`, `Elim'` carry only Show/Eq/Ord/Functor). So runtime generic traversal is not
-- available — but Template Haskell's `reify` needs no derivation, only importability, and
-- Agda exports these types. The constructor list, arities and FULLY-QUALIFIED field types
-- come from the type itself at compile time.
--
-- ⚑ THE TYPE CLOSURE FROM `Term` IS 116 TYPES, MEASURED, and it does not need 116 rules —
-- it partitions into four zones:
--     RECURSE   ~70  Agda.Syntax.*      the structure we want (incl. Modality/Quantity/
--                                       Cohesion/Relevance — the 2.8.0 features the old
--                                       shim dropped entirely)
--     PRUNE     ~12  Agda.Syntax.Position.*, Agda.Utils.FileName.*
--                                       source spans: provenance, not proof structure
--     LEAF      ~20  Text/Integer/Char/Double/Word*/Bool/String — emit the VALUE
--     CONTAINER      List/List1/NonEmpty/Maybe/Seq — unfold to ELEMENTS, never spine
--
-- ⚑ AND THE CONTAINER RULE IS LOAD-BEARING, NOT TIDINESS. `Data.Sequence.Internal.FingerTree`
-- and `Data.IntSet.Internal.BitMap` are IN the closure (reached via Notation/FreeVariables).
-- Recursing into them would dump finger-tree spine and bitmap internals into the SPPF as if
-- they were proof structure — noise that swamps the signal. Unfolding to elements keeps the
-- container's CONTENT and discards its representation.
--
-- ⚑ RECURSING MORE SHOULD MAKE THE SPPF SMALLER, not larger (user). A modality subtree is
-- identical across nearly every term that carries one, so hash-consing collapses them to a
-- single shared node. Faithfulness and compactness are the same move here; the flattened
-- alternative would keep a distinct opaque node per site.
module AgdaiReflect (Zone(..), zoneOf, closureFrom, dumpDecls, genWalkers, maybe'toList) where

import Language.Haskell.TH
import Data.List (isPrefixOf, sort)
import qualified Data.Set as S
-- referenced only by NAME inside generated code (the `Container` branch's `F.toList`),
-- so the splice SITE need not import it.
import qualified Data.Foldable as F


-- | What the generic walk does at a type.
--
-- ⚑ `Pack` WAS `Prune`, AND THE DIFFERENCE IS THE WHOLE POINT (user, 2026-08-06: *"That's a
-- packed node! Also, that's hugely valuable information for my purposes"*). A `Range` holds
-- absolute file offsets, so recursing it INLINE gives two structurally identical terms
-- different subtrees and destroys the sharing the SPPF exists to find. But pruning DISCARDS
-- it, and a source coordinate is exactly what tells you WHERE a shared structure occurred.
--
-- Neither. A positioned term is `term = recon(structure, position)`: the structure interns
-- and shares; the position is the RESIDUE of that reduction. `intern_signature`'s
-- `⟨CARRIER⟩` already does this — converge the key, record the path back in `unhold_path`,
-- "never a lossy erase — the wedge `⟨CARRIER⟩ = recon q b r` at the interner".
--
-- ⚑ AND THE RESIDUE'S HOME IS THE BRIDGE TABLE, WHICH ALREADY EXISTS (user: *"a bridge
-- table between the event record and the thing the event record got reduced to"*). That is
-- `obs(core_id, local_id, ekey)` — occurrence on the left, content-addressed reduction on
-- the right, one row per occurrence. So position is a COLUMN ON THE BRIDGE, not a subtree
-- in the node: the key stays content-addressed, and the per-occurrence coordinate rides
-- beside `local_id` where the occurrence already lives.
data Zone
  = Recurse       -- ^ an Agda data/newtype: emit a node, recurse into every field
  | Pack          -- ^ ranges/paths: RESIDUE — converged in the key, carried on the bridge
  | Leaf          -- ^ a primitive: emit its VALUE, do not traverse
  | Container     -- ^ list-like: emit the ELEMENTS, never the representation
  deriving (Eq, Show)


-- | The zone policy — FOUR RULES over 116 types, keyed on the module a type is declared in
--   rather than on the type itself. That is what makes it self-updating: a constructor (or a
--   whole type) added under `Agda.Syntax.*` is recursed with no edit here.
zoneOf :: Name -> Zone
zoneOf n
  | any (`isPrefixOf` s) packed     = Pack
  | any (`isPrefixOf` s) container  = Container
  | any (s ==) leaves               = Leaf
  | "GHC." `isPrefixOf` s           = Leaf     -- incl. GHC.Prim unboxed: unreifiable floor
  | "Data.Text" `isPrefixOf` s      = Leaf
  | "Data.Array.Byte" `isPrefixOf` s = Leaf
  | any (`isPrefixOf` s) internals  = Leaf     -- container INTERNALS: never spine-walk
  | "Agda." `isPrefixOf` s          = Recurse
  -- ⚑ A `MiniTypes.` TEST HOOK WAS HERE AND IS DELETED, because the fixture it served
  -- CANNOT REPRODUCE THE BUG IT WAS BUILT FOR. Measured: a 2-3 type fixture compiles green
  -- even with two instantiations of one parameterized type, because GHC's dependency
  -- analysis puts the parameterized walkers in a SEPARATE SCC from their callers and
  -- generalizes them. Agda's closure has genuine cycles through parameterized types, so
  -- the SCC does not split and monomorphic recursion bites. A green fixture is therefore a
  -- fact about the fixture, not evidence the generator is sound — and a fast path that
  -- cannot fail is one a future reader will trust.
  | otherwise                       = Leaf     -- unknown: leaf, never a silent traversal
  where
    s = show n
    -- ⚑ PACKED, NOT PRUNED: these converge to a single key and their VALUE is carried as
    -- residue on the bridge. Note the measured side effect — cutting the recursion here
    -- also severs `Seq`/`IntSet`/`FingerTree` from the closure entirely (116 types → 86),
    -- so the container-internals worry never arises structurally.
    packed    = [ "Agda.Syntax.Position."
                , "Agda.Utils.FileName."
                , "Agda.Syntax.TopLevelModuleName.Boot.TopLevelModuleName'"
                ]
    container = [ "Agda.Utils.List1.List1"
                , "GHC.Internal.Base.NonEmpty"
                ]
    internals = [ "Data.Sequence.Internal."
                , "Data.IntSet.Internal."
                , "Data.Strict.Maybe."
                ]
    leaves    = [ "GHC.Types.Bool", "GHC.Types.Char", "GHC.Types.Double"
                , "GHC.Types.Int", "GHC.Types.Word" ]


-- | Type names mentioned in a type expression (the edges of the type graph).
namesIn :: Type -> [Name]
namesIn t = case t of
  ConT n       -> [n]
  AppT a b     -> namesIn a ++ namesIn b
  SigT a _     -> namesIn a
  ParensT a    -> namesIn a
  InfixT a n b -> n : namesIn a ++ namesIn b
  _            -> []

conFields :: Con -> [Type]
conFields c = case c of
  NormalC _ bts     -> map snd bts
  RecC _ vbts       -> map (\(_,_,t) -> t) vbts
  InfixC a _ b      -> [snd a, snd b]
  ForallC _ _ c'    -> conFields c'
  GadtC _ bts _     -> map snd bts
  RecGadtC _ vbts _ -> map (\(_,_,t) -> t) vbts

conName' :: Con -> Name
conName' c = case c of
  NormalC n _       -> n
  RecC n _          -> n
  InfixC _ n _      -> n
  ForallC _ _ c'    -> conName' c'
  GadtC (n:_) _ _   -> n
  RecGadtC (n:_) _ _-> n
  _                 -> mkName "?"


-- | The transitive type closure from a root, following ONLY types the policy recurses into.
--
-- ⚑ THE SEEN-SET IS NOT OPTIONAL. The type graph is mutually recursive (`Term` → `Elims` →
-- `Elim'` → `Arg` → `Term`), so a naive walk does not terminate. `recover` keeps an
-- unreifiable name (a GHC primitive) from aborting the whole splice.
closureFrom :: Name -> Q [Name]
closureFrom root = go S.empty [root]
  where
    go seen [] = return (sort (S.toList seen))
    go seen (x:xs)
      | x `S.member` seen = go seen xs
      | zoneOf x /= Recurse = go (S.insert x seen) xs   -- record it, do not expand it
      | otherwise = do
          i <- recover (return Nothing) (Just <$> reify x)
          let next = case i of
                Just (TyConI (DataD _ _ _ _ cons _))   -> concatMap namesIn (concatMap conFields cons)
                Just (TyConI (NewtypeD _ _ _ _ con _)) -> concatMap namesIn (conFields con)
                Just (TyConI (TySynD _ _ ty))          -> namesIn ty
                _                                      -> []
          go (S.insert x seen) (xs ++ next)


-- | The generated walker's name for a type: `walk_Agda_Syntax_Internal_Term`.
--   Derived from the qualified name so two same-basename types (`Abstract.Name.Name` vs
--   `Concrete.Name.Name` — BOTH in the closure) cannot collide.
walkerName :: Name -> Name
walkerName n = mkName ("walk_" ++ map fix (show n))
  where fix c = if c `elem` (".'" :: String) then '_' else c

-- | GENERATE one walker per recursing type, from the type's OWN constructor list.
--
-- Each walker is `\emitFn x -> case x of C f1 .. fn -> do { k1 <- ...; emitFn "C" [k1..] }`,
-- so the constructor NAME and ARITY come from `reify`, never from a hand-written branch.
-- A constructor added to any recursing type appears on the next rebuild with no edit here —
-- which is the property the 30 hand-written branches in `agdai_shim.hs` do not have.
--
-- ⚑ FIELD DISPATCH IS BY ZONE, RESOLVED AT COMPILE TIME. For each field the splice looks at
-- its type head: `Recurse` → call that type's walker; `Leaf` → emit the shown value;
-- `Pack` → emit the converged key (the residue rides the bridge, not the node);
-- `Container` → walk the elements. Unknown heads fall to `Leaf`, so a type nobody classified
-- is emitted as an opaque value rather than silently traversed or silently dropped.
--
-- ⚑ AND MUTUAL RECURSION IS WHY THESE MUST BE ONE `mapM`, not per-type splices: the closure
-- is cyclic (`Term` → `Elims` → `Elim'` → `Arg` → `Term`), so every walker must be in scope
-- for every other. Generating them as one declaration group is what makes that legal.
genWalkers :: Name -> Q [Dec]
genWalkers root = do
  names <- closureFrom root
  let recursing = [n | n <- names, zoneOf n == Recurse]
  decs <- mapM (genOne root) recursing
  return (concat decs)
  where
    -- the type a bare type-VARIABLE field is instantiated at: the walk's own root.
    varInstantiation = root
    genOne :: Name -> Name -> Q [Dec]
    genOne _root tn = do
      i <- recover (return Nothing) (Just <$> reify tn)
      case i of
        Just (TyConI (DataD _ _ tvs _ cons _))   -> mkFn tn (map tvName tvs) cons
        Just (TyConI (NewtypeD _ _ tvs _ con _)) -> mkFn tn (map tvName tvs) [con]
        _                                        -> return []

    tvName (PlainTV v _)    = v
    tvName (KindedTV v _ _) = v

    -- ⚑ ONE WALKER PER TYPE, PARAMETERIZED BY A WALKER PER TYPE PARAMETER — not N walkers,
    -- one per instantiation. The walker's only interaction with a parameter field is to walk
    -- it and hand the id to `emit`, so nothing in the BODY depends on the parameter's type;
    -- it appears only in the signature. Taking the sub-walker as an ARGUMENT therefore covers
    -- every instantiation with one function.
    --
    -- The alternative (generate `walk_Ranged_String` and `walk_Ranged_BoundVariablePosition`
    -- separately) preserves a type-level distinction the SPPF immediately collapses: two
    -- `Ranged` nodes with identical children ARE the same node, by content-addressing. That
    -- would be unfolding at the type level to re-fold at the intern level.
    --
    -- ⚑ AND THE PATH STAYS RECOVERABLE WITHOUT THE TYPE. Children are emitted in DECLARATION
    -- ORDER and recorded positionally, so `position in parent` + `parent's constructor` gives
    -- the field, and the declaration gives its type. VERIFIED on real terms: `Max/2 [Integer,
    -- [PlusLevel]]` emits `Max [1,2]` with 1 the integer and 2 the list; `Var/2 [Int, Elims]`
    -- emits `Var [0,1]`. The instantiation never needs to be recorded in the node.
    mkFn :: Name -> [Name] -> [Con] -> Q [Dec]
    mkFn tn tvs cons = do
      emitV <- newName "emitFn"
      subs  <- mapM (\_ -> newName "sub") tvs
      let env = zip tvs subs
      clauses <- mapM (mkClause emitV env subs) cons
      let fname = walkerName tn
      -- ⚑ THE EXPLICIT SIGNATURE IS LOAD-BEARING, NOT DECORATION. These ~73 walkers are ONE
      -- mutually-recursive binding group. Inside such a group GHC types recursive uses
      -- MONOMORPHICALLY (no polymorphic recursion without a signature), so a walker used at
      -- two instantiations — `Ranged String`, `Ranged Int`, `Ranged BoundVariablePosition`
      -- all occur in `NotationPart` — has its element tyvar UNIFIED across all three. The
      -- resulting `a0` is ambiguous, and the error is reported at whichever `show` first
      -- needed a `Show` dictionary (`#String:`), pages from the cause. A SigD makes each
      -- walker polymorphic AT ITS RECURSIVE USES, which is the whole fix.
      let m = mkName "m"
          tvs' = map (\v -> PlainTV v SpecifiedSpec) (m : tvs)
          mInt = AppT (VarT m) (ConT ''Int)
          emitTy = arrT (ConT ''String) (arrT (AppT ListT (ConT ''Int)) mInt)
          subTy v = arrT (VarT v) mInt
          selfTy = foldl AppT (ConT tn) (map VarT tvs)
          ty = ForallT tvs' [AppT (ConT ''Monad) (VarT m)]
                 (foldr arrT (arrT selfTy mInt) (emitTy : map subTy tvs))
      return [ SigD fname ty
             , FunD fname (if null clauses then [nullClause emitV subs tn] else clauses)]

    arrT a b = AppT (AppT ArrowT a) b

    -- a type with no constructors still needs an equation, or the walker is a scope error
    nullClause emitV subs tn =
      Clause (VarP emitV : map VarP subs ++ [WildP])
             (NormalB (AppE (AppE (VarE emitV) (LitE (StringL (show tn))))
                            (ListE []))) []

    mkClause :: Name -> [(Name, Name)] -> [Name] -> Con -> Q Clause
    mkClause emitV env subs c = do
      let cn = conName' c
          fields = conFields c
      vs <- mapM (const (newName "f")) fields
      let pat = ConP cn [] (map VarP vs)
      kids <- mapM (\(v, t) -> fieldExpr emitV env v t) (zip vs fields)
      ks <- mapM (const (newName "k")) fields
      let binds = zipWith (\k e -> BindS (VarP k) e) ks kids
          call  = NoBindS (AppE (AppE (VarE emitV) (LitE (StringL (nameBase cn))))
                                (ListE (map VarE ks)))
      return (Clause (VarP emitV : map VarP subs ++ [pat])
                     (NormalB (DoE Nothing (binds ++ [call]))) [])

    -- what to do with ONE field, by the zone of its type head
    --
    -- ⚑ SYNONYMS MUST BE RESOLVED FIRST, and skipping that was the ONE bug in the first
    -- generated build — it produced 18 "Variable not in scope: walk_..._Elims" errors that
    -- look like 18 problems and are one. `Elims`, `Sort`, `Level`, `Dom`, `ArgName`,
    -- `RawName` and `NameParts` are all `type` synonyms: `closureFrom` follows them to the
    -- EXPANSION and generates a walker for the target (`Elim'`), while a field's head name
    -- is the SYNONYM (`Elims`) — so the call named a function nobody generated.
    fieldExpr :: Name -> [(Name, Name)] -> Name -> Type -> Q Exp
    fieldExpr emitV env v t = do
      -- ⚑ CHECK FOR A STRING *BEFORE* RESOLVING SYNONYMS. `RawName = String = [Char]`, so
      -- `resolveSyn` turns it into a LIST and the list branch then walks it character by
      -- character — one node per character, and the element type stays a variable, giving
      -- `Could not deduce (Show a0)` reported at the splice rather than at the field.
      -- A string is a VALUE, not a sequence to traverse.
      isStr <- isStringLike t
      if isStr
        then return (AppE (AppE (VarE emitV)
                            (InfixE (Just (LitE (StringL "#String:")))
                                    (VarE '(++))
                                    (Just (AppE (VarE 'show) (VarE v)))))
                          (ListE []))
        else fieldExpr' emitV env v t

    fieldExpr' :: Name -> [(Name, Name)] -> Name -> Type -> Q Exp
    fieldExpr' emitV env v t = do
      t' <- resolveSyn t
      -- ⚑ A LIST FIELD IS A CONTAINER, AND ITS HEAD IS `ListT` (no Name). `Elims = [Elim]`
      -- resolves to a list, so without this branch every elimination list would emit
      -- `#opaque` — the arguments of every application, silently dropped. Emit the
      -- ELEMENTS under a `[]` node: the container's CONTENT is structure, its
      -- representation is not.
      case listElem t' of
        Just el -> do
          x  <- newName "x"
          -- ⚑ `newName`, NEVER `mkName`, for a binder inside generated code. `mkName` makes
          -- a CAPTURABLE name: nested list fields would each bind the same `ks_` and shadow
          -- one another. `newName` is hygienic by construction.
          ks <- newName "ks"
          inner <- fieldExpr emitV env x el
          let lam = LamE [VarP x] inner
          return (DoE Nothing
                   [ BindS (VarP ks) (AppE (AppE (VarE 'mapM) lam) (VarE v))
                   , NoBindS (AppE (AppE (VarE emitV) (LitE (StringL "[]"))) (VarE ks)) ])
        Nothing -> case maybeElem t' of
         Just el -> do
          -- ⚑ `Maybe` IS A CONTAINER, and treating it as a Leaf is what survived the SigD
          -- fix as the LAST error. `Dom' t e` has `domTactic :: Maybe t` and `Named name a`
          -- has `nameOf :: Maybe name` — both PARAMETERIZED, so the leaf branch emitted
          -- `"#Maybe:" ++ show f` and demanded `Show t` / `Show name` the signature cannot
          -- give. Unfold to the element (using the sub-walker for the parameter) instead.
          x  <- newName "x"
          ks <- newName "ks"
          inner <- fieldExpr emitV env x el
          let lam = LamE [VarP x] inner
          return (DoE Nothing
                   [ BindS (VarP ks) (AppE (AppE (VarE 'mapM) lam) (VarE v))
                   , NoBindS (AppE (AppE (VarE emitV) (LitE (StringL "?")))
                                   (AppE (VarE 'maybe'toList) (VarE ks))) ])
         Nothing -> case headName t' of
          Just h -> case zoneOf h of
            -- ⚑ A RECURSING TYPE'S OWN ARGUMENTS BECOME SUB-WALKERS, passed positionally.
            -- `Dom' Term` is `walk_Dom_ emit (walk_Term emit) x` — the walker for the
            -- argument is built HERE, at the call site, where the instantiation is concrete.
            -- ⚑ THE SUB-WALKER COUNT MUST MATCH THE TYPE'S DECLARED ARITY, NOT THE NUMBER
            -- OF ARGUMENTS AT THIS USE SITE. My first cut passed one per `typeArgs`, which
            -- disagrees whenever a synonym expands to a partially- or over-applied form —
            -- GHC then infers `emitFn :: String -> [a] -> Named name t -> a`, an `emit` that
            -- has silently GAINED a parameter, and the error surfaces pages from the cause.
            -- `reify` knows the declared arity; take it from there and pad or truncate.
            Recurse   -> do
              ar <- arityOf h
              let args = typeArgs t'
              real <- mapM (subWalkerFor emitV env) (take ar args)
              -- ⚑ PADDING MUST NOT TOUCH ITS ARGUMENT. A missing sub-walker is a slot the
              -- use site never fills, so its walker must IGNORE the value and emit a
              -- constant — `\_ -> emit "#unused" []`. My first cut padded with a type
              -- VARIABLE, whose generated body called `show`, giving an ambiguous `Show a0`
              -- that GHC reports at the splice rather than at the padding.
              let padW = LamE [WildP]
                           (AppE (AppE (VarE emitV) (LitE (StringL "#unused")))
                                 (ListE []))
              let argWs = real ++ replicate (max 0 (ar - length args)) padW
              return (foldl AppE (AppE (VarE (walkerName h)) (VarE emitV))
                            (argWs ++ [VarE v]))
            Pack      -> return (AppE (AppE (VarE emitV)
                                        (LitE (StringL ("⟨" ++ nameBase h ++ "⟩"))))
                                      (ListE []))
            -- ⚑ THE `Container` ZONE WAS DECLARED, DOCUMENTED, AND NEVER DISPATCHED ON.
            -- `zoneOf` has classified `List1`/`NonEmpty` as `Container` since the first
            -- version, and the header above still promises "`Container` → walk the elements"
            -- — but this `case` had no `Container` arm, so every one of them fell through the
            -- `_` catch-all to the LEAF branch and was emitted as `"#NonEmpty:" ++ show`.
            -- MEASURED on `Substrate/Lifecycle/Instance.agdai`: 2058 `#NonEmpty:Id` plus 56
            -- `#NonEmpty:Hole` nodes, each one a whole name/notation subtree flattened into a
            -- `show` string. A zone that exists in the policy but not in the dispatch is worse
            -- than an unclassified type: the policy READS as if it were handled.
            --
            -- A `Container` is `[a]` with a non-empty guarantee, so it unfolds exactly like the
            -- list branch — `toList` to a list, walk each element, group under `[]`. Using the
            -- SAME `[]` node as a real list is deliberate: `List1 a` and `[a]` with the same
            -- contents ARE the same structure, and the SPPF should share them rather than keep
            -- a representation distinction the content does not carry.
            Container -> do
              x  <- newName "x"
              ks <- newName "ks"
              let el = case typeArgs t' of
                         (a:_) -> a
                         []    -> t'
              inner <- fieldExpr emitV env x el
              let lam = LamE [VarP x] inner
              return (DoE Nothing
                       [ BindS (VarP ks) (AppE (AppE (VarE 'mapM) lam)
                                               (AppE (VarE 'F.toList) (VarE v)))
                       , NoBindS (AppE (AppE (VarE emitV) (LitE (StringL "[]"))) (VarE ks)) ])
            -- ⚑ A LEAF MUST CARRY ITS VALUE, NOT JUST ITS TYPE. My first cut emitted
            -- `#Integer` with the number DROPPED — which would collapse every de Bruijn
            -- index to one shared node and make `Var 0` and `Var 7` identical. That is the
            -- same purging this whole rewrite exists to stop, reproduced in the replacement.
            -- `show` is available on every leaf type in the closure (all derive Show), so
            -- the value rides in the node's own key.
            _         -> return (AppE (AppE (VarE emitV)
                                        (InfixE (Just (LitE (StringL ("#" ++ nameBase h ++ ":"))))
                                                (VarE '(++))
                                                (Just (AppE (VarE 'show) (VarE v)))))
                                      (ListE []))
          -- ⚑ A TYPE VARIABLE IS NOT OPAQUE — IT IS THE INSTANTIATION, AND TREATING IT AS
          -- OPAQUE DROPPED EVERY TERM BODY. `Type'' t a` holds its term in the VARIABLE `a`
          -- (`Type = Type'' Term Term`), so a field typed `a` reached `headName = Nothing`
          -- and emitted `#opaque`. MEASURED on a one-definition core: `El [Univ.., #opaque]`
          -- — the sort fully recursed, the term GONE. Node counts went DOWN versus the
          -- hand-written walk, which is how the regression surfaced: recursing more must
          -- never emit less.
          --
          -- These types are all instantiated at `Term` in the closure reachable from `Term`
          -- (`Type`, `Sort`, `Level`, `Elim`, `Dom` are each `X' Term`), so a bare variable
          -- is a Term. That is narrow and TRUE HERE rather than true in general — a second
          -- root with a different instantiation would need the substitution threaded through
          -- `closureFrom`, which is real work this does not do.
          -- ⚑ A TYPE VARIABLE IS NOT OPAQUE — IT IS THE INSTANTIATION — BUT ONE WALKER
          -- CANNOT SERVE TWO INSTANTIATIONS, AND MY FIRST FIX ASSUMED IT COULD.
          --
          -- The defect it corrects is real and was measured: `Type'' t a` holds its term in
          -- the VARIABLE `a` (`Type = Type'' Term Term`), so the field reached
          -- `headName = Nothing` and emitted `#opaque` — `El [Univ.., #opaque]`, the sort
          -- fully recursed and the TERM GONE. Node counts fell below the hand-written walk,
          -- which is how it surfaced: recursing more must never emit less.
          --
          -- But "a bare variable is the root type" is false. GHC named the counterexample:
          -- `RString = Ranged String` and `Ranged BoundVariablePosition` are two
          -- instantiations of ONE parameterized type, so a single
          -- `walk_..._Ranged` cannot type-check against both. Doing this properly means
          -- generating walkers that TAKE a per-element walker (rank-1 polymorphism over the
          -- parameter), not assuming a fixed instantiation.
          --
          -- Emitting a LABELLED marker rather than `#opaque` keeps that honest: the node
          -- says a parameter was reached and not descended, so the gap is visible in the
          -- SPPF instead of silently indistinguishable from a real leaf.
          -- ⚑ A TYPE VARIABLE CALLS ITS SUB-WALKER — the argument this walker was given for
          -- that parameter. Emitting `#opaque` here is what DROPPED EVERY TERM BODY:
          -- `Type'' t a` holds its term in `a`, so `El [Univ.., #opaque]` recursed the sort
          -- and lost the term, and the node count fell BELOW the hand-written walk's.
          -- Recursing more must never emit less.
          Nothing -> case t' of
            VarT nv | Just s <- lookup nv env ->
                        return (AppE (VarE s) (VarE v))
            VarT nv -> return (AppE (AppE (VarE emitV)
                                      (LitE (StringL ("#param:" ++ nameBase nv))))
                                    (ListE []))
            _       -> return (AppE (AppE (VarE emitV) (LitE (StringL "#opaque")))
                                    (ListE []))

    -- build the walker EXPRESSION for one type argument (used as a sub-walker)
    subWalkerFor :: Name -> [(Name, Name)] -> Type -> Q Exp
    subWalkerFor emitV env a = do
      a' <- resolveSyn a
      y  <- newName "y"
      body <- fieldExpr emitV env y a'
      return (LamE [VarP y] body)

-- | Expand a type synonym to its target, repeatedly (a synonym may name a synonym:
--   `Sort = Sort' Term`, `Elims = [Elim]`, `Elim = Elim' Term`). Bounded so a pathological
--   or self-referential synonym cannot hang the splice — a TERMINATION bound, which is
--   fine, as distinct from a capability bound, which would silently stop resolving.
--
-- ⚑ EXPANSION IS SUBSTITUTION AND APPLICATION, NOT "RETURN THE RHS". This function used to
-- do `TySynD _ _ ty -> go (k-1) ty`, which throws away BOTH halves of the synonym's beta
-- redex: the synonym's own PARAMETERS and the ARGUMENTS applied at the use site. That is a
-- head-only expansion, and it silently mangled every parameterized synonym in Agda's core —
-- ONE defect that surfaced as two different give-up markers, which is why it read as two
-- bugs. Both were MEASURED in `-ddump-splices`:
--
--   * ARGUMENTS DROPPED → `#unused`. `Term`'s `Pi` field is `Dom Type`. `Dom` is the 0-param
--     synonym `Dom' Term`, so the old code returned `Dom' Term` and DISCARDED the applied
--     `Type`. `Dom'` declares arity 2, so `typeArgs` (1) fell short of `arityOf` (2) and the
--     padding fired: `walk_Dom_ emit (walk_Term) (\_ -> emit "#unused" [])`. The `#unused`
--     slot is `unDom` — the DOMAIN TYPE OF EVERY Pi, dropped outright.
--
--   * PARAMETERS UNSUBSTITUTED → `#param:a`. `Type = Type' Term` and `Type' a = Type'' Term a`.
--     Expanding the second link returned the body `Type'' Term a` with `a` left FREE — a
--     `VarT` bound by nothing, since the synonym's binder was discarded along with the
--     argument that should have replaced it. `fieldExpr'` found it in no `env` and emitted
--     `#param:a`, which is `El`'s `unEl` field: THE TERM ITSELF.
--
-- ⚑ AND THE `env` HYPOTHESIS WAS THE WRONG SUSPECT, though it is where the marker is printed.
-- Threading more into `env` cannot help: the free `a` is not a parameter of any walker being
-- generated, so there is no sub-walker it could ever name. The variable should not have
-- survived expansion at all.
--
-- So: peel the application spine, substitute the first `length params` arguments for the
-- synonym's parameters in its body, and RE-APPLY whatever arguments are left over (a synonym
-- may be applied to more arguments than it binds — `Elim = Elim' Term` used as `Elim` is the
-- degenerate case, `NamedArg p` the general one).
resolveSyn :: Type -> Q Type
resolveSyn = go (20 :: Int)
  where
    go 0 t = return t
    go k t = case headName t of
      Nothing -> return t
      Just h  -> do
        i <- recover (return Nothing) (Just <$> reify h)
        case i of
          Just (TyConI (TySynD _ params body)) -> do
            let args    = typeArgs t
                ps      = map tvName' params
                n       = length ps
                sub     = zip ps args
                extra   = drop n args
                body'   = substTy sub body
            -- Under-applied (fewer args than params) leaves the un-substituted params free,
            -- which is exactly the state this fix exists to prevent — so refuse to expand
            -- rather than manufacture a free variable. A partially-applied synonym is not
            -- something the walker can descend anyway.
            if length args < n
              then return t
              else go (k - 1) (foldl AppT body' extra)
          _ -> return t

    tvName' (PlainTV v _)    = v
    tvName' (KindedTV v _ _) = v

-- | Capture-free enough for this use: type-synonym RHSs bind no type variables of their own
--   (no `forall` in a vanilla synonym body), so a plain structural substitution is sound.
--   `ForallT` is traversed with its own binders REMOVED from the substitution, which keeps it
--   honest if a rank-N synonym ever appears.
substTy :: [(Name, Type)] -> Type -> Type
substTy s ty = case ty of
  VarT v            -> maybe ty id (lookup v s)
  AppT a b          -> AppT (substTy s a) (substTy s b)
  AppKindT a b      -> AppKindT (substTy s a) (substTy s b)
  SigT a k          -> SigT (substTy s a) (substTy s k)
  ParensT a         -> ParensT (substTy s a)
  InfixT a n b      -> InfixT (substTy s a) n (substTy s b)
  UInfixT a n b     -> UInfixT (substTy s a) n (substTy s b)
  ForallT bs cxt a  -> let bound = map bndrName bs
                           s'    = [p | p@(v, _) <- s, v `notElem` bound]
                       in ForallT bs (map (substTy s') cxt) (substTy s' a)
  _                 -> ty
  where
    bndrName (PlainTV v _)    = v
    bndrName (KindedTV v _ _) = v

-- | Is this type a string (`String`, `RawName`, `ArgName`, … — anything that resolves to
--   `[Char]`)? Strings are LEAVES: a value, not a sequence to walk one character per node.
isStringLike :: Type -> Q Bool
isStringLike t = do
  t' <- resolveSyn t
  return $ case t' of
    AppT ListT (ConT c) -> c == ''Char
    ConT c              -> c == ''Char
    _                   -> False

-- | How many type parameters a type DECLARES (its walker's sub-walker count).
arityOf :: Name -> Q Int
arityOf n = do
  i <- recover (return Nothing) (Just <$> reify n)
  return $ case i of
    Just (TyConI (DataD _ _ tvs _ _ _))    -> length tvs
    Just (TyConI (NewtypeD _ _ tvs _ _ _)) -> length tvs
    _                                      -> 0

-- | The ARGUMENTS of an applied type: `Dom' Term` → `[Term]`, `Type'' a b` → `[a, b]`.
--   Left-to-right, matching the declaration's parameter order.
typeArgs :: Type -> [Type]
typeArgs = reverse . go
  where
    go (AppT f a) = a : go f
    go (SigT a _) = go a
    go (ParensT a) = go a
    go _          = []

-- | Runtime helper referenced by generated code (spliced by fully-qualified `Name`, so the
--   splice site need not import it).
maybe'toList :: Maybe a -> [a]
maybe'toList = maybe [] (:[])

-- | `Maybe a` → `Just a`. A `Maybe` is a CONTAINER (0-or-1 elements), never a leaf: its
--   element may be a type PARAMETER (`Dom'.domTactic :: Maybe t`), which no `show` can reach.
maybeElem :: Type -> Maybe Type
maybeElem (AppT (ConT c) e) | c == ''Maybe = Just e
maybeElem _ = Nothing

-- | `[a]` → `Just a`; anything else → Nothing.
listElem :: Type -> Maybe Type
listElem (AppT ListT e) = Just e
listElem _              = Nothing

-- | The head type constructor of a (possibly applied) type: `Dom Type` → `Dom`.
headName :: Type -> Maybe Name
headName t = case t of
  ConT n     -> Just n
  AppT a _   -> headName a
  SigT a _   -> headName a
  ParensT a  -> headName a
  ListT      -> Nothing
  _          -> Nothing


-- | Emit the constructor table as a compile-time report: what the generated walk WOULD cover,
--   with each type's zone. Printing it is what makes the coverage auditable instead of
--   assumed — the current shim's coverage is only discoverable by reading 30 branches.
dumpDecls :: Name -> Q [Dec]
dumpDecls root = do
  names <- closureFrom root
  let z t = (t, zoneOf t)
      byZone k = [n | (n, zz) <- map z names, zz == k]
  runIO $ do
    putStrLn ("-- type closure from " ++ show root ++ ": " ++ show (length names) ++ " types")
    mapM_ (\(k, ns) -> putStrLn ("--   " ++ show k ++ ": " ++ show (length ns)))
          [(Recurse, byZone Recurse), (Pack, byZone Pack)
          ,(Leaf, byZone Leaf), (Container, byZone Container)]
  -- per RECURSE type, report its constructors + arities (the generated walk's cases)
  mapM_ (\n -> do
            i <- recover (return Nothing) (Just <$> reify n)
            case i of
              Just (TyConI (DataD _ _ _ _ cons _)) -> runIO $
                putStrLn ("--   " ++ show n ++ ": " ++ show (length cons) ++ " ctors "
                          ++ show (map (\c -> nameBase (conName' c) ++ "/"
                                              ++ show (length (conFields c))) cons))
              _ -> return ())
        (byZone Recurse)
  return []
