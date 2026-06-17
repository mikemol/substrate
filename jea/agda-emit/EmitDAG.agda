------------------------------------------------------------------------
-- jea/agda-emit/EmitDAG.agda
--
-- U8: the SPPF/DAG end of the Agda-on-GPU bridge. Emit.agda emits a TREE
-- (every occurrence its own node); this emits the SHARED SPPF form the real
-- substrate traces use: a node LIST where children are INDICES into earlier
-- nodes, so one node can be referenced by multiple parents (sharing =
-- memoization = SPPF/Register packing). Repeated squaring makes the sharing
-- dramatic: x^8 is 6 shared nodes whose tree expansion is ~31.
--
-- Same voucher discipline as Emit.agda: `renderDAG dag` and `evalStr dag` are
-- proved EQUAL to string literals by refl, so the literals are machine-verified
-- to be the DAG's faithful serialization and value. The bridge (jea_agda_dag.py)
-- typechecks this, parses the node list preserving sharing, evaluates it on the
-- GPU cooperative generators (a shared node computed ONCE), and checks equality.
------------------------------------------------------------------------

{-# OPTIONS --safe #-}

module EmitDAG where

open import Data.Nat using (ℕ; zero; suc; _+_; _*_)
open import Data.Nat.Show using (show)
open import Data.String using (String) renaming (_++_ to _&_)
open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Data.List using (List; []; _∷_; foldl; _++_; [_])
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

------------------------------------------------------------------------
-- A DAG node: a leaf rational, or +/x of two EARLIER nodes (by index).
-- Children-before-parent; an index may be reused = sharing.
------------------------------------------------------------------------

data Node : Set where
  lf   : ℕ → ℕ → Node          -- leaf num/den (gen)
  nadd : ℕ → ℕ → Node          -- _⊕_ of nodes i j
  nmul : ℕ → ℕ → Node          -- _⊗_ of nodes i j

-- the shared SPPF: x = 2/3 + 1/2, then x^2, x^4, x^8 by repeated squaring.
-- node 2 (x) feeds node 3; node 3 (x^2) feeds node 4; etc. -- each reused twice.
dag : List Node
dag = lf 2 3 ∷ lf 1 2 ∷ nadd 0 1 ∷ nmul 2 2 ∷ nmul 3 3 ∷ nmul 4 4 ∷ []

------------------------------------------------------------------------
-- eval: fold the node list, threading the computed (num,den) values; a node
-- looks up its children by index in the values-so-far (total lookup, default 0/1).
------------------------------------------------------------------------

get : List (ℕ × ℕ) → ℕ → ℕ × ℕ
get []       _       = 0 , 1
get (x ∷ _)  zero    = x
get (_ ∷ xs) (suc n) = get xs n

step : List (ℕ × ℕ) → Node → List (ℕ × ℕ)
step vs (lf n d)   = vs ++ [ n , d ]
step vs (nadd i j) = vs ++ [ proj₁ (get vs i) * proj₂ (get vs j) + proj₁ (get vs j) * proj₂ (get vs i)
                           , proj₂ (get vs i) * proj₂ (get vs j) ]
step vs (nmul i j) = vs ++ [ proj₁ (get vs i) * proj₁ (get vs j)
                           , proj₂ (get vs i) * proj₂ (get vs j) ]

lastVal : List (ℕ × ℕ) → ℕ × ℕ
lastVal []           = 0 , 1
lastVal (x ∷ [])     = x
lastVal (_ ∷ y ∷ ys) = lastVal (y ∷ ys)

eval : List Node → ℕ × ℕ
eval nodes = lastVal (foldl step [] nodes)

evalStr : List Node → String
evalStr nodes = let v = eval nodes in show (proj₁ v) & "/" & show (proj₂ v)

------------------------------------------------------------------------
-- render: the node list as "lf n d | add i j | mul i j | ..." (the bridge parses
-- this directly into the shared GPU DAG; the | separators keep node order).
------------------------------------------------------------------------

rnode : Node → String
rnode (lf n d)   = "lf " & show n & " " & show d
rnode (nadd i j) = "add " & show i & " " & show j
rnode (nmul i j) = "mul " & show i & " " & show j

renderDAG : List Node → String
renderDAG []           = ""
renderDAG (x ∷ [])     = rnode x
renderDAG (x ∷ y ∷ ys) = rnode x & " | " & renderDAG (y ∷ ys)

------------------------------------------------------------------------
-- THE VOUCHERS (refl = Agda's machine-checked guarantee the literals are faithful).
------------------------------------------------------------------------

termStr : String
termStr = "lf 2 3 | lf 1 2 | add 0 1 | mul 2 2 | mul 3 3 | mul 4 4"

valStr : String
valStr = "5764801/1679616"      -- x=7/6; x^8 = 7^8/6^8 = 5764801/1679616 (unreduced eval; already coprime)

dag-serialises : renderDAG dag ≡ termStr
dag-serialises = refl

dag-evaluates : evalStr dag ≡ valStr
dag-evaluates = refl
