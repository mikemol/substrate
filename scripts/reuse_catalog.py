#!/usr/bin/env python3
# reuse_catalog.py — the SHARED extraction + render core behind every discoverability catalog.
#
# ONE expensive phase, MANY cheap renders. The expensive phase is the walk: decode each typechecked
# `.agdai` under Substrate/ with the raw `agdai_shim` once (walk_cores) and load the facts into a
# relational store, catalog/catalog.db (DbBuilder). EVERY catalog artifact is then a fast RENDER
# over that DB — no re-walking:
#   * render_index   -> catalog/reuse-index.md      (name -> home + cross-name shape-parallels)
#   * render_graph   -> catalog/reuse-graph.{dot,md}(STRUCT refinement edges + degree census)
#   * render_sitemap -> catalog/reuse-sitemap.xml   (flat discovery manifest; priority = in-degree)
#   * render_usage   -> catalog/usage-stats.md      (reuse distribution: primitives vs isolated)
#   * render_import  -> catalog/import-graph.{dot,md}(MODULE semantic-dependency edges + degree census)
#
# History: gen_reuse_index and gen_reuse_graph each used to shim the whole tree independently (the
# tree decoded TWICE — core_intern_agdai, which the index used, ALSO shells out to agdai_shim under
# the hood). Ⓓ.gate-graph factored the common WALK into walk_cores + in-memory reducers; Ⓓ.catalog-db
# added the relational store; Ⓓ.render-from-db (this) makes the DB the SOLE canonical store and turns
# the index/graph reducers into DB renders, so a new artifact (sitemap, usage-stats, …) is one more
# render function — never a new walk. The markdown/xml files are the committed, diffable,
# LLM-consumable renders; catalog.db is a derived, non-deterministic binary cache (gitignored,
# rebuilt by the gate / on demand). Byte-identity of the renders is HELD across the refactor and
# checked by the two-run + vs-committed harness; the renders sort in PYTHON (not SQL ORDER BY),
# because SQLite's lower()/collation differs from Python's on the Unicode struct names (ℕ, ℚ, α, …).
import os, re, json, subprocess, collections, hashlib, sqlite3

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ⟡walk-cores-empty-is-not-success: the build dir is VERSION-STAMPED by agda
# (_build/<ver>/agda). Hardcoding one version makes walk_cores yield NOTHING on any
# other toolchain — 0 cores AND 0 failures, i.e. SILENT SUCCESS. Discover the version
# instead, and make an empty walk a hard error (below).
def _discover_build_ag(root):
    base = os.path.join(root, "agda", "_build")
    if os.path.isdir(base):
        vers = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d, "agda")))
        if vers:
            return os.path.join(base, vers[-1], "agda")
    return os.path.join(base, "2.8.0", "agda")   # legacy default

BUILD_AG  = _discover_build_ag(ROOT)
SUB_AGDAI = os.path.join(BUILD_AG, "Substrate")
SHIM      = os.path.join(ROOT, "jea", "metalanguage", "agdai_shim")
IDX_DOC    = os.path.join(ROOT, "catalog", "reuse-index.md")
GRAPH_DOT  = os.path.join(ROOT, "catalog", "reuse-graph.dot")
GRAPH_MD   = os.path.join(ROOT, "catalog", "reuse-graph.md")
SITEMAP    = os.path.join(ROOT, "catalog", "reuse-sitemap.xml")
USAGE_MD   = os.path.join(ROOT, "catalog", "usage-stats.md")
IMPORT_DOT = os.path.join(ROOT, "catalog", "import-graph.dot")
IMPORT_MD  = os.path.join(ROOT, "catalog", "import-graph.md")
CATALOG_DB = os.path.join(ROOT, "catalog", "catalog.db")

