#!/usr/bin/env python3
"""reuse_tui.py — a Textual TUI over the interned SPPF (the whole agglomerated structural space).

Every canonical node with fanin ≥ 2 is duplicated structure = a consolidation opportunity (N instances
of one pattern → parameterize; fanin = instances = the win). Left: a TREE of ORBITS — shared subtrees
grouped by their instance-set (the set of units that co-share them), so a big structure and all its
sub-slices (which share the same units) collapse to ONE orbit; expand an orbit to its shared subtrees.
Right: the selected orbit/subtree's instances as a MODULE TREE (navigate to the canonical home) + what
it ⊃ contains. Filter by head; sort orbits by impact/size/fanin/n_subtrees. `x` exports an LLM
consolidation work-order (orbit or subtree). CLI --observe Q / --between A B do the same non-interactively.

  scripts/reuse_tui.py --build     # intern the forest (~90s) → cache (do once)
  scripts/reuse_tui.py             # load cache, launch the browser
"""
import sys, os, re, json, argparse, glob

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGDA = os.path.join(REPO, "agda")
CACHE = os.path.join(REPO, "scratch", "generated", "sppf_index.json")
OBS_DIR = os.path.join(REPO, "scratch", "generated", "observations")

# --------------------------------------------------------------------------- observation export
def qname_to_file(qname):
    """map a def qname to its source .agda file (deepest existing module prefix)."""
    parts = qname.split(".")
    for k in range(len(parts), 0, -1):
        p = os.path.join(AGDA, *parts[:k]) + ".agda"
        if os.path.exists(p):
            return os.path.relpath(p, REPO)
    return "?"

def observation_md(r):
    """an LLM-ready consolidation work-order for one shared subtree."""
    insts = sorted(r["instances"], key=lambda n: (n.count("."), n))
    canonical = insts[0]
    files = sorted({qname_to_file(n) for n in insts})
    L = [f"# Consolidation observation — `{r['head']}`", "",
         f"Shared subtree `{r['head']}` — size {r['size']}, **{r['fanin']} instances**, rung {r['rung']}, "
         f"impact {r['fanin'] * r['size']}."]
    if r["contains"]:
        L.append(f"⊃ contains: {', '.join(r['contains'])}.")
    L += ["", "## Instances (canonical candidate first = shallowest module)", ""]
    for n in insts:
        L.append(f"- `{n}`  →  `{qname_to_file(n)}`")
    L += ["", "## Files touched", ""] + [f"- `{f}`" for f in files]
    L += ["", "## Instruction (for an LLM)", "",
          f"These {r['fanin']} units share the structure rooted at `{r['head']}`. Consolidate it:",
          f"1. Extract ONE parameterized abstraction (a record / def / parameterized module) capturing the",
          f"   shared shape, homed at the canonical module of `{canonical}` (or a shallower shared parent).",
          f"2. Rewrite each instance above to INSTANTIATE that abstraction — X is an instance of Y, and that",
          f"   is the goal (consolidation), not a workaround.",
          f"3. Verify: every touched file typechecks `--safe --without-K`; then re-run",
          f"   `scripts/reuse_sweep.py <changed files>` and confirm this subtree's fanin has collapsed onto",
          f"   the single abstraction.", ""]
    return "\n".join(L)

# --------------------------------------------------------------------------- build (query the DB)
CATALOG_DB = os.path.join(REPO, "catalog", "catalog.db")

