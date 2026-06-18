import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, IR
import jea_grammar_fixpoint as G

# HYPOTHESIS: the parse forest is a torsor-bundle over the input-position affine line.
#   base  = span (origin:end) = the GAUGE (where in the input)
#   fiber = production+dot + witness-SHAPE = the INVARIANT (what was recognized)
#   action = translate all positions by k (shift the input window)
# TEST (Σ-TORSOR-VERIFY discipline): is the fiber SHIFT-INVARIANT (equivariance),
#   and is the action FREE (no nonzero shift fixes a parse) + TRANSITIVE (any span reachable)?
# Guard against degeneracy: use a grammar that ACTUALLY consumes structure (not a one-token toy),
#   and shift by embedding the SAME phrase at different offsets in a longer input.

# A grammar with real structure: S -> a S b | a b   (balanced a^n b^n, n>=1)
grammar = {"S": [["a","S","b"], ["a","b"]]}

def fiber_skeleton(I, idx):
    """The recognition FIBER of an item: its production+dot (op) and the SHAPE of its witness chain
    (the ops of its children, recursively) — everything EXCEPT the absolute span (role)."""
    nd = I.nodes[idx]
    return (nd.op, tuple(fiber_skeleton(I, c) for c in nd.children))

def span_of(I, idx):
    nd = I.nodes[idx]
    o,e = map(int, nd.role.split(":"))
    return (o,e)

def parse_at_offset(phrase, k):
    """Parse `phrase` but with the whole thing SHIFTED to start at position k, by prepending k
    'pad' tokens and wrapping: W -> pad^k S. The S-subforest should be the phrase's forest, translated."""
    g = {"W": [["pad"]*k + ["S"]] if k>0 else [["S"]], "S": grammar["S"]}
    toks = ["pad"]*k + list(phrase)
    return G.recognize(g, toks, "W", intern=Intern())

phrase = ["a","a","b","b"]   # S=>aSb=>a(ab)b, n=2 — real nesting

print("=== EQUIVARIANCE: is the recognition fiber shift-invariant? ===")
fibers = {}
spans_S = {}
for k in (0,1,2,3):
    r = parse_at_offset(phrase, k)
    I = r["intern"]
    # find the top S-completed parse node (kind 'parse', op 'S') and its item
    S_items = [i for i in range(I.size())
               if I.nodes[i].kind=="it" and I.nodes[i].op.startswith("S|")
               and int(I.nodes[i].op.split("|")[2])==len(I.nodes[i].op.split("|")[1].split(">"))
               and span_of(I,i)[1]-span_of(I,i)[0]==len(phrase)]   # the full-phrase S
    assert S_items, f"k={k}: no full S parse"
    si = S_items[0]
    fibers[k] = fiber_skeleton(I, si)
    spans_S[k] = span_of(I, si)
    print(f"  k={k}: S-fiber-skeleton hash={hash(fibers[k])&0xffff:04x}  span={spans_S[k]}")

base = fibers[0]
equivariant = all(fibers[k]==base for k in fibers)
print(f"  fiber identical across all shifts? {equivariant}  (equivariance = the fiber is shift-INVARIANT)")
print(f"  span translates by exactly k? {all(spans_S[k]==(k, k+len(phrase)) for k in spans_S)}")

print("\n=== FREENESS: does any NONZERO shift fix the span (a stabilizer)? ===")
# free = the action on the BASE (spans) has no fixed point for nonzero k: span(k) != span(0) for k!=0
moved = all(spans_S[k]!=spans_S[0] for k in spans_S if k!=0)
print(f"  every nonzero shift MOVES the span? {moved}  -> {'FREE on the base' if moved else 'STABILIZER'}")

print("\n=== TRANSITIVITY: can a shift carry span(0) to span(k) for every k? ===")
# transitive = for any two offsets the shift k2-k1 maps one span to the other (affine line, by construction)
trans = all(spans_S[k]==(spans_S[0][0]+k, spans_S[0][1]+k) for k in spans_S)
print(f"  shift k maps span(0)->span(k) for all k? {trans}  -> {'TRANSITIVE' if trans else 'NOT'}")

print("\n=== DEGENERACY GUARD: is the fiber RICH (real witness structure), not a trivial 1-node? ===")
def depth(f): return 1 + (max((depth(c) for c in f[1]), default=0))
def count(f): return 1 + sum(count(c) for c in f[1])
print(f"  fiber depth={depth(base)}  node-count={count(base)}  (>1 each = nondegenerate; a 1-token toy would be 1)")

print("\n=== VERDICT ===")
torsor = equivariant and moved and trans and count(base)>2
if torsor:
    print("  The parse forest IS a torsor-bundle over the input-position line:")
    print("  fiber (production+witness-shape) shift-INVARIANT; base (span) a FREE+TRANSITIVE affine action.")
    print("  The keyed claim+witness = the invariant fiber; the span = the gauge. THEOREM-SHAPED, witnessed.")
else:
    print("  NOT a clean torsor — one of equivariance/free/transitive/nondegeneracy failed (see above).")

# fail-hard so this is a runnable CHECK (gated), not a print-only demo.
sys.exit(0 if torsor else 1)
