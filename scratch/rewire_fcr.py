#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Rewire every `FromCommRing` TIP consumer to its MINIMAL prefix slice.

⟡cap64-fcr-split, the bind-at-owner half.  `FromCommRing.agda` no longer re-exports
the `Graded` barrel; it is the CommutativeRing→flat-ops ADAPTER alone.  Each consumer
must now also open the prefix slice that owns the polynomial names it uses:

    FromCommRing.Defs …  P0 only            (Poly, nth, _+P_, _·c_, _*P_, outer, …)
    FromCommRing.Nth  …  P0..P1
    …
    FromCommRing.AssocMain … P0..P15        (the retired barrel's full surface)

THE OWNER MAP IS DERIVED, never hand-written: each part module's `module Over` block
is scanned for the names it DEFINES, and a name's owner is the LOWEST part that
defines it.  A consumer's slice = the MAX owner index over the names it mentions.
A consumer that mentions no polynomial name at all keeps the bare adapter.

⚑ REFERENCE FORMS handled (each unhandled form looks EXACTLY like "uses nothing" and
would get its import dropped — the standing lesson from the Mod/Div/Core retirements):
  (a) `import …FromCommRing as F`      + `open F.Over <args> [using (…)] [-- cmt]`
  (b) bare `import …FromCommRing`      + `open Substrate.….FromCommRing.Over <args>`
  (c) `module X = …FromCommRing.Over <args>`  (module-alias binding, used as `X.name`)
  (d) qualified `F.Over.name` with no `open` at all

USAGE: rewire_fcr.py <file>...            (dry run)
       rewire_fcr.py <file>... --apply
       rewire_fcr.py --siblings <Leaf-dir | Dotted.Module.Path>
              # REPORT THE SIBLING OWNER MAP — which leaf owns which name — and, per
              # file, the exact leaves it cites. READ-ONLY, deliberately: the write path
              # is prefix-shaped and would over-open.
              # ⚑ THE PACKAGE IS AN ARGUMENT, NOT A FROZEN CONSTANT. This took a bare
              # leaf-DIRECTORY name and joined it to the hardcoded `Graded` package, so
              # the mode could only ever serve the split it was written for. A DOTTED
              # module (`Substrate.Groups.Coxeter.Cyclic.Base`) names its own package and
              # leaf dir; the bare form still works for the `Graded/Defs` callers.
              # ⚑ IT REPORTS ITS OWN SCAN ROOT, because a missing directory and an empty
              # one give a caller the same answer: `ROOT` already ends in `agda`, and
              # joining it again produced `agda/agda/…`, whose empty owner map read as
              # "this package has no leaves".
       rewire_fcr.py --selftest
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
        edit_snapshot.guard('rewire_fcr', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")
PKG = "Substrate.Algebra.Polynomial.Graded"
FCR = PKG + ".FromCommRing"

PARTS = [
    ("Defs",          "Defs.agda"),
    ("Nth",           "Laws/Nth.agda"),
    ("Conv",          "Laws/Conv.agda"),
    ("Distrib",       "Laws/Distrib.agda"),
    ("Scalar",        "Laws/Scalar.agda"),
    ("Basis",         "Laws/Basis.agda"),
    ("Linear",        "Laws/Linear.agda"),
    ("Monomial",      "Laws/Monomial.agda"),
    ("MonomialDelta", "Laws/MonomialDelta.agda"),
    ("Comm",          "Laws/Comm.agda"),
    ("Assoc",         "Laws/Assoc.agda"),
    ("AssocMono",     "Laws/AssocMono.agda"),
    ("AssocLinearP",  "Laws/AssocLinearP.agda"),
    ("AssocLinearQ",  "Laws/AssocLinearQ.agda"),
    ("AssocLinearR",  "Laws/AssocLinearR.agda"),
    ("AssocMain",     "Laws/AssocMain.agda"),
]

GDIR = os.path.join(ROOT, PKG.replace(".", "/"))


def part_exports(rel, base=None):
    """Names a Graded part's `module Over` DEFINES (indent≥2, `name :`), plus the
    names it re-exports from Base via `open Base.Over … public using (…)`.

    ⚑ `base` DEFAULTS TO `GDIR` BUT MUST BE OVERRIDABLE. The join was hardcoded,
    so this reader could only ever see one directory — which made it untestable
    on a fixture (the selftest's first run silently read a nonexistent path and
    returned no names) and unusable for the sibling map, whose leaves live in a
    subdirectory. Fixed arity is a capability bound, per the standing rule.
    """
    out = []
    for l in open(os.path.join(base or GDIR, rel), encoding="utf-8"):
        if l.lstrip().startswith("--"):
            continue
        m = re.match(r"^ {2,}([^\s{}()]+)\s*:(?!:)", l)
        if m and m.group(1) not in ("private", "opaque", "field"):
            out.append(m.group(1))
        m = re.match(r"^\s*open\s+\S+\.Over\b.*\bpublic\s+using\s*\((.*?)\)", l)
        if m:
            out += [x.strip() for x in m.group(1).split(";") if x.strip()]
    return out


def owner_map():
    own = {}
    for i, (_, rel) in enumerate(PARTS):
        for n in part_exports(rel):
            own.setdefault(n, i)          # lowest index wins
    return own


OWN = owner_map()
# an operator is `_*P_` at its definition but `*P` at an infix use site
ALIASES = {n.strip("_"): n for n in OWN if n != n.strip("_")}

IMP = re.compile(r"^(?P<pre>\s*)(?:open\s+)?import\s+" + re.escape(FCR) +
                 r"(?:\s+as\s+(?P<alias>\S+))?\s*$")
MODALIAS = re.compile(r"^(?P<ind>\s*)module\s+(?P<name>\S+)\s*=\s*" + re.escape(FCR) +
                      r"\.Over\b(?P<rest>.*)$")


def open_re(alias):
    who = re.escape(alias) if alias else re.escape(FCR)
    return re.compile(r"^(?P<ind>\s*)open\s+" + who + r"\.Over\b(?P<rest>.*)$")


def split_rest(rest):
    """`rest` -> (args, ' using (…)'|'', ' public'|'', ' -- comment'|'')."""
    cmt = ""
    m = re.search(r"\s--.*$", rest)
    if m:
        cmt, rest = m.group(0), rest[:m.start()]
    pub = ""
    if re.search(r"\s+public\s*$", rest):
        pub, rest = " public", re.sub(r"\s+public\s*$", "", rest)
    use = ""
    m = re.search(r"\s+using\s*\(.*\)\s*$", rest)
    if m:
        use, rest = m.group(0).rstrip(), rest[:m.start()]
    return rest.rstrip(), use, pub, cmt


def _selftest():
    """Counted from len(cases). Fixture-driven — no live tree.

    ⚑ THIS TOOL REWRITES AGDA ACROSS 16+ FILES AND HAD NO TEST (`pycodemod
    --calls _selftest` → 0 defs). Same gap `fix_notinscope` carried. The cases
    below pin the two things a SIBLING map must get right, both measured during
    the split that produced these leaves.
    """
    import tempfile
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    d = tempfile.mkdtemp()
    ld = os.path.join(d, "Defs")
    os.makedirs(ld, exist_ok=True)
    # two leaves with DIFFERENT minimal telescopes — the whole point of the split
    open(os.path.join(ld, "PadEnd.agda"), "w", encoding="utf-8").write(
        "module Substrate.Algebra.Polynomial.Graded.Defs.PadEnd"
        " {A : Set} (_+_ : A → A → A) (𝟘 : A) where\n"
        "pad-end : A\npad-end = 𝟘\n")
    open(os.path.join(ld, "Outer.agda"), "w", encoding="utf-8").write(
        "module Substrate.Algebra.Polynomial.Graded.Defs.Outer"
        " {A : Set} (_+_ : A → A → A) (_*_ : A → A → A) (𝟘 : A) where\n"
        "outer : A\nouter = 𝟘\n")
    smap = sibling_owner_map(d, "Defs")

    check("both leaves' names are mapped", sorted(smap), ["outer", "pad-end"])
    # ⚑ PER-LEAF ARGUMENTS, READ FROM THE HEADER. Passing one leaf's list to
    # another is `[ModuleArityMismatch]` — measured twice during the split.
    check("⚑ each leaf carries its OWN minimal argument list",
          smap["pad-end"][1], ["_+_", "𝟘"])
    check("...and a leaf needing more gets more", smap["outer"][1],
          ["_+_", "_*_", "𝟘"])
    # ⚑ AN IMPLICIT IS NEVER PASSED POSITIONALLY — it is unification-solved.
    check("⚑ the implicit `{A : Set}` is NOT in any argument list",
          any("A" in v[1] for v in smap.values()), False)
    # ⚑ SET, NOT INTERVAL: a consumer citing one leaf gets ONE, not a prefix.
    check("⚑ Ⓡ2ᵈ: a consumer citing one name gets exactly that leaf",
          sorted(needed_leaves(["f = pad-end x"], None, smap)),
          ["Substrate.Algebra.Polynomial.Graded.Defs.PadEnd"])
    check("...and citing both gets both, with no leaf between them",
          len(needed_leaves(["f = pad-end (outer x)"], None, smap)), 2)
    check("a consumer citing neither gets none",
          needed_leaves(["f = g x"], None, smap), {})
    # ⚑ THE FALSE ZERO, PINNED. `part_exports` requires indent≥2 and returns
    # NOTHING for a column-0 leaf — it reported 0 names over 8 populated leaves
    # and read as "these leaves export nothing" rather than "wrong reader".
    # This case fails the moment the sibling map is routed back through it.
    check("⚑ the part reader (indent≥2) is BLIND to a column-0 leaf",
          part_exports("PadEnd.agda", base=os.path.join(d, "Defs")), [])
    check("...and the leaf reader sees it",
          leaf_exports(os.path.join(d, "Defs", "PadEnd.agda")), ["pad-end"])
    # ⚑⚑ A DATA CONSTRUCTOR IS AN EXPORTED NAME. The reader matched only column-0
    # signatures, so `data Gen : Set where` / `  a : Gen` yielded `Gen` and NOT
    # `a` — and a consumer citing the constructor got no leaf import. MEASURED on
    # `InsertPowerEqYes`: rewired correctly for `insert`/`power`/`σ`, still failed
    # `[NotInScope] a`. Third instance of the constructor-blindness class (Ⓒ9 twice
    # in the splitter's seed, now here in the owner map).
    _dp = os.path.join(d, "Defs", "WithData.agda")
    open(_dp, "w", encoding="utf-8").write(
        "module Substrate.Algebra.Polynomial.Graded.Defs.WithData where\n"
        "data Gen : Set where\n  a : Gen\n"
        "data Two : Set where\n  x y : Two\n"
        "f : Gen\nf = a\n")
    _de = leaf_exports(_dp)
    check("⚑⚑ a data TYPE and its constructors are both exported",
          ("Gen" in _de) and ("a" in _de), True)
    # ⚑ AND A MULTI-NAME CONSTRUCTOR LINE IS SEVERAL NAMES — the same telescope
    # sugar that broke the shape hash (`S K I : Tm` is three constructors).
    check("⚑ `x y : Two` contributes BOTH constructors",
          ("x" in _de) and ("y" in _de), True)
    check("...and ordinary signatures still register",
          "f" in _de, True)

    # --- the WRITE path -------------------------------------------------
    cpath = os.path.join(d, "Consumer.agda")
    open(cpath, "w", encoding="utf-8").write(
        "module C where\n"
        "import Substrate.Algebra.Polynomial.Graded.Defs as A0\n"
        "module Over {A : Set} (_+_ : A → A → A) (𝟘 𝟙 : A) where\n"
        "  open A0.Over _+_ 𝟘 𝟙\n"
        "  f = pad-end x\n")
    r1, hits1 = sibling_rewrite(cpath, smap, apply=True)
    body1 = open(cpath, encoding="utf-8").read()
    check("write: reports the cited leaves", hits1,
          ["Substrate.Algebra.Polynomial.Graded.Defs.PadEnd"])
    # ⚑ THE INSERT MUST LAND INSIDE `module Over`, AFTER THE TELESCOPE — the
    # leaf is applied to `_+_ 𝟘 𝟙`, which nothing above the header binds.
    check("⚑ the open lands after the `open A0.Over` anchor, indented",
          "  open import Substrate.Algebra.Polynomial.Graded.Defs.PadEnd _+_ 𝟘"
          in body1, True)
    check("...and below the anchor line, not above it",
          body1.index("open A0.Over") < body1.index("Defs.PadEnd _+_"), True)
    # ⚑ IDEMPOTENCE: these census modes get re-run freely; a write beside them
    # that stacks a second copy on the second run turns a query into damage.
    r2, _ = sibling_rewrite(cpath, smap, apply=True)
    check("⚑ re-running is a no-op, not a second copy", r2, "already rewired")
    check("...and the file is byte-identical after the second run",
          open(cpath, encoding="utf-8").read(), body1)
    check("a file citing no leaf name is left alone",
          sibling_rewrite(os.path.join(d, "Defs", "Outer.agda"), smap)[0], None)

    # ── Ⓡ7ᵇ FIDELITY-FOR-REWRITE ────────────────────────────────────────
    # ⚑ THE INVARIANT INVERTS FROM Ⓡ7's. Nothing this tool writes traces to
    # source (it INSERTS), so the arms are preservation + derivability instead.
    _ok = "\n".join(["a", "  open A0.Over x", "b"])

    def _fid(new, ind="  "):
        return _rewrite_fidelity(_ok, new, smap, ind)

    _P = "Substrate.Algebra.Polynomial.Graded.Defs.PadEnd"
    _O = "Substrate.Algebra.Polynomial.Graded.Defs.Outer"
    check("a clean insert passes both arms",
          _fid("\n".join(["a", "  open A0.Over x",
                          f"  open import {_P} _+_ 𝟘", "b"])), (None, []))
    # ⚑ PRESERVATION — an anchor-slice bug drops a line and the result still
    # parses. This is what a whole-file diff is actually good for.
    check("⚑ a DROPPED original line is caught",
          _fid("\n".join(["a", "  open A0.Over x",
                          f"  open import {_P} _+_ 𝟘"]))[0],
          "original lines not preserved verbatim")
    # ⚑ DERIVABILITY — the [ModuleArityMismatch] class, measured twice during
    # the split. Invisible to preservation: the line count is right.
    check("⚑ another leaf's argument list is caught",
          _fid("\n".join(["a", "  open A0.Over x",
                          f"  open import {_P} _+_ _*_ 𝟘 𝟙", "b"]))[1][0][1],
          f"open import {_P} _+_ _*_ 𝟘 𝟙")
    check("...and a leaf that is not in the derived map",
          _fid("\n".join(["a", "  open A0.Over x",
                          "  open import Some.Other.Leaf _+_ 𝟘", "b"]))[1][0][0],
          "leaf not in the derived map")
    check("...and an inserted line that is not an import at all",
          _fid("\n".join(["a", "  open A0.Over x", "  x = 1", "b"]))[1][0][0],
          "not an `open import`")
    # ⚑ THE ARGUMENT LIST HERE IS THE FIXTURE'S, NOT THE LIVE TREE'S. My first
    # cut wrote `_+_ _*_ 𝟘 𝟙` from memory of the real `Outer` leaf; the fixture
    # declares `(𝟘 : A)` so its `Outer` takes three. The guard caught the
    # mismatch — which is the arm working, on its author.
    check("a comment line inserted alongside is allowed",
          _fid("\n".join(["a", "  open A0.Over x", "  -- note",
                          f"  open import {_O} _+_ _*_ 𝟘", "b"])), (None, []))

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n_, g, got_, want in cases:
        if not g:
            print(f"  FAIL {n_}\n       got {got_!r} want {want!r}")
    print(f"rewire_fcr selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def leaf_exports(path):
    """Top-level names a SPLIT LEAF defines — signatures at column 0.

    Sibling of `part_exports`, which reads a `Graded` part whose names sit
    inside `module Over` at indent≥2. Same question, different indent regime;
    kept separate rather than loosening `part_exports` to `\\s*`, because that
    would make the part reader accept its own module header and telescope
    lines as definitions.
    """
    out = []
    _in_data = False
    for l in open(path, encoding="utf-8"):
        if l.lstrip().startswith("--") or l.startswith(("module ", "open ", "import ")):
            continue
        # ⚑⚑ A DATA CONSTRUCTOR IS AN EXPORTED NAME AND THIS READ ONLY SIGNATURES.
        # `data Gen : Set where` / `  a : Gen` — the leaf exports BOTH `Gen` and
        # `a`, but only `Gen` matched (a constructor is indented, so the column-0
        # test skipped it). MEASURED: `InsertPowerEqYes` rewired correctly for
        # `insert`/`power`/`σ` and still failed `[NotInScope] a`, because the map
        # could not say which leaf owns the constructor. Same constructor-blindness
        # as Ⓒ9 in the splitter's import seed — third instance of the class.
        if re.match(r"^data\s+\S+", l):
            _in_data = True
            m = re.match(r"^data\s+([^\s{}()]+)", l)
            if m:
                out.append(m.group(1))
            continue
        if _in_data and (l[:1] in " \t") and l.strip():
            cm = re.match(r"^\s+([^\s{}()]+(?:\s+[^\s{}():]+)*)\s*:(?!:)", l)
            if cm:
                out.extend(cm.group(1).split())
            continue
        if l.strip() and l[:1] not in " \t":
            _in_data = False
        m = re.match(r"^([^\s{}()]+)\s*:(?!:)", l)
        if m and m.group(1) not in ("private", "opaque", "field", "variable"):
            out.append(m.group(1))
    return out


def sibling_owner_map(pkg_dir, leafdir, pkg=None):
    """Ⓡ2ᵈ — {name -> (leaf_module, [explicit args])} for a SIBLING leaf set.

    ⚑ THE PREFIX MODEL DOES NOT FIT A SIBLING SPLIT, AND FORCING IT WOULD OVER-OPEN.
    `needed_slice` returns the MAX owner index and the caller opens `P0..Pn`,
    which is right for the `Graded` shards: they are a numbered chain where each
    part genuinely builds on the last. `Defs`'s eight leaves are INDEPENDENT —
    `PadEnd` and `XShift` share nothing — so a consumer citing both should get
    exactly those two, not an interval containing six it never mentions. Handing
    this topology to the prefix rewirer would reintroduce the dead applications
    `narrow_leaf_opens` exists to delete.

    ⚑ THE ARGUMENT LIST IS PER LEAF AND MUST BE READ, NOT ASSUMED. Each leaf
    carries the MINIMAL telescope its body needs (`split_telescoped`'s closure),
    so `PadEnd` takes `_+_ 𝟘 𝟙` while `Outer` takes `_+_ _*_ 𝟘 𝟙`. Passing one
    leaf's arguments to another is `[ModuleArityMismatch]` — measured twice during
    the split itself. The header is the authority; parse it.
    """
    d = os.path.join(pkg_dir, leafdir)
    # ⚑⚑ A MISSING DIRECTORY AND AN EMPTY ONE MUST NOT BE ONE ANSWER. This returned
    # `{}` for both, so a wrong scan root read as "this package has no leaves" —
    # and it did, for two rounds, because `ROOT` already ends in `agda` and the
    # caller joined it again. A census that cannot say whether it LOOKED is the
    # false-zero shape this repo keeps paying for; RAISE on an unreadable root.
    if not os.path.isdir(d):
        raise ValueError(
            f"sibling_owner_map: no such leaf directory {d!r} — a fact about the "
            f"PATH, not about the package. Check the scan root before reading the "
            f"empty map as 'no leaves'.")
    out = {}
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".agda"):
            continue
        rel = os.path.join(leafdir, fn)
        # ⚑ Ⓒ13 — THE LAST FROZEN `PKG`. Every leaf module name was built from the
        # `Graded` package regardless of which directory was scanned, so a map over
        # `Cyclic/Base` named its leaves `…Graded.Base.Insert` — modules that do not
        # exist. The map came back empty and read as "this package has no leaves"
        # rather than "the tool cannot name them".
        leaf = f"{pkg or PKG}.{leafdir}.{fn[:-5]}"
        args = []
        for l in open(os.path.join(d, fn), encoding="utf-8"):
            m = re.match(r"^module\s+\S+\s+(.*?)\s+where\s*$", l)
            if m:
                # ⚑ EXPLICIT GROUPS ONLY — an implicit `{A : Set}` is
                # unification-solved and passing it positionally is
                # [ModuleArityMismatch], measured during the split.
                # ⚑ AND A GROUP MAY BIND SEVERAL NAMES. `Defs`'s telescope has
                # `(𝟘 𝟙 : A)`, which is TWO arguments; a `(\S+?)` capture takes
                # only `𝟘` and every application after it is short by one. This
                # is the same positional-desync that broke the split's own
                # cursor walk — fixed there by counting names, not groups.
                for grp in re.findall(r"\(([^():]+):", m.group(1)):
                    args.extend(grp.split())
                break
        # ⚑ `part_exports`'s INDENT≥2 RULE IS WRONG FOR A LEAF, and its zero was
        # a fact about the METHOD, not the tree. A `Graded` part's names live
        # inside `module Over` (hence indent≥2); a split LEAF is a top-level
        # module whose definitions sit at COLUMN 0. Run unchanged it reported
        # 0 names over 8 populated leaves — a false zero of exactly the shape
        # that gets banked rather than investigated.
        # ⚑ AND `agda_defs.provides` IS NOT THE SUBSTITUTE, though it answers
        # the same question live: it resolves through the whole-tree def index,
        # so the sibling map would depend on a tree scan and could not be
        # exercised on a fixture at all. Read the leaf directly, at leaf indent.
        for n in leaf_exports(os.path.join(d, fn)):
            out[n] = (leaf, args)
    return out


# ⚑ THE IDEMPOTENCE KEY IS THE GLYPH, NOT THE FULL SENTENCE. It used to be the
# whole `Defs`-specific line, so the moment the block text became package-aware
# (Ⓒ13) a second run would no longer recognise its own previous insert and would
# stack a duplicate block. Keying on the marker glyph alone keeps re-runs inert
# across packages — the property the census modes depend on, since they are
# re-run freely beside the write path.
MARK = "-- ⛑ "


def _rewrite_fidelity(old, new, smap, ind):
    """Ⓡ7ᵇ — the rewrite INSERTED derivable lines and CHANGED nothing else.

    ⚑ THE INVARIANT INVERTS RELATIVE TO THE EMITTER, and copying Ⓡ7's shape here
    would check the wrong thing. `split_telescoped._emit_fidelity` asks that every
    emitted line TRACE TO SOURCE, because emission carries a body out to new
    files. This tool does the opposite: it INSERTS constructed lines into a file
    that is otherwise untouched. Nothing it writes traces to source — by design —
    so a provenance check would refuse every correct run.

    The two arms that do hold, and each is a real failure mode:

      * **PRESERVATION** — the original lines survive, in order, unmodified. This
        is what an anchor-based insert can silently break: a bad slice drops or
        duplicates a line, and the result still parses. The check is that deleting
        the inserted block from the new file reproduces the old file EXACTLY.
      * **DERIVABILITY** — every inserted non-comment line is an `open import` of
        a leaf IN THE MAP, applied to that leaf's OWN recorded arguments. This is
        the `[ModuleArityMismatch]` class: passing one leaf's telescope to another
        typechecks nowhere but is invisible to a preservation check, and it was
        measured twice during the split that produced these leaves.

    ⚑ IT DOES NOT CHECK PLACEMENT, which is the one thing that actually broke
    first. The insert must land after the telescope binds `_+_ 𝟘 𝟙`; an insert
    above the header parses but does not typecheck. Anchoring is asserted in the
    selftest against a fixture, not here — a whole-file diff cannot tell a correct
    anchor from a wrong one, and claiming otherwise would be the overread this
    guard's sibling explicitly warns about.
    """
    o, n = old.split("\n"), new.split("\n")
    inserted = [l for l in n if l not in o or n.count(l) > o.count(l)]
    # PRESERVATION: strip exactly the inserted block, expect the original back.
    pool = list(n)
    for l in inserted:
        pool.remove(l)
    broken = None if pool == o else "original lines not preserved verbatim"
    # DERIVABILITY: every inserted code line names a mapped leaf with ITS args.
    homes = {lf: a for lf, a in smap.values()}
    bad = []
    for l in inserted:
        s = l.strip()
        if not s or s.startswith("--"):
            continue
        m = re.match(r"^open import (\S+)\s*(.*)$", s)
        if not m:
            bad.append(("not an `open import`", s))
        elif m.group(1) not in homes:
            bad.append(("leaf not in the derived map", s))
        elif m.group(2).split() != homes[m.group(1)]:
            bad.append((f"args are not {m.group(1).rsplit('.', 1)[1]}'s own "
                        f"({' '.join(homes[m.group(1)])})", s))
        elif not l.startswith(ind):
            bad.append(("not at the anchor's indent", s))
    return broken, bad


def sibling_rewrite(path, smap, apply=False, smap_root=None):
    """Ⓡ2ᵈ — insert each cited leaf's `open import … <args>` into one consumer.

    ⚑ ANCHORED ON THE ROOT'S OWN `open <alias>.Over …` LINE, not on a line
    number or the header. The insert must land INSIDE `module Over`, after the
    telescope binds `_+_ 𝟘 𝟙` — those are the arguments each leaf is applied to,
    so an insert above the header does not typecheck and an insert at the file's
    import block cannot see them at all.

    ⚑ IDEMPOTENT BY MARKER. Re-running must not stack a second copy of the
    opens; the census modes here are read-only and get re-run freely, and a
    write path beside them that double-inserts on the second run is the shape
    that turns a query into damage.
    """
    src = open(path, encoding="utf-8").read()
    lines = src.split("\n")
    alias = None
    # ⚑⚑ Ⓒ13 — TWO ANCHOR SHAPES, AND THIS KNEW ONLY ONE. The `Graded/Defs` case
    # is `import <PKG>.Defs as A0` + `open A0.Over …`, so the alias names the
    # anchor. `Cyclic.Base`'s consumers are the OTHER shape: a DIRECT applied open
    # (`open import …Cyclic.Base n`) — no alias, no `.Over`. Frozen to the first,
    # this returned "no `import … as` for Defs" for 23 files that plainly needed
    # rewiring, which reads as "nothing to do" rather than "wrong shape".
    #
    # ⚑ FIXED ARITY IS A CAPABILITY BOUND. `PKG`, the alias form and the `.Over`
    # suffix were three separate hardcodings of one package; a tool named for
    # `FromCommRing` could not serve the split it was generalised from.
    _root = smap_root or f"{PKG}.Defs"
    for l in lines:
        m = re.match(r"^\s*import\s+(\S+)\s+as\s+(\S+)", l)
        if m and m.group(1) == _root:
            alias = m.group(2)
    if MARK in src:
        return "already rewired", []
    anchor = None
    if alias is not None:
        for i, l in enumerate(lines):
            if re.match(rf"^\s*open\s+{re.escape(alias)}\.Over\b", l):
                anchor = i
    else:
        # the DIRECT applied-open shape: `open import <root> <args>`
        for i, l in enumerate(lines):
            if re.match(rf"^\s*open\s+import\s+{re.escape(_root)}(\s|$)", l):
                anchor = i
    if anchor is None:
        return None, []
    hits = needed_leaves(lines, alias, smap)
    if not hits:
        return "cites no leaf name", []
    ind = re.match(r"^(\s*)", lines[anchor]).group(1)
    # ⚑ Ⓒ13 — THE COMMENT NAMES THE ACTUAL PACKAGE, NOT `Defs`. The block text was
    # frozen alongside the anchor, so the first cross-package run wrote *"the
    # `Defs` LEAVES this shard cites"* into 21 `Cyclic.Base` consumers — prose
    # describing a module they do not import, in a repo whose plan file records
    # Ⓕ-PROSE-DECORRUPT for exactly this. A generated comment that names the wrong
    # subject is worse than none: it reads as provenance and misdirects the reader.
    _short = _root.rsplit(".", 1)[1]
    block = [
        f"{ind}-- ⛑ the `{_short}` LEAVES this module cites, derived by",
        f"{ind}-- `rewire_fcr --siblings {_root} <file>` — a SET, not a prefix.",
        f"{ind}-- `{_short}`'s re-opens are bare (Ⓡ1), so a leaf-defined name no",
        f"{ind}-- longer arrives through the root. Each leaf carries its OWN minimal",
        f"{ind}-- telescope, so the argument lists differ by leaf and are read from",
        f"{ind}-- each header.",
    ] + [f"{ind}open import {lf} {' '.join(hits[lf])}".rstrip()
         for lf in sorted(hits)]
    out = lines[:anchor + 1] + block + lines[anchor + 1:]
    # ⚑ Ⓡ7ᵇ — CHECKED ON EVERY CALL, NOT JUST `--apply`, so a dry run reports the
    # verdict the apply would rather than looking clean and failing at write time.
    # Same placement rule the emitter's two guards follow.
    _broken, _bad = _rewrite_fidelity("\n".join(lines), "\n".join(out), smap, ind)
    if _broken or _bad:
        raise ValueError("\n".join(
            [f"refusing to rewrite {os.path.relpath(path, ROOT)}:"]
            + ([f"  {_broken}"] if _broken else [])
            + [f"  {why}: {s[:70]}" for why, s in _bad[:12]]))
    if apply:
        open(path, "w", encoding="utf-8").write("\n".join(out))
    return f"{len(hits)} leaf/leaves", sorted(hits)


def needed_leaves(lines, alias, smap):
    """Ⓡ2ᵈ — the SET of sibling leaves whose names this file cites.

    Token extraction, alias expansion and the two-spelling check are lifted from
    `needed_slice` unchanged — only the prefix `max` is replaced by set union.
    """
    txt = " ".join(re.sub(r"(^|\s)--.*$", "", l) for l in lines)
    toks = set(re.findall(r"[^\s(){}\[\];,]+", txt))
    if alias:
        toks |= {t.split(".", 1)[1] for t in toks if t.startswith(alias + ".") and "." in t}
        toks |= {t.rsplit(".", 1)[1] for t in toks if t.startswith(alias + ".") and "." in t}
    hits = {}
    for n, (leaf, args) in smap.items():
        if n in toks or (n.strip("_") in toks and n != n.strip("_")):
            hits[leaf] = args
    return hits


def needed_slice(lines, alias):
    """MAX owner index over every polynomial name the file mentions; None if none."""
    txt = " ".join(re.sub(r"(^|\s)--.*$", "", l) for l in lines)
    toks = set(re.findall(r"[^\s(){}\[\];,]+", txt))
    if alias:
        toks |= {t.split(".", 1)[1] for t in toks if t.startswith(alias + ".") and "." in t}
        toks |= {t.rsplit(".", 1)[1] for t in toks if t.startswith(alias + ".") and "." in t}
    best, hits = None, []
    for n, idx in OWN.items():
        if n in toks or (n.strip("_") in toks and n != n.strip("_")):
            hits.append(n)
            if best is None or idx > best:
                best = idx
    return best, hits


def rewrite(path, apply):
    lines = open(path, encoding="utf-8").read().split("\n")
    imp_i, alias = None, None
    for i, l in enumerate(lines):
        m = IMP.match(l)
        if m:
            imp_i, alias = i, m.group("alias")
            break
    if imp_i is None:
        return None

    idx, hits = needed_slice(lines, alias)
    if idx is None:
        return ["<adapter only: no polynomial name used>"]
    slice_name = PARTS[idx][0]
    target = f"{FCR}.{slice_name}"

    out = list(lines)
    # 1. the `open …Over` sites gain a second open at the slice
    orx = open_re(alias)
    for i in reversed(range(len(out))):
        m = orx.match(out[i])
        if not m:
            continue
        ind = m.group("ind")
        args, use, pub, cmt = split_rest(m.group("rest"))
        blk = []
        if use:
            # ⚑ SPLIT the narrowing by owner. Re-opening the adapter WITHOUT the
            # `using` would widen 17 coefficient names into a scope that asked for
            # none of them (an [AmbiguousName] generator); dropping the adapter open
            # entirely would lose the ones it does ask for.
            names = [x.strip() for x in re.search(r"\((.*)\)", use).group(1).split(";")]
            poly = [n for n in names if n in OWN or ALIASES.get(n) in OWN]
            adpt = [n for n in names if n not in poly]
            if adpt:
                blk.append(f"{ind}open {alias or FCR}.Over{args} using ({'; '.join(adpt)}){pub}{cmt}")
            if poly:
                blk.append(f"{ind}open {target}.Over{args} using ({'; '.join(poly)}){pub}")
        else:
            blk = [f"{ind}open {alias or FCR}.Over{args}{pub}{cmt}",
                   f"{ind}open {target}.Over{args}{pub}"]
        out[i:i + 1] = blk
    # 2. `module X = …FromCommRing.Over args` -> retarget at the slice
    for i, l in enumerate(out):
        m = MODALIAS.match(l)
        if m:
            out[i] = f"{m.group('ind')}module {m.group('name')} = {target}.Over{m.group('rest')}"
    # 3. add the slice import beside the tip import
    out[imp_i + 1:imp_i + 1] = [f"import {target}"]
    # 4. qualified `Alias.Over.name` with no open
    if alias:
        for i, l in enumerate(out):
            if l.lstrip().startswith("--"):
                continue
            out[i] = re.sub(r"(?<![^\\s(){}\\[\\];,])" + re.escape(alias) + r"\.Over\.(" +
                            "|".join(re.escape(n) for n in sorted(OWN, key=len, reverse=True)) +
                            r")\b", lambda mm: f"{target}.Over.{mm.group(1)}", l)

    if apply:
        _snapshot_once(path)
        open(path, "w", encoding="utf-8").write("\n".join(out))
    return [slice_name, f"(P0..P{idx})", f"{len(hits)} names"]


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    if "--siblings" in sys.argv:
        # ⚑ Ⓡ2ᵈ — report the SIBLING owner map and, per file, the exact leaves it
        # cites. Read-only: the write path is prefix-shaped and would over-open.
        # ⚑ Ⓒ13 — THE PACKAGE IS AN ARGUMENT NOW, NOT `GDIR`. `--siblings` took a
        # leaf-DIRECTORY name and joined it to the frozen `Graded` package, so the
        # mode could only ever serve the split it was written for. A dotted module
        # (`Substrate.Groups.Coxeter.Cyclic.Base`) names its own package and leaf
        # dir; the bare form keeps working for the `Graded/Defs` callers.
        _arg = sys.argv[sys.argv.index("--siblings") + 1]
        if "." in _arg:
            _root = _arg
            # ⚑ `ROOT` ALREADY ENDS IN `agda` (:54) — joining it again produced
            # `agda/agda/…`, a path that does not exist, and `sibling_owner_map`
            # returned {} which reads as "this package has no leaves". A missing
            # directory and an empty one are the same answer to a caller that does
            # not check, which is why the map now reports its own scan root below.
            _pkgdir = os.path.join(ROOT, os.path.dirname(_arg.replace(".", "/")))
            _leafdir = _arg.rsplit(".", 1)[1]
        else:
            _root, _pkgdir, _leafdir = f"{PKG}.{_arg}", GDIR, _arg
        _smap = sibling_owner_map(_pkgdir, _leafdir,
                                  pkg=_root.rsplit(".", 1)[0])
        _files = [a for a in sys.argv[1:]
                  if a.endswith(".agda") and os.path.exists(a)]
        print(f"sibling owner map: {len(_smap)} name(s) over "
              f"{len({v[0] for v in _smap.values()})} leaf/leaves")
        for _n in sorted(_smap):
            _lf, _ar = _smap[_n]
            print(f"   {_n:<22} -> {_lf.rsplit('.', 1)[1]:<18} args={' '.join(_ar)}")
        _w = "--apply" in sys.argv
        for _f in _files:
            _r, _hits = sibling_rewrite(_f, _smap, apply=_w, smap_root=_root)
            print(f"\n{os.path.relpath(_f, ROOT)}: "
                  f"{_r if _r else f'no anchor for {_root}'}")
            for _lf in _hits:
                print(f"   open import {_lf}")
        if not _w:
            print("\n(dry run — pass --apply to write)")
        sys.exit(0)
    argv = [a for a in sys.argv[1:] if a != "--apply"]
    if not argv:
        print(f"owner map: {len(OWN)} names over {len(PARTS)} parts")
        for i, (n, _) in enumerate(PARTS):
            c = sum(1 for v in OWN.values() if v == i)
            print(f"  P{i:<2} {n:<14} defines {c}")
        sys.exit(0)
    for p in argv:
        r = rewrite(p, apply)
        print(f"{os.path.relpath(p, ROOT)}: {'no tip import' if r is None else ' '.join(r)}")
    if not apply:
        print("(dry run — pass --apply to write)")
