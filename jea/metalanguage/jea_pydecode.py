#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""THE Python front-end for the event tier — one top-level definition = one core.

The Agda side decodes a `.agdai` into `{nodes, defmarks}` and `sppf_db._insert_decoded`
writes it. This module produces the SAME shape from Python source, so both corpora land
in ONE set of relations, discriminated by `core_fp.producer`.

⚑ WHAT THIS DELIBERATELY DOES NOT DO — `jea_pyalg` ALREADY WALKS PYTHON'S AST.
The reuse-search fired before a line was written: `jea_pyalg.Intern`/`IR` already turn
Python into an interned IR whose `children` are IDs into the intern table — which IS the
SPPF property `_insert_decoded` assumes ("structural equality all the way down,
established once at intern"). Writing a second AST walker here would be the
rebuild-vs-read failure with the target sitting one import away. So this module is an
ADAPTER plus the `defmarks` half, not a decoder:

    IR.kind      -> constructor      (the ast node class name, uncollapsed)
    IR.children  -> children         (already local IDs; same convention as the shim)
    IR.lit       -> lit              (the literal KIND; the VALUE is payload residue)
    IR.role/op   -> qname            (the binding role / operator token — see below)

⚑ AND THE FIELDS WITH NO PYTHON MEANING ARE LEFT EMPTY, NOT INVENTED. `level` is Agda's
elaborated universe level and `copy` is defCopy instantiation provenance; neither exists
in Python. They are `None` and `0`. Filling them with a plausible-looking number would
put fiction into a tier whose whole value is that a row means one thing.

⚑ WHY A DEFINITION AND NOT A FILE IS A CORE (user, 2026-08-06). The faithful analogue of
an `.agdai` is a FILE — but the repo's decomposition objective is one-definition-per-file,
and the tooling corpus is emphatically undecomposed (`pycodemod.py` is ~4500 lines). Coring
per definition makes the Python tier's granularity match the OBJECTIVE rather than the
current layout, so a cross-corpus comparison compares like with like.

    The consequence, and it is load-bearing: `core_id` must be `<relpath>::<qualname>`.
    `core_fp` is keyed by an interned path and `_delete_core_rows` prunes by `core_id`, so
    the path ALONE would collide every definition in a file onto one key and the last
    write would win — silently, since interning accepts any string.
"""

import ast
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from jea_pyalg import Intern, IR  # THE interner — children-as-IDs, hash-consed


CORE_SEP = "::"  # <relpath>::<qualname> — the core identity


def _lit_kind(v):
    """The literal KIND, never its value — matching IR.lit's contract."""
    if v is None:
        return "none"
    return {bool: "bool", int: "int", float: "float", str: "str", bytes: "bytes"}.get(
        type(v), "other"
    )


def _walk(node, itn, qual):
    """Intern one ast node and its children, returning its intern id.

    ⚑ CHILDREN ARE INTERNED FIRST, BOTTOM-UP. `IR.key()` includes `children`, which are
    IDs — so a parent cannot be interned until its children have ids. Interning top-down
    would key every parent on an empty child tuple and collapse the whole corpus onto a
    handful of nodes, which is the failure mode that looks like enormous sharing.
    """
    kids = []
    for f in ast.iter_child_nodes(node):
        kids.append(_walk(f, itn, qual))

    kind = type(node).__name__
    role = op = lit = ""
    payload = ()

    if isinstance(node, ast.Name):
        role = "name"
        payload = (node.id,)
    elif isinstance(node, ast.Attribute):
        role = "attr"
        payload = (node.attr,)
    elif isinstance(node, ast.Constant):
        lit = _lit_kind(node.value)
        payload = (repr(node.value)[:120],)
    elif isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp)):
        op = type(node.op).__name__
    elif isinstance(node, ast.Compare) and node.ops:
        op = type(node.ops[0]).__name__

    span = (
        getattr(node, "lineno", 0),
        getattr(node, "col_offset", 0),
        getattr(node, "end_lineno", 0),
    )
    return itn.intern(
        IR(kind=kind, role=role, op=op, lit=lit, children=tuple(kids), payload=payload), span
    )


