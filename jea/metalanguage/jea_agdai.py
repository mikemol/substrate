#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
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


def intern_signature(core, intern: Intern) -> dict:
    """Upgrade path (Δ-Π-agdai full): intern the FULL child-edge DAG from the Agda-2.8.0 shim's
    output. The shim (see module docstring "HOW TO RECOVER IT") emits JSON-lines, one per core node.

    SHIM JSON SCHEMA (what the readInterface walk must emit per node):
        {"id": int,
         "constructor": str,          # the Term/Defn constructor: "Var","Def","Con","Lam","Pi",...
         "qname": str|null,           # for Def/Con/Prim: the FREE qualified name (referential identity)
         "index": int|null,           # for Var: the de Bruijn INDEX (bound, position identity)
         "lit": str,                   # for Lit/PLit: the literal VALUE (prettyShow); absent elsewhere
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
    # ⟡lift-shared-core-machinery — take the DECODED core `{"defmarks","nodes"}` from `decode_core`
    # (the one shim-decode). Back-compat: a path str is decoded here; a raw JSON-lines file is read.
    if isinstance(core, str):
        if os.path.isfile(core):
            import json as _json

            defmarks, nodes = [], {}
            for line in open(core):
                line = line.strip()
                if not line:
                    continue
                rec = _json.loads(line)
                if "unit" in rec:
                    defmarks.append(rec)
                else:
                    nodes[rec["id"]] = rec
            core = {"defmarks": defmarks, "nodes": nodes}
        else:
            core = decode_core(core)
    raw = core["nodes"]  # {shim-local id: rec}
    unit_markers = [
        (
            r["unit"],
            r["root"],
            r.get("kind", "?"),  # (qname, root, kind, members, level, sort)
            tuple(r.get("members", [])),  # Φ7b: parent->member links
            r.get("level"),
            r.get("sort"),
        )  # Φ7c: inhabited universe
        for r in core["defmarks"]
    ]
    interned: dict[int, int] = {}
    # ⚑ `unhold_path` REMOVED with `--unhold` (⟡unhold-is-fingerprint). It mapped a raw nid to
    # the carrier it packed into ⟨CARRIER⟩ — the residue that made the convergence a wedge —
    # and NOTHING EVER READ IT (`--calls unhold_path` → 0 defs, 0 calls, 3 refs, all in this
    # file). Returned in the report dict and consumed by no consumer, which is why the
    # not-a-lossy-erase argument could not save the mode it belonged to.
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
        ctor = rec.get("constructor", "")
        qname = rec.get("qname")
        # ── ⟡dedup-unhold-normalizer — REMOVED 2026-08-22 (⟡unhold-is-fingerprint).
        #
        # A `Sort`, or a Def/Con whose qname was in a supplied `carrier_qnames` set, interned to
        # a shared canonical `⟨CARRIER⟩` node, with `unhold_path[nid]` keeping the original so
        # the convergence was a wedge (`⟨CARRIER⟩ = recon q b r`) rather than a lossy erase.
        #
        # ⚑ THE MECHANISM WAS RIGHT AND THE RECOGNIZER WAS THE PROBLEM. Membership in a
        # hardcoded `("Record","Datatype")`-derived set is a CLASSIFICATION: an unmodelled
        # carrier kind is invisible, and on a non-Agda corpus the set is empty and the whole
        # pass silently no-ops. `pycodemod --fingerprint` asks the same question by
        # CONSTRUCTION instead — a prime per DISTINCT referent, *"asserting only that it is
        # distinct and countable, never what it IS"* — so shared structure is `gcd`, and what
        # is not modelled returns as an exact integer remainder rather than as an absence.
        #
        # ⚑ AND THE RESIDUE HAD NO READER, which is why the wedge argument did not save it:
        # `--calls unhold_path` → 0 defs, 0 calls, 3 refs, all inside this producer. It was
        # written into the returned dict and consumed by nothing.
        #
        # ⚑ THE PARAMETER REACHED ONE CALLER IN ELEVEN (`--forwards core_intern_agdai
        # carrier_qnames` → 1 of 11), so it was dead weight on every other path through a
        # shared interner — the `finalize=` shape: a mode's body surviving as a parameter.
        kids = tuple(go(c) for c in rec.get("children", []))
        if ctor in BOUND:
            # BOUND (de Bruijn): identity = index (position), in `role` -> alpha-equivalent.
            role = f"db{rec.get('index', '?')}"
            op = ""
            payload = ()
        elif ctor in FREE and qname:
            # FREE referential: identity = qname, in the KEY (`op`) -> distinct globals stay distinct.
            role = ""
            op = qname
            payload = (qname,)  # keep the name as residue too (for readout)
        else:
            # structural constructor: identity = constructor + children.
            role = ""
            op = ctor
            payload = ()
        # Lit/PLit carry a VALUE (the shim's "lit" field); it is IDENTITY for a literal (num 61 ≠
        # num 78 are distinct terms), so it keys into `lit`. Absent on every other constructor -> ""
        # -> those nodes intern exactly as before (additive; the earlier shim dropped the value).
        litval = rec.get("lit", "")
        node = IR(kind="AgdaCore", role=role, op=op, lit=litval, children=kids, payload=payload)
        i = intern.intern(node)
        interned[nid] = i
        return i

    roots = [go(nid) for nid in raw]
    # map each definition's unit-marker (shim-local root) to its INTERNED root id -> per-def units (Φ4b)
    units = [(name, interned[r]) for name, r, _k, _m, _lv, _st in unit_markers if r in interned]
    kinds = {
        name: k for name, r, k, _m, _lv, _st in unit_markers if r in interned
    }  # Φ6: per-def Defn kind
    members = {
        name: list(m) for name, r, k, m, _lv, _st in unit_markers if r in interned and m
    }  # Φ7b: parent->members
    levels = {
        name: lv for name, r, k, m, lv, _st in unit_markers if r in interned
    }  # Φ7c: inhabited-universe level
    sorts = {
        name: st for name, r, k, m, _lv, st in unit_markers if r in interned
    }  # Φ7c: codomain sort

    # Φ4c per-unit SUPPORT (membership): the interned nodes of a def's term, reachable from its root in
    # the ORIGINAL (acyclic) core `raw` — NOT via the interned bridge (which shares/reenters and would
    # cross-product across defs, or cycle). This is the correct source for a support/cluster analysis
    # once ids are content-addressed (shared): membership is captured pre-sharing, at intern time.
    def _reach(shim_root):
        seen, out, stack = set(), set(), [shim_root]
        while stack:
            k = stack.pop()
            if k in seen:
                continue
            seen.add(k)
            if k in interned:
                out.add(interned[k])
            rec = raw.get(k)
            if rec:
                stack.extend(rec.get("children", []))
        return out

    unit_members = {
        name: sorted(_reach(r)) for name, r, _k, _m, _lv, _st in unit_markers if r in interned
    }
    # Φ-provenance: Agda's defCopy per definition (True ⟺ created by a MODULE INSTANTIATION) — the exact
    # "came from parameterizing that module" signal (vs an independently-written def).
    copies = {r["unit"]: bool(r.get("copy", False)) for r in core["defmarks"]}
    return {
        "core_nodes": len(raw),
        "interned": intern.size(),
        "roots": roots,
        "units": units,
        "kinds": kinds,
        "members": members,
        "unit_members": unit_members,
        "levels": levels,
        "sorts": sorts,
        "copies": copies,
        "edges_present": True,
    }


def substrate_core_root(agda_root: str) -> str:
    """⟡lift-shared-core-machinery — the ONE home for the core-tree path logic. Agda-2.8.0 puts
    cores under <agda_root>/_build/<latest-ver>/agda/Substrate; pre-2.8.0 they sat alongside the
    source. set1_census_cores._default_core_root and set1_locate_census._core_root each re-rolled
    this (the dogfood's structural dup); they import it now."""
    import os

    base = os.path.join(agda_root, "_build")
    if os.path.isdir(base):
        vers = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d, "agda")))
        if vers:
            return os.path.join(base, vers[-1], "agda", "Substrate")
    return os.path.join(agda_root, "Substrate")


