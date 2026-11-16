#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""EVERY non-ASCII codepoint in the repo, counted — the census that enumerates what is THERE.

⚑⚑⚑ WHY THIS IS A TOOL AND NOT A MODE.  Every other structural reader here claims ONE artifact
kind (`.py`, `.md`, `.bib`, `.agda`) and answers questions ABOUT that kind's structure.  This asks
a question no artifact kind owns: *which characters does this repository use, and where?*  A
codepoint is below every grammar — it is in Agda operators, markdown labels, Python docstrings,
shell comments, TSV ledgers and JSON alike — so scoping it to one reader would rebuild the exact
defect it exists to measure.

⚑⚑ THE DEFECT IT EXISTS TO MEASURE, in two parts, both recorded rather than assumed:

  1. `agda_defs --prose <regex>` answers "which comments match this pattern", so a family nobody
     thought to NAME is invisible to it.  The surveyor said so directly: *"there is no mode that
     enumerates the distinct non-ASCII codepoints in comments … a family I did not think to name
     is invisible to this census."*  That is the roster defect one level down — an instrument
     whose population is a GUESS cannot report what was not guessed.  This enumerates instead.

  2. The same survey reported `{- … -}` block comments UNMEASURED: `--prose` returned none across
     ~4000 lines, and *"the corpus has none"* could not be distinguished from *"the reader skips
     them"* without grepping.  Splitting `line` from `block` answers that by construction — two
     populations that a skipping reader and an empty corpus distinguish measurably.

⚑ AND THE SCOPE IS THE WHOLE REPO BECAUSE THE PRIOR ART IS NOT WHERE ANYONE EXPECTS.  The Agda
tree was searched first because someone knew roughly what lived there — but a census scoped to the
place you already suspect is confirmatory, which is the thing this replaces.  Ignored paths are
included by default: `~/.claude/`-style scratch, drop zones and build trees are where a NEW
vocabulary gets invented, so a tracked-files-only walk is blind exactly where invention happens.

⚑ IT REPORTS A SPLIT AND NEVER A VERDICT.  Code is saturated with unicode as MATHEMATICS
(`≡ → ∀ ℕ ⊎ Σ ×`); comments carry markers.  A glyph's code-vs-comment ratio is EVIDENCE about
which it is — not a decision.  `★` is simultaneously the Hodge operator, an emphasis bullet, and
half of the label `Ξ★`; no count resolves that and this tool does not pretend to.  Position does,
and position is the caller's judgement to make.

    codepoints.py [root]              # the histogram, ranked by FILE SPREAD
    codepoints.py [root] --where comment|code|line|block|all   # which population to count
    codepoints.py [root] --block <name>   # one Unicode block, e.g. GREEK, WHITE
    codepoints.py [root] --char <c>       # one character, with witnesses
    codepoints.py [root] --char <c> --limit <n>   # bound the witness list
    codepoints.py <A> --diff <B>          # codepoints in A not B, in B not A, and both —
                                          # ONE command, and BOTH sides censused at the SAME
                                          # `--where`, because comparing two censuses taken at
                                          # different scopes is the defect this mode exists for
    codepoints.py --selftest