# The relational store (Ⓓ.catalog-db): the canonical facts every markdown/xml catalog renders. The
# `fp` (shape fingerprint) and `desc` are computed in Python at build time — fp so the member-name
# sort matches the reuse-index fingerprint exactly without a recent SQLite's ordered GROUP_CONCAT;
# desc because it comes from the .agda source comment, not the core.
_DB_SCHEMA = """
-- qname is NOT unique: an anonymous `module _` collapses several declarations to one qname
-- (e.g. two `data _⇒*_` in two `module _` blocks → one qname, two nodes). That collision is the
-- dedup FAN-IN signal (name-granularity), not a bug to drop — so the key is composite (qname, root)
-- and every colliding node is kept, rather than one clobbering the rest. (Ⓓ.catalog-fanin-key)
CREATE TABLE structs (qname TEXT, name TEXT, kind TEXT, module TEXT, fp TEXT, desc TEXT, root INTEGER, PRIMARY KEY (qname, root));
CREATE TABLE members (struct_qname TEXT, name TEXT, ord INTEGER);
CREATE TABLE refs    (struct_qname TEXT, ref_qname TEXT);
CREATE TABLE edges   (src TEXT, dst TEXT);
CREATE TABLE module_edges (src TEXT, dst TEXT);   -- module -> module semantic dependency (import-graph)
CREATE TABLE modules (module TEXT PRIMARY KEY, purpose TEXT, is_index INTEGER);
CREATE TABLE meta    (key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX ix_structs_name ON structs(name);
CREATE INDEX ix_members_sq   ON members(struct_qname);
CREATE INDEX ix_edges_src    ON edges(src);
CREATE INDEX ix_edges_dst    ON edges(dst);
CREATE INDEX ix_medges_src   ON module_edges(src);
CREATE INDEX ix_medges_dst   ON module_edges(dst);
-- The catalogs' key queries, as views (the "new question = a SELECT" payoff):
CREATE VIEW in_degree  AS SELECT dst AS qname, COUNT(*) AS deg FROM edges GROUP BY dst;
CREATE VIEW out_degree AS SELECT src AS qname, COUNT(*) AS deg FROM edges GROUP BY src;
CREATE VIEW module_in_degree  AS SELECT dst AS module, COUNT(*) AS deg FROM module_edges GROUP BY dst;
CREATE VIEW module_out_degree AS SELECT src AS module, COUNT(*) AS deg FROM module_edges GROUP BY src;
CREATE VIEW multiply_homed AS
  SELECT name, COUNT(DISTINCT module) AS homes, GROUP_CONCAT(DISTINCT module) AS modules
  FROM structs GROUP BY name HAVING homes > 1;
CREATE VIEW shape_parallel AS
  SELECT fp, COUNT(DISTINCT name) AS names, GROUP_CONCAT(qname) AS structs
  FROM structs GROUP BY fp HAVING names >= 2;
"""

shapetag = re.compile(r"⟦shape:[^⟧]*⟧")
decl_c   = re.compile(r"^\s*(?:data|record)\s+([^\s({:]+).*?--(.*)$")
idxkind  = re.compile(r"Registry|Generators|Index|Catalogue|Catalog|Bridge")

_short = lambda q: q.rsplit(".", 1)[-1]
_home  = lambda q: q.rsplit(".", 1)[0]


# ─────────────────────────── the ONE shim-walk (the expensive phase) ───────────────────────────
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
    if not os.path.isdir(SUB_AGDAI):
        raise RuntimeError(
            f"walk_cores: no core tree at {SUB_AGDAI} — nothing to walk. "
            "An empty walk is NOT success. Build the tree first (agda/Makefile).")
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