def build_agda_root(agda_root: str) -> str:
    """⟡lift-shared-core-machinery — the `<_build>/<latest-ver>/agda` level, i.e. the directory
    build ARTIFACTS are rooted at (`.agdai`, and the per-module `.agdai.log` the makefiles emit).
    `substrate_core_root` is this plus `Substrate`; both derive the version by LISTING `_build`,
    never by naming it.

    ⚑ ADDED BECAUSE A CONSUMER HARDCODED THE VERSION.  `figures._failures_by_kind` and
    `figures.failing_modules` each wrote `os.path.join(ROOT, "agda", "_build", "2.8.0", "agda", …)`
    — a literal that rots on the next Agda upgrade, and rots SILENTLY: the log path simply misses,
    `_classify` receives the empty string, and every build failure classifies as the fallback kind.
    A census that reads nothing reports a clean-looking answer, which is the same shape as
    `catalog_db.completeness()` certifying a corpus it never looked at.

    Slicing `substrate_core_root(...)` back one component at the call site would work and is the
    wrong home: the caller would then encode the fact that cores live under `Substrate`, which is
    exactly the knowledge this module exists to hold once."""
    import os

    return os.path.dirname(substrate_core_root(agda_root))


def decode_reason(returncode: int, stderr: str) -> str:
    """The TYPED reason a shim run failed — a pure function of its exit status and stderr.

    ⚑ LIFTED OUT OF `decode_core_diag` SO A CASE CAN DRIVE IT, which is the same seam
    `schema_diag` exists on: *"inline in a branch, the one judgement the result depends on was
    reachable only by running the real thing."* Here that bites harder than usual — MEASURED,
    the shim maps EVERY decode failure it has been shown to `decode Nothing`, including a
    markdown file handed to it, so the `shim-exit-N` arm is **not reachable from any input this
    repo can produce**. A case written against the subprocess can therefore only ever exercise
    one arm, and a mutation collapsing the discriminator to a constant PASSES (verified). Made
    pure, both arms are driven directly.

      `decode-nothing: …`  Agda's own deserialiser refused the interface — the CORE is stale or
                           wrong-version, and the repair is to rebuild that module.
      `shim-exit-N: …`     the shim or its environment failed — the TOOL is the problem.

    ⚑ THE HEAD OF STDERR, NOT THE TAIL. My first cut kept the LAST 400 characters and every
    reason came back as the bottom of a GHC `CallStack` — `throwIO, called at
    libraries/ghc-internal/src/GHC/Internal/IO/Exception.hs:319:20` for all nine cores, which
    is a fact about GHC's exception plumbing and identical whatever went wrong. A Haskell error
    puts its MESSAGE first and its provenance after; truncating from the wrong end kept the
    half that cannot discriminate.
    """
    msg = " / ".join(ln.strip() for ln in stderr.splitlines() if ln.strip())[:400]
    kind = "decode-nothing" if "decode Nothing" in stderr else "shim-exit-%d" % returncode
    return "%s: %s" % (kind, msg or "(no stderr)")