def db_rows(min_size, min_fanin, cap=None):
    """The consolidation rows DERIVED from the event-sourced projection (catalog.db) — NOT a re-intern.
    The SPPF (_node/node_child/shared_subtree/unit_node) and defCopy provenance (unit.copy) are already
    materialized there; head/size/instances/contains/rung all derive from node_child + unit_node.
    Returns (rows, copy_units, ncores, n_candidates). Shared by --build (caches) and reuse_sweep."""
    import sqlite3
    from collections import defaultdict as _dd
    if not os.path.exists(CATALOG_DB):
        sys.exit(f"reuse: ABORT — no catalog.db at {CATALOG_DB}. Regenerate the projection:\n"
                 f"    python3 scripts/sppf_db.py \"\"        # event-source all cores → SPPF projection")
    con = sqlite3.connect(CATALOG_DB)
    have_copy = any(r[1] == "copy" for r in con.execute("PRAGMA table_info(_unit)"))
    if not have_copy:                                              # loud, not silent — verdicts degrade
        print("⚠ catalog.db has NO defCopy provenance (copy column absent) — orbit verdicts degrade to the "
              "def-site HEURISTIC. Rebuild with the current sppf_db:  python3 scripts/sppf_db.py \"\"",
              file=sys.stderr, flush=True)
    sys.setrecursionlimit(1 << 20)
    print("loading SPPF from catalog.db …", flush=True)
    child = _dd(list)
    for nid, cid in con.execute("SELECT node_id, child_id FROM node_child ORDER BY node_id, ord"):
        child[nid].append(cid)
    # head from _node with LEFT JOINs (the `node` view inner-joins kind_id, which doesn't resolve — a
    # pre-existing projection bug; role_id does resolve, so op ▸ role ▸ '?').
    head = {}
    for nid, op_p, op_t, role in con.execute(
            "SELECT n.node_id, pt.text, o.text, r.text FROM _node n "
            "LEFT JOIN path_text pt ON pt.path_id=n.op_path_id "
            "LEFT JOIN terms o ON o.term_id=n.op_term_id "
            "LEFT JOIN terms r ON r.term_id=n.role_id"):
        head[nid] = op_p or op_t or role or "?"
    shared = {nid: f for nid, f in
              con.execute("SELECT node_id, fanin FROM shared_subtree WHERE fanin>=?", (min_fanin,))}
    # subtree weight: unfolded node count, CAPPED (a DAG's true unfolding explodes exponentially under
    # sharing, and the exact distinct-descendant count costs ~4.5GB/32s — too heavy for a browse tool).
    # Capping keeps it O(V+E) and bounded; top nodes saturate at SIZE_CAP, where fanin is the real ranker.
    SIZE_CAP = 99999
    size = {}
    def sz(n):
        v = size.get(n)
        if v is not None: return v
        size[n] = 1                                               # cycle guard
        s = 1
        for c in child.get(n, ()):
            s += sz(c)
            if s >= SIZE_CAP: s = SIZE_CAP; break
        size[n] = s; return s
    for n in shared: sz(n)
    # topmost shared descendants (→ `contains`) + containment height (→ `rung`), memoized
    dsc = {}
    def descsh(n):
        v = dsc.get(n)
        if v is not None: return v
        dsc[n] = frozenset()
        acc = set()
        for c in child.get(n, ()):
            acc.add(c) if c in shared else acc.update(descsh(c))
        r = frozenset(acc); dsc[n] = r; return r
    rung = {}
    def hei(n):
        v = rung.get(n)
        if v is not None: return v
        rung[n] = 0
        kids = descsh(n)
        h = 1 + max((hei(k) for k in kids), default=-1) if kids else 0
        rung[n] = h; return h
    # instances (unit names) sharing each shared node, + the defCopy set
    uname, copy_units = {}, []
    for uid, name in con.execute("SELECT u.unit_id, pt.text FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid"):
        uname[uid] = name
    if have_copy:
        copy_units = sorted(name for uid, name in
            ((uid, uname[uid]) for uid, in con.execute("SELECT unit_id FROM _unit WHERE copy=1")) if uid in uname)
    units_of = _dd(set)
    for uid, nid in con.execute("SELECT unit_id, node_id FROM unit_node"):
        if nid in shared and uid in uname: units_of[nid].add(uid)
    print(f"{len(uname)} units, {len(shared)} shared subtrees; assembling rows …", flush=True)
    rows = []
    for nid in shared:
        if size.get(nid, 0) < min_size: continue
        insts = sorted(uname[u] for u in units_of.get(nid, ()))
        if len(insts) < min_fanin: continue                       # instance-fanin: shared across ≥min_fanin units
        contains = sorted({head.get(k, "?") for k in descsh(nid)})
        rows.append({"fanin": len(insts), "size": size[nid], "head": head.get(nid, "?"),
                     "rung": hei(nid), "contains": contains, "instances": insts})
    rows.sort(key=lambda r: -(r["fanin"] * r["size"]))
    if cap: rows = rows[:cap]
    ncores = con.execute("SELECT COUNT(DISTINCT file_id) FROM _unit").fetchone()[0]
    return rows, copy_units, ncores, len(shared)

