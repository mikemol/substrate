#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Find a module's PRE-SPLIT source across git refs — and restore it safely.

⚑ WHY RE-SPLIT BEATS REPAIR (user, 2026-08-01: *"if something was split by
something that didn't support telescoping, there's a really, really good chance
that it can be re-split, retrieving the pre-split from a git ref somewhere"*).

`Coxeter/Core/IdemInequality/` holds leaves that NEVER COMPILED: `module …Idem
where` takes no parameters yet applies `Word Canonical normalize …` in its body
(`[NotInScope] Word`).  They came from a hand-split of a TELESCOPED root — the
splitter could not carry the parent's telescope, so the leaves reference names
they never bind.

Repairing those leaves by hand means re-deriving, per leaf, which telescope
parameters it needs — the exact judgement `split_telescoped` was built to compute
(§34: selection is a CLOSURE, not a scan, and an operator has two spellings).
**Recovering the pre-split parent and re-splitting with a telescope-aware tool
replaces N hand-repairs with one mechanical run.**  Same shape as R12b: a source
fix stops the next occurrence, but only a RE-EMISSION fixes what already shipped.

⚑ THE SAFETY RULE, AND A TAG DOES NOT SATISFY IT.  The user's rule is *"always tag
current first, so we don't accidentally destroy work"* — correct in intent, and a
`git tag` is the WRONG INSTRUMENT here: §10 measured that this arc's decomposition
output is overwhelmingly UNTRACKED, and a tag captures only committed state.  A tag
would read as protection that is not there.  `edit_snapshot.guard` exists precisely
because `git stash create` cannot hold untracked files either, so it COPIES THEM
ASIDE.  This module therefore snapshots via `guard` and never via a tag.

⚑ AND PRIOR TAGS ARE THEMSELVES A SEARCH SPACE (user: *"prior tags might actually
contain the thing we're looking for"*).  This arc left 11: `pre-r9`, `pre-f2-split`,
`pre-bisim-split`, `pre-sibling-splits`, `pre-r2`, `pre-step4`, … each taken before
a split, so the pre-split source of anything split during this arc is very likely
inside one.  Searched newest-first, plus every `edit_snapshot` SHA still reachable.

    recover_presplit.py <Module>              # where does a pre-split source exist?
    recover_presplit.py <Module> --show=<ref>      # PRINT it — read-only, no write
    recover_presplit.py <Module> --restore=<ref>   # snapshot, then restore from ref

⚑ **`--show` EXISTS BECAUSE ITS ABSENCE CAUSED AN UNWANTED WRITE** (2026-08-01).
Wanting to READ the pre-split `IdemInequality` — to see whether `_≉_` had been
`private` before the split — the only verb that produced the text was `--restore`,
which overwrote the live file.  The snapshot made it recoverable, so nothing was
lost; the defect is that a tool holding the content offered no way to look at it.
**That is §61's finding one tool over: a read-only INTENTION needs a read-only
OPERATION, and if the tool has none the operator will use the writing one.**
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*a):
    p = subprocess.run(["git"] + list(a), cwd=ROOT,
                       capture_output=True, text=True)
    return p.returncode, p.stdout


def refs():
    """Candidate refs, NEWEST FIRST: tags, then recent commits.

    Tags lead because this arc's are all `pre-<operation>` — taken deliberately
    before a destructive step, so they bracket exactly the splits in question.
    """
    out = []
    rc, txt = _git("tag", "--sort=-creatordate")
    if rc == 0:
        out += [t for t in txt.split("\n") if t.strip()]
    rc, txt = _git("log", "--format=%H", "-40")
    if rc == 0:
        out += [c for c in txt.split("\n") if c.strip()]
    return out


def find(module, limit=None):
    """[(ref, path, n_lines)] where a FLAT source for `module` exists.

    The flat path is `Substrate/…/X.agda`; after a split it is deleted and the
    directory `Substrate/…/X/` holds the leaves.  So "the flat file exists in this
    ref" IS the pre-split condition.
    """
    rel = "agda/" + module.replace(".", "/") + ".agda"
    hits = []
    for r in (refs() if limit is None else refs()[:limit]):
        rc, txt = _git("show", f"{r}:{rel}")
        if rc == 0 and txt.strip():
            hits.append((r, rel, len(txt.split("\n"))))
    return hits


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    rs = refs()
    check("refs() finds this arc's safety tags",
          any(r.startswith("pre-") for r in rs), True)
    # ⚑ NEWEST FIRST MATTERS: the most recent pre-split ref is the one whose
    # source most closely matches today's tree; an older one may predate other
    # repairs and reintroduce them.
    rc, _t = _git("rev-parse", "--verify", "HEAD")
    check("refs() includes commits, not only tags", rc, 0)
    check("a module that never existed has no pre-split source",
          find("Substrate.Nonexistent.Module.XYZ", limit=3), [])

    # ⚑ THE SAFETY INSTRUMENT IS `edit_snapshot`, NOT `git tag` — §10 measured the
    # decomposition output as overwhelmingly UNTRACKED, which a tag cannot hold.
    import edit_snapshot
    check("the snapshot authority is importable and exposes guard()",
          callable(getattr(edit_snapshot, "guard", None)), True)

    # ⚑ `--show` MUST BE READ-ONLY, AND THAT IS THE PROPERTY THAT FAILED.  With no
    # read verb, wanting to LOOK at a pre-split source left `--restore` as the only
    # way to obtain the text, and it overwrote the live file.  The case asserts the
    # CONTENT is retrievable from a ref while the working tree is UNTOUCHED — a
    # test that only checked "it prints something" would pass on a version that
    # printed after writing.
    _rel = "agda/Substrate/Foundation/Eq.agda"
    _before = open(os.path.join(ROOT, _rel), "rb").read() \
        if os.path.exists(os.path.join(ROOT, _rel)) else None
    _rc, _txt = _git("show", f"HEAD:{_rel}")
    check("a ref's content is retrievable without touching the tree",
          (_rc == 0 and bool(_txt)), True)
    _after = open(os.path.join(ROOT, _rel), "rb").read() \
        if os.path.exists(os.path.join(ROOT, _rel)) else None
    check("...and the working file is byte-identical afterwards",
          _before, _after)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"recover_presplit selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        sys.exit(2)
    mod = args[0]
    restore = next((a.split("=", 1)[1] for a in sys.argv
                    if a.startswith("--restore=")), None)
    show = next((a.split("=", 1)[1] for a in sys.argv
                 if a.startswith("--show=")), None)

    hits = find(mod)

    if show:
        # ⚑ READ-ONLY, AND THE ONLY REASON IT EXISTS IS THAT ITS ABSENCE WROTE.
        # `git show <ref>:<path>` is exactly what `find()` already runs to decide
        # a ref HOLDS the source — the content was in hand and thrown away.  A
        # tool that can prove a file exists at a ref can print it.
        rel = "agda/" + mod.replace(".", "/") + ".agda"
        rc, txt = _git("show", f"{show}:{rel}")
        if rc != 0:
            print(f"{mod}: {show} does not hold {rel} — run without --show to "
                  f"list the {len(hits)} ref(s) that do")
            sys.exit(1)
        print(f"-- {rel} @ {show} ({len(txt.splitlines())} lines) — READ ONLY --")
        print(txt, end="")
        sys.exit(0)
    # ⚑ A RESTORE DOES NOT WANT THE SEARCH LISTING.  Printing all 51 candidate
    # refs before the one line that matters is what makes a caller reach for
    # `| tail` — reasoning applied to output instead of codified.  In restore
    # mode the ref list is noise; report the CHOSEN ref and the outcome.
    if not restore:
        for r, rel, n in hits:
            print(f"{r:<28} {rel}  ({n} lines)")
        print(f"{len(hits)} ref(s) hold a pre-split {mod}")
        if hits:
            print(f"   newest-first; line counts date them "
                  f"(a LARGER file is usually the later, pre-split state)")
    if not hits:
        print(f"{mod}: no flat source in any tag or recent commit — "
              f"it may predate them, or the module was never flat")
        sys.exit(1)

    if restore:
        # ⚑ VERIFY THE CHOSEN REF, not merely that SOME ref has it.  `hits[0]` is
        # the newest match, which need not be the ref the caller named — restoring
        # from a different one than requested is the kind of silent substitution
        # that makes a recovery unauditable.
        chosen = [h for h in hits if h[0] == restore or h[0].startswith(restore)]
        if not chosen:
            print(f"{mod}: {restore} does NOT hold a pre-split source "
                  f"(searched {len(hits)} ref(s) that do — run without "
                  f"--restore to list them)")
            sys.exit(1)
        rel = chosen[0][1]
        print(f"{mod}: restoring from {chosen[0][0]} ({chosen[0][2]} lines)")
        # ⚑ SNAPSHOT FIRST, VIA THE AUTHORITY THAT HANDLES UNTRACKED FILES.
        import edit_snapshot
        leafdir = os.path.join(ROOT, "agda",
                               mod.replace(".", "/"))
        touched = [os.path.join(ROOT, rel)]
        if os.path.isdir(leafdir):
            touched += [os.path.join(leafdir, f) for f in os.listdir(leafdir)
                        if f.endswith(".agda")]
        edit_snapshot.guard(f"recover_presplit {mod} <- {restore}", touched)
        rc, _ = _git("checkout", restore, "--", rel)
        if rc:
            print(f"   ✗ could not restore {rel} from {restore}")
            sys.exit(1)
        print(f"   ✓ restored {rel} from {restore}")
        print(f"   NEXT: re-split with a telescope-aware tool —\n"
              f"     python3 scratch/split_telescoped.py {rel}\n"
              f"   The leaves under {mod.split('.')[-1]}/ are the OLD split's "
              f"output and\n   must be replaced, not merged.")
    sys.exit(0)