# ─────────────────────────── the store builder (walk -> catalog.db) ───────────────────────────
class DbBuilder:
    """The ONLY accumulator: loads the walk into catalog.db. Every catalog is then a render over it."""
    def __init__(self):
        self.structs, self.members, self.refrows, self.modrows = [], [], [], []
        self.kinds, self.refs = {}, {}
        self.allmods, self.modrefs = set(), {}         # for the module import graph (all modules)

    def add(self, core):
        mod, nodes = core["mod"], core["nodes"]
        # Module import graph (Ⓓ.import-graph): EVERY module (struct-bearing or not — a law/function
        # module still imports), and every qname its elaborated core references (all node qnames, not
        # just struct-subtree refs). Collected BEFORE the struct early-return below so struct-less
        # modules are still graph nodes. Resolved to module->module edges in write() (needs all modules).
        self.allmods.add(mod)
        self.modrefs[mod] = {qn for qn, _ch in nodes.values() if qn}
        cs = [(u, r, k, m) for u, r, k, m in core["defmarks"] if k in ("Datatype", "Record")]
        if not cs:                                     # a module with no data/record contributes no STRUCTS
            return
        # descriptions + purpose + is-index from the .agda source (best-effort; not in the core)
        src = agda_source(mod)
        purpose, comments = "", {}
        if os.path.exists(src):
            text = open(src, encoding="utf-8").read()
            purpose = mod_purpose(text)
            for ln in text.splitlines():
                m = decl_c.match(ln)
                if m:
                    comments[m.group(1)] = shapetag.sub("", m.group(2)).strip()
        self.modrows.append((mod, purpose, 1 if idxkind.search(mod.rsplit(".", 1)[-1]) else 0))
        for unit, root, kind, members in cs:
            name = unit.rsplit(".", 1)[-1]
            kd   = "data" if kind == "Datatype" else "record"
            heads = [m.rsplit(".", 1)[-1] for m in members]
            fp   = kd + "|" + ",".join(sorted(heads))    # == the reuse-index fingerprint
            desc = comments.get(name, "") or purpose
            self.structs.append((unit, name, kd, mod, fp, desc, root))
            for i, h in enumerate(heads):
                self.members.append((unit, h, i))
            self.kinds[unit] = kd
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
            for r in sorted(refd):
                self.refrows.append((unit, r))

    def write(self, failed=0):
        structs = set(self.kinds)

        def owner(qn):                         # longest structure-prefix (the refinement-edge rule)
            parts = qn.split(".")
            for j in range(len(parts), 0, -1):
                p = ".".join(parts[:j])
                if p in structs:
                    return p
            return None

        edges = sorted({(x, y) for x, rs in self.refs.items()
                        for y in (owner(r) for r in rs) if y and y != x})

        # module import edges: M -> N iff M references a qname whose DEFINING module (longest
        # module-prefix in the full module set) is N ≠ M. Cache prefix→module resolution (many
        # qnames share a module prefix).
        allmods = self.allmods
        _mcache = {}

        def owner_mod(qn):
            if qn in _mcache:
                return _mcache[qn]
            parts, res = qn.split("."), None
            for j in range(len(parts) - 1, 0, -1):     # a def-qname is module + ≥1 local component
                p = ".".join(parts[:j])
                if p in allmods:
                    res = p
                    break
            _mcache[qn] = res
            return res

        module_edges = sorted({(m, n) for m, rs in self.modrefs.items()
                               for n in (owner_mod(r) for r in rs) if n and n != m})

        if os.path.exists(CATALOG_DB):
            os.remove(CATALOG_DB)
        os.makedirs(os.path.dirname(CATALOG_DB), exist_ok=True)
        con = sqlite3.connect(CATALOG_DB)
        con.executescript(_DB_SCHEMA)
        con.executemany("INSERT INTO structs VALUES (?,?,?,?,?,?,?)", sorted(self.structs))
        con.executemany("INSERT INTO members VALUES (?,?,?)",       self.members)
        con.executemany("INSERT INTO refs    VALUES (?,?)",         self.refrows)
        con.executemany("INSERT INTO edges   VALUES (?,?)",         edges)
        con.executemany("INSERT INTO module_edges VALUES (?,?)",    module_edges)
        con.executemany("INSERT INTO modules VALUES (?,?,?)",       sorted(self.modrows))
        con.execute("INSERT INTO meta VALUES ('failed', ?)", (str(failed),))
        con.commit()
        con.close()
        return (f"catalog-db: {len(self.structs)} structs, {len(edges)} refinement edges, "
                f"{len(self.allmods)} modules, {len(module_edges)} import edges -> catalog/catalog.db")


def _failed(con):
    row = con.execute("SELECT value FROM meta WHERE key='failed'").fetchone()
    return int(row[0]) if row else 0


# ─────────────────────────── render 1: reuse-INDEX (name -> home) ───────────────────────────
def render_index(con):
    failed  = _failed(con)
    structs = sorted(((r[0], r[1], r[2], r[3] or "")
                      for r in con.execute("SELECT name, kind, module, desc FROM structs")),
                     key=lambda x: (x[0].lower(), x[2]))
    namehomes = {}
    for name, module in con.execute("SELECT name, module FROM structs"):
        namehomes.setdefault(name, set()).add(module)
    fingerprints = {}
    for fp, name, module in con.execute("SELECT fp, name, module FROM structs"):
        fingerprints.setdefault(fp, []).append((name, module))
    idxmods = [(m, p or "") for m, p in
               con.execute("SELECT module, purpose FROM modules WHERE is_index = 1")]

    nmods = len(set(s[2] for s in structs))
    amb   = {n: h for n, h in namehomes.items() if len(h) > 1}
    parallels = {fp: es for fp, es in fingerprints.items()
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
    for mod, purpose in sorted(set(idxmods)):
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
            f"{len(set(idxmods))} index modules, {failed} unreadable -> catalog/reuse-index.md")