def build(cache_path, min_size, min_fanin, cap):
    """Cache the DB-derived consolidation rows for the TUI. Sourced from catalog.db (db_rows), no re-intern."""
    rows, copy_units, ncores, ncand = db_rows(min_size, min_fanin, cap)
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    json.dump({"rows": rows, "units": None, "cores": ncores, "n_candidates": ncand,
               "copy_units": copy_units, "source": "catalog.db"}, open(cache_path, "w"))
    print(f"✓ cached {len(rows)} shared subtrees ({len(copy_units)} defCopy instances) from catalog.db "
          f"→ {cache_path}")
    if not copy_units:
        print("⚠ 0 defCopy instances — the projection may predate a fresh ingest (python3 scripts/sppf_db.py \"\").",
              file=sys.stderr, flush=True)

# --------------------------------------------------------------------------- orbit grouping
from collections import defaultdict

def _impact(r): return r["fanin"] * r["size"]

def orbit_pref(units):
    """the shared neighbourhood: common module prefix of an orbit's units."""
    cp = os.path.commonprefix(list(units))
    return cp.rsplit(".", 1)[0] if "." in cp else cp or "(mixed)"

# --- consolidated vs dup, mechanically: does the orbit resolve to ONE shared definition, or is each
#     instance's leaf defined INSIDE its own module?  (WithLemmas.normalize-idem → one Core file = ✓;
#     each group redefining it → def-site == instance file = ✗.)
DEF_INDEX_PATH = os.path.join(REPO, "scratch", "generated", "def_index.json")
def scan_def_index():
    idx = defaultdict(set)
    sub = os.path.join(AGDA, "Substrate")
    for root, _, files in os.walk(sub):
        if "_build" in root:
            continue
        for f in files:
            if not f.endswith(".agda"):
                continue
            rel = os.path.relpath(os.path.join(root, f), REPO)
            try:
                for line in open(os.path.join(root, f), errors="replace"):
                    m = re.match(r"^\s*([^\s:{}()]+)\s+:\s", line)
                    if m:
                        idx[m.group(1)].add(rel)
            except OSError:
                pass
    return {k: sorted(v) for k, v in idx.items()}

def load_def_index():
    if os.path.exists(DEF_INDEX_PATH):
        return json.load(open(DEF_INDEX_PATH))
    idx = scan_def_index()
    os.makedirs(os.path.dirname(DEF_INDEX_PATH), exist_ok=True)
    json.dump(idx, open(DEF_INDEX_PATH, "w"))
    return idx

def resolve_orbit(units, defidx, copy_units=None):
    """verdict: is this orbit already CONSOLIDATED (instances of shared defs) or a DUP (each redefines)?
    PRECISE via Agda's defCopy when available (copy_units = the set of defCopy=True qnames); else the
    def-site heuristic (is each leaf defined in a module OTHER than the instances)."""
    if copy_units:                                   # provenance present → the EXACT signal (defCopy)
        cop = sum(1 for u in units if u in copy_units)
        if cop >= 0.8 * len(units):                  # (nearly) all instances are module-instantiation copies
            return "CONSOLIDATED", [f"defCopy: {cop}/{len(units)} are module-instantiation copies"], cop, len(units) - cop, "defCopy"
        if cop == 0:                                 # all originals sharing structure → genuine dup
            return "DUP", ["defCopy: 0 copies — independent definitions"], 0, len(units), "defCopy"
        return "MIXED", [f"defCopy: {cop}/{len(units)} copies"], cop, len(units) - cop, "defCopy"
    # NO provenance in the cache — the def-site HEURISTIC (weaker; announce it, do not pass silently).
    from collections import defaultdict as _dd
    inst_files = {qname_to_file(u) for u in units}
    ext_homes, ext, local = _dd(int), 0, 0
    for leaf in {u.split(".")[-1] for u in units}:
        sites = set(defidx.get(leaf, []))
        outside = sites - inst_files
        if outside:                                  # defined in a shared module (not an instance) → consolidated
            ext += 1
            for h in outside: ext_homes[h] += 1
        elif sites:                                  # defined only inside the instances → duplicated
            local += 1
    homes = sorted(ext_homes, key=lambda h: -ext_homes[h])[:5]
    verdict = "CONSOLIDATED" if ext > local else ("DUP" if local else "mixed")
    return verdict, homes, ext, local, "heuristic"

