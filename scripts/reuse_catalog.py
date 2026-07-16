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
import os, re, json, subprocess, collections, hashlib, sqlite3, base64

def _b64(s):   # ⟡content-addressed-interner: the id of an interned string IS base64(string) — a
    return base64.b64encode(("" if s is None else s).encode("utf-8")).decode("ascii")  # BIJECTIVE
# content-address (reversible, collision-free — NOT a hash). Bounded because every interned string is
# atomic (latent structure already decomposed out into path_seg/members): max ~92 chars → ~123 base64.

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys as _sys; _sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
import query_builders as QB               # ⟡query-rawtocore: single-source Core builders (run = execute)
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
import sys as _sys                     # ⟡lift-shared-core-machinery: the ONE shim-decode (typehole-
_sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))  # confirmed shared with core_intern_agdai
from jea_agdai import decode_core      # + the census; the CWD/locale/decode-Nothing invariants live there
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
-- ⟡catalog-term-ids — the DB-level INTERNER: every string lives ONCE in `terms`; the base tables
-- reference terms by INTEGER id (the hash-cons the SPPF uses, applied to catalog strings — no TEXT
-- repeated across qname/ref/src/dst). The compat VIEWS re-present the pre-interning TEXT schema, so
-- the renders (which sort in PYTHON, not SQL) are untouched and the output stays byte-identical.
-- `terms` is ALSO the diagnostic: `flattened_terms` (a term holding . | , — an encoded module-path,
-- a members-list crammed into an fp) shows where STRUCTURAL info was flattened into a string.
-- ⟡content-addressed-interner: term_id IS base64(text) — a bijective content-address (reversible,
-- collision-free), so interning is idempotent and shared by construction (base64('Substrate') is the
-- same id everywhere, no autonumber coordination). All *_id/_pid columns are these base64 ids (TEXT).
CREATE TABLE terms (term_id TEXT PRIMARY KEY, text TEXT);
CREATE UNIQUE INDEX ix_terms_text ON terms(text);
-- qname is NOT unique: an anonymous `module _` collapses several declarations to one qname
-- (e.g. two `data _⇒*_` in two `module _` blocks → one qname, two nodes). That collision is the
-- dedup FAN-IN signal (name-granularity), not a bug to drop — so the key is composite (qname, root)
-- and every colliding node is kept, rather than one clobbering the rest. (Ⓓ.catalog-fanin-key)
-- ⟡catalog-decompose-fp: fp/unhold_fp are NO LONGER stored — they were `kind|member,member,…` and
-- `kind|⟨CARRIER⟩,…`, i.e. the members / field-heads relations FLATTENED into a string (what
-- `flattened_terms` surfaced). They are now VIEWS over _members / _member_heads. Both member relations
-- are keyed by (struct_qname_id, struct_root), NOT qname alone — a non-unique qname (the module-`_`
-- fan-in) has several structs, and keying by qname conflated their members (the stored fp was per-root
-- and correct; the flat members table was the latent bug the decomposition fixes).
-- ⟡catalog-path-ids: a qname/module/ref IS a PATH — carried as a surrogate path_id whose STRING is
-- DERIVED from its interned segments (path_seg), never stored flat. `terms` now holds only ATOMIC
-- strings (segments, names, kinds, descs); the *_pid columns are path_ids. path_text reconstructs
-- (losslessly — proven). This removes every dotted path from the term table; the reference graph joins
-- on path_id. (Unlike fp — redundant with members, removed — a qname is the graph's IDENTITY.)
CREATE TABLE path_seg (path_id TEXT, ord INT, seg_term_id TEXT);
CREATE TABLE _structs (qname_pid TEXT, name_id TEXT, kind_id TEXT, module_pid TEXT, desc_id TEXT, root INTEGER, PRIMARY KEY (qname_pid, root));
CREATE TABLE _members      (struct_qname_pid TEXT, struct_root INTEGER, name_id TEXT, ord INTEGER);
CREATE TABLE _member_heads (struct_qname_pid TEXT, struct_root INTEGER, head_id TEXT, ord INTEGER);
CREATE TABLE _refs    (struct_qname_pid TEXT, ref_qname_pid TEXT);
CREATE TABLE _edges   (src_pid TEXT, dst_pid TEXT);
CREATE TABLE _module_edges (src_pid TEXT, dst_pid TEXT);   -- module -> module semantic dependency (import-graph)
CREATE TABLE _modules (module_pid TEXT, purpose_id TEXT, is_index INTEGER);
CREATE TABLE meta    (key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX ix_pathseg_seg  ON path_seg(seg_term_id);
-- a (path_id, ord) has exactly ONE segment (base64 path_id ⟹ fixed qname ⟹ fixed segment sequence).
-- This UNIQUE invariant makes INSERT-OR-IGNORE into the SHARED path_seg idempotent — the catalog dedups
-- via a Python set in one build, but streaming writers (sppf_db) rely on the constraint. It also serves
-- path_id-prefix lookups, so it subsumes the old ix_pathseg_path. (⟡catalog-pathseg-unique: hoisted here
-- from sppf_db, which kept a defensive IF-NOT-EXISTS copy for fresh-db self-sufficiency.)
CREATE UNIQUE INDEX ix_pathseg_uniq ON path_seg(path_id, ord);
CREATE INDEX ix_structs_name ON _structs(name_id);
CREATE INDEX ix_members_sq   ON _members(struct_qname_pid, struct_root);
CREATE INDEX ix_mheads_sq    ON _member_heads(struct_qname_pid, struct_root);
CREATE INDEX ix_edges_src    ON _edges(src_pid);
CREATE INDEX ix_edges_dst    ON _edges(dst_pid);
CREATE INDEX ix_medges_src   ON _module_edges(src_pid);
CREATE INDEX ix_medges_dst   ON _module_edges(dst_pid);
-- path reconstruction (the dotted string derived from segments) + the module-hierarchy sharing.
CREATE VIEW path_text AS
  SELECT path_id, GROUP_CONCAT(seg, '.') AS text FROM (
    SELECT ps.path_id, t.text AS seg FROM path_seg ps JOIN terms t ON t.term_id=ps.seg_term_id
    ORDER BY ps.path_id, ps.ord) GROUP BY path_id;
CREATE VIEW segment_sharing AS
  SELECT t.text AS segment, COUNT(DISTINCT ps.path_id) AS paths
  FROM path_seg ps JOIN terms t ON t.term_id=ps.seg_term_id GROUP BY ps.seg_term_id HAVING paths >= 2;
-- compat views: the pre-interning TEXT schema (paths reconstructed via path_text). Renders query THESE.
CREATE VIEW structs AS
  SELECT pq.text AS qname, n.text AS name, k.text AS kind, pm.text AS module,
         -- fp / unhold_fp COMPUTED from the relational member tables (per (qname,root)), not stored:
         k.text || '|' || COALESCE((SELECT GROUP_CONCAT(t) FROM (
             SELECT nm.text AS t FROM _members mm JOIN terms nm ON nm.term_id=mm.name_id
             WHERE mm.struct_qname_pid=s.qname_pid AND mm.struct_root=s.root ORDER BY nm.text)), '') AS fp,
         d.text AS desc, s.root AS root,
         k.text || '|' || COALESCE((SELECT GROUP_CONCAT(t) FROM (
             SELECT h.text AS t FROM _member_heads mh JOIN terms h ON h.term_id=mh.head_id
             WHERE mh.struct_qname_pid=s.qname_pid AND mh.struct_root=s.root ORDER BY h.text)), '') AS unhold_fp
  FROM _structs s JOIN path_text pq ON pq.path_id=s.qname_pid JOIN terms n ON n.term_id=s.name_id
    JOIN terms k ON k.term_id=s.kind_id JOIN path_text pm ON pm.path_id=s.module_pid
    JOIN terms d ON d.term_id=s.desc_id;
CREATE VIEW members AS SELECT psq.text AS struct_qname, n.text AS name, x.ord AS ord
  FROM _members x JOIN path_text psq ON psq.path_id=x.struct_qname_pid JOIN terms n ON n.term_id=x.name_id;
CREATE VIEW refs AS SELECT psq.text AS struct_qname, pr.text AS ref_qname
  FROM _refs x JOIN path_text psq ON psq.path_id=x.struct_qname_pid JOIN path_text pr ON pr.path_id=x.ref_qname_pid;
CREATE VIEW edges AS SELECT ps.text AS src, pd.text AS dst
  FROM _edges x JOIN path_text ps ON ps.path_id=x.src_pid JOIN path_text pd ON pd.path_id=x.dst_pid;
CREATE VIEW module_edges AS SELECT ps.text AS src, pd.text AS dst
  FROM _module_edges x JOIN path_text ps ON ps.path_id=x.src_pid JOIN path_text pd ON pd.path_id=x.dst_pid;
CREATE VIEW modules AS SELECT pm.text AS module, p.text AS purpose, x.is_index AS is_index
  FROM _modules x JOIN path_text pm ON pm.path_id=x.module_pid JOIN terms p ON p.term_id=x.purpose_id;
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
-- ⟡catalog-term-ids diagnostic: terms that FLATTEN structure into a string (glare here for the
-- decomposition worklist — a dotted qname flattens a module-path, an fp flattens the members table).
CREATE VIEW flattened_terms AS
  SELECT text,
         LENGTH(text)-LENGTH(REPLACE(text,'.','')) AS dots,
         LENGTH(text)-LENGTH(REPLACE(text,'|','')) AS pipes,
         LENGTH(text)-LENGTH(REPLACE(text,',','')) AS commas
  FROM terms WHERE text LIKE '%.%' OR text LIKE '%|%' OR text LIKE '%,%';
-- ⟡catalog-unhold-fp — REDUNDANCY-UNDER-INVERSION as a standing query. `fp` groups by member
-- NAMES (so a HELD-carrier record and a grade-INDEXED one, with different field names, never
-- match); `unhold_fp` groups by member CODOMAIN-HEADS with every carrier (a Record/Datatype ref
-- or a Sort) abstracted to ⟨CARRIER⟩ — so UPArrow² (3 ⟨CARRIER⟩ fields) and the rig cat's carrier-
-- holding records land on the same shape. This is the persistent form of the by-hand UPArrow²↔rig-cat
-- recognition: `SELECT * FROM shape_parallel_unhold` surfaces the inversion candidates the raw
-- structural dedup is blind to (feedback_dedup_misses_inversions_normalize_via_unhold).
CREATE VIEW shape_parallel_unhold AS
  SELECT unhold_fp, COUNT(DISTINCT name) AS names, GROUP_CONCAT(qname) AS structs
  FROM structs WHERE unhold_fp IS NOT NULL GROUP BY unhold_fp HAVING names >= 2;
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

def walk_cores(filt=""):
    """Streaming generator: decode each `.agdai` under Substrate/ via the shared `decode_core` ONCE
    and yield its parsed core (or None on a shim failure, so callers can count it). A core is
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
            d = decode_core(path, shim_bin=SHIM)          # the one shim-decode (cwd/locale/decode-Nothing)
            if d is None:
                yield None
                continue
            nodes    = {i: (r.get("constructor"), r.get("qname"), r.get("children", []))
                        for i, r in d["nodes"].items()}      # keep ctor: ⟡catalog-unhold-fp peels Π / detects Sort
            defmarks = [(r["unit"], r["root"], r.get("kind"), r.get("members", [])) for r in d["defmarks"]]
            yield {"mod": agdai_module(path), "path": path, "nodes": nodes, "defmarks": defmarks}


def raw_final_head(nodes, root):
    """⟡catalog-unhold-fp — over the raw core nodes {id: (ctor, qname, children)}: unwrap the `Defn`
    wrapper (child[0] = the defType), peel the Π-telescope (codomain = last child), return the
    codomain head as (ctor, qname). Mirrors set1_locate_census.final_head, over raw (not interned)
    nodes — the same shape at a different node representation (the final_head dup is itself an
    ⟡lift candidate, noted)."""
    n = nodes.get(root)
    if n is None:
        return (None, None)
    ctor, qn, ch = n
    if ctor == "Defn" and ch:
        ctor, qn, ch = nodes.get(ch[0], (None, None, []))
    seen = 0
    while ctor == "Pi" and ch and seen < 4096:
        ctor, qn, ch = nodes.get(ch[-1], (None, None, []))
        seen += 1
    return (ctor, qn)


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


# ─────────────────────────── DESERIALIZE (tokenize → structure), decoupled ───────────────────────────
# The "parameterize the deserialization" move: a raw walk-core becomes a fully-STRUCTURED object here —
# every qname-split, member-head peel, and ref-graph traversal DONE in this phase — so the structural-
# processing phase (DbBuilder) consumes the structure and NEVER re-splits a string next to using it.
ParsedStruct = collections.namedtuple(
    "ParsedStruct", "qname name kind module member_names field_heads refs root desc")
ParsedCore = collections.namedtuple(
    "ParsedCore", "module purpose is_index modrefs carriers structs")

def deserialize_core(core):
    """Raw walk-core {mod, nodes, defmarks} → ParsedCore. All tokenizing (rsplit qnames), field-head
    peeling (raw_final_head), source-comment parsing, and ref-graph traversal happen HERE and nowhere
    else. Downstream works on ParsedStruct fields, never on raw strings it re-parses."""
    mod, nodes = core["mod"], core["nodes"]
    modrefs  = {qn for _c, qn, _ch in nodes.values() if qn}
    defmarks = core["defmarks"]
    root_of  = {u: r for u, r, _k, _m in defmarks}
    cs       = [(u, r, k, m) for u, r, k, m in defmarks if k in ("Datatype", "Record")]
    carriers = {u for u, _r, _k, _m in cs}                 # every record/datatype IS a carrier
    # source-side deserialization: module purpose + per-declaration comments (best-effort; not in the core)
    src, purpose, comments = agda_source(mod), "", {}
    if os.path.exists(src):
        text = open(src, encoding="utf-8").read()
        purpose = mod_purpose(text)
        for ln in text.splitlines():
            m = decl_c.match(ln)
            if m:
                comments[m.group(1)] = shapetag.sub("", m.group(2)).strip()
    structs = []
    for unit, root, kind, members in cs:
        name = unit.rsplit(".", 1)[-1]
        kd   = "data" if kind == "Datatype" else "record"
        member_names = [m.rsplit(".", 1)[-1] for m in members]
        field_heads  = [raw_final_head(nodes, root_of.get(m)) for m in members]
        seen, refd, stack = set(), set(), [root]           # ref-graph traversal (structure, not a use-site)
        while stack:
            i = stack.pop()
            if i in seen or i not in nodes:
                continue
            seen.add(i)
            _c, qn, ch = nodes[i]
            if qn:
                refd.add(qn)
            stack.extend(ch)
        structs.append(ParsedStruct(unit, name, kd, mod, member_names, field_heads,
                                    refd, root, comments.get(name, "") or purpose))
    is_index = 1 if idxkind.search(mod.rsplit(".", 1)[-1]) else 0
    return ParsedCore(mod, purpose, is_index, modrefs, carriers, structs)


def deserialize_from_projection(con):
    """⟡es-p3-wire — build ParsedCore per module from the SPPF PROJECTION (not a core-walk). The
    structural data (structs, members, field-heads, refs, modrefs, carriers) is QUERIED from the
    projection (proven identical to deserialize_core's walk); only the module purpose + per-decl desc
    come from the .agda source (they are not term structure). Yields in module order."""
    pt = {p: t for p, t in QB.run(con, QB.q_pathtext_all())}
    tt = {i: t for i, t in QB.run(con, QB.q_terms_all())}
    units = {u: (pt.get(np), tt.get(k), pt.get(mp), rl)                 # unit_id -> (qname,kind,module,root_lid)
             for u, np, k, mp, rl in QB.run(con, QB.q_unit_fields())}
    cod = {u: (tt.get(cc) if cc else None, pt.get(cq) if cq else None)  # unit_id -> codomain (ctor,qname)
           for u, cc, cq in QB.run(con, QB.q_unit_cod())}
    members = collections.defaultdict(list)
    for su, o, mnp, muid in QB.run(con, QB.q_unit_member()):
        members[su].append((pt.get(mnp), muid))
    refs = collections.defaultdict(set)
    for u, rq in QB.run(con, QB.q_deserialize_oppath()):
        refs[u].add(rq)
    mod_structs, mod_refs, all_modules = collections.defaultdict(list), collections.defaultdict(set), set()
    for u, (qn, kd, md, rl) in units.items():
        all_modules.add(md)
        if kd in ("Datatype", "Record"):
            mod_structs[md].append(u)
        mod_refs[md] |= refs.get(u, set())
    for md in sorted(all_modules):
        src = agda_source(md)
        purpose, comments = "", {}
        if os.path.exists(src):
            text = open(src, encoding="utf-8").read()
            purpose = mod_purpose(text)
            for ln in text.splitlines():
                m = decl_c.match(ln)
                if m:
                    comments[m.group(1)] = shapetag.sub("", m.group(2)).strip()
        is_index = 1 if idxkind.search(md.rsplit(".", 1)[-1]) else 0
        structs = []
        for u in sorted(mod_structs.get(md, []), key=lambda x: (units[x][0], units[x][3])):
            qn, kd, _md, rl = units[u]
            structs.append(ParsedStruct(
                qn, qn.rsplit(".", 1)[-1], ("data" if kd == "Datatype" else "record"), md,
                [nm.rsplit(".", 1)[-1] for nm, _ in members.get(u, [])],
                [cod.get(muid, (None, None)) for _, muid in members.get(u, [])],
                refs.get(u, set()), rl, comments.get(qn.rsplit(".", 1)[-1], "") or purpose))
        yield ParsedCore(md, purpose, is_index, mod_refs.get(md, set()),
                         {units[u][0] for u in mod_structs.get(md, [])}, structs)


# ─────────────────────────── the store builder (walk -> catalog.db) ───────────────────────────
class DbBuilder:
    """The ONLY accumulator: loads the walk into catalog.db. Every catalog is then a render over it."""
    def __init__(self):
        self.structs, self.members, self.refrows, self.modrows = [], [], [], []
        self.kinds, self.refs = {}, {}
        self.allmods, self.modrefs = set(), {}         # for the module import graph (all modules)
        self.fieldheads = {}                           # ⟡catalog-unhold-fp: unit -> [(ctor,qname) codomain head per member]
        self.carriers = set()                          # ⟡catalog-unhold-fp: every Record/Datatype qname (the carriers)

    def add(self, core):
        self.add_pc(deserialize_core(core))

    def add_pc(self, pc):
        # STRUCTURAL PROCESSING — consumes the DESERIALIZED ParsedCore (from a core-walk OR from the SPPF
        # projection — ⟡es-p3-wire); no tokenizing here. The module import graph records EVERY module
        # (struct-bearing or not), so allmods/modrefs are set before the struct early-return.
        self.allmods.add(pc.module)
        self.modrefs[pc.module] = pc.modrefs
        self.carriers |= pc.carriers                   # ⟡catalog-unhold-fp: the global carrier set
        if not pc.structs:                             # a module with no data/record contributes no STRUCTS
            return
        self.modrows.append((pc.module, pc.purpose, pc.is_index))
        for s in pc.structs:
            # fp/unhold_fp are no longer stored — they are VIEWS over these member relations (keyed by
            # (qname,root), so a non-unique qname's structs don't conflate). ⟡catalog-decompose-fp.
            self.structs.append((s.qname, s.name, s.kind, s.module, s.desc, s.root))
            for i, h in enumerate(s.member_names):
                self.members.append((s.qname, s.root, h, i))
            self.kinds[s.qname] = s.kind
            self.fieldheads[(s.qname, s.root)] = s.field_heads
            self.refs[s.qname] = s.refs
            for r in sorted(s.refs):
                self.refrows.append((s.qname, r))

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

        # ⟡es-p3-wire: do NOT os.remove — the db already holds the events + SPPF projection this catalog
        # is DERIVED from. Append the catalog tables to it (terms/path_seg are shared, base64).
        os.makedirs(os.path.dirname(CATALOG_DB), exist_ok=True)
        # ⟡catalog-decompose-fp: abstract each member's codomain head (Sort or a Record/Datatype ref
        # → ⟨CARRIER⟩) into a RELATIONAL _member_heads row (keyed by (qname,root)); unhold_fp is then a
        # view GROUP_CONCAT over these, not a stored flattened string.
        def _head(ctor, qn):
            if ctor == "Sort" or (qn in self.carriers):
                return "⟨CARRIER⟩"
            return qn.rsplit(".", 1)[-1] if qn else (ctor or "?")

        # ⟡catalog-term-ids + ⟡catalog-path-ids: atomic strings → term ids (tid); a dotted PATH
        # (qname/module/ref/edge — NOT a free-text desc) → a surrogate path id (pid) whose SEGMENTS are
        # interned as terms. The flat path string is NEVER stored — it is derived from path_seg
        # (the path_text view). `terms` holds only atomic strings + path segments.
        # ⟡content-addressed-interner: an id IS base64(its string) — bijective, deterministic, shared
        # by construction (no autonumber). Atomic strings → tid; a qname is a PATH → pid = base64 of the
        # qname; its segments (themselves terms) live in path_seg.
        terms_seen, paths_seen = set(), set()
        def tid(s):
            s = "" if s is None else s
            terms_seen.add(s)
            return _b64(s)
        def pid(s):
            paths_seen.add(s)
            for seg in s.split("."):
                terms_seen.add(seg)
            return _b64(s)
        struct_rows = [(pid(u), tid(n), tid(kd), pid(md), tid(ds), rt)
                       for (u, n, kd, md, ds, rt) in sorted(self.structs)]
        member_rows = [(pid(sq), rt, tid(nm), o) for (sq, rt, nm, o) in self.members]
        mhead_rows  = [(pid(qr[0]), qr[1], tid(_head(ct, qn)), i)
                       for qr, heads in self.fieldheads.items()
                       for i, (ct, qn) in enumerate(heads)]
        ref_rows    = [(pid(sq), pid(r)) for (sq, r) in self.refrows]
        edge_rows   = [(pid(a), pid(b)) for (a, b) in edges]
        medge_rows  = [(pid(a), pid(b)) for (a, b) in module_edges]
        mod_rows    = [(pid(m), tid(p), ix) for (m, p, ix) in sorted(self.modrows)]
        pathseg_rows = sorted({(_b64(p), o, _b64(seg))
                               for p in paths_seen for o, seg in enumerate(p.split("."))})
        term_rows   = sorted((_b64(t), t) for t in terms_seen)

        con = sqlite3.connect(CATALOG_DB)
        # IF-NOT-EXISTS so it composes with the projection's schema (terms/path_seg/path_text already there).
        con.executescript(_DB_SCHEMA.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ")
                          .replace("CREATE UNIQUE INDEX ", "CREATE UNIQUE INDEX IF NOT EXISTS ")
                          .replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ")
                          .replace("CREATE VIEW ", "CREATE VIEW IF NOT EXISTS "))
        for t in ("_structs", "_members", "_member_heads", "_refs", "_edges", "_module_edges", "_modules", "meta"):
            con.execute(f"DELETE FROM {t}")                # clean rebuild of the catalog tables (idempotent re-run)
        con.executemany("INSERT OR IGNORE INTO terms   VALUES (?,?)",   term_rows)     # shared with projection
        con.executemany("INSERT OR IGNORE INTO path_seg VALUES (?,?,?)",pathseg_rows)  # shared with projection
        con.executemany("INSERT INTO _structs VALUES (?,?,?,?,?,?)",    struct_rows)
        con.executemany("INSERT INTO _members VALUES (?,?,?,?)",        member_rows)
        con.executemany("INSERT INTO _member_heads VALUES (?,?,?,?)",   mhead_rows)
        con.executemany("INSERT INTO _refs    VALUES (?,?)",            ref_rows)
        con.executemany("INSERT INTO _edges   VALUES (?,?)",            edge_rows)
        con.executemany("INSERT INTO _module_edges VALUES (?,?)",       medge_rows)
        con.executemany("INSERT INTO _modules VALUES (?,?,?)",          mod_rows)
        con.execute("INSERT INTO meta VALUES ('failed', ?)", (str(failed),))
        con.commit()
        con.close()
        return (f"catalog-db: {len(self.structs)} structs, {len(edges)} refinement edges, "
                f"{len(self.allmods)} modules, {len(module_edges)} import edges -> catalog/catalog.db")


def _failed(con):
    row = QB.run(con, QB.q_meta_failed()).fetchone()
    return int(row[0]) if row else 0


# ─────────────────────────── render 1: reuse-INDEX (name -> home) ───────────────────────────
def render_index(con):
    failed  = _failed(con)
    structs = sorted(((r[0], r[1], r[2], r[3] or "")
                      for r in QB.run(con, QB.q_structs_index())),
                     key=lambda x: (x[0].lower(), x[2]))
    namehomes = {}
    for name, module in QB.run(con, QB.q_structs_namemod()):
        namehomes.setdefault(name, set()).add(module)
    fingerprints = {}
    for fp, name, module in QB.run(con, QB.q_structs_fpnamemod()):
        fingerprints.setdefault(fp, []).append((name, module))
    idxmods = [(m, p or "") for m, p in
               QB.run(con, QB.q_modules_index())]

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
    struct_kind = dict(QB.run(con, QB.q_structs_qnamekind()).fetchall())
    edges = {(x, y) for x, y in QB.run(con, QB.q_edges_all())}
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
    rows = QB.run(con, QB.q_sitemap()).fetchall()
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
    total = QB.run(con, QB.q_structs_count()).fetchone()[0]
    refined_in  = {r[0] for r in QB.run(con, QB.q_edges_dst_distinct())}
    refines_out = {r[0] for r in QB.run(con, QB.q_edges_src_distinct())}
    allq = [r[0] for r in QB.run(con, QB.q_structs_qname())]
    never_refined = [q for q in allq if q not in refined_in]           # in-degree 0
    refines_none  = [q for q in allq if q not in refines_out]          # out-degree 0
    isolated = sorted(q for q in allq if q not in refined_in and q not in refines_out)
    top = QB.run(con, QB.q_indegree_top()).fetchall()

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
    kinds = dict(QB.run(con, QB.q_structs_qnamekind()).fetchall())
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
    edges = {(x, y) for x, y in QB.run(con, QB.q_modedges_all())}
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
        # ⟡es-p3-wire: BUILD the events + SPPF projection first (sppf_db), then DERIVE the catalog from it
        # (deserialize_from_projection → the UNCHANGED DbBuilder.add_pc/write). One content-addressed store.
        import glob as _glob
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))       # scripts/ (for sppf_db)
        import sppf_db
        base = sppf_db.substrate_core_root(os.path.join(ROOT, "agda"))
        cores = [c for c in sorted(_glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)) if filt in c]
        n, u, _sh, _mx = sppf_db.build(cores, argperm=True)   # ⟡orbit-projections-on: populate _orbit_def (graded coset residues) so orbit_cosets/graded_orbit --cosets light up; bounded (⟡deinline-graded-key: int handles, not inlined keys), paid only in the post-full-build catalog regen
        msgs.append(f"projection (events → SPPF): {n} packings, {u} units -> catalog.db")
        pcon = sqlite3.connect(CATALOG_DB)
        db = DbBuilder()
        for pc in deserialize_from_projection(pcon):
            db.add_pc(pc)
        pcon.close()
        msgs.append(db.write(0))
    con = sqlite3.connect(f"file:{CATALOG_DB}?mode=ro", uri=True)
    try:
        for t in targets:
            msgs.append(_RENDERERS[t](con))
    finally:
        con.close()
    return msgs