_DATADIR_MEMO = []


def agda_datadir():
    """Agda's DATA DIR (`<datadir>/lib/prim`) — ASKED OF THE BINARY, never hardcoded.

    ⚑⚑ THIS EXISTS BECAUSE A DATA DIR BAKED IN AT LINK TIME OUTLIVED THE PACKAGE THAT
    SUPPLIED IT (2026-08-14). `agdai_shim` links Agda as a LIBRARY, and GHC compiles that
    library's `Paths_Agda.getDataDir` in as a LITERAL — here the Debian package's
    `/usr/share/libghc-agda-dev`. When that package was removed, the shim (statically
    linked, so `ldd` shows no missing object and the binary still runs) began dying at
    startup with *"The lib directory /usr/share/libghc-agda-dev/lib does not exist"*
    — `Agda.Interaction.Library:116` — for EVERY core, including a trivial standalone one
    that had decoded seconds earlier.

    ⚑ AND THE FAILURE IS THE `shim-exit-N` KIND, NOT `decode-nothing`. That distinction is
    the whole value of `decode_reason`'s typing: `decode-nothing` means THIS CORE is stale
    and the repair is a rebuild; `shim-exit-N` means the TOOL is broken and no rebuild of
    anything would have helped. Untyped, a removed system package would have read as 3,400
    simultaneously-rotten interfaces.

    ⚑ THE VALUE IS DERIVED, WHICH IS THE POINT. `agda --print-agda-data-dir` is the
    binary's OWN answer, so this follows a reinstall, a store-path change or a version bump
    with no edit here. A literal store path would be a second baked-in constant — the very
    defect this works around, re-created one layer up.

    ⚑ AND THE QUERY DELIBERATELY AVOIDS THE MEMBUDGET SHIM. `scripts/agda-shim/agda` is a
    bash wrapper that takes a RAM lease before exec'ing the real binary; routing a 50 ms
    metadata question through it would block on the build's semaphore. The shim dir is
    dropped from PATH for this lookup only.

    Returns "" when it cannot be established — an empty string is "unmeasured", and the
    caller leaves the environment alone rather than asserting a path that may not exist.
    """
    if _DATADIR_MEMO:
        return _DATADIR_MEMO[0]
    import os, shutil, subprocess

    val = os.environ.get("Agda_datadir", "")
    if not val:
        _path = os.pathsep.join(
            d for d in os.environ.get("PATH", "").split(os.pathsep) if "agda-shim" not in d
        )
        _bin = shutil.which("agda", path=_path) or "agda"
        try:
            r = subprocess.run(
                [_bin, "--print-agda-data-dir"], capture_output=True, text=True, timeout=120
            )
            val = r.stdout.strip() if r.returncode == 0 else ""
        except Exception:
            val = ""
    # ⚑ VERIFIED, NOT TRUSTED: Agda's own check is for `<datadir>/lib`, so this asks the
    # same question rather than accepting any string the query happened to print.
    if not (val and os.path.isdir(os.path.join(val, "lib"))):
        val = ""
    _DATADIR_MEMO.append(val)
    return val


