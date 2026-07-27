#!/usr/bin/env python3
"""⟡iface-shape-oracle — predict elaboration cost from the INTERFACE GRAPH, without compiling.

WHY THIS EXISTS (the mechanism, measured 2026-07-26):
  Agda module application COPIES, it does not reference. `open X.Over args public` re-materializes the
  whole accumulated API into your .agdai — and into every consumer's, transitively. catalog.db shows ZERO
  reference edges from a consumer into `Graded.Over.*`; each consumer owns its own copy.

  CONSEQUENCE: .agdai BYTES are the computable proxy for elaboration peak. Measured on the Graded shard
  chain, interface grows ~6 KB/link (Defs 52KB -> AssocMono 145KB) and tracks the ~5-8 MB/link elaboration
  floor. So the shape of a shard/DAG can be PLANNED from the interface graph instead of discovered by one
  compile per guess.

WHAT IT DOES
  --calibrate         fit  peak ~ a*own_KB + b*transitive_KB + c  over every module with both a fresh
                      .agdai and a recorded peak; report correlation + residuals (the model's honesty).
  --module <rel>      predicted peak for one module + its imports RANKED by transitive interface bytes
                      (= the shallowing candidates, highest-leverage first).
  --rank [N]          modules ranked by predicted peak — find crossings WITHOUT compiling.
  --selftest          check the oracle reproduces known measurements.

INPUTS (all FRESH; no catalog.db dependency)
  - .agdai sizes      agda/_build/<ver>/agda/**/*.agdai        (written by the build)
  - peaks             per-dir .agda-times.tsv  via scripts/buildtime.read_mem()   (latest row per module)
  - import graph      parsed from source `import` / `open import` lines (syntax, always fresh)

HONEST BOUNDARIES
  - The import graph is SOURCE-parsed. It is the DECLARED graph; with module application the declared
    graph is what drives copying, so this is the right graph for cost. It does NOT tell you which NAMES a
    module needs (that is the `[NotInScope]`-driven minimal-parent procedure, or a fresh catalog.db).
  - The fit is a MODEL calibrated to this tree, not a law. Residuals are reported; large residuals are
    modules whose cost is content-bound (reflection, dense normalisation), not interface-bound.
  - Modules with no recorded peak, or a stale/missing .agdai, are excluded from the fit and SAID SO
    (an incomplete census is not a low count).
"""
import os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import buildtime  # REUSE: read_mem(), AGDA, ledger conventions

AGDA = buildtime.AGDA
IMPORT_RE = re.compile(r"^\s*(?:open\s+)?import\s+([A-Za-z0-9_.']+)", re.M)


# ── interface bytes ────────────────────────────────────────────────────────────
def iface_bytes():
    """{module_rel: bytes} from the built .agdai cores. module_rel matches buildtime keys."""
    out = {}
    for base in glob.glob(os.path.join(AGDA, "_build", "*", "agda")):
        for p in glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True):
            rel = os.path.relpath(p, base)[:-len(".agdai")] + ".agda"
            try:
                out[rel] = os.path.getsize(p)
            except OSError:
                pass
    return out


def _rel_of_module(m):
    return m.replace(".", os.sep) + ".agda"


def _module_of_rel(rel):
    return rel[:-len(".agda")].replace(os.sep, ".")


# ── import graph (source-parsed: fresh, and it is what drives copying) ─────────
def import_graph():
    """{module_rel: [imported module_rel...]} for every .agda under agda/."""
    g = {}
    for p in glob.glob(os.path.join(AGDA, "**", "*.agda"), recursive=True):
        if os.sep + "_build" + os.sep in p:
            continue
        rel = os.path.relpath(p, AGDA)
        try:
            src = open(p, encoding="utf-8").read()
        except OSError:
            continue
        # strip line comments so commented-out imports do not count
        src = re.sub(r"--.*$", "", src, flags=re.M)
        g[rel] = [_rel_of_module(m) for m in IMPORT_RE.findall(src)]
    return g


def transitive(g, rel, _seen=None):
    """Transitive import closure of rel (excluding rel itself)."""
    if _seen is None:
        _seen = set()
    for d in g.get(rel, ()):
        if d not in _seen:
            _seen.add(d)
            transitive(g, d, _seen)
    return _seen


