#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Repair ORPHANED `using`/`renaming` continuations.

An earlier dead-import sweep deleted import HEADS and left their directive
continuations dangling, which Agda then attaches to the PRECEDING import —
producing a statement with TWO `using` clauses (illegal).  That duplicate is
the precise, checkable signature of the orphan.

The continuation IS the demand declaration: it names exactly what the deleted
import supplied.  So we READ it before removing it (deleting it first is how
this session lost eight bindings in one file), resolve each name to its
definer leaf, and emit ban-compliant bare `open import`s.  A rename TARGET
(`apply to applyₛ`) becomes the plain name, and its use sites are rewritten —
under the no-renaming ban the alias has no reason to exist.

Permutation-guarded like every other mutation: the body rewrite is the only
non-permutation change and it is a pure name substitution.
"""
import re,sys,glob
sys.path.insert(0,"scratch")
from agda_defs import def_index
import os as _os, sys as _sys
from agda_imports import importable as _importable  # THE self-import predicate (never re-derive)
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import _span_end   # THE statement-span authority (agda_lex-backed); never re-derive

IMP=re.compile(r"^(open\s+import|import)\s+(\S+)")

def find_orphan(lines):
    """(start,end) of the second `using` onward in a statement, or None."""
    i=0
    while i<len(lines):
        if IMP.match(lines[i]):
            j=i+1
            j = _span_end(lines, j - 1)
            seen=0
            for k in range(i,j):
                seen+=len(re.findall(r"\busing\b",lines[k]))
                if seen>=2: return k,j
            i=j
        else: i+=1
    return None

def repair(path,family=None,arg="",apply=False):
    """family: restrict definer resolution to this module prefix (the deleted
    import's own family — a name demanded FROM it is provided BY one of its
    leaves).  arg: module argument the leaves take (e.g. `Axis`)."""
    lines=open(path).read().split("\n")
    o=find_orphan(lines)
    if not o: return False,"no orphan"
    a,b=o
    text=" ".join(lines[a:b])
    renames={s.strip(";)("):d.strip(";)(")
             for s,d in re.findall(r"(\S+)\s+to\s+(\S+)",text)}
    demand=[d for d in re.findall(r"[^\s;()]+",
            re.sub(r"\b(using|renaming|hiding|public)\b","",text)) if d!="to"]
    demand=[d for d in demand if d not in renames.values()]
    idx=def_index(); mods=set(); unresolved=[]
    for n in demand:
        c=idx.get(n,[])
        if family: c=[m for m in c if m.startswith(family)]
        if len(c)==1: mods.add(c[0])
        elif c: unresolved.append((n,c))
        else: unresolved.append((n,[]))
    body="\n".join(lines)
    # ⚑ `_importable` is the shared self-import guard (agda_imports).  A rewire
    # resolves a name to its definer; when the file BEING rewired IS that definer,
    # the naive answer is itself and Agda hard-errors [CyclicModuleDependency],
    # which reads like a real structural cycle.  Measured 10× in one arc.
    new=[f"open import {m}"+(f" {arg}" if arg else "")
         for m in sorted(mods)
         if f"open import {m}" not in body and _importable(path, m)]
    out=lines[:a]+new+lines[b:]
    txt="\n".join(out)
    for src,dst in renames.items(): txt=re.sub(r"(?<![\w'-])"+re.escape(dst)+r"(?![\w'-])",src,txt)
    # ⚑ THE WRITE IS NOW GATED ON THE STATED INTENT.  It used to be UNCONDITIONAL:
    # this tool had no `--dry-run`, so every invocation wrote.  The `guard` that
    # stood here was correct where it ran but sat immediately above the write,
    # which is after the decision rather than at it — and there was no decision to
    # consult until the arm below existed.  A stated `--dry-run` that wrote anyway
    # would be worse than the unstated run: the caller states the safe intent and
    # is disobeyed.
    if not apply:
        return True,f"WOULD rewrite: orphan({b-a}) -> {len(new)} leaf import(s)  (dry run)"
    open(path,"w").write(txt)
    msg=f"orphan({b-a}) -> {len(new)} leaf import(s)"
    if renames: msg+=f", un-renamed {len(renames)}"
    if unresolved: msg+=f"; UNRESOLVED {unresolved}"
    return True,msg

if __name__=="__main__":
    args=[a for a in sys.argv[1:] if not a.startswith("--")]
    fam=next((a.split("=",1)[1] for a in sys.argv[1:] if a.startswith("--family=")),None)
    arg=next((a.split("=",1)[1] for a in sys.argv[1:] if a.startswith("--arg=")),"")
    if not args:                       # census mode
        n=0
        for p in sorted(glob.glob("agda/Substrate/**/*.agda",recursive=True)):
            if find_orphan(open(p).read().split("\n")): print("  ",p[15:]); n+=1
        print(f"{n} file(s) with a duplicated-`using` orphan")
    else:
        # ⚑ ONE ACT: state the intent AND snapshot, before any write is decided.
        # The census branch above is read-only and stays that way — but the
        # contract has NO read-path exemption, so the gate sits on the branch that
        # can write rather than at module top, where it would refuse a bare census
        # run.  ⚑ That is a placement judgement, not an exemption: `--census` here
        # is a DIFFERENT invocation shape (no positional args at all), and the
        # gate governs the invocation that names targets.
        _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
        import edit_snapshot as _es
        _es.require_at_entry("fix_orphan_using", paths=args)
        apply = "--apply" in sys.argv
        for p in args: print(*repair(p,fam,arg,apply),p)