def decode_core_diag(agdai_path: str, shim_bin: str = None):
    """The ONE shim-decode, returning `(core, reason)` — the core, or None WITH ITS REASON.

    ⚑⚑ THE REASON EXISTS BECAUSE ITS ABSENCE MADE NINE CORES AN UNEXPLAINED NUMBER (⑼,
    2026-08-12). `decode_core` returned a bare `None` for THREE different conditions — the
    shim exiting non-zero, the shim printing `decode Nothing`, and (via `sppf_decode._decode_raw`'s
    blanket `except Exception`) any python-side failure at all — so `converge` could report
    *"9 core(s) UNDECODABLE"* and nothing anywhere could say why. Its own note said the
    skip *"bounds the loop; a restart retries it exactly once more, which is the correct
    amount for a condition that may be a rebuild away from fixed"*: sound about the LOOP,
    and silent about the CAUSE. A bounded retry over an undiagnosed condition is silent
    coverage loss — a core that never decodes contributes nothing to the SPPF and nothing
    says so.

    ⚑ THE REASON IS MEASURED, NEVER GUESSED. `decode_cost` used to answer this question with
    the string *"shim could not decode (version mismatch or stale core)"* — a hypothesis
    formatted as a finding, and (measured here) the WRONG hypothesis for every one of the
    nine. The reason returned now is the shim's own exit status and its own stderr.

    The invocation invariants each consumer (set1_census_cores, reuse_catalog,
    core_intern_agdai) re-learned the hard way, in a single place: cwd = the core's own
    directory (Agda resolves the interface's recorded include paths against CWD), LC_ALL/LANG
    = C.UTF-8 (the shim prints qnames like `_≈_`; a C locale dies with "commitBuffer: cannot
    encode character" AFTER a good decode — a locale bug, not a stale core).

    `core` is the RAW parsed core `{"defmarks": [rec,…], "nodes": {id: rec}}` (rec = the shim's
    JSON-lines record, qname refs intact). Consumers pick fields; core_intern_agdai adds interning.
    """
    import os, subprocess, json

    if shim_bin is None:
        shim_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agdai_shim")
    ap = os.path.abspath(agdai_path)
    env = dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")
    # ⚑ THE THIRD INVOCATION INVARIANT, beside cwd and the locale, and learned the same
    # way: `Agda_datadir` overrides the link-time literal that a package removal can
    # invalidate. Set only when we could ESTABLISH it, and never over an explicit choice
    # already in the environment.
    _dd = agda_datadir()
    if _dd:
        env.setdefault("Agda_datadir", _dd)
    r = subprocess.run(
        [shim_bin, ap], capture_output=True, text=True, cwd=os.path.dirname(ap), env=env
    )
    if r.returncode != 0 or "decode Nothing" in r.stderr:
        # ⚑ THE TWO CONDITIONS ARE DIFFERENT FACTS AND ARE TYPED APART. `decode Nothing` is
        # Agda's deserialiser REFUSING the interface (version skew / truncation) — the core is
        # the problem. A non-zero exit with other stderr is the shim or its environment
        # failing — the TOOL is the problem, and the repair is not the same one.
        return None, decode_reason(r.returncode, r.stderr)
    defmarks, nodes = [], {}
    for line in r.stdout.splitlines():
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if "unit" in rec:
            defmarks.append(rec)
        elif "id" in rec:
            nodes[rec["id"]] = rec
    return {"defmarks": defmarks, "nodes": nodes}, None