# ─────────────────────────── render 2: reuse-GRAPH (refinement edges) ───────────────────────────
def render_graph(con):
    failed = _failed(con)
    struct_kind = dict(con.execute("SELECT qname, kind FROM structs").fetchall())
    edges = {(x, y) for x, y in con.execute("SELECT src, dst FROM edges")}
    indeg  = collections.Counter(y for _, y in edges)
    outdeg = collections.Counter(x for x, _ in edges)
    # DETERMINISTIC ranking: Counter.most_common() breaks count-ties by insertion order (hash-seed
    # randomized, since edges is a set) — byte-unstable, would churn the file. Sort ties by qname.
    rank = lambda ctr, n: sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

    # --- DOT: every edge (tooling) ---
    dl = ['digraph reuse {', '  rankdir=LR; node [shape=box, fontsize=9];',
          '  // structure X -> Y : X is built on / refines Y. Auto-generated: scripts/gen_reuse_graph.py']
    for q, k in sorted(struct_kind.items()):
        dl.append(f'  "{q}" [label="{_short(q)}\\n{_home(q)}"{"" if k=="record" else ", style=rounded"}];')
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
          f"_{len(struct_kind)} structures, {len(edges)} refinement edges"
          + (f"; {failed} cores unreadable" if failed else "") + "._\n",
          "**Reading:** `X --> Y` means X's elaborated core is built on Y (Y is a field/parameter/component "
          "of X). Before reinventing a structure, check whether the thing you want already **refines** an "
          "existing primitive here. Full graph: `catalog/reuse-graph.dot` (GraphViz). Mermaid slice below = "
          "the top reuse-primitives (highest in-degree — the most-built-on) and their direct refiners.\n",
          "## Most-reused primitives (in-degree) — the centers everything is built on\n",
          "| structure | ← refined by | home |", "|---|---:|---|"]
    for q, d in rank(indeg, 25):
        ml.append(f"| `{_short(q)}` | {d} | `{_home(q)}` |")
    ml += ["", "## Most-composite structures (out-degree) — built on the most others\n",
           "| structure | → builds on | home |", "|---|---:|---|"]
    for q, d in rank(outdeg, 15):
        ml.append(f"| `{_short(q)}` | {d} | `{_home(q)}` |")
    ml += ["", f"## Mermaid — top {TOPN} primitives + their refiners\n", "```mermaid", "graph LR"]

    def nid(q):                                # mermaid-safe, DETERMINISTIC node id (hash() is
        return "n" + hashlib.md5(q.encode()).hexdigest()[:10]   # seed-randomized; md5 is stable
    emitted = set()
    for x, y in sorted(edges):
        if y in prims_set:                     # edges INTO a top primitive (its refiners)
            for q in (x, y):
                if q not in emitted:
                    ml.append(f'  {nid(q)}["{_short(q)}"]')
                    emitted.add(q)
            ml.append(f"  {nid(x)} --> {nid(y)}")
    ml += ["```", ""]
    open(GRAPH_MD, "w", encoding="utf-8").write("\n".join(ml) + "\n")
    return (f"reuse-graph: {len(struct_kind)} structures, {len(edges)} edges, {failed} unreadable "
            f"-> catalog/reuse-graph.dot + .md")


