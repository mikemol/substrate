#!/usr/bin/env python3
"""check_scratch_independence.py — Λ8: assert the migrated projects make NO LIVE scratch/ reference.

The invariant (the G9 escalation from the 2026-06-17 scratch-dissolution arc): once a project is
promoted out of scratch/ (jea/, el-atlas/), it must not silently re-acquire a runtime dependency on
scratch/. Before this gate, "is jea independent of scratch?" was answered by re-grepping by hand --
and the answer was wrong twice (the el-atlas tools coupling, then the Agda-emit-dir coupling surfaced
serially). This makes the answer correct-by-construction: a live scratch reference blocks the commit.

WHAT COUNTS AS "LIVE" (vs the exempt "dated historical note" the arc agreed to keep):
  * LIVE  = `scratch` in EXECUTABLE CODE -- a string literal used as a path (os.path.join(..,"scratch",..),
            open("scratch/.."), sys.path inserts), or an import naming scratch. These create a runtime dep.
  * EXEMPT = comments (`# .. scratch ..`), module/function/class DOCSTRINGS, and all .md/.agda prose.
            Dated WAL/ledger notes ("MERGE .. scratch/el-atlas/el-atlas-repo", "Was scratch/..tar.gz")
            are historical facts; they carry no runtime dependency and stay.

The comment/docstring/markdown exemption is MECHANICAL, not a denylist: we parse each .py with `ast`
(comments are absent from the AST entirely; docstrings are the identifiable first-Expr-Constant of a
module/def/class) and flag ONLY non-docstring string constants + imports that mention scratch.

Scope: jea/ and el-atlas/ (the promoted projects). scripts/ is NOT guarded (el-atlas legitimately
reaches repo-root scripts/, e.g. decide_groundtruth -> witness_sanity; the invariant is scratch-freedom,
not isolation). Extend ROOTS when another project is promoted out of scratch/.

Usage: check_scratch_independence.py [--quiet]   (silent on success with --quiet; exit 1 on any live ref)
"""
import ast
import os
import sys

ROOTS = ["jea", "el-atlas"]


def _docstring_node_ids(tree):
    """ids of the Constant nodes that are docstrings (module/def/class first statement) -- exempt as prose."""
    ds = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                ds.add(id(body[0].value))
    return ds


def scan_file(path):
    """Return (hits, warns). hit = (lineno, kind, snippet) for a LIVE scratch reference."""
    hits, warns = [], []
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src, filename=path)
    except (SyntaxError, UnicodeDecodeError) as e:
        warns.append(f"{path}: could not parse ({e.__class__.__name__}); not scanned")
        return hits, warns
    doc_ids = _docstring_node_ids(tree)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and "scratch" in node.value and id(node) not in doc_ids):
            hits.append((node.lineno, "path-string", node.value.strip()[:70]))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names]
            if isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            if any(n and "scratch" in n for n in names):
                hits.append((node.lineno, "import", ",".join(n for n in names if n)))
    return hits, warns


def main():
    quiet = "--quiet" in sys.argv or "--check" in sys.argv
    all_hits, all_warns, n_scanned = [], [], 0
    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            for f in files:
                if not f.endswith(".py"):
                    continue
                p = os.path.join(dirpath, f)
                n_scanned += 1
                hits, warns = scan_file(p)
                all_warns += warns
                for ln, kind, snip in hits:
                    all_hits.append((p, ln, kind, snip))

    for w in all_warns:
        print(f"  scratch-independence: WARN {w}", file=sys.stderr)

    if all_hits:
        print(f"scratch-independence (Λ8): FAILED — {len(all_hits)} LIVE scratch/ reference(s) in a "
              f"promoted project ({'/'.join(ROOTS)}):", file=sys.stderr)
        for p, ln, kind, snip in all_hits:
            print(f"    {p}:{ln}  [{kind}]  {snip}", file=sys.stderr)
        print("  A promoted project must not depend on scratch/ at runtime. Either repoint the path to "
              "the artifact's real home, or — if this is a dated HISTORICAL note — move it into a comment "
              "or a .md ledger (those are exempt; live code is not).", file=sys.stderr)
        return 1

    if not quiet:
        print(f"scratch-independence (Λ8): OK ({n_scanned} .py scanned across {'/'.join(ROOTS)}, 0 live refs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
