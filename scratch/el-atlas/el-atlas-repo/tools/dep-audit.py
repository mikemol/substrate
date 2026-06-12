"""
dep-audit.py — R-V35 G8 handoff discharge: record the ACTUAL knob reads of
every claim test and compare against the DECLARED support in _CLAIM_DEPS.
Both the v3.5 bug and the v3.5a fix trusted these declarations (memoization
keys AND the stance guard key on them); this instruments the trust.

Method: wrap the model dict in a read-recorder; evaluate every RAW
(unmemoized) claim over BASE, every single-knob mutation, and 600 random
models; union the observed reads. MISSING (read but undeclared) = memo
pollution bug. EXTRA (declared, never read in sample) = over-declaration —
benign for correctness (cache splits finer), reported for the record.
"""
import importlib.util, random
spec = importlib.util.spec_from_file_location("h", "tools/el-atlas-depsort-v3.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)

class Rec(dict):
    def __init__(self, m): super().__init__(m); self.reads = set()
    def __getitem__(self, k): self.reads.add(k); return super().__getitem__(k)
    def get(self, k, d=None): self.reads.add(k); return super().get(k, d)

rng = random.Random(41)
models = [dict(h.BASE)]
for k, vals in h.KNOBS.items():
    for v in vals: models.append(dict(h.BASE, **{k: v}))
for _ in range(600):
    models.append({k: rng.choice(vals) for k, vals in h.KNOBS.items()})

clean = True
for name, f in h._RAW_CLAIMS.items():
    seen = set()
    for m in models:
        r = Rec(m)
        try: f(r)
        except Exception as ex:
            print(f"  {name}: EVALUATION ERROR {ex!r}"); clean = False; break
        seen |= r.reads
    declared = set(h._CLAIM_DEPS[name])
    missing = seen - declared            # read but undeclared: BUG
    extra   = declared - seen            # declared, never observed: benign
    if missing:
        clean = False
        print(f"  {name}: UNDECLARED READS {sorted(missing)}  (declared {sorted(declared)})")
    elif extra:
        print(f"  {name}: over-declared (never read in sample): {sorted(extra)}")
print("AUDIT:", "CLEAN — every observed read is declared; memoization and the stance guard are keyed correctly" if clean else "FINDINGS ABOVE")
