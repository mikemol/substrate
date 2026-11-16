#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Resolve `[AmbiguousName]` by DROPPING the import that supplies the losing name.

⟡public-policy.  Removing a `using` filter widens scope, so two modules that
both export a name now clash.  The filter was MASKING the collision, not
preventing it — and the ban forbids re-adding it.  Where the file uses only ONE
of the two providers, the other import is simply DEAD: declining to import is
ban-compliant, and it is the fix the compiler's own diagnosis points at.

WHY THE COMPILER IS THE RIGHT INSTRUMENT.  A token-based use-scan cannot tell
which provider supplies an occurrence of `_<_` — every occurrence is ambiguous,
which is the error.  But Agda's `[AmbiguousName]` block names the FILE, the
NAME, and BOTH providers.  This tool reads that, and decides by asking a
question the scan CAN answer: does the file use any OTHER name from the
candidate provider?  Definition-per-file decomposition makes this sharp — a Fin
leaf exports exactly one name, so "no other name used" means the whole import
is dead.

REFUSE-ON-AMBIGUITY.  If both providers have other names in use, or neither
does, the tool prints and declines — it never guesses.  The build arbitrates:
each drop is isolate-typechecked and REVERTED if the name goes out of scope
(which is the proof that the file genuinely needed the dropped side, and the
honest fix is then a rename at source).
"""
import re, sys, os, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agda_defs import def_index

from agda_imports import _span_end   # THE statement-span authority (agda_lex-backed); never re-derive

HEAD = re.compile(r"^(\S+\.agda):(\d+)\.(\d+)-[\d.]+:?\s*error: \[AmbiguousName\]")
NAME = re.compile(r"^Ambiguous name (\S+)\. It could refer to")
PROV = re.compile(r"^\s{2}([\w.]+)\.([^\s]+) bound at")


def parse(log):
    """(file, line, col, ambiguous-name, [providers]) per AmbiguousName block."""
    out, lines = [], open(log, errors="replace").read().split("\n")
    for i, l in enumerate(lines):
        h = HEAD.match(l)
        if not h:
            continue
        nm = NAME.match(lines[i + 1]) if i + 1 < len(lines) else None
        if not nm:
            continue
        provs = []
        for l2 in lines[i + 2:i + 14]:
            p = PROV.match(l2)
            if p and p.group(2) == nm.group(1):
                provs.append(p.group(1))
            elif l2.startswith(nm.group(1) + " is in scope"):
                break
        if len(provs) == 2:
            out.append((h.group(1), int(h.group(2)), int(h.group(3)), nm.group(1), provs))
    return out


def qualify_at(path, line, col, name, owner):
    """Prefix the ONE reported occurrence with its owner: `head r` → `RealTrace.head r`.

    The other repair (drop the losing import) presupposes both providers are
    IMPORTED MODULES.  When one is a RECORD FIELD — `RealTrace.head` vs
    `Foundation.Vec.head` — there is no import to drop: the file genuinely needs
    Vec (for the type and its constructors) and genuinely needs the record.  So
    name the field at its owner, which is a record projection, not an import
    alias, and therefore not `as`-alias debt.

    (The STRUCTURAL fix is to decompose Vec, so a `Vec.Vec` leaf never exports
    `head` at all.  This is the local repair until that lands.)
    """
    L = open(path).read().split("\n")
    i, c = line - 1, col - 1
    if i >= len(L) or L[i][c:c + len(name)] != name:
        return False
    L[i] = L[i][:c] + owner + "." + name + L[i][c + len(name):]
    # ⚑ recoverable-by-construction: this rewrites a file it read.
    import edit_snapshot as _es; _es.guard("fix_ambiguous_import", [path])
    open(path, "w").write("\n".join(L))
    return True


def body_tokens(src):
    """Tokens OUTSIDE import statements — an import must not keep itself alive."""
    L = src.split("\n")
    keep, i = [], 0
    while i < len(L):
        if re.match(r"^(open\s+import|import)\s+\S+", L[i]):
            i += 1
            i = _span_end(L, i - 1)
            continue
        keep.append(L[i]); i += 1
    t = set(re.findall(r"[^\s(){}\[\];,]+", " ".join(keep)))
    return t | {x.strip("_") for x in list(t)}


def drop_import(path, mod):
    L = open(path).read().split("\n")
    out, i, n = [], 0, 0
    while i < len(L):
        m = re.match(r"^(open\s+import|import)\s+(\S+)", L[i])
        if m and m.group(2) == mod:
            i = _span_end(L, i); n += 1; continue
        out.append(L[i]); i += 1
    open(path, "w").write("\n".join(out))
    return n


def check(path):
    rel = os.path.relpath(path, "agda")
    r = subprocess.run(["../scripts/membudget", "run", "384", "amb", "--",
                        "agda", "--safe", "--without-K", "-i.", rel],
                       cwd="agda", capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr


def scan(idx, root="agda/Substrate"):
    """Find every collision STATICALLY, instead of one build round at a time.

    ⚠ MEASURED AND REJECTED AS THE PRIMARY MODE — kept only as a census.
    The idea was to beat the build-round latency (a log reports only the errors
    the build REACHED, and each fix unblocks more).  But co-importing two
    providers is NOT an ambiguity: Agda resolves most by target type, so this
    scan reported 1344 candidates where the build reports ~10, and REFUSED four
    fifths of them.  A worse proxy than the instrument it was meant to replace.
    USE THE BUILD LOG; this mode is for measuring the collision surface only.
    """
    multi = {n: ms for n, ms in idx.items() if len({m for m in ms if m.startswith("Substrate")}) > 1}
    out = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".agda"):
                continue
            p = os.path.join(dirpath, fn)
            src = open(p, errors="replace").read()
            imported = {m.group(1) for m in re.finditer(r"^(?:open\s+import|import)\s+(\S+)", src, re.M)}
            for n, ms in multi.items():
                both = sorted(set(ms) & imported)
                if len(both) == 2 and n.strip("_") in body_tokens(src):
                    out.append((p, n, both))
    return out


if __name__ == "__main__":
    log = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
    idx = def_index()
    if "--scan" in sys.argv:
        cases = scan(idx)
        print(f"# static scan: {len(cases)} latent collision(s)")
    elif log:
        cases = parse(log)
    else:
        print(__doc__); print("usage: fix_ambiguous_import.py (<build.log> | --scan) [--apply]"); sys.exit(2)
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound, and AFTER
    # `cases` resolves — argv[0] here is a build LOG (or `--scan`, which names no
    # file at all), so the rewritten paths are only knowable from the case list.
    # ⚑⚑ AND THIS TOOL HAD TWO WRITES AND ONE GUARD.  `qualify_at` is armed;
    # `drop_import` writes with no snapshot at all, in a tool the `snapshot-guard`
    # census scores as ARMED because that census asks whether `edit_snapshot` is
    # mentioned anywhere in the file. An entry snapshot covers both by construction.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("fix_ambiguous_import", paths=sorted({c[0] for c in cases}))
    apply = "--apply" in sys.argv
    for path, line, col, name, provs in cases:
        src = open(path).read()
        toks = body_tokens(src)
        imported = [m for m in provs
                    if re.search(r"^(open\s+import|import)\s+" + re.escape(m) + r"\b", src, re.M)]
        # A provider that is not an imported MODULE is a record/nested scope: it
        # has no import to drop, so name the field at its owner instead.
        if len(imported) == 1 and len(provs) == 2:
            owner = [m for m in provs if m not in imported][0]
            print(f"{'QUALIFY' if apply else 'WOULD QUALIFY'} {path}:{line}:{col}  {name} -> {owner}.{name}")
            if apply and qualify_at(path, line, col, name, owner):
                ok, _ = check(path)
                print(f"  isolate-check {'OK' if ok else 'still failing (re-run on the next log)'}")
            continue
        # names each candidate supplies BESIDES the ambiguous one, that the file uses.
        # An operator has TWO spellings (`_<_` in a signature, bare `<` in an infix
        # clause) and the def index records both — exclude both, or the ambiguous
        # name itself reads as "another name in use" and every case REFUSES.
        alias = {name, name.strip("_")}
        other = {m: {n for n, ms in idx.items() if m in ms and n not in alias} & toks for m in imported}
        dead = [m for m, o in other.items() if not o]
        if len(dead) != 1:
            print(f"REFUSE {path}  {name}  -> {other} (not exactly one dead provider)")
            continue
        m = dead[0]
        print(f"{'DROP  ' if apply else 'WOULD DROP'} {path}  {name}: dead import {m}")
        if not apply:
            continue
        before = src
        if not drop_import(path, m):
            continue
        ok, out = check(path)
        if not ok and "NotInScope" in out:
            open(path, "w").write(before)
            print(f"  REVERTED — {path} genuinely needs {m}; rename at source instead")
        else:
            print(f"  isolate-check {'OK' if ok else 'still failing (a DIFFERENT error — kept)'}")
