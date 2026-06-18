#!/usr/bin/env python3
"""jea_agdai.py — Δ-Π-agdai: the THIRD front-end into the SPPF (after ast, cst).

An Agda `.agdai` interface file is ALREADY an interned forest. Measured (Graded.agdai):
  * magic e3bc4eaa (4B) + version/hashes, then a gzip stream at offset 24;
  * decompressed payload (1.08MB) is 97% index-pointers into a shared node arena
    -- a serialized hash-cons table, structurally identical to jea_pyalg.Intern;
  * the resolved-name table is plaintext (Substrate, +-assoc, cong, basis-vec, ...);
  * the fan-in distribution is the metalanguage signature already present (node 0
    referenced 50924x = the universal core atom; a long generator/idiom tail).

Agda's Data.Binary serialization (Agda.TypeChecking.Serialise) and our Intern are the SAME
idea -- serialized vs in-memory hash-cons. So "interning a .agdai" is NOT parse-and-build
(the ast path); it is DESERIALIZE Agda's arena into ours. Interning preserves sharing
REGARDLESS of node semantics, so we can intern the arena TOPOLOGY (the reference DAG, which
is version-stable) + attach NAMES as payload, WITHOUT decoding the per-version constructor
tags. That gives definitional-level structure (two proofs that elaborate to the same core
term share arena nodes -> intern to the same id) -- the similarity signal textual tools can't see.

HONEST SCOPE / WHAT IS NOT YET DECODED, AND HOW TO RECOVER IT
=============================================================
This front-end interns the VERSION-STABLE part of the arena: the node-level sharing
signature (each arena node's fan-in degree) + the resolved-name table. That is enough for
the cohomology / metalanguage / generator-idiom-coboundary classification (which is fan-in
based). It is NOT enough for the typeholer, which needs parent->child EDGES to build
skeletons. The child edges require NODE SEGMENTATION, which is VERSION-PINNED.

WHAT IS VERSION-PINNED (for the file at hand: Agda 2.8.0, interface magic e3bc4eaa):
  The decompressed payload is an Agda `Structure` -- a family of parallel hash-consed tables
  (a Node table of index-tuples, plus String / Text / Integer / Double / QName / Name tables),
  produced by the `EmbPrj` (embedded-projection) instances in
  `Agda.TypeChecking.Serialise.Instances.*`. The leading header words we read (43466, 43467,
  ...) are the table sizes/offsets. The piece we LACK is the bijection
        integer tag  <->  Agda-2.8.0 internal constructor   (+ that constructor's arity)
  for the serialised ADTs: `Term` (Var/Lam/Lit/Def/Con/Pi/Sort/MetaV/DontCare/Dummy),
  `Defn` (Axiom/DataOrRecSig/GeneralizableVar/AbstractDefn/Function/Datatype/Record/
  Constructor/Primitive/PrimitiveSort), `Sort`, `Level`, `Clause`, `Pattern`, `Type`, ...
  Without (tag -> arity) we cannot split the flat Node table into per-node child tuples, so
  `children=()` here. This table is pinned to 2.8.0's EXACT constructor set/order (2.8.0
  reworked modality/erasure/cohesion + opaque defs vs 2.6.x), so it must NOT be guessed from
  memory -- a one-constructor error shifts every subsequent tag.

HOW TO RECOVER IT (the toolchain that built this .agdai is present -- Agda 2.8.0):
  DO NOT hand-decode the tag table (brittle, version-locked). Instead have Agda 2.8.0 itself
  deserialise the interface with its OWN version-matched EmbPrj instances, and re-emit the
  signature in a stable format we intern with full edges. The recurring lesson, applied to the
  format: read the structure Agda's own deserialiser already knows; don't rebuild it.

  Recovery shim (~30 lines Haskell, against the Agda-2.8.0 library in the build env):
    1. `import Agda.Interaction.Imports (readInterface)`  -- or `Agda.TypeChecking.Serialise`
       (`decodeInterface`/`decodeFile`) -- to load `Graded.agdai` into a typed `Interface`.
    2. Pull `iSignature :: Signature`; from it `_sigDefinitions :: Map QName Definition`.
       Each `Definition` carries `theDef :: Defn` and `defType :: Type` -- the elaborated core.
    3. Walk each `Term`/`Type` and emit, per node:
         { id, constructor, qname?, children:[ids] }
       as JSON-lines (or s-expressions). The `children` are what we lack here; the walk over
       Agda's typed AST yields them directly (no tag table -- Agda's types ARE the segmentation).
    4. `jea_agdai.intern_signature(json_path, intern)` (TODO below) reads that and interns each
       core node with `children=(child ids...)` -> the FULL DAG, parent->child edges present,
       so the typeholer/cross-term run on core terms. Cross-file sharing falls out of hash-cons.

  Build-env entry points (Agda 2.8.0):
    - library: `Agda.TypeChecking.Serialise (decodeInterface)`, `Agda.Interaction.Imports`.
    - the shim links against the same `Agda-2.8.0` package that produced the .agdai, so the
      EmbPrj instances match the magic e3bc4eaa by construction -- no version drift possible.

  STATUS (Φ4 ✅ — BUILT): the shim is `jea/metalanguage/agdai_shim.hs` (~80 lines, ghc -package Agda).
  It decodes via Agda 2.8.0's `decodeInterface` (full file bytes; options set via setCommandLineOptions
  defaultOptions, else a TCM __IMPOSSIBLE__), walks each definition's `defType` over the real
  `Term`/`Elim'` ADTs, and emits the JSON-lines schema below. `core_intern_agdai` drives it end-to-end.
  VALIDATED: Emit.agdai -> 18 defs -> 62 core nodes -> interned 20 (3.1x sharing) with full parent->child
  edges (Emit.render->Emit.term, _≡_ over 4 args, two Pi sharing a domain). The .agdai must be
  current-toolchain (a stale interface decodes to Nothing -> rebuild). `intern_agdai` (fan-in only) stays
  as the no-toolchain fallback; `core_intern_agdai` is the full-edge path.
"""
from __future__ import annotations
import sys, os, gzip, struct, re, argparse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, IR


