# EL-Atlas — coverage as a section over the prerequisite-DAG
# (replaces the matrix-with-holes audit; LEM verdict retracted)

## Why this replaces the matrix audit

The first audit returned 49 "unreachable" cells as **theorems of non-existence** —
a law-of-excluded-middle move: each cell is *either* fillable *or* provably-not.
That is the forbidden collapse (Remark 2.5c) committed against the matrix itself:
a two-axis question — *is there structure at this coordinate?* and *does structure
transmit to it?* — projected down to one negative bit, the other axis forgotten.

Correct frame: a **section `D` over the prerequisite-DAG**, not a matrix with holes.
`D : (obligation poset) → Obligation`, `depth = 1 + max(prereq depth)`. The base
case is **specified by construction** — the DAG roots are forced by the carrier — so
no cell's nonemptiness is *proven*; it is *constructed*. The inductive step is the
Π-type itself:

```
D(node) = authored          if node is a root or a stated obligation
        = restrict(D(c))     if node is the local shadow of cross-cutting c   [R1]
        = glue(D(l…))         if node is the cross-cutting completion of locals [R2]
        = transport(D(p))     along a prerequisite edge p                      [R3]
        = HOLE(phase)         if D's value here depends on an undetermined input
```

Result: **0 non-existence theorems.** The 49 former "unreachable" cells are
construction recipes (R1/R2/R3); genuine openness is a **hole in dom(D)** — a value
that is a function of an undetermined input — not a proven absence.

## The DAG

Single root: **carrier** (depth 0), forced by the spec. Everything else is reached by
transport up the prerequisite edges — "base case specified by construction" made literal.

| depth | node | (layer, role) | origin | derivation |
|---|---|---|---|---|
| 0 | carrier | bootstrap, local | authored | root (forced by spec) |
| 1 | atlas | bootstrap, invariant | authored | transport from carrier |
| 1 | register | meta, invariant | authored | transport from carrier |
| 1 | carrier@xc | bootstrap, cross-cutting | derived | glue [R2] |
| 2 | crossbar | ladder, local | authored | transport from atlas |
| 2 | prohibition | governance, cross-cutting | authored | transport from atlas |
| 3 | involutions | groupoid, invariant | authored | transport from crossbar |
| 3 | noether | **governance, invariant** | authored | transport from crossbar (collision-split: see below) |
| 3 | wheatstone | testing, invariant | authored | from crossbar + prohibition |
| 3 | consumption | ladder, cross-cutting | authored | transport from prohibition |
| 3 | crossbar@xc | ladder, cross-cutting | derived | glue [R2] |
| 3 | prohibition@local | governance, local | derived | restrict [R1] |
| 3 | **amplitude** | **typethy, invariant** | **open** | **HOLE(phase): value is a function of OB-2/OB-9, undetermined** |
| 4 | overlay | topos, cross-cutting | authored | transport from consumption |
| 4 | consumption@local | ladder, local | derived | restrict [R1] |
| 5 | overlay@local | topos, local | derived | restrict [R1] |

(The table lists representative derived nodes; R1 applies to every cross-cutting
node and R2 to every local node, so the derived family is generated, not enumerated.)

## The collision dissolved by construction

In the matrix framing, involutions and noether collided at (groupoid, invariant, 3).
In the DAG they are different nodes with different prerequisite signatures; keying on
**prerequisite** rather than **layer label** sends noether to (governance, invariant, 3)
automatically — the conservation-law cell — with no collision. A clash in one framing
that simply does not arise in the other is evidence the DAG is the faithful object.
The earlier "recommended split" is not a manual fix; it is what D returns.

## The one genuine hole

`amplitude` (§8) is the sole **open** node: D's value there is a function of the phase
type, which is undetermined (OB-2/OB-9). This is a hole in the *domain* of D — the
function cannot be evaluated until phase is supplied — **not** a proven absence and
**not** a base case to discharge. The whole "empty typethy layer" of the matrix audit
is this single domain-hole, seen through the product projection. Phase remains the
load-bearing open input; everything else is constructed.

## Net

Matrix audit: 9 filled, 49 unreachable, 62 open — a LEM partition.
DAG section: 10 authored, 5+ derived-by-construction, **1 genuine hole** (phase).
No non-existence theorems. The base case is the carrier, forced; the inductive step is
the Π-type; the only openness is a domain-hole depending on phase.