def _toplevel(tree):
    """Top-level `def`/`class` nodes, with their qualnames and member qualnames.

    ⚑ MEMBERS ARE QUALNAMES, matching the Agda `defmarks` convention (`jea_agdai:210` —
    "Φ7b: parent->member links"), because `_insert_decoded` resolves them through
    `root_of`, a qname->root map. Emitting bare method names would silently fail that
    lookup and write NULL member_unit_id for every method in the corpus.
    """
    out = []
    for n in tree.body:
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        members = []
        if isinstance(n, ast.ClassDef):
            members = [
                n.name + "." + m.name
                for m in n.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
        out.append((n, n.name, type(n).__name__, members))
    return out


def decode_defs(path, module=None):
    """Decode ONE python file into a LIST of `(core_id, dec)` — one per top-level def.

    `dec` is exactly `_insert_decoded`'s contract: `{"nodes", "defmarks", "module"}`.
    Returns [] for a file that will not parse — the analogue of an undecodable core, and
    reported as such rather than raised, so one bad file does not abort a corpus sweep.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, ValueError):
        return []

    # ⚑ A PATH OUTSIDE THE CWD MAKES `relpath` EMIT `../../..`, AND THE MODULE NAME IS
    # DERIVED FROM IT — so a file elsewhere on disk was filed under
    # `............tmp.tmpXXXX.sample`. Caught by the members case, which compares a
    # qualname against a literal; a case that only counted members would have passed.
    # Fall back to the basename rather than emitting an ascending path as a module.
    rel = os.path.relpath(path)
    if rel.startswith(".."):
        rel = os.path.basename(path)
    if module is None:
        module = rel[:-3].replace(os.sep, ".") if rel.endswith(".py") else rel

    out = []
    for node, name, kind, members in _toplevel(tree):
        itn = Intern()  # ⚑ PER-CORE, so local ids start at 0 —
        # `obs` is keyed (core_id, local_id) and a
        # shared interner would make ids global,
        # breaking that primary key's meaning.
        root = _walk(node, itn, name)
        nodes = {}
        for lid, ir in enumerate(itn.nodes):
            rec = {"constructor": ir.kind, "children": list(ir.children)}
            if ir.role or ir.op:
                rec["qname"] = ir.role or ir.op
            if ir.lit:
                rec["lit"] = ir.lit
            nodes[lid] = rec
        dec = {
            "nodes": nodes,
            "defmarks": [
                {
                    "unit": module + "." + name,
                    "root": root,
                    "kind": kind,
                    "members": [module + "." + m for m in members],
                    "copy": 0,
                    "level": None,
                }
            ],
            "module": module,
        }
        out.append((rel + CORE_SEP + name, dec))
    return out


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    import tempfile

    d = tempfile.mkdtemp()
    p = os.path.join(d, "sample.py")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(
            "import os\n\n"
            "def alpha(x):\n    return x + 1\n\n"
            "def beta(y):\n    return y + 1\n\n"
            "class Gamma:\n    def m(self):\n        return 2\n"
        )

    got = decode_defs(p)
    check("one core per top-level def", len(got), 3)

    ids = [cid for cid, _ in got]
    # ⚑ THE COLLISION CASE. With `core_id = relpath` alone all three would be one key and
    # two would be silently overwritten. This asserts the qualname is IN the identity.
    check("core ids are distinct", len(set(ids)), 3)
    check("core id carries the qualname", ids[0].endswith("::alpha"), True)

    dec_a = dict(got)[ids[0]]
    dec_b = dict(got)[ids[1]]
    # alpha and beta are alpha-equivalent up to the ARG NAME, which lives in payload
    # (residue, not the key) — so their node COUNT must agree.
    check(
        "structurally identical defs intern to equal size", len(dec_a["nodes"]), len(dec_b["nodes"])
    )

    # ⚑ CHILDREN MUST BE IDS STRICTLY BELOW THEIR PARENT — the bottom-up invariant. A
    # top-down walk would key parents on empty child tuples; this case FAILS against that.
    bad = [(lid, c) for lid, r in dec_a["nodes"].items() for c in r["children"] if c >= lid]
    check("children are interned before parents", bad, [])

    # the root must be the LAST-interned node (nothing references it)
    check("root is a real node id", dec_a["defmarks"][0]["root"] in dec_a["nodes"], True)

    gamma = dict(got)[ids[2]]
    check("class members are QUALNAMES", gamma["defmarks"][0]["members"], ["sample.Gamma.m"])
    check("class kind is recorded", gamma["defmarks"][0]["kind"], "ClassDef")

    # ⚑ NO INVENTED FIELDS. level/copy have no python meaning.
    check("level is None, not a number", dec_a["defmarks"][0]["level"], None)
    check("copy is 0", dec_a["defmarks"][0]["copy"], 0)

    # module name must NOT acquire the Agda shape
    check("module is python-shaped", dec_a["module"].startswith("Substrate."), False)

    # an unparseable file is [] , not an exception
    bad_p = os.path.join(d, "broken.py")
    with open(bad_p, "w", encoding="utf-8") as fh:
        fh.write("def (:\n")
    check("unparseable file yields no cores", decode_defs(bad_p), [])

    failed = [c for c in cases if not c[1]]
    for label, _, got, want in failed:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(failed), len(cases)))
    return 0 if not failed else 1


# ⚑ ⟡mode-standardize — the `Mode(...)` shape via `climode.from_pairs`.
# ⚑⚑ THE SECOND ENTRY IS NOT A FLAG, AND THE LIFT HAD TO LEARN THAT. `<file.py>` is this
# tool's PRIMARY invocation — positional, no flag at all. Keyed as one it would match no
# argv token and `contract_rows` would report it DECLARED-never-dispatched: a false finding
# manufactured by the migration, inside the gate built to find real ones. It keys as
# `climode.POSITIONAL` instead, and the contract reader skips it by construction.
# `toolmodes --conventions` counts `(positional)` across 28 tools, so this is a shape the
# corpus HAS, not an oddity of this file.
_MODES = (
    ("--selftest", "the guarded cases"),
    ("<file.py>", "the cores this file would produce: id, kind, node count"),
)

import os.path as _osp  # noqa: E402

sys.path.insert(
    0, _osp.join(_osp.dirname(_osp.dirname(_osp.dirname(_osp.abspath(__file__)))), "scripts")
)
from climode import from_pairs  # noqa: E402

#: The declared roster, `{flag: Mode}` — plus `climode.POSITIONAL` for the bare invocation.
MODES = from_pairs(_MODES)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__.strip().splitlines()[0])
        print("\nmodes:")
        for flag, why in _MODES:
            print("  %-14s %s" % (flag, why))
        raise SystemExit(0)
    total = 0
    for a in args:
        cores = decode_defs(a)
        for cid, dec in cores:
            print("%-58s %-14s %5d nodes" % (cid, dec["defmarks"][0]["kind"], len(dec["nodes"])))
        total += len(cores)
    print("%d core(s) from %d file(s)" % (total, len(args)))
