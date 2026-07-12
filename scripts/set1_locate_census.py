#!/usr/bin/env python3
"""set1_locate_census.py — ⟡defect-locate-census.

Run the §4 `Defect.locate` predicates (structural only — NO repair, NO numpy) over
EVERY Set₁-inhabiting definition in the elaborated cores, and report the honest
DEGREE: reducible (a located defect-coordinate) vs FLOOR (matched-by-none / a
genuine type-former the recursion bottoms at).

This is the measurement ⟡set1-degree-mechanical asked for, as a defect
CLASSIFICATION. Two structural facts the flat census surfaces:

  (1) 73% of the 697 Set₁ *units* are FUNCTION-INSTANCES `f : Γ → D args` returning
      a Def `D` — they are not defects themselves, they INHERIT D's status. They
      collapse onto ~100 distinct TARGETS `D` (the real defect surface). So the
      degree is a property of the ~100 targets, not the 697.
  (2) The root targets `D` are mostly RECORDS the shim marks `level=None` (its level
      probe punts on a record whose sort it can't peel), so they hide in the 1143
      null-level units, not the 697. We classify them via their FIELD-PROJECTION
      head signatures, gathered in the same pass.

LIFTED + IMPORTED, not re-rolled: the interned core term graph + per-unit
level/kind/members come from `jea.metalanguage.jea_agdai.core_intern_agdai` (the
same interner jea_pysim drives; its `intern_signature` was widened Φ7c to return
the `levels`/`sorts` it already parsed). We read constructor heads (`op`) off the
interned nodes — no bespoke JSON parse, no source regex.

locate predicates (structural, over the interned core term):
  · typeformer-floor  — Function/Datatype, codomain head (Πs peeled) == Sort.
                        Produces a type; irreducible — the Level floor.
  · set1-carrier      — Record with SOME field-projection returning Sort (a held
                        `: Set` carrier). The current `reconstruct` target; REDUCIBLE.
  · holds-set1-field  — Record whose SOME field is itself a Set₁ record/Σ (holds a
                        held structure); REDUCIBLE transitively (recurse on that field).
  · exists-collapse   — codomain / field head is a Σ Def.
  · foundation-floor  — target is a Foundation type-former (_≡_ over Set, List, …):
                        an irreducible Set₁ (type-equality / builtin). FLOOR.
  · instance          — Function returning a Def target; inherits the target's status
                        (residue = the target; deferred to the recursive descent).
  · constructor       — a Set₁ data constructor; attributed to its parent datatype.
  · UNMATCHED         — no locate fired: the honest residue (do NOT force a class).
"""
import sys, os, glob, collections
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from jea.metalanguage.jea_agdai import core_intern_agdai, Intern, substrate_core_root

AGDA_ROOT = os.environ.get("AGDA_ROOT") or os.path.join(_ROOT, "agda")

def cores():   # ⟡lift-shared-core-machinery: core-root path logic lifted to jea_agdai
    return sorted(glob.glob(os.path.join(substrate_core_root(AGDA_ROOT), "**", "*.agdai"), recursive=True))

SIGMA = ("Σ", "Sigma")
def _is_sigma(q):  return isinstance(q, str) and any(s in q for s in SIGMA)
def _is_qname(op): return isinstance(op, str) and "." in op

# Foundation type-formers whose Set₁-ness is irreducible (a type-equality / a builtin
# family), not a held carrier — the honest FLOOR the recursion bottoms at.
FOUNDATION_FLOOR = ("Foundation.Eq._≡_", "Foundation.List.List", "Foundation.Sigma",
                    "Foundation.Product", "Foundation.Sum", "Foundation.Vec.Vec",
                    "Foundation.Maybe", "Foundation.Bool", "Foundation.Fin")
def _is_foundation(q):
    return isinstance(q, str) and (".Foundation." in q or any(f in q for f in FOUNDATION_FLOOR))

def final_head(I, root):
    """Unwrap the `Defn` wrapper (child[0]=defType), then peel the Π-telescope;
    return the codomain's head node."""
    n = I.nodes[root]
    if n.op == "Defn" and n.children:
        n = I.nodes[n.children[0]]
    seen = 0
    while n.op == "Pi" and n.children and seen < 4096:
        n = I.nodes[n.children[-1]]
        seen += 1
    return n

def field_heads(I, name, root_of, members):
    """The codomain head-op of each of a record/datatype's field projections /
    constructor fields — the record's structural locate signature."""
    heads = []
    for m in members.get(name, ()):
        mr = root_of.get(m)
        if mr is not None:
            heads.append(final_head(I, mr).op)
    return heads