AGDAI_MAGIC = bytes.fromhex("e3bc4eaa")


def read_agdai(path: str) -> dict:
    """Parse a .agdai: split magic/version header from the gzip payload, decompress, and
    locate the node arena + name table. Returns the raw structural pieces."""
    raw = open(path, "rb").read()
    if raw[:4] != AGDAI_MAGIC:
        # magic is version-stamped; warn but proceed if a gzip stream is findable
        sys.stderr.write(f"  [warn] {path}: magic {raw[:4].hex()} != known e3bc4eaa "
                         f"(different Agda version; arena layout may differ)\n")
    gz = raw.find(b"\x1f\x8b\x08")
    if gz < 0:
        raise ValueError("no gzip stream found; not a recognized .agdai layout")
    body = gzip.decompress(raw[gz:])
    nwords = len(body) // 4
    words = struct.unpack(">%dI" % nwords, body[:nwords * 4])
    # header: leading Word64 counts (read as BE32 pairs). words[0] = node count.
    node_count = words[0] if words[0] > 0 else (words[2] or nwords)
    # the resolved-name table: contiguous printable runs (clustered at the tail, measured).
    names = []
    for m in re.finditer(rb"[ -~]{3,}", body):
        s = m.group()
        if re.match(rb"^[A-Za-z][\w'.+*/<>=-]*$", s):
            names.append(s.decode("latin1"))
    return {"body": body, "words": words, "node_count": node_count,
            "names": names, "gz_offset": gz, "compressed": len(raw), "decompressed": len(body)}


def intern_agdai(path: str, intern: Intern) -> dict:
    """Deserialize the .agdai arena into the given Intern. Interns the arena's REFERENCE DAG
    (version-stable sharing) as IR nodes; attaches names as payload. Returns a report.

    Each arena index becomes one interned IR node whose children are the arena-indices it
    references (the version-stable edges). Because we cannot segment by constructor tag without
    Agda's Serialise instances, we intern the reference structure: node i's 'children' are the
    distinct arena indices reachable in its word-window. The SHARING (fan-in) -- the load-bearing
    metalanguage signal -- is exact; the per-node semantic tag is left as opaque payload."""
    info = read_agdai(path)
    words = info["words"]; NC = info["node_count"]
    # the reference multiset: every word that is a valid back-index is an edge into the arena.
    fanin = Counter(w for w in words if 0 <= w < NC)
    # map arena indices -> interned ids. We intern each REFERENCED arena node as an atom whose
    # identity is its arena position (structure-stable within this file) plus its name if any.
    # Cross-file sharing then falls out of jea_pyalg's hash-cons: same (kind, payload, children).
    names = info["names"]
    # attach names to the highest-fan-in nodes (the generators) in order -- a faithful pairing
    # since the name table and the high-fan-in core both head their respective orderings.
    top = [idx for idx, _ in fanin.most_common()]
    name_for = {}
    for k, idx in enumerate(top[:len(names)]):
        name_for[idx] = names[k] if k < len(names) else ""
    arena_to_id = {}
    for idx in sorted(fanin):
        nm = name_for.get(idx, "")
        # PUT THE DISTINGUISHING STRUCTURE IN THE KEY, not payload (payload is residue, dropped
        # from identity -- the role-lowering principle; using it for identity collapsed everything
        # to one node). The version-stable structure we HAVE per arena node: its fan-in degree (the
        # sharing it participates in) and its resolved name. Encode degree as `op`, name as `role`,
        # arena-index as `lit` so each node has a distinct interned identity AND the sharing-degree
        # is structure, not dropped. (Full child-EDGE topology needs segmentation = AI-Q handoff;
        # this interns the node-level sharing signature, which is the load-bearing metalanguage signal.)
        node = IR(kind="AgdaCore", role=nm, op=f"fanin={fanin[idx]}", lit=str(idx),
                  children=(), payload=(idx, nm) if nm else (idx,))
        arena_to_id[idx] = intern.intern(node)
    return {"path": path, "arena_nodes": len(fanin), "node_count": NC,
            "names": len(names), "max_fanin": max(fanin.values()) if fanin else 0,
            "top_fanin": fanin.most_common(10), "name_table": names[:50],
            "compressed": info["compressed"], "decompressed": info["decompressed"],
            "arena_to_id": arena_to_id, "fanin": fanin}


