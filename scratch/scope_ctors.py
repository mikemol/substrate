#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_ctors.py — the PATTERN-POSITION constructor repairs: the class with no error to drive it.

⚑⚑ SPLIT OUT OF `scope_fix.py` 2026-08-11 (⟡split-1200), AND THIS FAMILY IS DEFINED BY WHAT IT
CANNOT SEE. Every other handler is driven by a message; these three exist because a constructor
that is not in scope produces NO `[NotInScope]` when it appears in a PATTERN — Agda silently
reads it as a fresh pattern VARIABLE, so the clause becomes a CATCH-ALL and the file compiles
clean with the WRONG SEMANTICS.

    fix_missing_ctor(out, t)  the three DOWNSTREAM errors the silent demotion eventually causes
    fix_alias_repoint(out)    `[InvalidPattern] V4.e` — the alias, not the name, is what is stale
    fix_silent_ctors(path)    NO error at all: driven by the DATA, from the pre-strip shape DB

⚑ THE WITNESS IS WHY THEY ARE ONE MODULE. `Rotate.agda` imported `V₄; β; γ; α` but not `e`, so

    rotate e = e ;  rotate α = β ;  rotate β = γ ;  rotate γ = α

collapsed to `rotate _ = _` — EXIT 0, and `rotate α` now reduces to `α`. The failure appeared
only downstream, as `[UnequalTerms] α != β` in TWO consumers whose own imports were perfect.
(β/γ/α got imported because they also appear on right-hand sides and DID error; `e` never did.)
So the same defect surfaces as a warning, as three unrelated type errors, and as nothing at all
— and a reader repairing one of those needs the other two in front of them.

⚑ AND `fix_silent_ctors` IS THE ONE HANDLER THE LOOP CANNOT REACH FROM AN ERROR. `fix()` calls
it off the `-W[no]PatternShadowsConstructor` / `ModuleDoesntExport` warning branch, in the file
the warning NAMES — often a dependency rather than the target. It was written, documented as
THE silent-miscompile repair, and for a while called from nowhere (⚑ T7 ⟡pd-wire-silent-ctors),
which is the dead-capability shape `pycodemod --dead` exists to catch.
"""
import os
import os as _o, sys as _s
import re

_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from scope_edit import add_import
from scope_errors import ALIAS_ERR, CTOR_ERRS
from scope_resolve import owner_from_shape, owner_of_ctor
from scope_source import _alias_names, _is_file_module, _write
from scope_store import consumer_refs, split_qname


def fix_missing_ctor(out, target, dry=False):
    """Bring a pattern-position constructor back into scope. Returns True if it wrote."""
    for rx in CTOR_ERRS:
        m = rx.search(out)
        if not m:
            continue
        name = m.group("name")
        try:
            path = os.path.relpath(m.group("file"), os.getcwd())
        except (IndexError, AttributeError, ValueError):
            path = target
        if not os.path.exists(path):
            path = target
        owner, spell = owner_of_ctor(name, path)
        if not owner:
            continue
        ok, how = add_import(path, owner, spell, dry)
        if ok:
            print(f"    {path}: constructor {name} ← {owner}   [{how}]")
            return True
    return False


def fix_alias_repoint(out, dry=False):
    """Point a stale barrel-alias at the owner the shape DB says the file actually used."""
    m = ALIAS_ERR.search(out)
    if not m:
        return False
    path = os.path.relpath(m.group("file"), os.getcwd())
    alias = m.group("alias")
    try:
        src = open(path).read()
    except OSError:
        return False
    imp = re.search(rf"^(?P<kw>open import|import) (?P<mod>[\w.-]+) as {re.escape(alias)}\b",
                    src, re.M)
    if not imp:
        return False
    owners, unresolved = set(), []
    for n in _alias_names(src, alias):
        o, _ = owner_of_ctor(n, path)                 # ctors first (this is a pattern failure)
        if not o:
            o, _ = owner_from_shape(n, path)
        (owners.add(o) if o else unresolved.append(n))
    if len(owners) != 1:
        print(f"    ! {path}: alias {alias} spans {len(owners)} owner(s) "
              f"{sorted(owners)}; unresolved={unresolved} — NOT repointed")
        return False
    owner = owners.pop()
    if owner == imp.group("mod") or not _is_file_module(owner):
        return False
    new = src[:imp.start()] + f"{imp.group('kw')} {owner} as {alias}" + src[imp.end():]
    if new == src:
        return False
    if not dry:
        _write(path, new)
    print(f"    {path}: alias {alias} → {owner}   [was the stripped barrel {imp.group('mod')}]")
    return True


# ── ⟡paydown-silent-ctors ────────────────────────────────────────────────────────────────────
# THE SILENT MISCOMPILE. A constructor used ONLY in pattern position never errors — Agda binds
# it as a fresh VARIABLE, so the clause becomes a CATCH-ALL and the file compiles clean with the
# WRONG SEMANTICS. Witness: `Rotate.agda` imported `V₄; β; γ; α` but not `e`, so
#     rotate e = e ;  rotate α = β ;  rotate β = γ ;  rotate γ = α
# collapsed to `rotate _ = _` — EXIT 0, but `rotate α` now reduces to `α`. The failure appeared
# only downstream, as `[UnequalTerms] α != β` in TWO consumers whose own imports were perfect.
# (β/γ/α got imported because they also appear on right-hand sides and DID error; `e` never did.)
#
# This cannot be driven by an error, because there is no error. It is driven by the DATA: the
# shape DB records every constructor the file referenced pre-strip. Restore any that the file
# still mentions but no longer imports.
def fix_silent_ctors(path, dry=False):
    """Restore constructors the file USES but no longer imports. Returns #added."""
    try:
        src = open(path).read()
    except OSError:
        return 0
    in_scope = set()
    for u in re.findall(r"using \(([^)]*)\)", src):
        in_scope |= {x.strip() for x in re.split(r"[;\s]+", u) if x.strip()}
    for r in re.findall(r"renaming \(([^)]*)\)", src):
        for pair in r.split(";"):
            q = pair.split(" to ")
            if len(q) == 2:
                in_scope.add(q[1].strip())
    # a bare `open import M` (no narrowing) brings everything — do not second-guess it
    if re.search(r"^open import [\w.-]+\s*$", src, re.M):
        return 0
    added = 0
    for qn in sorted(consumer_refs(path)):
        mod, extra = split_qname(qn)
        if not mod or len(extra) != 2:               # want module · TYPE · constructor
            continue
        ctor = extra[-1]
        if ctor in in_scope or ctor.startswith("_"):
            continue
        # only if the file still MENTIONS it — never import something unused
        if not re.search(rf"(?<![\w.-]){re.escape(ctor)}(?![\w])", src):
            continue
        ok, how = add_import(path, mod, ctor, dry)
        if ok:
            print(f"    {path}: SILENT ctor {ctor} ← {mod}   [{how}]")
            in_scope.add(ctor)
            added += 1
    return added