def main():
    cs = cores()
    print(f"  cores: {len(cs)}   (walking each Set₁ unit's interned root)")
    # one pass: classify Set₁ units flatly; gather every record/datatype's field-head signature.
    rec_sig = {}                       # qname -> [field codomain head-ops]  (all records, any level)
    rec_kind = {}                      # qname -> kind
    flat = []                          # (name, kind, bucket, target_qname_or_None)
    undec = 0
    for c in cs:
        I = Intern()
        try:
            rep = core_intern_agdai(c, I)
        except Exception:
            undec += 1; continue
        levels, kinds, members = rep["levels"], rep["kinds"], rep["members"]
        root_of = dict(rep["units"])
        for name, root in rep["units"]:
            k = kinds.get(name, "?")
            if k in ("Record", "Datatype"):
                rec_sig[name] = field_heads(I, name, root_of, members)
                rec_kind[name] = k
            lv = levels.get(name)
            if not (isinstance(lv, int) and lv >= 1):
                continue
            if k == "Constructor":
                flat.append((name, k, "constructor", None)); continue
            if k in ("Record", "Datatype"):
                flat.append((name, k, "__record__", name)); continue    # classify below vs its own sig
            # Function:
            fh = final_head(I, root)
            if fh.op == "Sort":
                flat.append((name, k, "typeformer-floor", None))
            elif _is_sigma(fh.op):
                flat.append((name, k, "exists-collapse", None))
            elif _is_qname(fh.op):
                flat.append((name, k, "instance", fh.op))               # inherits target
            else:
                flat.append((name, k, "function-other", None))

    def classify_record(q):
        """Locate a record/datatype target by its field-head signature."""
        if _is_foundation(q):                      return "foundation-floor"
        sig = rec_sig.get(q)
        if sig is None:                            return "record-unknown"   # not decoded as a record
        if any(h == "Sort" for h in sig):          return "set1-carrier"
        if any(_is_sigma(h) for h in sig):         return "exists-collapse"
        if any(_is_qname(h) and not _is_foundation(h) for h in sig):
            return "holds-set1-field"
        return "record-other"

    # resolve records + instances against the target classification
    buckets = collections.Counter()
    by_kind = collections.defaultdict(collections.Counter)
    target_fanin = collections.Counter()
    target_bucket = {}
    for name, kind, bucket, tq in flat:
        if bucket == "__record__":
            bucket = classify_record(name)
        elif bucket == "instance":
            tb = target_bucket.get(tq) or classify_record(tq)
            target_bucket[tq] = tb
            target_fanin[tq] += 1
            bucket = f"inst→{tb}"
        buckets[bucket] += 1
        by_kind[bucket][kind] += 1

    total = len(flat)
    REDUCIBLE = {"set1-carrier", "holds-set1-field", "exists-collapse",
                 "inst→set1-carrier", "inst→holds-set1-field", "inst→exists-collapse"}
    FLOOR = {"typeformer-floor", "constructor", "foundation-floor", "inst→foundation-floor"}
    print(f"  undecodable cores: {undec}")
    print(f"  Set₁-inhabiting units: {total}\n")
    print(f"  === locate buckets (flat degree over the 697) ===")
    for b, n in buckets.most_common():
        tag = "REDUCIBLE" if b in REDUCIBLE else ("FLOOR" if b in FLOOR else "RESIDUE")
        print(f"    {b:24s} {n:4d}  [{tag:9s}]  kinds={dict(by_kind[b])}")
    red = sum(n for b, n in buckets.items() if b in REDUCIBLE)
    flo = sum(n for b, n in buckets.items() if b in FLOOR)
    unm = total - red - flo
    print(f"\n  DEGREE (units):  reducible={red}  floor={flo}  residue={unm}   of {total}")

    print(f"\n  === the DEFECT SURFACE: {len(target_fanin)} distinct targets carry the "
          f"{sum(target_fanin.values())} instances ===")
    print(f"  (fix a target ⇒ all its instances pay down transitively)")
    for q, n in target_fanin.most_common(20):
        tb = target_bucket[q]
        tag = "REDUCIBLE" if tb in REDUCIBLE or tb in ("set1-carrier","holds-set1-field","exists-collapse") \
              else ("FLOOR" if tb in FLOOR or tb=="foundation-floor" else "RESIDUE")
        print(f"    {n:4d} inst  [{tb:16s} {tag:9s}] {q}")

    print(f"\n  === target buckets (the ~{len(target_fanin)} roots, by locate) ===")
    tb_count = collections.Counter(target_bucket[q] for q in target_fanin)
    for b, n in tb_count.most_common():
        print(f"    {b:20s} {n:3d} targets  ({sum(target_fanin[q] for q in target_fanin if target_bucket[q]==b)} inst)")

if __name__ == "__main__":
    main()