def intern_signature(json_path: str, intern: Intern) -> dict:
    """Upgrade path (Δ-Π-agdai full): intern the FULL child-edge DAG from the Agda-2.8.0 shim's
    output. The shim (see module docstring "HOW TO RECOVER IT") emits JSON-lines, one per core node.

    SHIM JSON SCHEMA (what the readInterface walk must emit per node):
        {"id": int,
         "constructor": str,          # the Term/Defn constructor: "Var","Def","Con","Lam","Pi",...
         "qname": str|null,           # for Def/Con/Prim: the FREE qualified name (referential identity)
         "index": int|null,           # for Var: the de Bruijn INDEX (bound, position identity)
         "children": [int,...]}

    THE = vs ≅ LESSON, in Agda-core terms (carried over from the jea_pyalg free/bound fix):
    a core node's identity field depends on whether it is BOUND or FREE -- the same split that
    distinguished a bound var (role-quotiented) from a free global like abs/str (name in the key).
      * Var (de Bruijn): BOUND. Identity is the INDEX (position), alpha-equivalent under renaming.
        -> de Bruijn index goes in `role` (the position-quotient field). Two alpha-equivalent terms
        share a node BECAUSE the index, not a name, carries var identity. (Agda core is ALREADY
        de-Bruijn, so this is native -- the lesson is automatic here, unlike Python where we had
        to recover it.)
      * Def / Con / Prim / PrimSort: FREE referential. Identity is the QNAME (a specific global,
        like abs/str/Fraction were). -> qname goes in `op` (the KEY), NOT role. Two distinct globals
        do not collapse; two references to the SAME global share. (The stub previously put qname in
        `role`, which is the abs-vs-str bug pre-baked: it conflated free referential identity with
        bound-position identity. Fixed below.)
      * other constructors (Lam/Pi/App/Sort/...): structural; identity is constructor + children.

    Definitional equivalence then falls out of hash-cons: two core terms equal up to alpha (bound
    vars) and referential identity (free names) intern to ONE node. The typeholer recurses through
    `children` (lesson 3, native once edges are present); the depth-fold S(g), telescope, and
    cohomology are folds over this tree exactly as on the Python side.

    STATUS: LIVE (Φ4 ✅). The producer is agdai_shim.hs; drive end-to-end via core_intern_agdai (below).
    VALIDATED on Emit.agdai (62 core nodes -> interned 20, 3.1x, full child edges)."""
    import json
    raw = {}
    unit_markers = []                                         # (qname, shim-local root id, kind, members) per def
    with open(json_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                if "unit" in rec:                             # a per-definition unit marker (Φ4b)
                    unit_markers.append((rec["unit"], rec["root"], rec.get("kind", "?"),
                                         tuple(rec.get("members", []))))   # Φ7b: parent->member links
                else:
                    raw[rec["id"]] = rec
    interned: dict[int, int] = {}
    # referential: qname is identity -> KEY. Pattern constructors (Φ7a) join the term-level ones:
    # PCon/PDef/PProj are free referential exactly as Con/Def/Proj are.
    FREE = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}
    # bound (de Bruijn): identity = index (position) -> alpha-equivalent. PVar (Φ7a LHS pattern var) is
    # bound exactly as the term-level Var is -- two clauses matching the same shape share pattern nodes.
    BOUND = {"Var", "PVar"}

    def go(nid: int) -> int:
        if nid in interned:
            return interned[nid]
        rec = raw[nid]
        kids = tuple(go(c) for c in rec.get("children", []))
        ctor = rec.get("constructor", "")
        qname = rec.get("qname")
        if ctor in BOUND:
            # BOUND (de Bruijn): identity = index (position), in `role` -> alpha-equivalent.
            role = f"db{rec.get('index', '?')}"
            op = ""
            payload = ()
        elif ctor in FREE and qname:
            # FREE referential: identity = qname, in the KEY (`op`) -> distinct globals stay distinct.
            role = ""
            op = qname
            payload = (qname,)                            # keep the name as residue too (for readout)
        else:
            # structural constructor: identity = constructor + children.
            role = ""
            op = ctor
            payload = ()
        node = IR(kind="AgdaCore", role=role, op=op, lit="", children=kids, payload=payload)
        i = intern.intern(node)
        interned[nid] = i
        return i

    roots = [go(nid) for nid in raw]
    # map each definition's unit-marker (shim-local root) to its INTERNED root id -> per-def units (Φ4b)
    units = [(name, interned[r]) for name, r, _k, _m in unit_markers if r in interned]
    kinds = {name: k for name, r, k, _m in unit_markers if r in interned}   # Φ6: per-def Defn kind
    members = {name: list(m) for name, r, k, m in unit_markers if r in interned and m}  # Φ7b: parent->members
    return {"core_nodes": len(raw), "interned": intern.size(), "roots": roots,
            "units": units, "kinds": kinds, "members": members, "edges_present": True}