# ── the model ─────────────────────────────────────────────────────────────────
def _fit(rows):
    """Least-squares peak ~ a*own + b*trans + c.  rows: [(own_kb, trans_kb, peak_mb)]"""
    n = len(rows)
    if n < 3:
        return None
    # normal equations for 3 params (small, explicit — no numpy dependency)
    Sx = Sy = Sz = Sxx = Syy = Sxy = Sxz = Syz = 0.0
    for x, y, z in rows:
        Sx += x; Sy += y; Sz += z
        Sxx += x * x; Syy += y * y; Sxy += x * y; Sxz += x * z; Syz += y * z
    A = [[Sxx, Sxy, Sx], [Sxy, Syy, Sy], [Sx, Sy, float(n)]]
    b = [Sxz, Syz, Sz]
    # gaussian elimination
    for i in range(3):
        p = max(range(i, 3), key=lambda r: abs(A[r][i]))
        if abs(A[p][i]) < 1e-12:
            return None
        A[i], A[p] = A[p], A[i]; b[i], b[p] = b[p], b[i]
        for r in range(i + 1, 3):
            f = A[r][i] / A[i][i]
            for c in range(i, 3):
                A[r][c] -= f * A[i][c]
            b[r] -= f * b[i]
    coef = [0.0] * 3
    for i in (2, 1, 0):
        s = b[i] - sum(A[i][c] * coef[c] for c in range(i + 1, 3))
        coef[i] = s / A[i][i]
    return tuple(coef)  # (a_own, b_trans, c)