def observation_orbit(units, subs, defidx=None, copy_units=None):
    """an LLM work-order for a whole ORBIT: these units co-share this structure — consolidate the pair/set."""
    us = sorted(units, key=lambda n: (n.count("."), n))
    big = max(subs, key=_impact)
    verdict, homes, ext, local, method = resolve_orbit(units, defidx if defidx is not None else load_def_index(), copy_units)
    L = [f"# Consolidation observation — ORBIT of {len(units)} co-sharing units @ `{orbit_pref(units)}`", "",
         f"**Verdict: {verdict}** — via {'defCopy (exact)' if method=='defCopy' else 'DEF-SITE HEURISTIC (no defCopy provenance in the cache — rebuild the .agdai for the exact signal)'}.", ""]
    if verdict == "CONSOLIDATED":
        L += [f"→ ALREADY CONSOLIDATED: these are INSTANCES of shared definitions homed at "
              f"{', '.join('`'+h+'`' for h in homes)}. **No action** — the sharing is the fingerprint of "
              f"an existing parameterization (e.g. a parameterized module instantiated per unit). Skip.", ""]
        L += [f"(Largest shared shape: `{big['head']}` size {big['size']}. Units: {len(units)}.)", ""]
        return "\n".join(L)
    L += [f"These {len(units)} units share {len(subs)} subtree(s) (one SPPF orbit); largest: `{big['head']}` "
          f"size {big['size']}. Their distinctive leaves are defined INDEPENDENTLY (not from a shared "
          f"module) — a genuine duplication.", "", "## Units (canonical = shallowest)", ""]
    L += [f"- `{u}`  →  `{qname_to_file(u)}`" for u in us[:40]]
    L += ["", "## Shared subtrees (this orbit)", ""]
    L += [f"- `{s['head']}` — size {s['size']}, rung {s['rung']}" for s in sorted(subs, key=lambda s: -_impact(s))[:20]]
    L += ["", "## Instruction (for an LLM)", "",
          f"These {len(units)} units are ONE orbit sharing the structure above, with INDEPENDENT definitions.",
          f"Consolidate:",
          f"1. Extract ONE parameterized abstraction (record / def / parameterized module) capturing the",
          f"   shared shape, homed at the canonical module of `{us[0]}` (or a shallower shared parent).",
          f"2. Rewrite each unit to INSTANTIATE it (X is an instance of Y — the goal).",
          f"3. Verify --safe --without-K; re-run scripts/reuse_sweep.py on the touched files; the orbit's",
          f"   shared subtrees should collapse onto the single abstraction.", ""]
    return "\n".join(L)

# --------------------------------------------------------------------------- Textual app
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Tree, Input, Header, Footer
from textual.binding import Binding

ORBIT_SORTS = ["impact", "size", "fanin", "n_subtrees"]