def decode_core(agdai_path: str, shim_bin: str = None):
    """The core, or None if the shim fails / reports `decode Nothing` (explicitly undecodable
    — NOT empty). The reason-discarding view of `decode_core_diag`, kept because eleven call
    sites across six modules ask only whether the decode worked.

    ⚑ A VIEW, NOT A SECOND IMPLEMENTATION. The invocation invariants live in ONE body; this
    projects it. A caller that needs to REPORT a failure must use `decode_core_diag` — and
    `sppf_decode._decode_raw`, the ingest path, now does.
    """
    return decode_core_diag(agdai_path, shim_bin=shim_bin)[0]


def decode_cost(agdai_path: str, shim_bin: str = None, reps: int = 5) -> dict:
    """Split ONE decode's wall time into SPAWN / SHIM-WORK / JSON-PARSE.

    ⚑ THIS EXISTS TO SIZE THE FFI DECISION, AND THE SPLIT IS THE WHOLE POINT. `sppf_db`
    already times decodes end-to-end (`_decode_window`) and the ledger records ~49ms —
    but a single number cannot say whether that is process spawn (which an FFI removes),
    Agda's own deserialise (which it does NOT — the same library does the same work), or
    JSON round-tripping (which `ctypes` + stdlib `json` largely KEEPS, since no fast codec
    is importable here). Proposing FFI on the strength of the total is proposing a fix
    whose size nobody measured.

    Method: `reps` runs, reporting the MINIMUM per phase. Minimum rather than mean because
    this measures a floor under contention — a slow sample is scheduler noise, never
    evidence the work is cheaper elsewhere.

      spawn_ms  a no-op run of the same binary (`--help`-less, missing arg → immediate
                exit): fork+exec+dynamic-link of a 95MB binary, the part FFI deletes.
      total_ms  the real decode, subprocess included.
      parse_ms  re-parsing the captured stdout, alone.
      work_ms   total − spawn − parse: Agda's deserialise + the term walk. FFI-INVARIANT.
    """
    import os, subprocess, json, time

    if shim_bin is None:
        shim_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agdai_shim")
    ap = os.path.abspath(agdai_path)
    env = dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")
    cwd = os.path.dirname(ap)

    def _t(fn):
        best = None
        for _ in range(reps):
            t0 = time.perf_counter()
            fn()
            dt = (time.perf_counter() - t0) * 1000.0
            best = dt if best is None else min(best, dt)
        return best

    # ⚑ THE SPAWN PROBE RUNS THE REAL BINARY WITH NO ARGUMENT, so it pays fork+exec and the
    # dynamic link of every Agda object — and then exits before decoding. A `/bin/true`
    # probe would measure the wrong binary and understate the cost it is here to isolate.
    spawn = _t(lambda: subprocess.run([shim_bin], capture_output=True, cwd=cwd, env=env))
    out = {}

    def _run():
        out["r"] = subprocess.run([shim_bin, ap], capture_output=True, text=True, cwd=cwd, env=env)

    total = _t(_run)
    r = out["r"]
    if r.returncode != 0 or "decode Nothing" in r.stderr:
        # ⚑ THE `why` WAS A GUESS AND IS NOW THE MEASUREMENT (⑼, 2026-08-12). It read
        # `"shim could not decode (version mismatch or stale core)"` — a hypothesis in the
        # shape of a finding, printed by `--cost` as though it were one, and wrong for every
        # core it was ever shown for. `decode_core_diag` returns the shim's own exit status
        # and stderr; a diagnostic that invents its diagnosis is worse than one that has none.
        _msg = " / ".join(ln.strip() for ln in r.stderr.splitlines() if ln.strip())[:400]
        _kind = "decode-nothing" if "decode Nothing" in r.stderr else "shim-exit-%d" % r.returncode
        return {
            "path": agdai_path,
            "decoded": False,
            "why": "%s: %s" % (_kind, _msg or "(no stderr)"),
        }
    text = r.stdout

    def _parse():
        for line in text.splitlines():
            try:
                json.loads(line)
            except Exception:
                pass

    parse = _t(_parse)
    return {
        "path": agdai_path,
        "decoded": True,
        "reps": reps,
        "bytes": len(text),
        "lines": text.count("\n"),
        "spawn_ms": round(spawn, 2),
        "total_ms": round(total, 2),
        "parse_ms": round(parse, 2),
        "work_ms": round(max(total - spawn - parse, 0.0), 2),
    }


