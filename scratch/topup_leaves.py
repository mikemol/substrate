#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Add the missing leaf `import`+`open` for every name a file cites but cannot see.

⚑ After a tip retirement the consumer is rewired against THAT tip's leaf directory
only.  A name the tip RE-EXPORTED from a deeper package (`vlast`, owned by
`Mod/Core/Vlast.agda`, reached through `Mod.Over`) has no owner in that map, so it
silently vanishes ⇒ [NotInScope].  This tops a file up from ANY leaf directory.

USAGE: TIP_PKG=<pkg> topup_leaves.py <file>... [--apply]
"""
import os, re, sys

_SNAPPED = []


def _snapshot_once(path):
    """Arm edit_snapshot on the FIRST write of a run; a no-op thereafter.

    ⚑ This tool rewrites files it read — the shape that made 33 files
    unrecoverable (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop,
    so a per-file `guard` would arm only the first file AND shell out to `git
    stash create` on every iteration; arming once per run is both correct and
    cheap.  Recovery is per-file and MANUAL by design — edit_snapshot never
    restores anything itself.
    """
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        edit_snapshot.guard('topup_leaves', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")
PKG = os.environ["TIP_PKG"]
DIR = os.path.join(ROOT, PKG.replace(".", "/"))


def exports(p):
    out = []
    for l in open(p, encoding="utf-8"):
        if l.strip().startswith("--"):
            continue
        m = re.match(r"^ {2,}([^\s{}()]+)\s*:(?!:)", l)
        if m and m.group(1) not in ("private", "opaque", "field"):
            out.append(m.group(1))
    return out


def arity(p):
    """Number of EXPLICIT binder groups in the leaf's `module Over` telescope.

    ⚑ Leaves of DIFFERENT tiers take different telescopes — `Mod/Core/Vlast.Over`
    is `(CR)(d)(f-lo)` while `Add/NegP.Over` is `(CR)` alone.  Copying the args
    from the FIRST sibling open in the file partially-applied the 3-param leaves
    (`open …Vlast.Over CR`), so `vlast` silently gained `(d)(f-lo)` as leading
    EXPLICIT arguments ⇒ [UnequalTerms] `Vec A (suc n) !=< ℕ` (measured on
    ModZero/Base).  Match the template by ARITY instead.
    """
    for l in open(p, encoding="utf-8"):
        m = re.match(r"^module\s+Over\b(.*?)\s+where\b", l)
        if m:
            return len(re.findall(r"\(", m.group(1)))
    return 0


OWN, ARITY = {}, {}
for f in sorted(os.listdir(DIR)):
    if f.endswith(".agda"):
        ARITY[f[:-5]] = arity(os.path.join(DIR, f))
        for n in exports(os.path.join(DIR, f)):
            OWN.setdefault(n, f[:-5])


def go(path, apply):
    L = open(path, encoding="utf-8").read().split("\n")
    txt = " ".join(re.sub(r"(^|\s)--.*$", "", l) for l in L)
    toks = set(re.findall(r"[^\s(){}\[\];,]+", txt))
    have = {m.group(1) for l in L
            if (m := re.match(r"^\s*open\s+" + re.escape(PKG) + r"\.(\w+)\.Over\b", l))}
    need = sorted({o for n, o in OWN.items()
                   if (n in toks or (n.strip("_") in toks and n != n.strip("_")))} - have)
    if not need:
        return None
    # copy the args from a sibling `open <mod>.Over <args>` of the SAME ARITY
    tmpls = {}
    for l in L:
        m = re.match(r"^(\s*)open\s+\S+\.Over(\s+(?:CR|F₂-CommRing)\b.*)$", l)
        if m:
            a = re.sub(r"\s+(using|public)\b.*$", "", m.group(2))
            tmpls.setdefault(len(a.split()), (m.group(1), a))
    missing = sorted({m for m in need if ARITY.get(m, 1) not in tmpls})
    if missing:
        return [f"<no arity-{ARITY.get(m,1)} sibling open for {m}>" for m in missing]
    oi = max(i for i, l in enumerate(L) if re.match(r"^\s*open\s+\S+\.Over\b", l))
    L[oi + 1:oi + 1] = [f"{tmpls[ARITY.get(m,1)][0]}open {PKG}.{m}.Over"
                        f"{tmpls[ARITY.get(m,1)][1]}" for m in need]
    li = max(i for i, l in enumerate(L) if re.match(r"^\s*(?:open\s+)?import\s", l))
    L[li + 1:li + 1] = [f"import {PKG}.{m}" for m in need]
    if apply:
        _snapshot_once(path)
        open(path, "w", encoding="utf-8").write("\n".join(L))
    return need


if __name__ == "__main__":
    _files = [a for a in sys.argv[1:] if not a.startswith("-")]
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound.
    # `_snapshot_once` sits under `if apply:` inside `go`, so it is consulted after
    # the decision rather than at it, and a run where every file is already
    # complete never reaches it at all.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("topup_leaves", paths=_files)
    apply = "--apply" in sys.argv
    for p in _files:
        r = go(p, apply)
        print(f"{os.path.relpath(p, ROOT)}: {', '.join(r) if r else 'complete'}")
    if not apply:
        print("(dry run — pass --apply to write)")
