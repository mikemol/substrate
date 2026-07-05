#!/usr/bin/env python3
# reuse_catalog.py — the SHARED extraction core behind the two discoverability catalogs.
#
# Both catalogs are derived from the SAME first phase: walk the typechecked `.agdai` tree and
# run the raw `agdai_shim` decoder once per file, parsing each core into (nodes, defmarks). They
# diverge only in the REDUCER:
#   * gen_reuse_index  — name -> canonical-home index + cross-name shape-parallels (from the
#                        def-markers' kind + member names).
#   * gen_reuse_graph  — structure -> structure refinement EDGES (from the qname references the
#                        core-nodes carry) + the reuse-primitive in/out-degree census.
#
# Previously each script shimmed the whole tree independently (~1751 files × 2 = the tree decoded
# TWICE). `core_intern_agdai` — which gen_reuse_index used — ALSO shells out to the same
# `agdai_shim` under the hood (it interns the shim's JSON), so the raw def-markers already carry
# the kind + members the index needs (verified byte-identical to the interned members). This module
# runs the shim ONCE per file (walk_cores, a streaming generator) and dispatches each core to both
# accumulators, so `gen_catalog.py` produces BOTH files from a single decode pass — halving the
# combined cost. The two standalone `gen_reuse_{index,graph}.py` remain as thin single-catalog
# entry points into this one source of truth.
import os, re, json, subprocess, collections, hashlib

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_AG  = os.path.join(ROOT, "agda", "_build", "2.8.0", "agda")
SUB_AGDAI = os.path.join(BUILD_AG, "Substrate")
SHIM      = os.path.join(ROOT, "jea", "metalanguage", "agdai_shim")
IDX_DOC   = os.path.join(ROOT, "catalog", "reuse-index.md")
GRAPH_DOT = os.path.join(ROOT, "catalog", "reuse-graph.dot")
GRAPH_MD  = os.path.join(ROOT, "catalog", "reuse-graph.md")

shapetag = re.compile(r"⟦shape:[^⟧]*⟧")
decl_c   = re.compile(r"^\s*(?:data|record)\s+([^\s({:]+).*?--(.*)$")
idxkind  = re.compile(r"Registry|Generators|Index|Catalogue|Catalog|Bridge")


# ─────────────────────────── the ONE shim-walk (shared phase) ───────────────────────────
def agdai_module(p):
    rel = os.path.relpath(p, BUILD_AG)                 # Substrate/X/Y.agdai
    return rel[:-len(".agdai")].replace(os.sep, ".")

def agda_source(mod):
    return os.path.join(ROOT, "agda", mod.replace(".", os.sep) + ".agda")

def _shim_raw(agdai):
    r = subprocess.run([SHIM, os.path.abspath(agdai)], capture_output=True, text=True,
                       cwd=os.path.dirname(agdai))
    return r.stdout if r.returncode == 0 else None

def walk_cores(filt=""):
    """Streaming generator: decode each `.agdai` under Substrate/ with the raw shim ONCE and
    yield its parsed core (or None on a shim failure, so callers can count it). A core is
    {mod, path, nodes, defmarks} where nodes = {id: (qname, [child-ids])} (qname references
    INTACT — the interned form drops them) and defmarks = [(unit, root, kind, members)]."""
    for dp, _, fns in os.walk(SUB_AGDAI):
        for fn in sorted(fns):
            if not fn.endswith(".agdai") or (filt and filt not in os.path.join(dp, fn)):
                continue
            path = os.path.join(dp, fn)
            out  = _shim_raw(path)
            if out is None:
                yield None
                continue
            nodes, defmarks = {}, []
            for line in out.splitlines():
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if "unit" in rec:
                    defmarks.append((rec["unit"], rec["root"], rec.get("kind"),
                                     rec.get("members", [])))
                elif "id" in rec:
                    nodes[rec["id"]] = (rec.get("qname"), rec.get("children", []))
            yield {"mod": agdai_module(path), "path": path, "nodes": nodes, "defmarks": defmarks}