class SPPF(App):
    CSS = """
    #orbits { width: 55%; }
    #detail { width: 45%; border-left: solid $accent; }
    Input { dock: top; }
    """
    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("s", "sort", "sort"),
        Binding("x", "extract", "extract obs"),
        Binding("slash", "focus_filter", "filter"),
        Binding("escape", "unfocus_filter", "unfilter"),
    ]

    def __init__(self, rows, meta):
        super().__init__()
        self.allrows = rows
        self.meta = meta
        self.sort_key = "impact"
        self.filt = ""
        self.defidx = load_def_index()
        self.copy_units = set(meta.get('copy_units', []))
        orbits = defaultdict(list)
        for r in rows:
            orbits[frozenset(r["instances"])].append(r)
        self.orbits = list(orbits.items())            # [(frozenset units, [rows])]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Input(placeholder="filter by head substring …  (/ focus, Esc leave)", id="filter")
        with Horizontal():
            yield Tree("orbits", id="orbits")
            yield Tree("detail", id="detail")
        yield Footer()

    def on_mount(self):
        self.refresh_orbits()
        self.query_one("#orbits", Tree).focus()

    def _orbit_key(self, item):
        units, subs = item
        if self.sort_key == "n_subtrees": return -len(subs)
        if self.sort_key == "fanin": return -len(units)
        if self.sort_key == "size": return -max(s["size"] for s in subs)
        return -max(_impact(s) for s in subs)

    def refresh_orbits(self):
        tree = self.query_one("#orbits", Tree)
        tree.reset("orbits")
        items = []
        for units, subs in self.orbits:
            fs = [s for s in subs if not self.filt or self.filt.lower() in s["head"].lower()]
            if fs: items.append((units, fs))
        items.sort(key=self._orbit_key)
        shown = items[:1500]
        for units, subs in shown:
            mx = max(_impact(s) for s in subs)
            node = tree.root.add(f"[{len(subs):>3} sub · ×{len(units)} · ≤{mx}]  {orbit_pref(units)}",
                                 data=("orbit", units, subs))
            for s in sorted(subs, key=lambda s: -_impact(s)):
                node.add_leaf(f"{s['head']}  · size {s['size']} rung {s['rung']}", data=("sub", s))
        tree.root.expand()
        self.sub_title = (f"{len(items)} orbits ({len(self.allrows)} subtrees, {self.meta['units']} units) · "
                          f"sort:{self.sort_key} · filter:'{self.filt}'")
        if shown: self.show_orbit(shown[0][0], shown[0][1])

    def _detail_instances(self, tree, units):
        ins = tree.root.add(f"instances ({len(units)}) — canonical = shallowest", expand=True)
        for name in sorted(units):
            node = ins
            parts = name.split(".")
            for j, p in enumerate(parts):
                if j == len(parts) - 1:
                    node.add_leaf(p)
                else:
                    child = next((c for c in node.children if str(c.label) == p), None)
                    node = child if child is not None else node.add(p)

    def show_orbit(self, units, subs):
        tree = self.query_one("#detail", Tree)
        verdict, homes, ext, local, method = resolve_orbit(units, self.defidx, self.copy_units)
        mark = {"CONSOLIDATED": "✓", "DUP": "✗"}.get(verdict, "·")
        via = "defCopy" if method == "defCopy" else "⚠HEURISTIC (no defCopy — rebuild cores)"
        tree.reset(f"{mark} {verdict} [{via}] — {len(units)} units · {len(subs)} subtrees @ {orbit_pref(units)}")
        if verdict == "CONSOLIDATED":
            h = tree.root.add(f"already consolidated onto ({ext}/{ext+local} leaves shared) — SKIP", expand=True)
            for m in homes: h.add_leaf(m)
        else:
            tree.root.add(f"⚠ {local}/{ext+local} distinct leaves defined INDEPENDENTLY — genuine dup", expand=True)
        self._detail_instances(tree, units)
        tree.root.expand()

    def show_sub(self, r):
        tree = self.query_one("#detail", Tree)
        tree.reset(f"{r['head']}  [{r['fanin']} instances × size {r['size']} · rung {r['rung']}]")
        if r["contains"]:
            c = tree.root.add(f"⊃ contains ({len(r['contains'])})")
            for h in r["contains"]:
                c.add_leaf(h)
        self._detail_instances(tree, r["instances"])
        tree.root.expand()

    def on_tree_node_highlighted(self, event):
        d = getattr(event.node, "data", None)
        if not d: return
        if d[0] == "orbit": self.show_orbit(d[1], d[2])
        elif d[0] == "sub": self.show_sub(d[1])

    def on_input_changed(self, event):
        self.filt = event.value
        self.refresh_orbits()

    def action_sort(self):
        self.sort_key = ORBIT_SORTS[(ORBIT_SORTS.index(self.sort_key) + 1) % len(ORBIT_SORTS)]
        self.refresh_orbits()

    def action_focus_filter(self):
        self.query_one("#filter", Input).focus()

    def action_unfocus_filter(self):
        self.query_one("#orbits", Tree).focus()

    def action_extract(self):
        node = self.query_one("#orbits", Tree).cursor_node
        d = getattr(node, "data", None) if node else None
        if not d: return
        os.makedirs(OBS_DIR, exist_ok=True)
        if d[0] == "orbit":
            units, subs = d[1], d[2]
            path = os.path.join(OBS_DIR, f"orbit_{re.sub(r'[^\w.+-]', '_', orbit_pref(units))[:40]}__x{len(units)}.md")
            open(path, "w").write(observation_orbit(units, subs, self.defidx, self.copy_units))
        else:
            r = d[1]
            path = os.path.join(OBS_DIR, f"{re.sub(r'[^\w.+-]', '_', r['head'])[:48]}__x{r['fanin']}.md")
            open(path, "w").write(observation_md(r))
        self.notify(f"observation → {os.path.relpath(path, REPO)}", timeout=6)

