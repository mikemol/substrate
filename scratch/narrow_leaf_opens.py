#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Narrow every `open <Leaf>.Over <args> using (…)` to the names that leaf OWNS
and the body actually CITES — and DELETE the application outright when that set
is empty.

⚑ THE DEFECT THIS REPAIRS (retire_mod_tip.py, measured on DLogHom/DLogPow/
GF16Inverse/Inverse).  When a retired tip's open carried a `using (a; b; c)`
list, the codemod emitted ONE open PER OWNING LEAF but handed EACH of them the
WHOLE list:

    open …Mod.Expand.Hsum.Over  … using (oneC; xpow; ytime; hsum; …)   -- owns only `hsum`
    open …Mod.OneC.Over         … using (oneC; xpow; ytime; hsum; …)   -- owns only `oneC`

A `using` naming something the module does not export is only a WARNING
(-W[no]ModuleDoesntExport), so the tree stays green — while every one of those
applications is still ELABORATED IN FULL.  A module application COPIES, so the
cost is ~the ⟡cap-residue constant PER application, and a leaf that supplies
nothing the body cites is a pure DEAD APPLICATION (the ⟡p1-gmul-dead-app class).

The owner map is DERIVED from each leaf's own source, never hand-written.

USAGE: narrow_leaf_opens.py <file>...            (dry run)
       narrow_leaf_opens.py <file>... --apply
"""
import os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")
OPEN = re.compile(r"^(?P<ind>\s*)open\s+(?P<mod>[\w.]+)\.Over\b(?P<rest>.*)$")


def exports(mod):
    """Names `<mod>`'s `module Over` DEFINES, plus what it re-exports `public`."""
    p = os.path.join(ROOT, mod.replace(".", "/") + ".agda")
    if not os.path.exists(p):
        return None                      # not a leaf we can resolve — leave alone
    out = []
    for l in open(p, encoding="utf-8"):
        if l.lstrip().startswith("--"):
            continue
        m = re.match(r"^ {2,}([^\s{}()]+)\s*:(?!:)", l)
        if m and m.group(1) not in ("private", "opaque", "field", "constructor"):
            out.append(m.group(1))
        m = re.match(r"^\s*open\s+\S+\.Over\b.*\bpublic\s+using\s*\((.*?)\)", l)
        if m:
            out += [x.strip() for x in m.group(1).split(";") if x.strip()]
    return set(out)


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


def rewrite(path, apply):
    lines = open(path, encoding="utf-8").read().split("\n")
    body = " ".join(re.sub(r"(^|\s)--.*$", "", l) for l in lines
                    if not OPEN.match(l) and not re.match(r"^\s*import\s", l))
    toks = set(re.findall(r"[^\s(){}\[\];,]+", body))

    def cited(n):
        return n in toks or (n != n.strip("_") and n.strip("_") in toks)

    out, dropped, narrowed = [], [], []
    for l in lines:
        m = OPEN.match(l)
        if not m:
            out.append(l)
            continue
        args, use, pub, cmt = split_rest(m.group("rest"))
        own = exports(m.group("mod"))
        if use is None or own is None:
            out.append(l)                # bare open / unresolvable — untouched
            continue
        keep = [n for n in use if n in own and cited(n)]
        leaf = m.group("mod").split(".")[-1]
        if not keep:
            dropped.append(leaf)         # DEAD APPLICATION — supplies nothing cited
            continue
        if len(keep) != len(use):
            narrowed.append(f"{leaf}({len(use)}→{len(keep)})")
        out.append(f"{m.group('ind')}open {m.group('mod')}.Over{args} "
                   f"using ({'; '.join(keep)}){pub}{cmt}")

    # drop imports whose module no longer appears anywhere
    txt = "\n".join(out)
    final = [l for l in out
             if not ((mm := re.match(r"^\s*import\s+([\w.]+)\s*$", l))
                     and not re.search(re.escape(mm.group(1)) + r"\.Over\b", txt))]
    if apply and (dropped or narrowed or len(final) != len(out)):
        import edit_snapshot as _es
        _es.guard("narrow_leaf_opens", [path])
        open(path, "w", encoding="utf-8").write("\n".join(final))
    return dropped, narrowed


if __name__ == "__main__":
    _files = [a for a in sys.argv[1:] if not a.startswith("-")]
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound.  The
    # `guard` this supersedes sat under `if apply and (dropped or narrowed or …)` —
    # the NARROWEST condition in this census — so a run over files that need no
    # change never snapshotted, and a run that needed one snapshotted only after
    # the decision had already been made.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("narrow_leaf_opens", paths=_files)
    apply = "--apply" in sys.argv
    for p in _files:
        d, n = rewrite(p, apply)
        if d or n:
            print(f"{os.path.relpath(p, ROOT)}: DROPPED {len(d)} "
                  f"[{', '.join(d)}]" + (f"  narrowed {', '.join(n)}" if n else ""))
    if not apply:
        print("(dry run — pass --apply to write)")
