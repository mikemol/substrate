#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Replace the FromCommRing PREFIX SLICES with DIRECT, NON-PUBLIC part opens.

⟡public-policy: a module re-exports ONLY what it DEFINES.  A prefix slice is a
wholesale re-export by construction (`open …Laws.X.Over … public`), so the slice
design mints one public-ratchet key per part per slice — the very conduit the
policy exists to remove.  It also over-binds: a slice is a PREFIX, so a consumer
that needs `_*P_` (P0) and `*P-comm` (P9) pays for P1..P8 it never cites.

THE DIRECT FORM is both policy-clean and cheaper (measured: `Graded.Defs.Over
<ops+laws>` 67MB vs the slice's 70, vs the retired tip's ~104):

    open …FromCommRing.Over CR                  -- the 14 flat ops, NON-public
    open …Graded.Defs.Over <the 14 args>        -- ONLY the parts that OWN
    open …Graded.Laws.Comm.Over <the 14 args>   -- the names this file cites

Each Laws link already binds its own ancestors NON-publicly (⟡graded-laws-
noreexport), so a consumer opens the OWNING parts — a SET, not a prefix.

USAGE: fcr_direct.py <file>...            (dry run)
       fcr_direct.py <file>... --apply
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
        edit_snapshot.guard('fcr_direct', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")
PKG = "Substrate.Algebra.Polynomial.Graded"
FCR = PKG + ".FromCommRing"
ARGS = ("_+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ "
        "*-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ")

PARTS = [("Defs", PKG + ".Defs", "Defs.agda")] + [
    (n, PKG + ".Laws." + n, "Laws/" + n + ".agda") for n in
    ["Nth", "Conv", "Distrib", "Scalar", "Basis", "Linear", "Monomial",
     "MonomialDelta", "Comm", "Assoc", "AssocMono", "AssocLinearP",
     "AssocLinearQ", "AssocLinearR", "AssocMain"]]
GDIR = os.path.join(ROOT, PKG.replace(".", "/"))


def part_exports(rel):
    out = []
    for l in open(os.path.join(GDIR, rel), encoding="utf-8"):
        if l.lstrip().startswith("--"):
            continue
        m = re.match(r"^ {2,}([^\s{}()]+)\s*:(?!:)", l)
        if m and m.group(1) not in ("private", "opaque", "field"):
            out.append(m.group(1))
        m = re.match(r"^\s*open\s+\S+\.Over\b.*\bpublic\s+using\s*\((.*?)\)", l)
        if m:
            out += [x.strip() for x in m.group(1).split(";") if x.strip()]
    return out


OWN = {}
for i, (_, _, rel) in enumerate(PARTS):
    for n in part_exports(rel):
        OWN.setdefault(n, i)

SLICE = re.compile(r"^(?P<ind>\s*)open\s+" + re.escape(FCR) +
                   r"\.(?P<slice>\w+)\.Over\b(?P<rest>.*)$")
IMPSL = re.compile(r"^\s*import\s+" + re.escape(FCR) + r"\.\w+\s*$")


def split_rest(rest):
    cmt = ""
    m = re.search(r"\s--.*$", rest)
    if m:
        cmt, rest = m.group(0), rest[:m.start()]
    pub = ""
    if re.search(r"\s+public\s*$", rest):
        pub, rest = " public", re.sub(r"\s+public\s*$", "", rest)
    use = None
    m = re.search(r"\s+using\s*\((.*)\)\s*$", rest)
    if m:
        use = [x.strip() for x in m.group(1).split(";") if x.strip()]
        rest = rest[:m.start()]
    return rest.rstrip(), use, pub, cmt


def owners(lines):
    """The SET of part indices owning names this file cites."""
    txt = " ".join(re.sub(r"(^|\s)--.*$", "", l) for l in lines)
    toks = set(re.findall(r"[^\s(){}\[\];,]+", txt))
    return {i for n, i in OWN.items()
            if n in toks or (n.strip("_") in toks and n != n.strip("_"))}


def rewrite(path, apply):
    lines = open(path, encoding="utf-8").read().split("\n")
    if not any(SLICE.match(l) for l in lines):
        return None
    need = sorted(owners(lines))
    out = []
    for l in lines:
        m = SLICE.match(l)
        if not m:
            if IMPSL.match(l):
                continue                    # slice imports are replaced below
            out.append(l)
            continue
        ind = m.group("ind")
        args, use, pub, cmt = split_rest(m.group("rest"))
        # the adapter (its 14 names feed every part application)
        adpt = [n for n in (use or []) if n not in OWN]
        if use is None:
            out.append(f"{ind}open {FCR}.Over{args}{cmt}")
        elif adpt:
            out.append(f"{ind}open {FCR}.Over{args} using ({'; '.join(adpt)}){cmt}")
        else:
            out.append(f"{ind}open {FCR}.Over{args}{cmt}")
        for i in need:
            names = None if use is None else [n for n in use if OWN.get(n) == i]
            if names is not None and not names:
                continue
            u = f" using ({'; '.join(names)})" if names else ""
            out.append(f"{ind}open {PARTS[i][1]}.Over {ARGS}{u}")
    # imports: the adapter + each owning part, placed where the slice import was
    imps = [f"import {FCR}"] + [f"import {PARTS[i][1]}" for i in need]
    have = {l.strip() for l in out}
    li = max((i for i, l in enumerate(out)
              if re.match(r"^\s*(?:open\s+)?import\s", l)), default=0)
    out[li + 1:li + 1] = [x for x in imps if x not in have]
    if apply:
        _snapshot_once(path)
        open(path, "w", encoding="utf-8").write("\n".join(out))
    return [PARTS[i][0] for i in need] or ["<adapter only>"]


if __name__ == "__main__":
    # ⚑ ONE ACT: state the intent AND take the snapshot, BEFORE `apply` is bound.
    # `_snapshot_once` fires at the first PENDING WRITE, which a run that matches
    # no slice never reaches, and it is consulted after the apply/dry decision
    # rather than at it. `paths=` is load-bearing — `_copy_untracked(paths)` is the
    # only mechanism reaching an untracked Agda leaf.
    _es_paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("fcr_direct", paths=_es_paths)
    apply = "--apply" in sys.argv
    for p in [a for a in sys.argv[1:] if a != "--apply"]:
        r = rewrite(p, apply)
        if r is not None:
            print(f"{os.path.relpath(p, ROOT)}: {', '.join(r)}")
    if not apply:
        print("(dry run — pass --apply to write)")