def mod_purpose(text):
    for ln in text.splitlines()[:45]:
        s = ln.strip()
        if s.startswith("--") and "—" in s:            # "-- Substrate.X.Y — purpose"
            return s.lstrip("-").strip().split("—", 1)[1].strip()
    for ln in text.splitlines()[:45]:
        s = ln.strip().lstrip("-").strip()
        if len(s) > 12 and re.search(r"[a-z]", s) and not s.startswith("Substrate.") \
           and not set(s) <= set("- "):
            return s
    return ""


# ─────────────────────────── reducer 1: reuse-INDEX (name -> home) ───────────────────────────
class IndexBuilder:
    def __init__(self):
        self.structs, self.idxmods = [], []
        self.namehomes, self.fingerprints = {}, {}

    def add(self, core):
        mod  = core["mod"]
        # structures from the raw def-markers (kind + members — byte-identical to the interned rep)
        cs   = [(unit, kind) for unit, _root, kind, _m in core["defmarks"]
                if kind in ("Datatype", "Record")]
        if not cs:
            return
        mems = {unit: m for unit, _root, kind, m in core["defmarks"]
                if kind in ("Datatype", "Record")}
        # descriptions + purpose from the .agda source (best-effort)
        src = agda_source(mod)
        purpose, comments = "", {}
        if os.path.exists(src):
            text = open(src, encoding="utf-8").read()
            purpose = mod_purpose(text)
            for ln in text.splitlines():
                m = decl_c.match(ln)
                if m:
                    comments[m.group(1)] = shapetag.sub("", m.group(2)).strip()
        if idxkind.search(mod.rsplit(".", 1)[-1]):
            self.idxmods.append((mod, purpose))
        for q, k in cs:
            name = q.rsplit(".", 1)[-1]
            desc = comments.get(name, "") or purpose
            kd   = "data" if k == "Datatype" else "record"
            self.structs.append((name, kd, mod, desc))
            self.namehomes.setdefault(name, set()).add(mod)
            heads = sorted(m.rsplit(".", 1)[-1] for m in mems.get(q, []))
            fp = kd + "|" + ",".join(heads)
            self.fingerprints.setdefault(fp, []).append((name, mod))

    def write(self, failed=0):
        structs = sorted(self.structs, key=lambda x: (x[0].lower(), x[2]))
        nmods = len(set(s[2] for s in structs))
        amb   = {n: h for n, h in self.namehomes.items() if len(h) > 1}
        parallels = {fp: es for fp, es in self.fingerprints.items()
                     if len({n for n, _ in es}) >= 2}
        out = ["# Reuse index — the substrate's structures, by name\n",
               "_Auto-generated by `scripts/gen_reuse_index.py` from the typechecked `.agdai` cores "
               "(jea_agdai) — do not edit; regenerate._\n",
               "**Consult BEFORE building a new `data`/`record`.** Grep this file for the concept you're "
               "about to reinvent — `V4`, `Real`, `Wedge`, `Monoid`, `Stream`, `Trace`, `DivStr`, `Setoid`, "
               "`Newman`, … — to find its canonical home, then instantiate / relate-by-iso the existing "
               "structure instead of re-deriving it (the CLAUDE.md reuse-search discipline; structural "
               "search is `python jea/metalanguage/jea_pysim.py … --clusters`). A name with several homes → "
               "see *Multiply-homed* and pick by shape.\n",
               f"_{len(structs)} structures across {nmods} modules; {len(amb)} names multiply-homed; "
               f"{len(parallels)} cross-name shape-parallels"
               + (f"; {failed} cores unreadable" if failed else "") + "._\n",
               "## Start here — index / registry / bridge modules\n"]
        for mod, purpose in sorted(set(self.idxmods)):
            out.append(f"- `{mod}`" + (f" — {purpose}" if purpose else ""))
        out += ["", f"## Parallel structures ({len(parallels)}) — same shape, DIFFERENT names → relate by iso/bridge\n",
                "One elaborated-members fingerprint (kind + ctor/field names) reached by ≥2 distinct names: a "
                "candidate reinvention (a KleinV4≅V₄-style witnessed bridge, not a silent collapse — "
                "[[feedback_dedup_preserve_crossdomain_bridges]]). Name-based screening; confirm the type-level "
                "match / cross-domain-vs-within with `jea_pysim … --clusters` before acting.\n"]
        for fp in sorted(parallels, key=lambda f: (-len({n for n, _ in parallels[f]}), f)):
            es = sorted(set(parallels[fp]))
            kind, heads = fp.split("|", 1)
            out.append(f"- `{kind} {{{heads}}}` — " + ", ".join(f"`{n}`@`{m}`" for n, m in es))
        out += ["", f"## Multiply-homed names ({len(amb)}) — one name, several structures; pick by shape\n"]
        for n in sorted(amb, key=str.lower):
            out.append(f"- `{n}` — " + ", ".join(f"`{m}`" for m in sorted(amb[n])))
        out += ["", "## Structures (data / record), alphabetical by name\n",
                "| name | kind | home | what |", "|---|---|---|---|"]
        for name, kind, mod, desc in structs:
            d = re.sub(r"\s+", " ", desc).replace("|", r"\|")[:100]
            out.append(f"| `{name}` | {kind} | `{mod}` | {d} |")
        os.makedirs(os.path.dirname(IDX_DOC), exist_ok=True)
        open(IDX_DOC, "w", encoding="utf-8").write("\n".join(out) + "\n")
        return (f"reuse-index: {len(structs)} structures, {nmods} modules, {len(amb)} multiply-homed, "
                f"{len(set(self.idxmods))} index modules, {failed} unreadable -> catalog/reuse-index.md")