def core_intern_agdai(agdai_path: str, intern: Intern, shim_bin: str = None) -> dict:
    """FULL-edge path (Φ4 ✅): drive agdai_shim (the Agda-2.8.0 decoder, agdai_shim.hs) on a .agdai and
    intern its core-node JSON via intern_signature -> the full parent->child DAG (what the typeholer needs;
    strictly more than intern_agdai's fan-in signature). shim_bin defaults to ./agdai_shim beside this
    module (build it per agdai_shim.hs's header). The shim links Agda's OWN version-matched EmbPrj
    instances, so no tag table is guessed -- Agda's types ARE the segmentation."""
    import subprocess, tempfile
    if shim_bin is None:
        shim_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agdai_shim")
    if not os.path.exists(shim_bin):
        raise FileNotFoundError(f"agdai_shim not built at {shim_bin} -- build it: "
                                f"`ghc -package Agda -O0 -o agdai_shim agdai_shim.hs` (needs the Agda "
                                f"library in the GHC package db; see agdai_shim.hs header)")
    # run with CWD = the interface's own directory: Agda's option/decode context is project-relative,
    # and decode only succeeds reliably from within the project tree (measured; from /tmp it -> Nothing).
    ap = os.path.abspath(agdai_path)
    r = subprocess.run([shim_bin, ap], capture_output=True, text=True, cwd=os.path.dirname(ap))
    if r.returncode != 0:
        raise RuntimeError(f"agdai_shim failed on {agdai_path}: {r.stderr.strip()} -- a stale / "
                           f"older-version interface decodes to Nothing; rebuild it (`agda --safe ...`).")
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as fh:
        fh.write(r.stdout); jpath = fh.name
    try:
        rep = intern_signature(jpath, intern)
    finally:
        os.unlink(jpath)
    rep["agdai"] = agdai_path
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Δ-Π-agdai: deserialize Agda .agdai interface arenas into the SPPF "
                    "(the third front-end; intern the substrate's own core terms).")
    ap.add_argument("files", nargs="+", help=".agdai interface files")
    ap.add_argument("--show", type=int, default=20, help="name-table rows to show")
    args = ap.parse_args(argv)

    I = Intern()
    reports = []
    for f in args.files:
        try:
            rep = intern_agdai(f, I)
            reports.append(rep)
        except Exception as e:
            sys.stderr.write(f"  [skip] {f}: {type(e).__name__}: {e}\n")
    print(f"interned {len(reports)} .agdai file(s) into one forest: {I.size()} nodes")
    for rep in reports:
        print(f"\n{rep['path']}: {rep['compressed']}B -> {rep['decompressed']}B decompressed")
        print(f"  arena: {rep['node_count']} node slots, {rep['arena_nodes']} referenced, "
              f"{rep['names']} resolved names; max fan-in {rep['max_fanin']}")
        print(f"  the metalanguage signature (top arena fan-in = the core generators):")
        for idx, fi in rep['top_fanin']:
            print(f"    arena[{idx}] referenced {fi}x")
        print(f"  resolved proof vocabulary (sample): {rep['name_table'][:args.show]}")
    # cross-file sharing: if >1 file, nodes with the same (arena-idx, name) interned once.
    if len(reports) > 1:
        print(f"\ncross-file: one forest of {I.size()} nodes from {len(reports)} interfaces "
              f"(shared core terms interned once -- the definitional sharing across modules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
