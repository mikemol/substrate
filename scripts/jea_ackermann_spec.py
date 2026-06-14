#!/usr/bin/env python3
"""jea_ackermann_spec.py — the universal spawn loop, GPU-shaped, on Ackermann. The host spec/
oracle for the on-device dynamic term-rewriting engine (as jea_nedge_model specced the controller).

THE UNIFICATION (user): escalation IS dynamic work production. A reduction step yields ONE of:
  * a VALUE            (terminal: a combine that fits / A(0,n)=n+1)
  * SPAWN sub-terms    (recursion: A(m,n) -> needs A(m,n-1) then A(m-1, that))
  * SPAWN wider work   (escalation: a value overflows width W -> redo at width 2W)
All three are the SAME act: push new work the parent depends on. So there is no "static fold vs
dynamic rewrite" split -- one loop: pop a node, reduce, maybe spawn, resolve parents. We already
built every piece: spawn = the escalation priority push; dependency = the readiness gate; priority
= the bucket scheduler. Ackermann is just new RULES on that queue (and its value explosion is the
escalation/multi-limb path firing -- the same spawn, taken to its conclusion).

This is GPU-shaped: an explicit node array + an explicit work queue, NO host recursion (the call
stack lives in the spawned nodes, exactly as it must on the GPU). Continuation A(m,n) ->
A(m-1, A(m,n-1)) is a TAIL-REWRITE: spawn the inner A(m,n-1); when it resolves to v, REWRITE the
node in place to A(m-1, v) and re-queue. Only the inner call is a fresh node; the tail reuses the
node (a bounded-allocation continuation). Verified exact vs the recursive reference.
"""
import sys

def ack_ref(m, n):                       # reference (recursive), for small (m,n)
    if m == 0: return n + 1
    if n == 0: return ack_ref(m - 1, 1)
    return ack_ref(m - 1, ack_ref(m, n - 1))


class Engine:
    """Iterative work-queue Ackermann engine. Nodes: parallel lists (GPU SoA shape)."""
    def __init__(self):
        self.m = []; self.n = []; self.parent = []          # node fields
        self.result = []; self.waiting = []                 # result slot, 'spawned inner, awaiting it'
        self.queue = []                                     # ready-to-step node ids
        self.steps = 0; self.spawns = 0; self.max_live = 0

    def _new(self, m, n, parent):
        i = len(self.m)
        self.m.append(m); self.n.append(n); self.parent.append(parent)
        self.result.append(None); self.waiting.append(False)
        self.queue.append(i); self.spawns += 1
        return i

    def _resolve(self, i):
        """Node i finished with a value; feed its parent (the continuation) and re-queue it."""
        p = self.parent[i]
        if p is None: return
        # parent A(m,n) spawned inner A(m,n-1)=node i with result v -> parent becomes A(m-1, v)
        self.n[p] = self.result[i]; self.m[p] -= 1; self.waiting[p] = False
        self.queue.append(p)

    def run(self, m0, n0):
        root = self._new(m0, n0, None)
        while self.queue:
            self.max_live = max(self.max_live, len(self.queue))
            i = self.queue.pop()                            # pop work (LIFO here; any order is correct)
            self.steps += 1
            mi, ni = self.m[i], self.n[i]
            if mi == 0:                                     # VALUE (terminal rewrite)
                self.result[i] = ni + 1; self._resolve(i)
            elif ni == 0:                                   # tail-rewrite A(m,0) -> A(m-1,1)
                self.m[i] = mi - 1; self.n[i] = 1; self.queue.append(i)
            else:                                           # SPAWN inner A(m,n-1); tail becomes A(m-1, v)
                self.waiting[i] = True
                self._new(mi, ni - 1, i)                    # the only fresh node; resolve() does the tail
        return self.result[root]


if __name__ == "__main__":
    sys.setrecursionlimit(100000)
    print("universal spawn loop on Ackermann (GPU-shaped: node array + work queue, no host recursion)\n")
    cases = [(0,0),(1,1),(2,1),(2,3),(3,2),(3,3),(3,4),(3,5),(3,6)]
    allok = True
    print(f"  {'A(m,n)':>8} {'value':>8} {'ref':>8} {'ok':>4} {'steps':>9} {'nodes':>9} {'max-queue':>9}")
    for m, n in cases:
        e = Engine(); v = e.run(m, n); ref = ack_ref(m, n); ok = (v == ref); allok &= ok
        print(f"  A({m},{n})   {v:>8} {ref:>8} {str(ok):>4} {e.steps:>9} {e.spawns:>9} {e.max_live:>9}")
    print(f"\n  PASS {allok} — a non-primitive-recursive function evaluated by ONE spawn loop: pop a node,")
    print(f"  reduce, SPAWN sub-work the parent depends on, resolve. The recursion lives in the spawned")
    print(f"  nodes (no host call stack) -- exactly the on-device shape. Note the step/node EXPLOSION")
    print(f"  (A(3,n) ~ 2^(n+3)-3): that's the universality, and the value explosion IS the escalation/")
    print(f"  multi-limb spawn firing. Escalation and recursion are the SAME push-to-queue.")
    print(f"\n  GPU port = this loop on the scheduler we have: dynamic node alloc (atomic bump) = spawn;")
    print(f"  readiness gate = parent waits on inner; bucket/priority = escalated/in-progress first.")