# ─────────────────────────── render 3: reuse-SITEMAP (flat discovery manifest) ───────────────────────────
def _xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_sitemap(con):
    """A sitemap-XML manifest of every structure — the format the LLM-consumer is TRAINED ON (the
    user's discovery-manifest point). Flat (no edges → the index layer, not the graph). loc is a
    SYNTHETIC url (the substrate is not web-served): https://substrate.local/<module-path>#<name>;
    non-ASCII names are left raw (readability over percent-encoding — the consumer is a model, not a
    validator). priority = in-degree normalized to [0,1] (the reuse-graph census as a crawl-priority
    signal). lastmod is OMITTED deliberately: the only 'modified' signal is the .agdai mtime, which
    is non-deterministic and would churn this committed file."""
    rows = con.execute("""SELECT s.qname, s.module, s.name, COALESCE(d.deg, 0) AS indeg
                          FROM structs s LEFT JOIN in_degree d ON d.qname = s.qname""").fetchall()
    maxdeg = max((r[3] for r in rows), default=0) or 1
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           "<!-- Auto-generated by scripts/gen_catalog.py from catalog.db (the typechecked .agdai",
           "     cores). Do not edit; regenerate. loc host is synthetic (substrate is not served);",
           "     priority = structure in-degree / max in-degree (reuse-graph census). -->",
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for qname, module, name, indeg in sorted(rows, key=lambda r: r[0]):
        loc = _xml_escape(f"https://substrate.local/{module.replace('.', '/')}#{name}")
        out.append(f"  <url><loc>{loc}</loc><priority>{round(indeg / maxdeg, 2)}</priority></url>")
    out.append("</urlset>")
    os.makedirs(os.path.dirname(SITEMAP), exist_ok=True)
    open(SITEMAP, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return f"reuse-sitemap: {len(rows)} url entries -> catalog/reuse-sitemap.xml"


# ─────────────────────────── render 4: USAGE-STATS (reuse distribution) ───────────────────────────
def render_usage(con):
    """The reuse distribution over the refinement graph: which structures are real PRIMITIVES
    (high in-degree) vs structurally ISOLATED (neither refine nor are refined — used, if at all,
    only via functions, not as struct components). Complements reuse-graph's top-of-ranking with
    its TAIL: the dead-center candidates a builder should look at before adding another."""
    total = con.execute("SELECT COUNT(*) FROM structs").fetchone()[0]
    refined_in  = {r[0] for r in con.execute("SELECT DISTINCT dst FROM edges")}
    refines_out = {r[0] for r in con.execute("SELECT DISTINCT src FROM edges")}
    allq = [r[0] for r in con.execute("SELECT qname FROM structs")]
    never_refined = [q for q in allq if q not in refined_in]           # in-degree 0
    refines_none  = [q for q in allq if q not in refines_out]          # out-degree 0
    isolated = sorted(q for q in allq if q not in refined_in and q not in refines_out)
    top = con.execute("SELECT qname, deg FROM in_degree ORDER BY deg DESC, qname LIMIT 20").fetchall()

    out = ["# Usage stats — reuse distribution over the refinement graph\n",
           "_Auto-generated by `scripts/gen_catalog.py` from catalog.db — do not edit; regenerate._\n",
           f"_{total} structures · {len(never_refined)} never-refined (in-degree 0) · "
           f"{len(refines_none)} refine-nothing (out-degree 0) · {len(isolated)} structurally "
           f"isolated (both)._\n",
           "**Reading.** In-degree 0 = nothing is built ON this structure (a result/endpoint, or a "
           "dead abstraction). Out-degree 0 = it is built on no other STRUCTURE (a primitive or a "
           "leaf). *Isolated* = both: it neither refines nor is refined — structurally disconnected "
           "in the refinement graph, so it is used (if at all) only via functions, not as a struct "
           "component. Before adding another near-isolated structure, check whether one of these is "
           "the center you want. (This is the reuse-graph census read from the TAIL.)\n",
           "## Real primitives — most-reused (in-degree), the opposite end\n",
           "| structure | ← refined by | home |", "|---|---:|---|"]
    for q, d in top:
        out.append(f"| `{_short(q)}` | {d} | `{_home(q)}` |")
    out += ["", f"## Structurally isolated ({len(isolated)}) — neither refine nor are refined\n",
            "| structure | kind | home |", "|---|---|---|"]
    kinds = dict(con.execute("SELECT qname, kind FROM structs").fetchall())
    for q in isolated:
        out.append(f"| `{_short(q)}` | {kinds.get(q, '')} | `{_home(q)}` |")
    os.makedirs(os.path.dirname(USAGE_MD), exist_ok=True)
    open(USAGE_MD, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return (f"usage-stats: {total} structs, {len(isolated)} isolated, {len(never_refined)} never-refined "
            f"-> catalog/usage-stats.md")


# ─────────────────────────── render 5: IMPORT-GRAPH (module semantic dependency) ───────────────────────────
def render_import(con):
    """The module dependency graph, SEMANTIC (over the elaborated .agdai cores, NOT source `import`
    lines): module X -> Y iff X's core references a name DEFINED in Y. This captures what is
    actually USED post-elaboration — it excludes unused source imports and includes transitively-
    used names. The module-level twin of reuse-graph (which is struct-level)."""
    failed = _failed(con)
    edges = {(x, y) for x, y in con.execute("SELECT src, dst FROM module_edges")}
    mods = sorted({m for e in edges for m in e})
    indeg  = collections.Counter(y for _, y in edges)
    outdeg = collections.Counter(x for x, _ in edges)
    rank = lambda ctr, n: sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[:n]
    tail = lambda m: ".".join(m.split(".")[-2:])       # last 2 components — a readable node label

    # --- DOT: every module edge ---
    dl = ['digraph imports {', '  rankdir=LR; node [shape=box, fontsize=9];',
          '  // module X -> Y : X semantically depends on Y (X\'s elaborated core references a',
          '  // Y-defined name). Over the .agdai cores, NOT source import lines. Auto: gen_catalog.py']
    for m in mods:
        dl.append(f'  "{m}" [label="{tail(m)}"];')
    for x, y in sorted(edges):
        dl.append(f'  "{x}" -> "{y}";')
    dl.append("}")
    os.makedirs(os.path.dirname(IMPORT_DOT), exist_ok=True)
    open(IMPORT_DOT, "w", encoding="utf-8").write("\n".join(dl) + "\n")

    # --- MD: most-depended-on modules + degree ranking + a Mermaid slice ---
    TOPN = 12
    prims = [q for q, _ in rank(indeg, TOPN)]
    prims_set = set(prims)
    ml = ["# Import graph — module semantic dependency (who depends on whom)\n",
          "_Auto-generated by `scripts/gen_catalog.py` from the RAW `.agdai` cores — do not edit; regenerate._\n",
          f"_{len(mods)} modules, {len(edges)} dependency edges"
          + (f"; {failed} cores unreadable" if failed else "") + "._\n",
          "**Reading:** `X --> Y` means X's ELABORATED core references a name defined in Y — a "
          "*semantic* dependency (what X actually uses), NOT a source `import` line (which may be "
          "unused or re-exported). Most-depended-on = the load-bearing modules. Full graph: "
          "`catalog/import-graph.dot`.\n",
          "## Most-depended-on modules (in-degree) — the load-bearing centers\n",
          "| module | ← depended on by |", "|---|---:|"]
    for q, d in rank(indeg, 30):
        ml.append(f"| `{q}` | {d} |")
    ml += ["", "## Widest-reaching modules (out-degree) — depend on the most others\n",
           "| module | → depends on |", "|---|---:|"]
    for q, d in rank(outdeg, 20):
        ml.append(f"| `{q}` | {d} |")
    ml += ["", f"## Mermaid — top {TOPN} depended-on modules + their dependents\n", "```mermaid", "graph LR"]

    def nid(q):
        return "n" + hashlib.md5(q.encode()).hexdigest()[:10]
    emitted = set()
    for x, y in sorted(edges):
        if y in prims_set:
            for q in (x, y):
                if q not in emitted:
                    ml.append(f'  {nid(q)}["{tail(q)}"]')
                    emitted.add(q)
            ml.append(f"  {nid(x)} --> {nid(y)}")
    ml += ["```", ""]
    open(IMPORT_MD, "w", encoding="utf-8").write("\n".join(ml) + "\n")
    return f"import-graph: {len(mods)} modules, {len(edges)} dependency edges -> catalog/import-graph.dot + .md"


# ─────────────────────────── driver: build the store ONCE, render targets ───────────────────────────
_RENDERERS = {"index": render_index, "graph": render_graph, "sitemap": render_sitemap,
              "usage": render_usage, "import": render_import}

def generate(filt="", targets=("index", "graph", "sitemap", "usage", "import"), reuse_db=False):
    """Build catalog.db from the ONE shim-walk (unless reuse_db and it already exists), then render
    each requested target from the DB. Returns the list of per-step summary strings."""
    msgs = []
    if not (reuse_db and os.path.exists(CATALOG_DB)):
        db, failed = DbBuilder(), 0
        for core in walk_cores(filt):
            if core is None:
                failed += 1
                continue
            db.add(core)
        msgs.append(db.write(failed))
    con = sqlite3.connect(f"file:{CATALOG_DB}?mode=ro", uri=True)
    try:
        for t in targets:
            msgs.append(_RENDERERS[t](con))
    finally:
        con.close()
    return msgs
