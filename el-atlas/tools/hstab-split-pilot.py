#!/usr/bin/env python3
"""W3: the split-test. A pair (a,b) is 'split by knob k' iff it has
truth-separators in the full space S but NONE in the restriction
S|k=base — i.e., every separating probe requires k off its base value:
the separation was purchased entirely by k, and before k's admission
the pair was (vacuously) circle-like. Any ledgered circle appearing
here would be an H-instability event; thread 20 predicts none."""
import importlib.util, os, sys
spec=importlib.util.spec_from_file_location("dep", os.path.join(os.path.dirname(__file__),"el-atlas-depsort-v3.py"))
dep=importlib.util.module_from_spec(spec); sys.modules['dep']=dep
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):  # module import only; run() not called
    spec.loader.exec_module(dep)
names=sorted(dep.TESTS) if hasattr(dep,'TESTS') else None
# discover the claim-test table the harness uses
tests={n[2:]:getattr(dep,n) for n in dir(dep) if n.startswith('t_') and callable(getattr(dep,n))}
names=sorted(tests)
print(f"claims: {len(names)}; space: {len(dep.SPACE)} models")
res={n:[tests[n](m) for m in dep.SPACE] for n in names}
def truth_sep_idx(a,b):
    A,B=res[a],res[b]
    return [i for i in range(len(dep.SPACE))
            if A[i] in 'PF' and B[i] in 'PF' and A[i]!=B[i]]
base=dep.BASE
split_events=[]
for x in range(len(names)):
    for y in range(x+1,len(names)):
        a,b=names[x],names[y]
        sep=truth_sep_idx(a,b)
        if not sep: continue            # current circles: cannot have been split
        for k in dep.KNOBS:
            if all(dep.SPACE[i][k]!=base[k] for i in sep):
                split_events.append((a,b,k,len(sep)))
print(f"\nseparated pairs whose ENTIRE truth-separation requires one knob off-base:")
if not split_events: print("  none")
ledgered_circles=[{'GCX','RAD','RDW','ZDG','ZDW'},{'D4C','NVE','TWN'},{'NGL','V4I'},{'PRO','PUR'},{'L26','LOC'}]
hits=0
for a,b,k,n in split_events:
    was_circle=any({a,b}<=c for c in ledgered_circles)
    if was_circle: hits+=1
    print(f"  {{{a},{b}}} split entirely by knob '{k}' ({n} separators){'  ** LEDGERED-CIRCLE HIT **' if was_circle else ''}")
print(f"\nledgered-circle hits (H-instability events): {hits}")
print("thread-20 verdict:", "STABILITY HOLDS — no ledgered circle was ever split by a knob admission" if hits==0 else "INSTABILITY FOUND — investigate")