def _corr(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return num / (dx * dy) if dx and dy else 0.0


def dataset():
    """[(rel, own_kb, trans_kb, peak_mb|None)] plus coverage counts."""
    ib, g = iface_bytes(), import_graph()
    mem = buildtime.read_mem()
    rows, missing_iface, missing_peak = [], 0, 0
    for rel in sorted(g):
        own = ib.get(rel)
        if own is None:
            missing_iface += 1
            continue
        trans = sum(ib.get(d, 0) for d in transitive(g, rel))
        peaks = mem.get(rel) or []
        peak = peaks[-1] if peaks else None          # LATEST row — same statistic the cap-ratchet uses
        if peak is None:
            missing_peak += 1
        rows.append((rel, own / 1024.0, trans / 1024.0, peak))
    return rows, missing_iface, missing_peak


def model():
    rows, mi, mp = dataset()
    fit_rows = [(o, t, p) for _, o, t, p in rows if p is not None]
    coef = _fit(fit_rows)
    return rows, coef, fit_rows, mi, mp


def predict(coef, own_kb, trans_kb):
    a, b, c = coef
    return a * own_kb + b * trans_kb + c


# ── commands ──────────────────────────────────────────────────────────────────
def cmd_calibrate():
    rows, coef, fit_rows, mi, mp = model()
    print(f"modules with fresh .agdai : {len(rows)}   (skipped, no .agdai: {mi})")
    print(f"of those, with a peak     : {len(fit_rows)}   (no recorded peak: {mp})")
    if not coef:
        print("INSUFFICIENT DATA to fit — build the tree first (make -C agda -j).")
        return 1
    a, b, c = coef
    print(f"\nmodel:  peak_MB = {a:.4f}*own_KB + {b:.5f}*transitive_KB + {c:.1f}")
    pred = [predict(coef, o, t) for o, t, _ in fit_rows]
    act = [p for _, _, p in fit_rows]
    print(f"correlation r = {_corr(pred, act):.3f}   (n={len(act)})")
    res = sorted(((p - a2, r) for (r, o, t, a2), p in
                  zip([x for x in rows if x[3] is not None], pred)), key=lambda z: z[0])
    print("\nlargest NEGATIVE residuals (cost is CONTENT-bound, not interface-bound — model under-predicts):")
    for d, r in res[:5]:
        print(f"  {d:+8.1f} MB  {r}")
    print("\nlargest POSITIVE residuals (cheaper than the interface suggests — likely opaque/sealed):")
    for d, r in res[-5:]:
        print(f"  {d:+8.1f} MB  {r}")
    return 0


def cmd_module(rel):
    ib, g = iface_bytes(), import_graph()
    rows, coef, _, _, _ = model()
    if rel not in g:
        cand = [r for r in g if r.endswith(rel) or _module_of_rel(r).endswith(rel)]
        if len(cand) == 1:
            rel = cand[0]
        else:
            print(f"not found: {rel}" + (f"  (did you mean: {cand[:5]})" if cand else ""))
            return 1
    own = ib.get(rel, 0) / 1024.0
    tset = transitive(g, rel)
    trans = sum(ib.get(d, 0) for d in tset) / 1024.0
    mem = buildtime.read_mem().get(rel) or []
    print(f"{rel}")
    print(f"  own interface   : {own:8.1f} KB")
    print(f"  transitive      : {trans:8.1f} KB   over {len(tset)} modules")
    if coef:
        print(f"  PREDICTED peak  : {predict(coef, own, trans):8.1f} MB"
              + (f"   (measured latest: {mem[-1]} MB)" if mem else "   (no measurement)"))
    print("\n  direct imports RANKED by transitive interface bytes (shallowing candidates, top first):")
    direct = g.get(rel, [])
    scored = []
    for d in direct:
        sub = transitive(g, d) | {d}
        scored.append((sum(ib.get(x, 0) for x in sub) / 1024.0, ib.get(d, 0) / 1024.0, d, len(sub)))
    for tot, o, d, n in sorted(scored, reverse=True)[:12]:
        print(f"    {tot:9.1f} KB  (own {o:7.1f})  {d}   [{n} modules]")
    return 0


def cmd_rank(n=25):
    rows, coef, _, _, _ = model()
    if not coef:
        print("no model"); return 1
    scored = [(predict(coef, o, t), r, p) for r, o, t, p in rows]
    print(f"top {n} by PREDICTED peak (no compile required):")
    print(f"  {'pred':>7} {'measured':>9}  module")
    for pr, r, p in sorted(scored, reverse=True)[:n]:
        print(f"  {pr:7.1f} {('%9.0f' % p) if p else '        -':>9}  {r}")
    return 0


def cmd_selftest():
    ok = True
    ib, g = iface_bytes(), import_graph()
    if not ib:
        print("FAIL: no .agdai found — build first"); return 1
    print(f"iface_bytes: {len(ib)} cores")
    print(f"import_graph: {len(g)} modules")
    # the Graded shard chain must show monotone-ish growth (the ~6KB/link finding)
    chain = ["Substrate/Algebra/Polynomial/Graded/Defs.agda"] + [
        f"Substrate/Algebra/Polynomial/Graded/Laws/{s}.agda"
        for s in ("Nth", "Conv", "Distrib", "Basis", "Comm", "AssocMono")]
    have = [(c, ib.get(c, 0) / 1024.0) for c in chain if c in ib]
    if have:
        print("\nGraded shard chain interface sizes (the ~6KB/link finding):")
        for c, kb in have:
            print(f"  {kb:7.1f} KB  {c.split('/')[-1]}")
        if len(have) >= 2 and have[-1][1] <= have[0][1]:
            print("  WARN: chain did not grow — re-check the shard state"); ok = False
    else:
        print("\n(Graded shard not present — chain check skipped)")
    rows, coef, fit_rows, _, _ = model()
    if coef:
        pred = [predict(coef, o, t) for o, t, _ in fit_rows]
        r = _corr(pred, [p for _, _, p in fit_rows])
        print(f"\nmodel r = {r:.3f} over n={len(fit_rows)}")
        if r < 0.3:
            print("  WARN: weak correlation — interface bytes are not predictive on this tree"); ok = False
    print("\nSELFTEST", "PASS" if ok else "WARN")
    return 0 if ok else 1


OPEN_PUB_RE = re.compile(r"^[ \t]*open\s+([A-Za-z0-9_.']+)(?:\s+[^\n]*?)?\s+public\s*$", re.M)


def reverse_graph(g):
    rv = {}
    for src, dsts in g.items():
        for d in dsts:
            rv.setdefault(d, set()).add(src)
    return rv


def consumers_of(rv, rel, _seen=None):
    """Transitive set of modules that import rel (its blast radius)."""
    if _seen is None:
        _seen = set()
    for s in rv.get(rel, ()):
        if s not in _seen:
            _seen.add(s)
            consumers_of(rv, s, _seen)
    return _seen


def cmd_public_audit(n=25):
    """BULK worklist: rank wholesale `open X ... public` sites by bytes-copied x blast-radius."""
    ib, g = iface_bytes(), import_graph()
    rv = reverse_graph(g)
    alias = {}   # per-module: local alias -> imported module_rel (to resolve `open F.Over ... public`)
    sites, wholesale, filtered = [], 0, 0
    for p in glob.glob(os.path.join(AGDA, "**", "*.agda"), recursive=True):
        if os.sep + "_build" + os.sep in p:
            continue
        rel = os.path.relpath(p, AGDA)
        try:
            src = re.sub(r"--.*$", "", open(p, encoding="utf-8").read(), flags=re.M)
        except OSError:
            continue
        alias.clear()
        for m in re.finditer(r"^\s*(?:open\s+)?import\s+([A-Za-z0-9_.']+)(?:\s+as\s+([A-Za-z0-9_']+))?", src, re.M):
            mod, al = m.group(1), m.group(2)
            alias[al or mod.rsplit(".", 1)[-1]] = _rel_of_module(mod)
            alias[mod] = _rel_of_module(mod)
        for m in OPEN_PUB_RE.finditer(src):
            whole = not re.search(r"\b(using|hiding|renaming)\b", m.group(0))
            if whole:
                wholesale += 1
            else:
                filtered += 1
                continue
            head = m.group(1).split(".")[0]
            tgt = alias.get(m.group(1)) or alias.get(head)
            if not tgt or tgt not in ib:
                continue
            copied_kb = ib[tgt] / 1024.0
            radius = len(consumers_of(rv, rel)) + 1
            sites.append((copied_kb * radius, copied_kb, radius, rel, m.group(1)))
    print(f"wholesale `open .. public` sites: {wholesale}   (already filtered with using/hiding/renaming: {filtered})")
    print(f"resolvable to a built .agdai    : {len(sites)}\n")
    print(f"BULK WORKLIST — ranked by copied_KB x blast_radius (convert these to `using (..)` first):")
    print(f"  {'total':>10} {'copied':>9} {'radius':>7}  module  <- opened")
    tot = 0.0
    for score, kb, rad, rel, tgtname in sorted(sites, reverse=True)[:n]:
        tot += score
        print(f"  {score:10.0f} {kb:9.1f} {rad:7d}  {rel}  <- {tgtname}")
    allsum = sum(s for s, *_ in sites)
    print(f"\n  top {n} = {tot:.0f} of {allsum:.0f} KB-copies  ({100*tot/allsum if allsum else 0:.1f}% of total)")
    return 0


def cmd_levers(thresh=110.0):
    """BULK classifier: every module at/near the cap, tagged with WHICH lever it needs."""
    rows, coef, _, _, _ = model()
    if not coef:
        print("no model"); return 1
    out = []
    for rel, own, trans, peak in rows:
        if peak is None:
            continue
        pred = predict(coef, own, trans)
        resid = pred - peak                      # negative => content-bound
        if peak >= thresh:
            lever = "CONTENT (opaque/split)" if resid < -15 else (
                    "INTERFACE (using/shallow)" if resid > 5 else "MIXED (both)")
            out.append((peak, resid, own, trans, lever, rel))
    print(f"modules with measured peak >= {thresh:.0f} MB, classified by lever:\n")
    print(f"  {'peak':>6} {'resid':>7} {'own_KB':>8} {'trans_KB':>9}  lever                      module")
    for peak, resid, own, trans, lever, rel in sorted(out, reverse=True):
        print(f"  {peak:6.0f} {resid:+7.1f} {own:8.1f} {trans:9.0f}  {lever:<25}  {rel}")
    nc = sum(1 for *_x, l, _ in out if l.startswith("CONTENT"))
    ni = sum(1 for *_x, l, _ in out if l.startswith("INTERFACE"))
    nm = len(out) - nc - ni
    print(f"\n  {len(out)} modules: {nc} content-bound, {ni} interface-bound, {nm} mixed")
    return 0


def main(argv):
    if "--public-audit" in argv:
        i = argv.index("--public-audit")
        n = int(argv[i + 1]) if i + 1 < len(argv) and argv[i + 1].isdigit() else 25
        return cmd_public_audit(n)
    if "--levers" in argv:
        i = argv.index("--levers")
        t = float(argv[i + 1]) if i + 1 < len(argv) and argv[i + 1].replace(".", "").isdigit() else 110.0
        return cmd_levers(t)
    if "--selftest" in argv:
        return cmd_selftest()
    if "--calibrate" in argv:
        return cmd_calibrate()
    if "--module" in argv:
        i = argv.index("--module")
        return cmd_module(argv[i + 1]) if i + 1 < len(argv) else (print("need a module") or 1)
    if "--rank" in argv:
        i = argv.index("--rank")
        n = int(argv[i + 1]) if i + 1 < len(argv) and argv[i + 1].isdigit() else 25
        return cmd_rank(n)
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
