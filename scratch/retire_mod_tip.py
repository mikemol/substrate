#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Retire the Graded.Mod TIP: rewire every consumer to the leaf that OWNS the
name it uses, then the tip can be deleted.

WHY (⟡cap64-mod-tip): a module application COPIES, so opening the 22-definition
tip to reach one lemma charges the consumer for all 22 (Mod measured 127MB
unsealed / 114 sealed / 103 as a pure barrel — all over the -M64m cap, while
every LEAF measures 84-104). Binding at the owner is the paydown; the tip is
then dead surface and is deleted (the BezoutFold/Base precedent).

THE MAP is derived from the leaves themselves (a name's owner is the leaf that
DEFINES it), never hand-written.

USAGE: retire_mod_tip.py <file>...            (dry run)
       retire_mod_tip.py <file>... --apply
       retire_mod_tip.py <file>... --alias <A> [--apply]
              # THE REPAIR PATH FOR A HALF-DONE RETIREMENT: the tip IMPORT is
              # already gone — dropped, perhaps wrongly — but qualified
              # `A.Over.<name>` sites remain, so there is no import line left
              # for the normal pass to recover the alias from. Naming the alias
              # directly lets it rewrite those sites to the owning leaf and add
              # the imports they now need. ⚑ Without it such a file reports
              # `no tip import` and is silently skipped, which reads as "already
              # clean" for a file that is actually broken.
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
        edit_snapshot.guard('retire_mod_tip', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")
PKG  = os.environ.get("TIP_PKG", "Substrate.Algebra.Polynomial.Graded.Mod")
DIR  = os.path.join(ROOT, PKG.replace(".", "/"))


def exports(path):
    """Names a leaf's `module Over` defines.

    ⚑ Indent is 2 for a bare definition but 4 once it is wrapped in `opaque`
    (seal-after-split). A 2-space-only match silently loses every SEALED name,
    so the consumer never gets that leaf and fails [NotInScope] — measured on
    Div, where `snoc-+P` vanished from the map after sealing.
    """
    out = []
    for l in open(path, encoding="utf-8"):
        if l.strip().startswith("--"):
            continue
        m = re.match(r"^ {2,}([^\s{}()]+)\s*:(?!:)", l)
        if m and m.group(1) not in ("private", "opaque"):
            out.append(m.group(1))
    return out


def owner_map():
    own = {}
    for f in sorted(os.listdir(DIR)):
        if f.endswith(".agda"):
            for n in exports(os.path.join(DIR, f)):
                own.setdefault(n, f[:-5])
    return own


OWN = owner_map()
# An operator is written `_*P_` at its definition but `*P` at an infix use site
# (the H2 class) — probe both spellings.
ALIASES = {n.strip("_"): n for n in OWN if n != n.strip("_")}

TIP_IMPORT = re.compile(
    r"^(?P<pre>\s*)(?:open\s+)?import\s+" + re.escape(PKG) + r"(?:\s+as\s+(?P<alias>\S+))?\s*$")
# NB: the argument list contains hyphenated names (`f-lo`), so the args group
# must NOT be "anything but a hyphen" — split the trailing ` --` comment off
# explicitly instead.
TIP_OPEN = re.compile(
    r"^(?P<ind>\s*)open\s+(?:" + re.escape(PKG) + r"|(?P<alias>[A-Za-z_][\w']*))\.Over\b"
    r"(?P<rest>.*)$")


def split_rest(rest):
    """`rest` -> (args, ' public'|'', ' -- comment'|'')."""
    cmt = ""
    m = re.search(r"\s--.*$", rest)
    if m:
        cmt, rest = m.group(0), rest[:m.start()]
    pub = ""
    if re.search(r"\s+public\s*$", rest):
        pub, rest = " public", re.sub(r"\s+public\s*$", "", rest)
    return rest.rstrip(), pub, cmt


def qual_uses(lines, alias):
    """`Alias.Over.name` sites — a qualified use with NO `open` at all.

    ⚑ Missed by a first-dot split (`Div.Over.b-poly` -> `Over.b-poly`), so the
    file looked like it cited nothing and its import was dropped as dead. That
    broke EEATrace (Div) and FuelEEA (Mod); FuelEEA's breakage was itself masked
    because it sat behind Div's failure in the `-k` census.
    """
    if not alias:
        return {}
    rx = re.compile(r"(?<![^\\s(){}\\[\\];,])" + re.escape(alias) + r"\.Over\.([^\s(){}\[\];,]+)")
    out = {}
    for l in lines:
        if l.lstrip().startswith("--"):
            continue
        for n in rx.findall(l):
            if n in OWN:
                out[n] = OWN[n]
    return out


MOD_ALIAS = re.compile(r"^(?P<ind>\s*)module\s+(?P<name>\S+)\s*=\s*" + re.escape(PKG) +
                       r"\.Over\b(?P<rest>.*)$")


def mod_alias_sites(lines):
    """`module X = <PKG>.Over <args>` bindings, used as `X.name`.

    ⚑ THE THIRD REFERENCE FORM.  `needed()` sees no bare name through a module
    ALIAS, so the file reads as "uses nothing" and its import is dropped as dead
    — leaving the alias dangling ([NoSuchModule]).  A module alias binds ONE
    module, so when the names it serves span several leaves it must become one
    alias PER LEAF (the QuotF2/{Core,Expand,Seam} hand-repair, mechanized).
    """
    out = []
    for i, l in enumerate(lines):
        m = MOD_ALIAS.match(l)
        if not m:
            continue
        nm = m.group("name")
        rx = re.compile(r"(?<![^\\s(){}\\[\\];,])" + re.escape(nm) + r"\.([^\s(){}\[\];,]+)")
        by = {}
        for x in lines:
            if x.lstrip().startswith("--"):
                continue
            for n in rx.findall(x):
                o = OWN.get(n) or OWN.get(ALIASES.get(n, ""))
                if o:
                    by.setdefault(o, set()).add(n)
        out.append((i, m, by))
    return out


def needed(lines, alias):
    """Owners whose names this file actually mentions (comments excluded)."""
    txt = " ".join(re.sub(r"(^|\s)--.*$", "", l) for l in lines)
    toks = set(re.findall(r"[^\s(){}\[\];,]+", txt))
    # a qualified use `M.foo` names foo too — and `M.Over.foo` names foo as its
    # LAST component, not its second.
    if alias:
        toks |= {t.split(".", 1)[1] for t in toks
                 if t.startswith(alias + ".") and "." in t}
        toks |= {t.rsplit(".", 1)[1] for t in toks
                 if t.startswith(alias + ".") and "." in t}
    hit = set()
    for n, mod in OWN.items():
        if n in toks or (n.strip("_") in toks and n != n.strip("_")):
            hit.add(mod)
    return sorted(hit)


def rewrite(path, apply, forced_alias=None):
    lines = open(path, encoding="utf-8").read().split("\n")

    # --alias: the tip import is already gone (dropped, perhaps wrongly) but
    # qualified `Alias.Over.name` sites remain. Repair those directly.
    if forced_alias:
        q = qual_uses(lines, forced_alias)
        if not q:
            return None
        out = []
        for l in lines:
            for n, mod in q.items():
                l = re.sub(r"(?<![^\\s(){}\\[\\];,])" + re.escape(forced_alias) + r"\.Over\." + re.escape(n) + r"\b",
                           f"{PKG}.{mod}.Over.{n}", l)
            out.append(l)
        have = {l.split(f"import {PKG}.", 1)[1].strip()
                for l in out if l.startswith(f"import {PKG}.")}
        miss = [m for m in sorted(set(q.values())) if m not in have]
        if miss:
            li = max(i for i, l in enumerate(out) if re.match(r"(?:open )?import ", l))
            out[li + 1:li + 1] = [f"import {PKG}.{m}" for m in miss]
        if apply:
            _snapshot_once(path)
            open(path, "w", encoding="utf-8").write("\n".join(out))
        return [f"<qualified: {', '.join(sorted(set(q.values())))}>"]

    alias = None
    imp_i = None
    for i, l in enumerate(lines):
        m = TIP_IMPORT.match(l)
        if m:
            imp_i, alias = i, m.group("alias")
            break
    if imp_i is None:
        # TOP-UP: an already-rewired file whose owner map has since GROWN (e.g.
        # the map was built before the leaves were sealed, so every sealed name
        # was missing from it) needs the missing leaves ADDED beside the ones
        # already there — never a re-expansion.
        have = {l.split(f"import {PKG}.", 1)[1].strip()
                for l in lines if l.startswith(f"import {PKG}.")}
        if have:
            miss = [m for m in needed(lines, None) if m not in have]
            if not miss:
                return None
            li = max(i for i, l in enumerate(lines) if l.startswith(f"import {PKG}."))
            oi = max(i for i, l in enumerate(lines)
                     if re.match(r"\s*open\s+" + re.escape(PKG) + r"\.\w+\.Over\b", l))
            ind, rest = re.match(r"^(\s*)open\s+\S+\.Over(.*)$", lines[oi]).groups()
            args, pub, _ = split_rest(rest)
            out = list(lines)
            out[oi + 1:oi + 1] = [f"{ind}open {PKG}.{m}.Over{args}{pub}" for m in miss]
            out[li + 1:li + 1] = [f"import {PKG}.{m}" for m in miss]
            if apply:
                open(path, "w", encoding="utf-8").write("\n".join(out))
            return [f"<topped up: {', '.join(miss)}>"]
        # IDEMPOTENT RE-RUN: the tip import is already retired but a tip `open`
        # may remain (a partially-applied pass). Recover the alias from the
        # dangling open and finish the opens without touching the imports.
        for l in lines:
            m = TIP_OPEN.match(l)
            # ⚑ `import … as F` is NOT matched by `import \S*\bF\b` — `\S*`
            # cannot cross the space. Getting this wrong made the pass expand
            # `open F.Over` (FromCommRing) instead of `open M.Over` in every
            # tracked consumer of Mod. Match the `as` clause explicitly.
            if m and (m.group("alias") is None
                      or not any(re.match(r"\s*(?:open\s+)?import\s+\S+\s+as\s+"
                                          + re.escape(m.group("alias")) + r"\s*$", x)
                                 for x in lines)):
                alias = m.group("alias")
                break
        else:
            return None

    # the tip's `open …Over` sites (via the alias, or fully qualified)
    open_ix = [i for i, l in enumerate(lines)
               if (m := TIP_OPEN.match(l)) and (m.group("alias") in (None, alias))]

    if forced_alias:
        alias = forced_alias
    q = qual_uses(lines, alias)
    if q:
        # rewrite `Alias.Over.name` -> `PKG.<Leaf>.Over.name` and add imports
        out = []
        for l in lines:
            for n, mod in q.items():
                l = re.sub(r"(?<![^\\s(){}\\[\\];,])" + re.escape(alias) + r"\.Over\." + re.escape(n) + r"\b",
                           f"{PKG}.{mod}.Over.{n}", l)
            out.append(l)
        have = {l.split(f"import {PKG}.", 1)[1].strip()
                for l in out if l.startswith(f"import {PKG}.")}
        miss = [m for m in sorted(set(q.values())) if m not in have]
        if miss:
            li = max(i for i, l in enumerate(out) if re.match(r"(?:open )?import ", l))
            out[li + 1:li + 1] = [f"import {PKG}.{m}" for m in miss]
        if apply:
            open(path, "w", encoding="utf-8").write("\n".join(out))
        return [f"<qualified: {', '.join(sorted(set(q.values())))}>"]

    # ── the module-ALIAS form, rewritten to one alias per OWNING leaf ────────
    msites = mod_alias_sites(lines)
    if msites:
        out = list(lines)
        extra_imports = set()
        for i, m, by in reversed(msites):
            ind, nm, rest = m.group("ind"), m.group("name"), m.group("rest")
            args, pub, cmt = split_rest(rest)
            blk, first = [], True
            for leaf, names in sorted(by.items()):
                al = nm if first else f"{nm}_{leaf}"
                first = False
                blk.append(f"{ind}module {al} = {PKG}.{leaf}.Over{args}{cmt if blk == [] else ''}")
                extra_imports.add(leaf)
                if al != nm:
                    for n in names:
                        for j, x in enumerate(out):
                            if x.lstrip().startswith("--"):
                                continue
                            out[j] = re.sub(r"(?<![^\\s(){}\\[\\];,])" + re.escape(nm) + r"\." + re.escape(n) +
                                            r"(?![^\s(){}\[\];,])", f"{al}.{n}", out[j])
            out[i:i + 1] = blk or [f"{ind}-- (dead module alias {nm} dropped)"]
        if imp_i is not None:
            out[imp_i:imp_i + 1] = [f"import {PKG}.{l}" for l in sorted(extra_imports)]
        if apply:
            open(path, "w", encoding="utf-8").write("\n".join(out))
        return [f"<module-alias: {', '.join(sorted(extra_imports))}>"]

    mods = needed(lines, alias)
    if not mods:
        # DEAD TIP IMPORT: the file imports the tip and cites none of its names.
        # A module application COPIES, so a dead import is not free — it charges
        # the consumer the tip's whole elaboration. Drop it (the ⟡p1-div-strip
        # class); only ever when there is no `open` of it either.
        if imp_i is not None:
            # A dead `open <tip>.Over …` is worse than a dead import: the
            # APPLICATION is what copies. Drop the open sites with it.
            drop = set(open_ix) | {imp_i}
            if apply:
                open(path, "w", encoding="utf-8").write(
                    "\n".join(l for i, l in enumerate(lines) if i not in drop))
            return [f"<dead: dropped import + {len(open_ix)} open(s)>"]
        return None

    out = list(lines)
    for i in reversed(open_ix):
        m = TIP_OPEN.match(lines[i])
        ind = m.group("ind")
        args, pub, cmt = split_rest(m.group("rest"))
        block = [f"{ind}open {PKG}.{mod}.Over{args}{pub}" for mod in mods]
        block[0] += cmt
        out[i:i + 1] = block
    if imp_i is not None:
        out[imp_i:imp_i + 1] = [f"import {PKG}.{mod}" for mod in mods]

    if apply:
        open(path, "w", encoding="utf-8").write("\n".join(out))
    return mods


if __name__ == "__main__":
    argv = [a for a in sys.argv[1:] if a != "--apply" and a != "--dry-run"]
    forced = None
    if "--alias" in argv:
        i = argv.index("--alias"); forced = argv[i + 1]; del argv[i:i + 2]
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound.
    # ⚑⚑ AND THIS TOOL HAD FOUR WRITES AND ONE `_snapshot_once`.  `rewrite` writes
    # under `if apply:` at FIVE places (the qualified-use arm, the top-up arm, the
    # module-alias arm, the dead-tip drop, and the main expansion) and only the
    # first was armed — the other four were unguarded writes in a tool the
    # `snapshot-guard` census scores as ARMED, because that census asks whether the
    # tool mentions `edit_snapshot` at all.  A snapshot at entry covers every arm
    # by construction, which is the property a per-write guard cannot have.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("retire_mod_tip", paths=argv)
    apply = "--apply" in sys.argv
    for p in argv:
        mods = rewrite(p, apply, forced)
        print(f"{p}: {'no tip import' if mods is None else ', '.join(mods)}")
    if not apply:
        print("(dry run — pass --apply to write)")
