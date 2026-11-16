#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""feedcorpus.py — stage the memory-tooling scripts for the banding pipeline in
one of three FIDELITIES, so the projection is a knob rather than a hidden choice.

  raw   the literal .py bytes, renamed .md (no preprocessing at all)
  cst   the libcst CONCRETE syntax tree, one node-type per line, indented by depth
        (structure as text; the grammar sees nesting, not identifiers)
  cstx  cst node types WITH their identifier values (structure + content)

    feedcorpus.py <raw|cst|cstx> <dstdir>
"""
import os
import sys

SRC = "/home/mikemol/github/substrate/catalog/memory"
MODE, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)


def cst_lines(src, with_values):
    import libcst as cst

    mod = cst.parse_module(src)
    out = []

    def walk(node, depth):
        name = type(node).__name__
        if with_values:
            val = getattr(node, "value", None)
            if isinstance(val, str) and val.isidentifier():
                name = f"{name} {val}"
        out.append("  " * min(depth, 40) + name)
        for child in node.children:
            walk(child, depth + 1)

    walk(mod, 0)
    return "\n".join(out)


n = 0
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".py"):
        continue
    src = open(os.path.join(SRC, fn), encoding="utf-8").read()
    if MODE == "raw":
        body = src
    else:
        try:
            body = cst_lines(src, with_values=(MODE == "cstx"))
        except Exception as e:                      # a parse failure is a verdict
            print(f"  SKIP {fn}: {type(e).__name__}")
            continue
    open(os.path.join(DST, fn[:-3] + ".md"), "w", encoding="utf-8").write(body)
    n += 1
print(f"{MODE}: staged {n} scripts -> {DST}")