# ─────────────────────────── reducer 2: reuse-GRAPH (refinement edges) ───────────────────────────
class GraphBuilder:
    def __init__(self):
        self.struct_kind, self.refs = {}, {}

    def add(self, core):
        nodes = core["nodes"]
        for unit, root, kind, _m in core["defmarks"]:
            if kind not in ("Datatype", "Record"):
                continue
            self.struct_kind[unit] = "data" if kind == "Datatype" else "record"
            seen, refd, stack = set(), set(), [root]
            while stack:
                i = stack.pop()
                if i in seen or i not in nodes:
                    continue
                seen.add(i)
                qn, ch = nodes[i]
                if qn:
                    refd.add(qn)
                stack.extend(ch)
            self.refs[unit] = refd

    def write(self, failed=0):
        structs = set(self.struct_kind)

        def owner_struct(qn):                  # longest prefix of qn that is itself a structure
            parts = qn.split(".")
            for j in range(len(parts), 0, -1):
                p = ".".join(parts[:j])
                if p in structs:
                    return p
            return None

        edges = set()
        for x, rs in self.refs.items():
            for r in rs:
                y = owner_struct(r)
                if y and y != x:
                    edges.add((x, y))
        indeg  = collections.Counter(y for _, y in edges)
        outdeg = collections.Counter(x for x, _ in edges)
        short  = lambda q: q.rsplit(".", 1)[-1]
        home   = lambda q: q.rsplit(".", 1)[0]
        # DETERMINISTIC ranking: Counter.most_common() breaks count-ties by insertion order,
        # which (edges is a set) is hash-seed-randomized — byte-unstable across processes, so a
        # gate that stages this file would churn it every commit. Sort ties by qname instead.
        rank   = lambda ctr, n: sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

        # --- DOT: every edge (tooling) ---
        dl = ['digraph reuse {', '  rankdir=LR; node [shape=box, fontsize=9];',
              '  // structure X -> Y : X is built on / refines Y. Auto-generated: scripts/gen_reuse_graph.py']
        for q, k in sorted(self.struct_kind.items()):
            dl.append(f'  "{q}" [label="{short(q)}\\n{home(q)}"{"" if k=="record" else ", style=rounded"}];')
        for x, y in sorted(edges):
            dl.append(f'  "{x}" -> "{y}";')
        dl.append("}")
        os.makedirs(os.path.dirname(GRAPH_DOT), exist_ok=True)
        open(GRAPH_DOT, "w", encoding="utf-8").write("\n".join(dl) + "\n")

        # --- MD: Mermaid slice of the top reuse-primitives + refiners, + degree ranking ---
        TOPN = 12
        prims = [q for q, _ in rank(indeg, TOPN)]
        prims_set = set(prims)
        ml = ["# Reuse graph — structure refinement (who is built on whom)\n",
              "_Auto-generated by `scripts/gen_reuse_graph.py` from the RAW `.agdai` cores (qname references "
              "intact; the interned form is shape-normalized and loses them) — do not edit; regenerate._\n",
              f"_{len(self.struct_kind)} structures, {len(edges)} refinement edges"
              + (f"; {failed} cores unreadable" if failed else "") + "._\n",
              "**Reading:** `X --> Y` means X's elaborated core is built on Y (Y is a field/parameter/component "
              "of X). Before reinventing a structure, check whether the thing you want already **refines** an "
              "existing primitive here. Full graph: `catalog/reuse-graph.dot` (GraphViz). Mermaid slice below = "
              "the top reuse-primitives (highest in-degree — the most-built-on) and their direct refiners.\n",
              "## Most-reused primitives (in-degree) — the centers everything is built on\n",
              "| structure | ← refined by | home |", "|---|---:|---|"]
        for q, d in rank(indeg, 25):
            ml.append(f"| `{short(q)}` | {d} | `{home(q)}` |")
        ml += ["", "## Most-composite structures (out-degree) — built on the most others\n",
               "| structure | → builds on | home |", "|---|---:|---|"]
        for q, d in rank(outdeg, 15):
            ml.append(f"| `{short(q)}` | {d} | `{home(q)}` |")
        ml += ["", f"## Mermaid — top {TOPN} primitives + their refiners\n", "```mermaid", "graph LR"]

        def nid(q):                            # mermaid-safe, DETERMINISTIC node id (hash() is
            return "n" + hashlib.md5(q.encode()).hexdigest()[:10]   # seed-randomized; md5 is stable
        emitted = set()
        for x, y in sorted(edges):
            if y in prims_set:                 # edges INTO a top primitive (its refiners)
                for q in (x, y):
                    if q not in emitted:
                        ml.append(f'  {nid(q)}["{short(q)}"]')
                        emitted.add(q)
                ml.append(f"  {nid(x)} --> {nid(y)}")
        ml += ["```", ""]
        open(GRAPH_MD, "w", encoding="utf-8").write("\n".join(ml) + "\n")
        return (f"reuse-graph: {len(self.struct_kind)} structures, {len(edges)} edges, {failed} unreadable "
                f"-> catalog/reuse-graph.dot + .md")


# ─────────────────────────── driver: ONE walk, chosen reducers ───────────────────────────
def generate(filt="", do_index=True, do_graph=True):
    """Run the shared shim-walk ONCE and drive the selected reducers off the single decode pass.
    Returns the list of per-catalog summary strings."""
    ib = IndexBuilder() if do_index else None
    gb = GraphBuilder() if do_graph else None
    failed = 0
    for core in walk_cores(filt):
        if core is None:
            failed += 1
            continue
        if ib:
            ib.add(core)
        if gb:
            gb.add(core)
    msgs = []
    if ib:
        msgs.append(ib.write(failed))
    if gb:
        msgs.append(gb.write(failed))
    return msgs