def run_tui(cache_path):
    data = json.load(open(cache_path))
    SPPF(data["rows"], data).run()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--min-size", type=int, default=3)
    ap.add_argument("--min-fanin", type=int, default=2)
    ap.add_argument("--cap", type=int, default=8000)
    ap.add_argument("--observe", metavar="Q", help="print observations for subtrees whose head/instances match Q")
    ap.add_argument("--between", nargs=2, metavar=("A", "B"),
                    help="observations for subtrees with an instance matching A AND one matching B")
    ap.add_argument("--top", type=int, default=8, help="max observations to print (--observe/--between)")
    args = ap.parse_args()
    if args.build:
        build(args.cache, args.min_size, args.min_fanin, args.cap); return
    if not os.path.exists(args.cache):
        print(f"no cache at {args.cache} — run:  scripts/reuse_tui.py --build"); return
    if not json.load(open(args.cache)).get("copy_units"):          # announce degraded provenance up front
        print("⚠ cache has NO defCopy provenance — orbit verdicts use the DEF-SITE HEURISTIC (weaker). "
              "Rebuild cores + shim and re-run --build for the exact signal.", file=sys.stderr, flush=True)

    if args.observe or args.between:
        rows = json.load(open(args.cache))["rows"]
        if args.between:
            a, b = args.between[0].lower(), args.between[1].lower()
            def rank(r):
                insts = [n.lower() for n in r["instances"]]
                if not (any(a in n for n in insts) and any(b in n for n in insts)):
                    return None
                # CONCENTRATION: fraction of instances actually in A∪B (specific dup vs tree-wide generic)
                inab = sum(1 for n in insts if a in n or b in n)
                return (inab / r["fanin"], r["size"])          # concentrated + big first
            scored = [(rank(r), r) for r in rows]
            matches = [r for k, r in sorted((kr for kr in scored if kr[0]), key=lambda kr: kr[0], reverse=True)]
        else:
            q = args.observe.lower()
            matches = sorted([r for r in rows if q in r["head"].lower() or any(q in n.lower() for n in r["instances"])],
                             key=lambda r: -(r["fanin"] * r["size"]))
        if not matches:
            print("no matching shared subtree."); return
        print(f"# {len(matches)} matching shared subtree(s); showing top {min(args.top, len(matches))}\n")
        for r in matches[:args.top]:
            print(observation_md(r)); print("\n" + "-" * 78 + "\n")
        return

    run_tui(args.cache)

if __name__ == "__main__":
    main()
