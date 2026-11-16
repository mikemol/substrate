#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Project the memory-tooling .py files into a memory-shaped .md corpus, so the
banding pipeline (synth_apex/synth_scale) can be run ON the tooling that manages
the memories.

Each script -> one <name>.md with the frontmatter the pipeline expects
(description is read by grammar_phrase_lattice.full()). Body = docstring +
identifier/comment tokens, so the Sequitur grammar sees the code's OWN
vocabulary, not just its prose.
"""
import ast
import io
import os
import re
import sys
import tokenize

SRC = "/home/mikemol/github/substrate/catalog/memory"
DST = sys.argv[1]


def split_ident(name):
    """snake_case / CamelCase -> words. The grammar tokenizes [a-z][a-z-]{2,}."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    return " ".join(p for p in re.split(r"[^A-Za-z0-9]+", s) if p)


def body_tokens(src):
    """Identifiers + comment words, in source order (order matters: Sequitur
    learns sequential structure)."""
    out = []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError):
        return ""
    for t in toks:
        if t.type == tokenize.NAME:
            out.append(split_ident(t.string))
        elif t.type == tokenize.COMMENT:
            out.append(re.sub(r"[^A-Za-z0-9 ]+", " ", t.string.lstrip("# ")))
        elif t.type == tokenize.STRING and len(t.string) < 400:
            out.append(re.sub(r"[^A-Za-z0-9 ]+", " ", t.string))
    return " ".join(out)


os.makedirs(DST, exist_ok=True)
n = 0
for fn in sorted(os.listdir(SRC)):
    if not fn.endswith(".py"):
        continue
    src = open(os.path.join(SRC, fn), encoding="utf-8").read()
    try:
        doc = ast.get_docstring(ast.parse(src)) or ""
    except SyntaxError:
        doc = ""
    stem = fn[:-3]
    # description = the docstring's first line, the way a memory's frontmatter reads
    first = (doc.strip().splitlines() or [stem])[0]
    first = first.replace('"', "'")[:300]
    out = [
        "---",
        f"name: {stem}",
        f'description: "{first}"',
        "metadata:",
        "  type: tooling",
        "---",
        "",
        doc,
        "",
        body_tokens(src),
        "",
    ]
    open(os.path.join(DST, stem + ".md"), "w", encoding="utf-8").write("\n".join(out))
    n += 1
print(f"projected {n} scripts -> {DST}")