"""
import os
import sys
import unicodedata

# ⚑ COMMENT SYNTAX PER SUFFIX, DECLARED ONCE.  A `--` opens a comment in Agda and Haskell and is
# a DECREMENT in C; `#` comments Python and shell and is a HEADING in markdown.  Getting this
# wrong does not fail loudly — it silently reclassifies markers as code, which is the one thing
# this tool must not do.  Suffixes with no comment syntax are read wholly as `code` rather than
# guessed at, and prose formats (.md/.txt) are read wholly as `comment`, since all of their text
# is prose by construction.
LINE_COMMENT = {".agda": "--", ".lagda": "--", ".hs": "--",
                ".py": "#", ".sh": "#", ".mk": "#", ".toml": "#", ".yml": "#", ".yaml": "#",
                ".tsv": "#", ".bib": "%"}
BLOCK_COMMENT = {".agda": ("{-", "-}"), ".lagda": ("{-", "-}"), ".hs": ("{-", "-}")}
ALL_PROSE = {".md", ".txt", ".bricks", ".rst"}
SKIP_DIRS = {".git", "_build", ".venv", "__pycache__", "node_modules", ".mypy_cache",
             ".ruff_cache", ".pytest_cache"}
SKIP_SUFFIX = {".png", ".jpg", ".pdf", ".zip", ".db", ".sqlite", ".agdai", ".o", ".hi",
               ".pyc", ".dyn_o", ".dyn_hi"}


def segments(text, suffix):
    """[(kind, text)] where kind ∈ {code, line, block} — the per-SEGMENT split.

    ⚑ A LINE CAN BE BOTH, and charging it to one bucket is the failure mode.  `f x = y  -- ⚑ note`
    carries code AND a marker; a per-line rule would file every trailing marker under `code` and
    manufacture the confusion this tool measures.
    """
    if suffix in ALL_PROSE:
        return [("line", text)]
    lc = LINE_COMMENT.get(suffix)
    bc = BLOCK_COMMENT.get(suffix)
    if not lc and not bc:
        return [("code", text)]
    out, rest, in_block = [], text, False
    while rest:
        if in_block:
            end = rest.find(bc[1]) if bc else -1
            if end < 0:
                out.append(("block", rest)); break
            out.append(("block", rest[:end])); rest = rest[end + len(bc[1]):]; in_block = False
            continue
        b = rest.find(bc[0]) if bc else -1
        l = rest.find(lc) if lc else -1
        if b >= 0 and (l < 0 or b < l):
            out.append(("code", rest[:b])); rest = rest[b + len(bc[0]):]; in_block = True
        elif l >= 0:
            nl = rest.find("\n", l)
            out.append(("code", rest[:l]))
            out.append(("line", rest[l:nl] if nl >= 0 else rest[l:]))
            rest = rest[nl:] if nl >= 0 else ""
        else:
            out.append(("code", rest)); break
    return out


def histogram(root=".", where="comment"):
    """{char: {files, lines, hits, name, block, cp, kinds}} plus the file count scanned."""
    out, nfiles = {}, 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            suf = os.path.splitext(fn)[1]
            if suf in SKIP_SUFFIX:
                continue
            path = os.path.join(dirpath, fn)
            try:
                text = open(path, encoding="utf-8", errors="strict").read()
            except (OSError, UnicodeDecodeError):
                continue          # ⚑ a binary or non-UTF8 file is SKIPPED, not guessed at
            nfiles += 1
            here = {}
            for kind, seg in segments(text, suf):
                if where != "all" and not (kind != "code" if where == "comment" else kind == where):
                    continue
                for ch in seg:
                    if ord(ch) < 128 or ch.isspace():
                        continue
                    e = out.get(ch)
                    if e is None:
                        try:
                            nm = unicodedata.name(ch)
                        except ValueError:
                            nm = "<unnamed>"
                        e = out[ch] = {"files": 0, "hits": 0, "name": nm,
                                       "block": nm.split()[0], "cp": ord(ch), "kinds": {}}
                    e["hits"] += 1
                    e["kinds"][kind] = e["kinds"].get(kind, 0) + 1
                    here[ch] = True
            for ch in here:
                out[ch]["files"] += 1
    return out, nfiles


def diff(root_a, root_b, where="all"):
    """Codepoints in A but not B, in B but not A, and in both — ONE command.

    ⚑⚑ THIS MODE EXISTS BECAUSE COMPARING TWO CENSUSES BY EYE PRODUCED TWO FALSE FINDINGS IN
    ONE SESSION.  `◅` was called "a marker that did not survive into committed text" and `⟐` "a
    live coinage"; both came from reading two printed tables side by side and inventing the
    relation between them.  A set difference is a computation, and a computation done in the
    turn evaporates when the turn ends — the next reader re-derives it differently, or the same
    reader re-derives it wrongly, which is what happened.

    ⚑ IT FORCES EQUAL SCOPE BY CONSTRUCTION.  Both sides are censused with the SAME `where`,
    which is the defect that made `◅` wrong: a `comment`-scoped count compared against an
    `all`-scoped one.  A single parameter cannot disagree with itself.

    ⚑ AND IT REPORTS `only_a` AS A FACT ABOUT THESE TWO ROOTS, never as absence.  A glyph
    missing from B is missing FROM B — not from the substrate, not from the other 52 repos,
    not from any store neither root covers.  The caller names the roots; the roots bound the
    claim.
    """
    ha, na = histogram(root_a, where=where)
    hb, nb = histogram(root_b, where=where)
    sa, sb = set(ha), set(hb)
    return {"only_a": sorted(sa - sb, key=ord), "only_b": sorted(sb - sa, key=ord),
            "both": sorted(sa & sb, key=ord), "a": ha, "b": hb, "files_a": na, "files_b": nb}


def witnesses(root, char, limit=6):
    """[(path, lineno, line)] — where this character actually appears.  A count without a
    witness is the shape this repo refuses; every claim here can be opened."""
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1] in SKIP_SUFFIX:
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, encoding="utf-8", errors="strict") as fh:
                    for i, line in enumerate(fh, 1):
                        if char in line:
                            hits.append((path, i, line.rstrip()[:140]))
                            if len(hits) >= limit:
                                return hits
            except (OSError, UnicodeDecodeError):
                continue
    return hits


def _selftest():
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    # ⚑ THE PER-SEGMENT SPLIT IS THE LOAD-BEARING PROPERTY — a line that is BOTH code and comment
    # must contribute to both, or every trailing marker is filed as code.
    segs = segments("f x = y  -- ⚑ note\n", ".agda")
    kinds = {k for k, _ in segs}
    check("a mixed line yields BOTH code and comment segments", {"code", "line"} <= kinds, True)
    check("...and the marker lands in the COMMENT half",
          any("⚑" in t for k, t in segs if k == "line"), True)
    check("...not in the code half",
          any("⚑" in t for k, t in segs if k == "code"), False)

    # ⚑⚑ BLOCK COMMENTS ARE A SEPARATE POPULATION, which is what settles the question `--prose`
    # could not: a corpus with no block comments and a reader that SKIPS them differ measurably.
    segs = segments("{- ⟡tag -}\ncode\n", ".agda")
    check("a block comment is read, and read AS a block",
          any("⟡" in t for k, t in segs if k == "block"), True)

    # ⚑ COMMENT SYNTAX IS PER-LANGUAGE. `--` opens a comment in Agda and is a DECREMENT elsewhere;
    # a shared rule would silently reclassify markers as code, the one error that matters here.
    check("`#` does not open a comment in Agda",
          [k for k, t in segments("x # ⚑\n", ".agda") if "⚑" in t], ["code"])
    check("`#` DOES open one in Python",
          [k for k, t in segments("x = 1  # ⚑\n", ".py") if "⚑" in t], ["line"])
    # ⚑ A prose format is comment THROUGHOUT — markdown has no code/comment distinction to make.
    check("markdown is read wholly as prose",
          [k for k, _ in segments("⟡label\n", ".md")], ["line"])

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.agda"), "w", encoding="utf-8").write(
            "postulate x : ℕ\n-- ⟡tag-one\n")
        open(os.path.join(d, "b.agda"), "w", encoding="utf-8").write("-- ⟡tag-two\n")
        h, n = histogram(d, where="comment")
        check("scans every file under the root", n, 2)
        check("a marker in comments is counted across BOTH files", h["⟡"]["files"], 2)
        # ⚑ THE CONTROL, without which the case above proves nothing: a mode that counted
        # everything would pass it while being useless.  ℕ is CODE and must NOT appear here.
        check("a code-only glyph is ABSENT from the comment census", "ℕ" in h, False)
        hc, _ = histogram(d, where="code")
        check("...and PRESENT in the code census", hc["ℕ"]["files"], 1)
        check("witnesses can be opened", witnesses(d, "⟡")[0][2].strip().startswith("--"), True)

        # ⚑⚑ THE DIFF CASE — guarding the mode that replaces reading two tables by eye.
        with tempfile.TemporaryDirectory() as d2:
            open(os.path.join(d2, "c.agda"), "w", encoding="utf-8").write("-- ⟡tag ◈only-here\n")
            dd = diff(d, d2, where="comment")
            check("a glyph in BOTH roots is reported in neither only-side",
                  "⟡" in dd["both"] and "⟡" not in dd["only_a"] + dd["only_b"], True)
            check("a glyph unique to B is reported only_b", dd["only_b"], ["◈"])
            # ⚑ THE CONTROL: a diff that reported everything as unique would pass the case
            # above while being useless.  A shares no exclusive glyph here, so only_a is empty.
            check("...and only_a is empty when A has no exclusive glyph", dd["only_a"], [])
        # ⚑⚑ THE SCOPE CASE — this is the `◅` defect, mechanized.  A glyph used ONLY in code is
        # invisible at comment scope and present at all scope; the same two roots must therefore
        # diff DIFFERENTLY under the two scopes, which is what makes cross-scope comparison a bug.
        with tempfile.TemporaryDirectory() as d3, tempfile.TemporaryDirectory() as d4:
            open(os.path.join(d3, "e.agda"), "w", encoding="utf-8").write("_◅_ : A → B\n")
            open(os.path.join(d4, "f.agda"), "w", encoding="utf-8").write("-- plain\n")
            check("a code-only glyph is INVISIBLE to a comment-scoped diff",
                  diff(d3, d4, where="comment")["only_a"], [])
            # ⚑ `→` is here too, and that is the case working: the signature `_◅_ : A → B` really
            # does contain two code-only glyphs.  The first expectation said `["◅"]` and the case
            # refused it — a guard that agrees with what you expected to see would not have.
            check("...and PRESENT in the same diff at all scope",
                  diff(d3, d4, where="all")["only_a"], ["→", "◅"])

    bad = [c for c in cases if not c[1]]
    for n, _, got, want in bad:
        print(f"  FAIL {n}: got {got!r} want {want!r}")
    print(f"codepoints selftest: {len(cases) - len(bad)}/{len(cases)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    args = sys.argv[1:]
    # ⚑ A BARE RUN PRINTS THE MODE LIST — `toolmodes --check` flags a tool with no
    # self-description, and rightly: the struct-tools rule is *run it bare to see what it can
    # do*, so a tool that answers a bare run by silently censusing the CWD is unaskable.
    if not args:
        print(__doc__)
        sys.exit(0)
    root = next((a for a in args if not a.startswith("-") and os.path.isdir(a)), ".")

    def opt(flag, default=None):
        return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default

    if "--char" in args:
        ch = opt("--char")
        # ⚑ `--limit` EXISTS BECAUSE ITS ABSENCE PRODUCED A PIPE.  Witnessing a glyph printed an
        # unbounded list and the next reach was `| head`, which the no-chaining hook refused —
        # correctly.  A caller wanting fewer rows is asking the tool a narrower question, and a
        # tool that cannot be asked it has a missing parameter, not a caller with a shell problem.
        for p, i, line in witnesses(root, ch, limit=int(opt("--limit", "6"))):
            print(f"  {p}:{i}  {line}")
        h, n = histogram(root, where="all")
        e = h.get(ch)
        if e:
            print(f"  {ch}  U+{e['cp']:04X}  {e['name']}")
            print(f"  {e['files']} file(s), {e['hits']} occurrence(s) over {n} scanned; "
                  f"by segment: {e['kinds']}")
        sys.exit(0)

    where = opt("--where", "comment")

    if "--diff" in args:
        other = opt("--diff")
        d = diff(root, other, where=where)
        print(f"  A = {root} ({d['files_a']} files) · B = {other} ({d['files_b']} files) · scope `{where}`")
        for lbl, key, src in (("only in A", "only_a", "a"), ("only in B", "only_b", "b")):
            print(f"  ── {lbl} — {len(d[key])} codepoint(s)")
            for ch in d[key]:
                e = d[src][ch]
                ks = ",".join(f"{k}:{v}" for k, v in sorted(e["kinds"].items()))
                print(f"     {ch}  U+{e['cp']:04X}  {e['files']:>5} file(s) {e['hits']:>7} hit(s)  "
                      f"{ks:<22} {e['name'][:40]}")
        print(f"  ── in both: {len(d['both'])} codepoint(s)")
        print("  ⚑ `only in A` is a fact about THESE TWO ROOTS. It is not absence from the")
        print("     substrate, from the other repos, or from any store neither root covers.")
        sys.exit(0)

    want_block = opt("--block")
    h, n = histogram(root, where=where)
    rows = sorted(h.items(), key=lambda kv: (-kv[1]["files"], kv[1]["cp"]))
    if want_block:
        rows = [r for r in rows if want_block.upper() in r[1]["block"].upper()]
    print(f"  {len(rows)} distinct non-ASCII codepoint(s) in `{where}` over {n} file(s) under {root}")
    if where != "all":
        # ⚑⚑ THE SCOPE IS STAMPED ON THE OUTPUT BECAUSE A FILTERED COUNT WAS READ AS A TOTAL.
        # Measured 2026-08-14: `◅` reported 4 hits under `--where comment` and was compared
        # against an all-scope count from another store, producing "a marker that did not
        # survive into committed text."  It is `_◅_`, the cons constructor of `_⇒*_` — 113 code
        # hits the flag had excluded.  The filter answered the question ASKED; the reader
        # supplied a question it had not asked.  Two censuses are comparable only at equal scope.
        print(f"  ⚑ SCOPE `{where}` — code positions are EXCLUDED from these counts. A low number")
        print(f"     here is evidence about {where} only, NEVER about the corpus. Do not compare")
        print(f"     it against a count taken at another scope; re-run both with --where all.")
    print(f"  {'files':>6} {'hits':>7}  {'char':<4} {'codepoint':<10} segment-split / name")
    for ch, e in rows[:60]:
        ks = ",".join(f"{k}:{v}" for k, v in sorted(e["kinds"].items()))
        print(f"  {e['files']:>6} {e['hits']:>7}  {ch:<4} U+{e['cp']:04X}    {ks:<22} {e['name'][:44]}")
    if len(rows) > 60:
        print(f"  … {len(rows) - 60} more (narrow with --block <name>)")
    print("  ⚑ counts are EVIDENCE, not a verdict: a glyph's code-vs-comment split argues for")
    print("     marker-vs-mathematics, and only POSITION decides. `★` is the Hodge operator, an")
    print("     emphasis bullet, AND half of the label `Ξ★` — no count resolves that.")