def core_intern_agdai(agdai_path: str, intern: Intern, shim_bin: str = None) -> dict:
    """FULL-edge path (Φ4 ✅): drive agdai_shim (the Agda-2.8.0 decoder, agdai_shim.hs) on a .agdai and
    intern its core-node JSON via intern_signature -> the full parent->child DAG (what the typeholer needs;
    strictly more than intern_agdai's fan-in signature). shim_bin defaults to ./agdai_shim beside this
    module (build it per agdai_shim.hs's header). The shim links Agda's OWN version-matched EmbPrj
    instances, so no tag table is guessed -- Agda's types ARE the segmentation."""
    if shim_bin is None:
        shim_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agdai_shim")
    if not os.path.exists(shim_bin):
        raise FileNotFoundError(
            f"agdai_shim not built at {shim_bin} -- build it: "
            f"`ghc -package Agda -O0 -o agdai_shim agdai_shim.hs` (needs the Agda "
            f"library in the GHC package db; see agdai_shim.hs header)"
        )
    # ⟡lift-shared-core-machinery — one shim-decode (decode_core: cwd=core-dir, LC_ALL UTF-8, the
    # invariants), then intern. No tempfile; the decode is shared with the census + reuse_catalog.
    core = decode_core(agdai_path, shim_bin=shim_bin)
    if core is None:
        raise RuntimeError(
            f"agdai_shim failed / decode Nothing on {agdai_path} -- a stale / "
            f"older-version interface decodes to Nothing; rebuild it (`agda --safe ...`)."
        )
    rep = intern_signature(core, intern)
    rep["agdai"] = agdai_path
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Δ-Π-agdai: deserialize Agda .agdai interface arenas into the SPPF "
        "(the third front-end; intern the substrate's own core terms)."
    )
    ap.add_argument("files", nargs="+", help=".agdai interface files")
    ap.add_argument("--show", type=int, default=20, help="name-table rows to show")
    ap.add_argument(
        "--raw",
        action="store_true",
        help="print the shim's decoded nodes verbatim (constructor + children) "
        "— what the walk EMITTED, before interning",
    )
    ap.add_argument(
        "--cost",
        action="store_true",
        help="split each decode into spawn / shim-work / json-parse "
        "(sizes what an FFI boundary would and would not remove)",
    )
    ap.add_argument(
        "--header",
        action="store_true",
        help="the interface HEADER — magic, version words, payload framing — and "
        "whether the shim decodes it. Separates a VERSION SKEW from a "
        "content the decoder refuses",
    )
    args = ap.parse_args(argv)

    # ⚑ THE SHIM IS THE ONLY PATH. `main` used to drive `intern_agdai`, the pure-Python
    # arena reader kept as a "no-toolchain fallback" — deleted 2026-08-06 with the 2.6.3
    # straddle it existed for. It read FAN-IN ONLY (`children=()`, by its own comment: full
    # edge topology needs Agda's segmentation), and carried a hardcoded interface magic that
    # can only ever match one build, so it WARNED on a file the shim decodes perfectly.
    #
    # ⚑ AND A FALLBACK IS WHAT A FRESH SESSION REACHES FOR (user): straddle-handling infra
    # gets bypassed precisely because using it correctly requires knowing a conditional
    # exists. The fix is not a better flag — it is deletion, so there is nothing to bypass.
    if args.raw:
        # ⚑ THIS EXISTS BECAUSE "WHAT DID THE WALK ACTUALLY EMIT" HAD NO MODE, and running
        # the shim by hand FAILS: `decode_core`'s invocation invariants (cwd = the core's
        # own directory, LC_ALL=C.UTF-8) are exactly what a bare `./agdai_shim <path>` gets
        # wrong, reporting `decode Nothing` on a perfectly good core.
        for f in args.files:
            # ⚑ WITH THE REASON (⑼). `NOT DECODED` alone is the same bare-count answer the
            # converge loop gave for nine cores: it names the outcome and withholds the only
            # thing a reader can act on.
            core, why = decode_core_diag(f)
            if core is None:
                print(f"{f}: NOT DECODED — {why}")
                continue
            nodes = core["nodes"]
            print(f"== {f}: {len(nodes)} nodes, {len(core['defmarks'])} defmarks")
            for nid in sorted(nodes):
                rec = nodes[nid]
                extra = "".join(
                    f" {k}={rec[k]!r}" for k in ("qname", "index", "lit") if rec.get(k) is not None
                )
                print(
                    f"  {nid:4d} {rec.get('constructor', '?'):24s} {rec.get('children', [])}{extra}"
                )
        return 0

    if args.header:
        # ⚑⚑ THE MODE THAT SEPARATES "STALE" FROM "REFUSED" (⑼, 2026-08-12). The shim's own
        # message for every failure is *"decode Nothing (stale/wrong-version .agdai; rebuild
        # it)"* — a HYPOTHESIS the shim states as a diagnosis, and the one thing a reader
        # needs is whether it is true. If a refused interface's magic and version words match
        # a DECODABLE one's, the file is not stale and "rebuild it" is the wrong instruction;
        # if they differ, it is exactly right.
        #
        # ⚑ THE HEADER IS THIS MODULE'S OWN SUBJECT, WHICH IS WHY THE MODE BELONGS HERE. The
        # docstring at the top measured it — *"magic e3bc4eaa (4B) + version/hashes, then a
        # gzip stream at offset 24"* — and then no mode could ask a file for it, so the fact
        # was reachable only by re-deriving it with a hex dump. Reading it back is the whole
        # point of having written it down.
        import binascii

        for f in args.files:
            with open(f, "rb") as fh:
                head = fh.read(32)
            size = os.path.getsize(f)
            _core, why = decode_core_diag(f)
            # ⚑ THE GZIP PROBE IS AT THE OFFSET THE HEADER DECLARES, not searched for. A scan
            # for `1f8b` anywhere would match compressed payload bytes by accident and report
            # a truncated file as well-framed.
            gz = head[24:26] == b"\x1f\x8b"
            print(
                "%s\n  %8d B  magic=%s  version=%s  gzip@24=%s  decode=%s"
                % (
                    f,
                    size,
                    binascii.hexlify(head[:4]).decode(),
                    binascii.hexlify(head[4:24]).decode(),
                    gz,
                    "OK" if _core is not None else why.split(":")[0],
                )
            )
        return 0

    if args.cost:
        tot = {"spawn_ms": 0.0, "work_ms": 0.0, "parse_ms": 0.0, "total_ms": 0.0}
        for f in args.files:
            c = decode_cost(f)
            if not c["decoded"]:
                print(f"{f}: NOT DECODED — {c['why']}")
                continue
            print(f"\n{f}  ({c['bytes']}B, {c['lines']} lines, best of {c['reps']})")
            print(f"  spawn   {c['spawn_ms']:8.2f} ms   fork+exec+link — FFI REMOVES this")
            print(f"  work    {c['work_ms']:8.2f} ms   Agda deserialise + walk — FFI KEEPS this")
            print(f"  parse   {c['parse_ms']:8.2f} ms   json — FFI keeps unless the codec changes")
            print(f"  total   {c['total_ms']:8.2f} ms")
            for k in tot:
                tot[k] += c[k]
        if tot["total_ms"]:
            share = 100.0 * tot["spawn_ms"] / tot["total_ms"]
            print(f"\nacross {len(args.files)} core(s): spawn is {share:.0f}% of wall time")
            print(
                "that share is the FFI's ceiling — the rest is work the same library "
                "does either way."
            )
        return 0

    I = Intern()
    reports = []
    for f in args.files:
        core = decode_core(f)
        if core is None:
            sys.stderr.write(
                f"  [FAIL] {f}: the shim could not decode this interface.\n"
                f"         The linked Agda MUST be the build that produced it. Rebuild the\n"
                f"         core (`agda --safe`) or the shim (`make -C jea/metalanguage shim`).\n"
            )
            continue
        reports.append((f, intern_signature(core, I)))
    print(f"interned {len(reports)} .agdai file(s) into one forest: {I.size()} nodes")
    # ⚑ THE KEYS ARE READ FROM `intern_signature`, NOT GUESSED. My first cut printed
    # `rep['nodes']` / `rep['units']` as counts; the real shape is `core_nodes` (int) and
    # `units` (a LIST of (qname, interned-root)). A `.get(k, '?')` would have printed "?"
    # forever and looked like missing data rather than a wrong key.
    for path, rep in reports:
        print(
            f"\n{path}: {rep['core_nodes']} core nodes -> {rep['interned']} interned, "
            f"{len(rep['units'])} units, edges={rep['edges_present']}"
        )
    if len(reports) > 1:
        print(
            f"\ncross-file: one forest of {I.size()} nodes from {len(reports)} interfaces "
            f"(shared core terms interned once -- the definitional sharing across modules)"
        )
    return 0 if reports else 1


if __name__ == "__main__":
    sys.exit(main())
