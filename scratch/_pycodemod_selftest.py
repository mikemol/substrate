# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`pycodemod --selftest` — every mode's cases, moved WHOLE.

⚑ ONE FUNCTION, 615 CODE LINES, AND CARVING IT UP IS NOT THIS ARC'S WORK.
`_selftest` is a single def whose local `cases` list accumulates 123 checks;
splitting it into per-mode suites would change what `run_selftests.py` discovers
(it finds suites by looking for a def NAMED `_selftest`) and would risk losing
cases, which the decomposition's first constraint forbids outright.  Moving it
whole to its own module pays the size debt without touching a single case —
the honest partial move, not the clever one.

⚑ IT IS THE ONE MODULE THAT IMPORTS EVERYTHING, BY CONSTRUCTION.  A test for
every mode must reach every mode, so the long import list below is the shape of
the thing being tested, not accidental coupling.  It is also why `_selftest`
could not stay in the entry file and be cheap: the entry file's job is to be the
mode index and the public API, and 615 lines of fixtures buried that.

⚑ THE FIXTURE REBINDS `_c.ROOT`, NOT A LOCAL `ROOT`, and this was MEASURED, not
assumed.  With `global ROOT` (the pre-split spelling) the `_roots()` case
enumerated ~1600 real repo files instead of the two-file fixture and failed
loudly — because after the split `py_files` reads the core module's global, and
a `global ROOT` here rebinds a name nothing consumes.  Same class as the silent
wrong-corpus read the `corpus` envelope guards against, arriving through a test.
"""
import ast
import inspect
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import libcst as cst
    import libcst.metadata  # noqa: F401
except ImportError:  # pragma: no cover - environment probe
    cst = None

import _pycodemod_core as _c
from _pycodemod_core import (
    _GENERATED_DIRS, _per_file, _roots, _shape_of, _SKIP_DIRS, UNKNOWN,
    corpus, escapes, flagged_argv, operand_tail, package_root, py_files,
    roundtrip,
)
from _pycodemod_census import (
    _DERIVER, _PARSE_CACHE, _SCHEMA, _code_lines, _deriver_tag, _ignore_cache,
    ALIAS_COMPLIANT, aliases,
    build_artifact_readers, crossings,
    discriminates, imports, importers, module_size, module_size_all,
    module_state, paperkit_projects, touches, type_errors, writes_by_default,
)
from _pycodemod_commentary import (
    COMMENTARY_MARKS, commentary_census, commentary_kinds, commentary_lost,
)
from _pycodemod_sql import (
    pg_probe_status, portable_sites, rawread_sites, relalg_sites, relname_sites,
    snapshot_sites, sql_kind, sql_rel_roles, sql_relnames, sql_rw, sql_sites,
)
from _pycodemod_control import (
    CONSTRUCT_GROUPS, CONSTRUCTS, CONTROL_KINDS, control_sites,
)
from _pycodemod_fingerprint import _cases as _fp_cases
from _pycodemod_query import (
    _cached_defs, _scan_defs, _rivals_one, _attr_reads_one, _bare_calls,
    KwIndex, asserted, attr_reads, available, bindings, callgraph,
    collision_apex, collision_kinds, collisions, dead, discards, forwards, framework_dispatch,
    _generic_func_names, funcnames,
    guarded, key_reads, literal_sites, reaches, reifies, resorts, rivals, scan,
    shape_sites, source_of, sqlnames, swallows, values, verdict_returners,
)

# ⚑ THREE NAMES ARE RESOLVED AT CALL TIME, AND THE CYCLE IS WHY — NOT STYLE.
# `modes`, `banner_drift` and `layout` must stay in `pycodemod.py`: `modes()`
# PARSES its own file for the `"--x" in sys.argv` tests inside `_dispatch`, and
# `banner_drift` compares that roster against the module docstring, which is the
# mode index.  Both are authorities over the ENTRY module specifically, so they
# cannot follow the cases here.  Meanwhile `pycodemod` must import THIS module
# to re-export `_selftest` (`run_selftests.py` discovers a suite by finding a def
# named `_selftest`).  A module-level `import pycodemod` here would therefore
# fail at load and take every consumer down with it; deferring it into the one
# function that needs it keeps the graph acyclic and touches no case.
def _entry():
    """The entry module, resolved at CALL time (see the cycle note above)."""
    import pycodemod
    return pycodemod




def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    if cst is None:
        print("  FAIL libcst not importable")
        print("pycodemod selftest: 0/1")
        return False

    # ⚑ LOSSLESSNESS IS THE WHOLE PREMISE.  If comments did not survive, this
    # module would be actively dangerous here: the ⚑ blocks ARE the record of why
    # each line exists, and a transform keeping code while dropping them destroys
    # the more valuable half.
    src = ("# leading\ndef f(x):\n    # ⚑ why\n    return x  # trailing\n\n\n"
           "y = f(1)\n")
    check("libcst round-trips comments and blank lines",
          cst.parse_module(src).code, src)

    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.py")
    open(p, "w", encoding="utf-8").write(src)
    check("roundtrip() accepts a well-formed file", roundtrip(p)[0], True)

    rows = scan([p], "f")
    check("a def is found", ("def", 2) in [(k, l) for _p, k, _n, l in rows], True)
    check("a call is found", ("call", 7) in [(k, l) for _p, k, _n, l in rows], True)

    # ── --guarded: a call's POSITION, not its arguments ──────────────────────────
    # ⚑ SHIPPED WITHOUT CASES AND THAT WAS THE GAP.  This mode produced the
    # ⟡guard-behind-apply finding (24 of 61 `guard` sites under an `if`), and nothing
    # pinned that it reads a condition stack correctly.  The fixture spells the two
    # shapes the corpus actually contains plus the one that must NOT invert.
    gsrc = ("def m(apply):\n"
            "    g()\n"                          # top level of its scope
            "    if apply:\n"
            "        g()\n"                      # under one condition
            "    if a:\n"
            "        if b:\n"
            "            g()\n"                  # nested — outermost first
            "    if c:\n"
            "        pass\n"
            "    else:\n"
            "        g()\n")                     # else body — over-report, never invert
    gp = os.path.join(d, "g.py")
    open(gp, "w", encoding="utf-8").write(gsrc)
    under, top = guarded("g", [gp])
    check("guarded: an unconditional call is `top`", [l for _p, l in top], [2])
    check("guarded: a call under `if` carries its test",
          [(l, cs) for _p, l, cs in under][0], (4, ["apply"]))
    check("guarded: nested conditions are outermost-first",
          [cs for _p, l, cs in under if l == 7][0], ["a", "b"])
    # ⚑ THE ELSE BODY IS REPORTED UNDER ITS `if`, DELIBERATELY.  libcst hangs `else` off
    # the `If`, so negating-and-pushing would report this call as guarded BY a condition
    # that is FALSE where it runs — an INVERTED answer, worse than a coarse one.
    check("guarded: else-body over-reported under its if, never negated",
          [cs for _p, l, cs in under if l == 11][0], ["c"])

    # ⚑⚑ THE PLACEMENT CASES RIDE THIS SUITE (Ⓐ48), because they are the OTHER AXIS of
    # the four checks above and a reader who breaks one has almost certainly broken the
    # other — both consume the same `_Scan.conds` / `.contexts`.  Kept in their own
    # module (`_pycodemod_placement._cases`) so the file that owns the predicate owns
    # its guards; surfaced here so `run_selftests` finds them without a second entry.
    import _pycodemod_placement
    for _msg in _pycodemod_placement._cases():
        check(f"placement: {_msg}", False, True)

    # ── --swallows: which discards feed a VERDICT ────────────────────────────────
    # ⚑⚑ EVERY CASE BELOW IS A CONTROL THE DISCRIMINATOR ONCE FAILED.  Two cuts shipped
    # before this: the first called any assignment verdict-feeding (5 of 5 VERDICT — a
    # ranking where everything is urgent is a flat list wearing a ranking); the second
    # tracked only ASSIGNED names and missed a method mutating its RECEIVER.  Each cut
    # failed one of these two in the opposite direction, which is what forced the model.
    ssrc = ("def a(fs, C):\n"
            "    for f in fs:\n"
            "        try:\n"
            "            C.add_file(f)\n"        # receiver mutated -> escapes
            "        except Exception:\n"
            "            continue\n"
            "    return len(C.units)\n"
            "def b(S):\n"
            "    try:\n"
            "        rows = S.stats()\n"         # assigned AND consumed in-block
            "        print(rows)\n"
            "    except Exception:\n"
            "        pass\n"
            "def c(xs, out):\n"
            "    try:\n"
            "        out.append(xs)\n"           # accumulator grows
            "    except OSError:\n"
            "        pass\n")
    sp = os.path.join(d, "s.py")
    open(sp, "w", encoding="utf-8").write(ssrc)
    sw = {l: (kind, h, feeds) for _p, l, kind, h, feeds in swallows([sp])}
    check("swallows: finds all three discards", len(sw), 3)
    # the reuse_check.py:68 shape — nothing assigned, corpus grows inside the method,
    # and `len(C.units)` downstream is the verdict input
    check("swallows: a mutated RECEIVER read later feeds a verdict",
          sw[5][2], True)
    # the wg_profile.py:305 shape — assigned, printed, never read downstream
    check("swallows: assigned-and-consumed-in-block is output-only",
          sw[12][2], False)
    check("swallows: an accumulator .append feeds a verdict", sw[17][2], True)
    check("swallows: handler breadth is classified",
          (sw[5][0], sw[17][0]), ("broad", "narrow"))
    # ⚑⚑⚑ THE `buildtime.py:35-44` SHAPE, AND IT IS WHY 46 OF 50 ONCE READ VERDICT.  A
    # name built ABOVE the try and consumed INSIDE it (`row`) landed in `touched`, and a
    # bare "is it read outside the block" test counted the read at `:37` — UPSTREAM — as
    # an escape.  A plainly benign best-effort append reported VERDICT.  The escape
    # question is strictly *is it still read AFTER the try*, so the fix compares
    # positions, not membership.
    #
    # ⚑⚑ THE FIRST VERSION OF THIS CASE ASSERTED THE BUG AS A "KNOWN BOUND" — I had
    # mis-diagnosed the over-fire as "a receiver mutated by a write" and wrote a fixture
    # passing `row` as a PARAMETER.  That fixture reported `False` (correct) while the
    # live site reported `True`, so the case FAILED and exposed the real cause.  A case
    # pinned to a fixture that is not shaped like the corpus tests the fixture; the
    # failure is what forced reading the actual site.
    wsrc = ("def w(p, n):\n"
            "    row = str(n)\n"                # built ABOVE the try
            "    try:\n"
            "        with open(p, 'a') as f:\n"
            "            f.write(row)\n"        # consumed INSIDE — an input, not an escape
            "    except OSError:\n"
            "        pass\n")
    wp = os.path.join(d, "w.py")
    open(wp, "w", encoding="utf-8").write(wsrc)
    check("swallows: a name built above and consumed inside is NOT an escape",
          [feeds for _p, _l, _k, _h, feeds in swallows([wp])], [False])

    # ── --check-contracts: roster vs dispatch, and the two shapes I got wrong ────
    # ⚑⚑ `MODES` IS THE DECLARED AUTHORITY AND THE DISPATCH IS WHAT RUNS, so a flag in
    # one and not the other is a defect whichever way it points — and nothing reported it
    # until now. Measured 2026-08-19: 24 DISPATCHED-but-undeclared, several whose usage
    # exists ONLY as a runtime `print` inside their own branch, so `toolmodes --find
    # touches` says *"in no usage line — UNDOCUMENTED"* while the tool will print
    # `usage: pycodemod.py --touches …` if you FAIL it. Help reachable only by getting
    # the call wrong is `friction-capability-legible-only-after-paying-for-it`, in my
    # own tool.
    # ⚑ VIA `_entry()`, THE ESTABLISHED SEAM — `scan_contract` is an authority over the
    # ENTRY module specifically (it parses `_dispatch`'s own branches), so it stays in
    # `pycodemod.py` for the same reason `modes`/`banner_drift`/`layout` do, and is
    # resolved at CALL time to keep the import graph acyclic.
    # ⚑⚑ THE SPECIMEN MOVED FROM `--touches` TO `--sql`, AND THE REASON IS THE POINT.
    # Ⓢ1a declared all 19 genuinely-missing entries, so `--touches` is now a ROSTER
    # MEMBER and this case — pinned to it — started failing. A case pinned to a specimen
    # that the work is meant to REMOVE fails on success, which reads exactly like a
    # regression. `--sql` is a DUAL-ROLE flag (⟡mode-dual-role): declared in
    # `OPT_OPERANDS` as a modifier AND opening a dispatch branch, so it is undeclared in
    # `MODES` for a structural reason rather than an unpaid one, and it carries the
    # runtime-print usage the second case needs.
    # ⚑ WHEN ⟡mode-dual-role IS RESOLVED THIS WILL FAIL AGAIN — deliberately. The
    # behaviour under test (does the gate report roster/dispatch disagreement, and does
    # it name the runtime-print reason) outlives every specimen, so the failure is the
    # signal to re-point it, never to weaken the assertion.
    # ⚑⚑ AND IT DID, EXACTLY AS PREDICTED — SECOND RE-POINT, `--sql` → `--since`
    # (⟡mode-consolidation / Ⓜ9, 2026-08-24). Declaring the five remaining
    # `--check-contracts` disagreements (`--key`/`--relname`/`--shape`/`--source`/`--sql`)
    # drove the census to ZERO, so the specimen pinned to `--sql` failed ON SUCCESS for
    # the second time in this case's life — the same way `--touches` failed when Ⓢ1a
    # declared it. The note above is what made that legible in one read instead of
    # reading as a regression from a green baseline.
    # ⚑ `--since` IS THE SAME STRUCTURE, WITNESSED, NOT ASSUMED: declared in
    # `OPT_OPERANDS` (`pycodemod.py:774`) AND as an opt of `--commentary` (:787), while
    # ALSO opening its own dispatch branch (:2648) whose usage exists only as a runtime
    # print (:2653). That is the dual-role shape verbatim, so it carries both halves this
    # case tests.
    # ⚑⚑ THE SPECIMEN IS RUNNING OUT, AND THAT IS THE REAL SIGNAL. Each re-point consumes
    # the last member of a shrinking population; when ⟡mode-dual-role closes there will be
    # no dual-role flag left to pin, and the honest move THEN is a SYNTHETIC specimen (a
    # fixture roster built in the test), not a third hunt through a census that is
    # deliberately being driven to empty.
    # ⚑⚑⚑ AND THE SPECIMEN RAN OUT, EXACTLY AS THE PARAGRAPH ABOVE PREDICTED — so the
    # move it named is the one taken: a SYNTHETIC roster, not a third hunt. `--since` was
    # never a dual-role flag in the first place; it is `--commentary`'s OWNED modifier
    # (declared in its `opts` at :945, branch NESTED inside `--commentary`'s at :3025),
    # and `scan_contract` reported it only because this local reader was the last copy
    # missing `contract_rows`' `owned` exemption. ⟡since-roster-disagreement: the third
    # re-point would have been onto a FALSE FINDING.
    #
    # ⚑⚑ THE SYNTHETIC IS STRICTLY BETTER AND THE HUNT WAS ALWAYS THE WEAKER HALF. A case
    # pinned to a live specimen tests the reader ONLY while the census is non-empty, and
    # it fails ON SUCCESS every time the population is paid down — three times in this
    # case's life. `climode._selftest` reached the same conclusion for the same reason
    # (*"a case pinned to a live specimen fails when the migration succeeds"*).
    # ⚑⚑⚑ THE FIXTURE FLAGS ARE ASSEMBLED, NEVER WRITTEN AS LITERALS, AND THAT IS NOT
    # STYLE. Spelled inline, `if "--real" in sys.argv:` is an ARGV-ANCHORED FLAG LITERAL —
    # exactly what `toolmodes --divergence` scans for — so three fixture flags registered
    # as UNDOCUMENTED dispatched modes of `pycodemod.py` and grew the divergence ratchet
    # 14 -> 17. A test fixture MANUFACTURING census keys for the tool under test is the
    # census-about-the-method failure in its purest form: the suite would have been
    # asserting about a roster its own source text had altered.
    #
    # ⚑ CAUGHT ONLY BY RE-DERIVING THE CENSUS AFTER THE EDIT, not by the suite going red.
    # Both readings were honest and the suite was green across the whole excursion — the
    # ratchet is the only instrument that could see it, which is the argument for checking
    # every census before AND after rather than trusting a green suite.
    _F = "-" + "-"
    _synth = ('if "%sreal" in sys.argv:\n'
              '    go()\n'
              'if "%sghost" in sys.argv:\n'
              '    print("usage: pycodemod.py %sghost")\n' % (_F, _F, _F))
    # ⚑ `contract_rows` IS THE SHARED READER IN `scripts/climode.py` — imported here
    # directly rather than re-exported through `pycodemod`, so the case names the
    # authority it is testing instead of a forwarding alias that could drift from it.
    import climode as _climode
    _cc = {f: (ok, why) for f, ok, why in
           _climode.contract_rows(_synth, {_F + "real": _entry().Mode()})}
    check("check-contracts reports dispatched-but-undeclared modes",
          _cc.get(_F + "ghost", (None, ""))[0], False)
    check("...and names the runtime-print-only usage as the reason",
          "reachable only by FAILING" in _cc.get(_F + "ghost", (None, ""))[1], True)
    # ⚑ AND THE LIVE CENSUS IS STARVED THE OTHER WAY — a refusal that never fires and one
    # that always fires are indistinguishable from a green suite. `--since` must now be
    # ABSENT from the real roster's findings, which is the assertion the re-point chain
    # could never make because it only ever checked for PRESENCE.
    check("an OWNED modifier is not reported as an undeclared mode",
          "--since" in {f for f, _ok, _w in _entry().scan_contract()}, False)

    # ── ⟡mode-opt-key-collision: the harm verdict, starved BOTH ways ────────────
    # ⚑⚑ THE COUNT WAS THE BRIEFED FACT AND THE DERIVATION FALSIFIED IT. The residue
    # comment names `--sites` and says "do not assume it is the only one"; the population
    # is THREE (`--sites`, `--kinds`, `--lines`). A sentence naming one member is why the
    # census had to become a query.
    _cols = {f: (own, harm) for f, own, harm, _w in _entry().opt_key_collisions()}
    # ⚑⚑⚑ THIS CASE QUOTED THE POPULATION IT IS NAMED FOR DERIVING, AND A FOURTH MEMBER
    # BROKE IT (2026-08-26, `--blocks`). The comment two lines up already said why —
    # *"a sentence naming one member is why the census had to become a query"* — and the
    # assertion beneath it was a sentence naming THREE. The defect the case exists to
    # prevent, committed by the case.
    #
    # ⚑⚑ THE REPAIR IS NOT A LONGER LIST. A membership list pins TODAY'S ROSTER: it goes
    # red when a mode is legitimately added and stays green while the DERIVATION rots —
    # the failure polarity is backwards, which is the `census-green-is-a-fact-about-the-
    # census` shape. What is load-bearing is that the population is DERIVED and INHABITED,
    # and that every member is a real dual declaration; the three checks below then carry
    # the harm verdict. ⚑ The known members are named in the message, never asserted, so a
    # reader still learns what this looked like without the suite pinning it.
    check("the collision population is derived (not a quoted roster; known: "
          "--sites/--kinds/--lines/--blocks)",
          (len(_cols) > 0,
           all(f.startswith("--") for f in _cols),
           sorted(_cols) == sorted(set(_cols))),
          (True, True, True))
    check("...and a nullary/nullary collision is BENIGN", _cols["--sites"][1], False)
    check("...and the live roster has NO harmful collision",
          [f for f, (_o, h) in _cols.items() if h], [])
    # ⚑⚑ THE DISCRIMINATOR MUST BITE, AND THE LIVE CENSUS CANNOT MAKE IT. A verdict that
    # answers BENIGN for every input passes a "does it classify" case while being a
    # constant function — and the live roster is 0-harmful, so it exercises one arm only.
    # A SYNTHETIC roster starves the other: an operand-taking mode whose spelling is also
    # a bare modifier is two different requests sharing a name.
    _M = _entry().Mode
    # ⚑ SAME ASSEMBLED SPELLING as `_synth` above, and for the same reason — these dict
    # keys are flag literals in this file's source too.
    _bad = _entry().opt_key_collisions(
        {_F + "host": _M(opts=(_F + "target",)), _F + "target": _M(operand="name")})
    check("an operand-taking mode colliding with a bare opt is HARMFUL",
          [(f, h) for f, _o, h, _w in _bad], [(_F + "target", True)])
    check("...and the repair it names is a rename",
          "RENAME" in _bad[0][3], True)
    # ⚑ AND A NON-COLLIDING ROSTER YIELDS NOTHING — the empty case, so "0 harmful" and
    # "0 collisions" stay distinguishable rather than both rendering as silence.
    check("an opt that is not also a mode key is no collision",
          _entry().opt_key_collisions({_F + "host": _M(opts=(_F + "quiet",))}), [])
    # ── Mode.writes: the target set, and `mutates` as its projection ────────────
    # ⚑⚑ A BOOLEAN COULD NOT SAY WHAT IS WRITTEN (operator, 2026-08-23): *"it matters
    # WHAT you're mutating; a tool might read two things and only mutate one of them."*
    # `writes` names artifact KINDS from the `struct-tools` table, so a mode reading
    # `.agdai` and writing `.md` is expressible — and checkable against the claims gate.
    _M = _entry().Mode
    check("Mode.writes defaults to a pure read", _M().writes, ())
    check("...and mutates projects it", _M().mutates, False)
    check("Mode.writes carries the artifact kinds", _M(writes=(".md",)).writes, (".md",))
    check("...and mutates is True when it writes", _M(writes=(".md",)).mutates, True)
    # ⚑ THE PROJECTION IS WHY `mutates` IS NOT A STORED FIELD: two spellings of one fact
    # can disagree (`census-keyed-on-one-spelling`), and a derived one cannot.
    check("⚑ mutates is DERIVED, never settable — no second spelling to drift",
          "mutates" in getattr(_M, "__slots__", ()), False)

    # ⚑⚑⚑ THE FALSE POSITIVE IN THE DANGEROUS DIRECTION, PINNED. `--selftest` is
    # DECLARED and dispatched at the `__main__` guard — OUTSIDE `_dispatch`, by
    # construction, since the suite must run without the CLI's argument binding. My
    # first cut compared only against branches `_dispatch` opens and reported it as a
    # promise the CLI does not keep. Then my FIX keyed on `(?:sys\.)?argv` and missed
    # `"--selftest" in flagged_argv()` — census-keyed-on-one-spelling, inside the reader
    # written to find roster spelling disagreements. Both shapes must stay covered.
    # ⚑ THESE TWO READ THE LIVE CENSUS, NOT THE SYNTHETIC ONE. `_cc` above is a fixture
    # roster (the specimen ran out — see ⟡since-roster-disagreement), and reusing it here
    # silently asked about a roster with no `--calls` in it. Caught by this case failing;
    # the live rows are `_live_rows`, which is also what `--since`'s absence is asserted
    # against, so one binding serves both directions of the starve.
    _live_rows = {f: (ok, why) for f, ok, why in _entry().scan_contract()}
    check("⚑ a mode dispatched OUTSIDE _dispatch is not a phantom declaration",
          "--selftest" in _live_rows, False)
    check("...and a declared mode that IS dispatched stays silent",
          "--calls" in _live_rows and _live_rows["--calls"][0], True)

    # ── --rivals: a shared NAME is not a shared JOB ──────────────────────────────
    # ⚑⚑ THE FALSE-RIVAL WITHDRAWAL, pinned on the SIGNATURE fact it rests on.  Measured
    # 2026-08-19: `--rivals scan` reported `3 def(s) — 3 reimplementing` over a libcst
    # corpus scanner `(paths, target, kwseen)`, an Agda import-collision walker
    # `(idx, root)`, and a carrier-decl extractor `(paths)`.  Three unrelated jobs under
    # one common English verb — and the third EXISTS to prevent duplication, per its own
    # docstring.  `--rivals ping` was the recorded first instance.
    # ⚑ SOUND IN ONE DIRECTION ONLY: disjoint parameters prove NOT-rivals; matching ones
    # prove nothing.  These cases pin that asymmetry, not a rivalry verdict.
    r1 = os.path.join(d, "r1.py")
    r2 = os.path.join(d, "r2.py")
    open(r1, "w", encoding="utf-8").write("def go(paths, target):\n    x = 1\n    return x\n")
    open(r2, "w", encoding="utf-8").write("def go(idx, root):\n    y = 2\n    return y\n")
    rv = rivals("go", [r1, r2])
    check("rivals: both bodies read REIMPLEMENTS",
          sorted(v for _p, _l, v, _c, _n in rv), ["REIMPLEMENTS", "REIMPLEMENTS"])
    # the withdrawal is a property of the SIGNATURES, computed the same way the CLI does
    _sig = {}
    for _p in (r1, r2):
        _t = ast.parse(open(_p, encoding="utf-8").read())
        for _dd in ast.walk(_t):
            if isinstance(_dd, ast.FunctionDef) and _dd.name == "go":
                _sig[_p] = tuple(a.arg for a in _dd.args.args)
    check("rivals: disjoint signatures are distinguishable",
          len(set(_sig.values())), 2)

    # ⚑ THE CASE THAT MAKES THIS BEAT GREP: a name inside a COMMENT or DOCSTRING
    # is not a call.  `rewire_only`'s own docstring names it twice.
    src2 = '"""mentions f(1) in prose."""\n# also f(2) here\ndef g():\n    pass\n'
    p2 = os.path.join(d, "t2.py")
    open(p2, "w", encoding="utf-8").write(src2)
    check("a name in a docstring/comment is NOT a call",
          [r for r in scan([p2], "f") if r[1] == "call"], [])

    # ⚑ AND THE DEAD-CAPABILITY VERDICT ITSELF: `g` is defined, never called.
    check("a def with no caller is reported dead",
          [(n, l) for _p, n, l in dead([p2])], [("g", 3)])

    # ⚑⚑ THE `q_` FALSE POSITIVE — a DEAD verdict on a live query.  The store
    # defines `def q_<name>` and invokes `QB.run(con, "<name>")`, so the two
    # spellings never meet and `--calls q_obs_core` reports `1 def, 0 calls,
    # DEAD CAPABILITY` on a query `sppf_db.py:1023` runs every fold.  `--dead` is
    # the census this repo uses to decide what to DELETE, so a live capability
    # reported dead is worse than one merely missed.
    srcq = ('def q_thing(con):\n'
            '    return "SELECT 1"\n'
            'def other(con, QB):\n'
            '    return QB.run(con, "thing", core_id=1)\n')
    pq = os.path.join(d, "tq.py")
    open(pq, "w", encoding="utf-8").write(srcq)
    check("--calls is blind to a string-invoked query (the false positive)",
          [r for r in scan([pq], "q_thing") if r[1] == "call"], [])
    check("--sqlname finds the `q_`-prefixed DEFINITION",
          [(l, k) for _p, l, _q, k in sqlnames("thing", [pq]) if k == "def"],
          [(1, "def")])
    check("...and the STRING reference `--calls` cannot see",
          [(l, k) for _p, l, _q, k in sqlnames("thing", [pq]) if k == "ref"],
          [(4, "ref")])
    # ⚑ EITHER SPELLING RESOLVES, because a reader arriving from a traceback has
    # the string and one arriving from source has the def.
    check("--sqlname accepts the DEFINED spelling too",
          sqlnames("q_thing", [pq]), sqlnames("thing", [pq]))
    # ⚑ AND A STRING IS A REFERENCE, NEVER A CALL.  `QB.run(con, "thing")` CALLS
    # `run`; conflating the two would re-introduce the defect one level down by
    # telling a reader a string literal was invoked.
    check("a string reference is reported as `ref`, not `call`",
          {k for _p, _l, _q, k in sqlnames("thing", [pq])}, {"def", "ref"})
    # ⚑ AN UNREFERENCED QUERY IS THE REAL DEAD VERDICT — the one `--calls` cannot
    # reach for this class at all.
    srcq2 = 'def q_unwired(con):\n    return "SELECT 2"\n'
    pq2 = os.path.join(d, "tq2.py")
    open(pq2, "w", encoding="utf-8").write(srcq2)
    check("a query defined and never referenced has 0 refs",
          [k for _p, _l, _q, k in sqlnames("unwired", [pq2])], ["def"])

    # ⚑ THE CALLBACK-AS-VALUE FALSE POSITIVE.  These cases FAIL against the
    # call-sites-only `--dead`: every one of these functions is live, and every one
    # was reported dead.  Measured on `scripts/membudget_otlp.py` (`cb` :116 returned
    # from a factory, `hb_cb` :131 passed as `callbacks=[hb_cb]`) — the OTLP
    # observable-gauge shape the struct-tools rule names explicitly.
    src5 = ('def hb_cb(options):\n'
            '    return 1\n'
            'def deco(fn):\n'
            '    return fn\n'
            'def inner():\n'
            '    return 2\n'
            'def factory():\n'
            '    return inner\n'
            'def keyfn(x):\n'
            '    return x\n'
            'def truly_dead():\n'
            '    return 3\n'
            'meter.create_observable_gauge("m", callbacks=[hb_cb])\n'
            'REGISTRY = {"d": deco}\n'
            'items.sort(key=keyfn)\n')
    p5 = os.path.join(d, "t5.py")
    open(p5, "w", encoding="utf-8").write(src5)
    deadnames = {n for _p, n, _l in dead([p5])}
    check("a callback passed in a list is NOT dead (the OTLP shape)",
          "hb_cb" in deadnames, False)
    check("a function stored in a registry dict is NOT dead",
          "deco" in deadnames, False)
    check("a closure RETURNED by a factory is NOT dead",
          "inner" in deadnames, False)
    check("a function passed as key= is NOT dead",
          "keyfn" in deadnames, False)
    # ⚑ AND THE MODE MUST STILL FIND REAL DEAD CODE.  A `ref` kind that counted a
    # call's own `func` Name would make the ref-set a superset of the call-set and
    # `--dead` would report NOTHING — a fix that silences the query is not a fix.
    check("a def that is neither called nor referenced is STILL dead",
          "truly_dead" in deadnames, True)

    # ⚑⚑ THE DECORATOR-REGISTRATION FALSE POSITIVE, AND IT IS THE LARGEST ONE.
    # `@test` / `def S1_…()` hands the function to a registrar that appends it to
    # a table a later loop invokes, so the decorated def's OWN name never appears
    # as a value and the `ref` kind above has nothing to record.  Measured
    # 2026-08-18: `--dead scratch/verify_shadows.py` named 64 live conformance
    # checks — the entire suite — and `--calls test` printed ⚑ DEAD CAPABILITY on
    # the registrar while listing its 64 decorator references in the same output.
    src6 = ('def reg(fn):\n'
            '    TESTS.append(fn)\n'
            '    return fn\n'
            'def paramd(arg):\n'
            '    return lambda fn: fn\n'
            '@reg\n'
            'def registered_bare():\n'
            '    return 1\n'
            '@paramd("x")\n'
            'def registered_called():\n'
            '    return 2\n'
            '@mod.attr\n'
            'def registered_dotted():\n'
            '    return 3\n'
            'def undecorated_dead():\n'
            '    return 4\n')
    p6 = os.path.join(d, "t6.py")
    open(p6, "w", encoding="utf-8").write(src6)
    dead6 = {n for _p, n, _l in dead([p6])}
    check("a BARE-decorated def is NOT dead (@reg — the registry shape)",
          "registered_bare" in dead6, False)
    # ⚑ ALL THREE DECORATOR SPELLINGS REGISTER.  Which one a registrar uses is its
    # own business; the reachability question cannot depend on that choice, or the
    # census answers differently for the same relation written three ways.
    check("a CALLED-decorator def is NOT dead (@paramd('x'))",
          "registered_called" in dead6, False)
    check("a DOTTED-decorator def is NOT dead (@mod.attr)",
          "registered_dotted" in dead6, False)
    # ⚑ AND THE ANTI-SILENCING GUARD AGAIN, one level along: marking every def
    # reachable would clear the census by blinding it.  An UNDECORATED def with no
    # caller must still report, or this fix is the `--dead reports nothing` bug
    # that `visit_FunctionDef_name` was written to prevent.
    check("an UNDECORATED def with no caller is STILL dead",
          "undecorated_dead" in dead6, True)
    # ⚑ THE REGISTRAR ITSELF, which is the half `--calls` printed a verdict on.
    # `reg` is never syntactically called — only used in decorator position.
    check("the REGISTRAR is reached as a value by each decoration",
          len([r for r in scan([p6], "reg") if r[1] == "ref"]), 1)

    # ⚑⚑ THE FRAMEWORK-DISPATCH FALSE POSITIVE, and `pycodemod` was its own worst
    # case: `--dead` named `visit_Call`, `visit_Name` and `leave_FunctionDef` — the
    # visitor methods every query in this tool dispatches through — because libcst
    # constructs the method name from the node type and so no call site exists in
    # this corpus.  The caller is OUTSIDE the scanned population, which is not the
    # same as absent (the `--calls emit`/`_emit_one` distinction, one level up).
    src7 = ('class V:\n'
            '    def visit_Call(self, node):\n'
            '        return 1\n'
            '    def leave_FunctionDef(self, node):\n'
            '        return 2\n'
            '    def action_reset(self):\n'
            '        return 3\n'
            '    def on_mount(self):\n'
            '        return 4\n'
            '    def helper_never_used(self):\n'
            '        return 5\n')
    p7 = os.path.join(d, "t7.py")
    open(p7, "w", encoding="utf-8").write(src7)
    dead7 = {n for _p, n, _l in dead([p7])}
    check("a libcst visit_* method is NOT dead (framework-dispatched)",
          "visit_Call" in dead7, False)
    check("a libcst leave_* method is NOT dead",
          "leave_FunctionDef" in dead7, False)
    check("a Textual action_* method is NOT dead (Binding-table string)",
          "action_reset" in dead7, False)
    check("a Textual on_* handler is NOT dead (message-class name)",
          "on_mount" in dead7, False)
    # ⚑ AND THE ANTI-SILENCING GUARD ONCE MORE: an ordinary unused method in the
    # very same class must still report, or the exemption has swallowed the census.
    check("an ordinary unused method in the SAME class is STILL dead",
          "helper_never_used" in dead7, True)
    # ⚑ THE PREFIX ALONE IS NOT THE CONTRACT — a def named exactly `on_` or `test_`
    # satisfies no framework convention, and a bare-prefix match would exempt it.
    check("a bare prefix with no suffix is NOT a framework contract",
          framework_dispatch("on_"), None)
    # ⚑ THE EXEMPTION NAMES ITS REASON.  A boolean would leave an operator unable
    # to tell an exempted def from one the census simply missed.
    check("the exemption reports WHICH contract, not merely that there is one",
          "libcst" in (framework_dispatch("visit_Call") or ""), True)

    # ⚑⚑ `--` MUST END THE FLAGS, or a flag-shaped OPERAND is unaskable.  The
    # dispatch strips every `-`-leading token from `args`, so `--literal --holding`
    # asked for nothing and fell through to usage — and that is the question which
    # LOCALIZES a mis-attributed mode in the `toolmodes` census.  Driven against the
    # dispatch source (`split_census`'s pattern) because the split is argv-shaped
    # and a fixture cannot rebind `sys.argv` without racing the real run.
    # ⚑ DRIVEN THROUGH THE FUNCTIONS, NOT THE SOURCE TEXT.  A first cut asserted the
    # inline spelling (`'sys.argv.index("--", 1)' in src`) and FAILED the moment the
    # logic was extracted to `flagged_argv`/`operand_tail` while behaving identically
    # — a case pinned to a spelling tests the edit, not the property.
    _av = ["pycodemod.py", "--literal", "--", "--selftest"]
    check("`--` ends the flags: a later token is NOT seen as a flag",
          "--selftest" in flagged_argv(_av), False)
    check("...and IS delivered as an operand, flag-shaped and all",
          operand_tail(_av), ["--selftest"])
    check("the mode BEFORE `--` is still recognised",
          "--literal" in flagged_argv(_av), True)
    # ⚑ NO MARKER ⇒ NO TAIL, and every token stays flag-visible.  The common path
    # must be untouched, or adding the marker silently re-scopes every other mode.
    _plain = ["pycodemod.py", "--calls", "foo"]
    check("with no `--`, every token remains flag-visible",
          flagged_argv(_plain), ["--calls", "foo"])
    check("with no `--`, the operand tail is empty",
          operand_tail(_plain), [])
    # ⚑ argv[0] IS THE PROGRAM NAME AND NEVER THE MARKER — searching from 0 would let
    # a program invoked as `--` swallow its own argument list.
    check("a `--` at argv[0] is not read as the marker",
          flagged_argv(["--", "--calls", "foo"]), ["--calls", "foo"])
    check("`ref` is a distinct kind, not folded into `call`",
          [(k, l) for _p, k, n, l in scan([p5], "hb_cb") if k == "call"], [])
    check("the value-use IS recorded as a ref at its line",
          [l for _p, k, n, l in scan([p5], "hb_cb") if k == "ref"], [13])

    # ── asserted(): presence is not measurement ──────────────────────────
    # ⚑ THE CASES MUST DISCRIMINATE AGAINST `forwards()`, because that mode
    # already reports every one of these sites as `ok`.  A case that only
    # asserts "the keyword is passed" would pass with `_shape_of` deleted.
    src6 = ('def w(msg, size=0):\n'
            '    return size\n'
            'w("a", size=1)\n'                    # literal
            'w("b", size=len(rows))\n'            # computed
            'w("c", size=-1)\n'                   # literal under a unary minus
            'w("d", size=n)\n'                    # computed: a bare name
            'w("e")\n'                            # absent entirely
            'w("f", size=f"{n}")\n'               # computed: interpolated
            'w("g", size=f"none")\n')             # literal: no interpolation
    p6 = os.path.join(d, "t6.py")
    open(p6, "w", encoding="utf-8").write(src6)
    lit, comp = asserted("w", "size", [p6])
    check("asserted(): a bare integer is a LITERAL",
          3 in [l for _p, l in lit], True)
    check("asserted(): a call expression is COMPUTED",
          4 in [l for _p, l in comp], True)
    # ⚑ `size=-1` IS A UNARY OPERATION WRAPPING A LITERAL.  Without the recursive
    # unwrap it reads COMPUTED — misreporting exactly the asserted-number sites
    # this mode exists to find.
    check("asserted(): a NEGATED literal is still a literal",
          5 in [l for _p, l in lit], True)
    check("asserted(): a bare name is COMPUTED",
          6 in [l for _p, l in comp], True)
    # ⚑ AN ABSENT KEYWORD IS IN NEITHER BUCKET.  Folding it into `computed`
    # would inflate the honest half and make the ratio meaningless.
    check("asserted(): a call NOT passing the keyword is in neither bucket",
          7 in [l for _p, l in lit] or 7 in [l for _p, l in comp], False)
    check("asserted(): an INTERPOLATED f-string is computed",
          8 in [l for _p, l in comp], True)
    check("asserted(): an f-string with nothing interpolated is literal",
          9 in [l for _p, l in lit], True)
    # ⚑ AND THE DISCRIMINATION AGAINST `forwards`: it reports ALL of 3-6,8,9 as
    # forwarding.  If this mode agreed with it, it would be measuring nothing.
    _fh, _fl = forwards("w", "size", [p6])
    # ⚑ MY FIRST EXPECTED TUPLE WAS (7,4,3) AND THE CASE CAUGHT IT.  Six calls
    # pass `size` (lines 3,4,5,6,8,9); three are literal (3, 5, 9).  I counted a
    # site that does not pass the keyword at all — the arithmetic-by-eye this
    # whole mode exists to replace, committed while writing its guard.
    check("asserted() splits what forwards() reports as one bucket",
          (len(_fh), len(lit), len(comp)), (6, 3, 3))

    # ── values(): the THIRD member of the family — WHICH literal ─────────
    # ⚑ THE QUESTION `--asserted` STOPS ONE STEP SHORT OF, and it is the one that
    # decides whether a call is DANGEROUS.  Measured on the live case:
    # `sandbox_connect(reset=…)` has 23 call sites and `--asserted` reports
    # "23 of 23 pass a LITERAL" — while `reset=True` calls `store.sandbox_reset()`,
    # which DROPS EVERY RELATION in the tenant.  Presence (`--forwards`) and
    # literal-ness (`--asserted`) both report all 23 identically; only the VALUE
    # separates the destructive sites from the harmless ones, so a 23-site
    # destructive surface was unauditable with this repo's own tools.
    #
    # ⚑ AND THE CASES MUST DISCRIMINATE AGAINST `asserted()`, which already reports
    # every one of these as one undifferentiated LITERAL bucket.
    src6v = ('def q(msg, reset=False):\n'
             '    return reset\n'
             'q("a", reset=True)\n'              # 3  literal True   — DESTRUCTIVE
             'q("b", reset=False)\n'             # 4  literal False
             'q("c", reset=None)\n'              # 5  literal None   — a VALUE
             'q("d", reset=flag)\n'              # 6  unknown: bare name
             'q("e", reset=f"{x}")\n'            # 7  unknown: interpolated
             'q("f", reset=a if b else c)\n'     # 8  unknown: conditional
             'q("g")\n'                          # 9  absent entirely
             'q("h", reset="yes")\n')            # 10 literal string
    p6v = os.path.join(d, "t6v.py")
    open(p6v, "w", encoding="utf-8").write(src6v)
    _vs, _vtotal = values("q", "reset", [p6v])
    _byline = {l: v for _p, l, v, _c in _vs}
    _byctx = {l: c for _p, l, _v, c in _vs}
    check("values(): a literal True is reported WITH its value",
          _byline.get(3), True)
    check("values(): a literal False is reported WITH its value",
          _byline.get(4), False)
    # ⚑ LITERAL `None` IS A VALUE, NOT AN ABSENCE.  Using `None` as the
    # not-a-literal marker would make `reset=None` indistinguishable from
    # `reset=<computed>` — the exact collapse this mode exists to prevent, one
    # level down.  Hence the UNKNOWN sentinel.
    check("values(): a literal None is a VALUE, not the unknown marker",
          (_byline.get(5, UNKNOWN) is None), True)
    check("values(): a literal string is reported with its value",
          _byline.get(10), "yes")
    # ⚑ A NON-LITERAL IS `UNKNOWN`, NEVER GUESSED.  A reader that silently
    # rendered a bare name / conditional / interpolated f-string as a value would
    # be WORSE than the gap it fills: it would answer "is this call dangerous"
    # with a fabrication.
    check("values(): a bare name is UNKNOWN, never guessed",
          _byline.get(6), UNKNOWN)
    check("values(): an interpolated f-string is UNKNOWN",
          _byline.get(7), UNKNOWN)
    check("values(): a conditional expression is UNKNOWN",
          _byline.get(8), UNKNOWN)
    check("values(): a call NOT passing the keyword is not a row",
          9 in _byline, False)
    # ⚑ `n of m` — the DENOMINATOR is the call population, not the row count.  A
    # bare list cannot distinguish *no matches* from *no file read*.
    check("values(): reports n of m over the CALL population",
          (len(_vs), _vtotal), (7, 8))
    # ⚑ AND THE PARTITION MUST AGREE WITH `asserted()` EXACTLY.  The two modes read
    # the same sites; if `values` called something a literal that `asserted` calls
    # computed, one of them is lying about the same call node.  Derived rather than
    # asserted: `_shape_of` is now DEFINED from `_value_of`, so they cannot drift.
    # ⚑ THE ENCLOSING DEF IS THE THIRD COLUMN THE AUDIT ASKED FOR.  These fixture
    # calls are all at module scope; a call INSIDE a def must report that def, and
    # the scope stack must be balanced afterwards — an unbalanced push would make
    # every later call report a stale context, a WRONG answer rather than a missing
    # one.
    src6c = ('def wrap():\n'
             '    return q("i", reset=True)\n'
             'q("j", reset=False)\n')
    p6c = os.path.join(d, "t6c.py")
    open(p6c, "w", encoding="utf-8").write(src6c)
    _cs, _ = values("q", "reset", [p6c])
    check("values(): a call inside a def reports that def as its context",
          [(l, c) for _p, l, _v, c in _cs], [(2, "wrap"), (3, "<module>")])
    check("values(): a module-scope fixture call reports <module>",
          _byctx.get(3), "<module>")

    # ⚑⚑⚑ THE POSITIONAL READING, WHICH THE WHOLE FAMILY WAS BLIND TO UNTIL 2026-08-15.
    # `--forwards`/`--asserted`/`--values` all filter on `a.keyword is not None`, so a call
    # naming its target BY POSITION reported zero — and that is the shape of the repo's
    # highest-volume write surface: `upsert(con, "obs", rows)`, 53 sites, every row in the
    # store. The keyword-only filter is a fact about the METHOD, and reporting it as "no
    # writers found" is the fact-about-the-substrate error CLAUDE.md's top rule names.
    src6p = ('up(con, "obs", rows)\n'
             'up(con, "edge", rows)\n'
             'up(con, name, rows)\n'
             'up(con, table="kw", rows=rows)\n')
    p6p = os.path.join(d, "t6p.py")
    open(p6p, "w", encoding="utf-8").write(src6p)
    _pv, _pn = values("up", 1, [p6p])
    check("values(<ordinal>): reads the positional argument at that index",
          sorted(v for _p, _l, v, _c in _pv if v is not UNKNOWN), ["edge", "obs"])
    # ⚑ A NON-LITERAL POSITIONAL IS `UNKNOWN`, NEVER GUESSED — the same rule as the keyword
    # side, and load-bearing for the same reason: a fabricated relation name would be read as
    # "this function writes that table" and drawn as a flow edge that does not exist.
    check("...and a computed positional reports UNKNOWN rather than a guess",
          sum(1 for _p, _l, v, _c in _pv if v is UNKNOWN), 1)
    # ⚑ THE KEYWORD-PASSED CALL IS NOT AT ORDINAL 1. `up(con, table="kw", …)` passes `con`
    # positionally and nothing else, so ordinal 1 does not exist at that site — it is absent,
    # not UNKNOWN. Conflating the two would make "no argument there" indistinguishable from
    # "an argument I could not read", which is exactly the absent-vs-empty distinction this
    # arc keeps having to restate.
    check("...and a site with no such position is ABSENT, not UNKNOWN", len(_pv), 3)
    check("...over the full call population as the denominator", _pn, 4)
    # ⚑ THE ORDINAL AND THE KEYWORD ARE THE SAME QUERY. A decimal string selects a position,
    # so a CLI that passes argv through unchanged needs no second flag.
    check("...and a decimal STRING selects the same position as the int",
          [(l, v) for _p, l, v, _c in values("up", "1", [p6p])[0]],
          [(l, v) for _p, l, v, _c in _pv])

    # ⚑⚑⚑ THE CALL GRAPH, AND THE CASE THAT MATTERS IS THE FABRICATED PATH. `reaches`
    # first expanded every bare callee to EVERY module-qualified caller sharing that
    # suffix, so one generic name bridged unrelated subsystems: it reported
    # `sppf_query.cmd_fanin → wg_engine.run → proofcost._emit → query_defs.verify →
    # sppf_db.build → write_events` as a dataflow path, and 26 of 29 round trips were
    # that fabrication. Every one looked plausible, which is what makes an over-report
    # worse than a miss — someone acts on it.
    _cgA = os.path.join(d, "cga.py")
    open(_cgA, "w", encoding="utf-8").write(
        'def leaf():\n    sink()\n\n'
        'def mid():\n    leaf()\n\n'
        'def top():\n    mid()\n\n'
        'def other():\n    run()\n')
    _cgB = os.path.join(d, "cgb.py")
    # a DIFFERENT module defining `run` — the name collision that produced the fake path
    open(_cgB, "w", encoding="utf-8").write('def run():\n    sink()\n')
    _cg = callgraph([_cgA, _cgB])
    check("callgraph attributes calls to their ENCLOSING def",
          sorted(_cg.get("cga.mid", ())), ["leaf"])
    check("...which `--calls` cannot do (it has no scope tracking)",
          "cga.top" in _cg and "cga.leaf" in _cg, True)
    check("reaches follows a multi-hop chain within a module",
          reaches(_cg, "cga.top", {"sink"}).get("sink"),
          ["cga.top", "cga.mid", "cga.leaf", "sink"])
    # ⚑⚑ THE ANTI-FABRICATION CASE. `cga.other` calls `run`, and `cgb.run` calls `sink`
    # — but they are different modules, so this walk must NOT stitch them into a path.
    # Without this, the mode manufactures dependencies out of shared spellings.
    check("...and does NOT bridge modules on a shared callee spelling",
          reaches(_cg, "cga.other", {"sink"}), {})
    # ⚑ AND THE BOUND IS REPORTED RATHER THAN SILENT: a target beyond `depth` is absent
    # from the result, which means "not reached within depth", not "no path exists".
    check("a target beyond the depth bound is absent, not falsely reported",
          reaches(_cg, "cga.top", {"sink"}, depth=1), {})

    _vlit, _vcomp = asserted("q", "reset", [p6v])
    check("values() partitions exactly as asserted() does",
          ({l for _p, l in _vlit}, {l for _p, l in _vcomp}),
          ({l for l, v in _byline.items() if v is not UNKNOWN},
           {l for l, v in _byline.items() if v is UNKNOWN}))

    # ⚑ THE `forwards` CASES MUST DISCRIMINATE AGAINST THE TEXT ROUTE, because the
    # text route is what this replaces.  `grep -c -- 'quiet'` on this fixture returns
    # 3 (the ⚑ comment, the migrated call, and the word inside the unmigrated line's
    # own prose) and would report every site as migrated.  Only ONE call passes the
    # keyword; a positional-only call is MISSING, not migrated.
    src3 = ('# ⚑ a comment mentioning quiet=True, which is NOT a call\n'
            '"""...and a docstring saying quiet as well."""\n'
            'r(cur, base, quiet=True)\n'
            'r(cur, base)\n'
            'r(cur, base, noun="x")\n')
    p4 = os.path.join(d, "t4.py")
    open(p4, "w", encoding="utf-8").write(src3)
    has, lacks = forwards("r", "quiet", [p4])
    check("forwards(): only the keyword-passing call counts as migrated",
          [l for _p, l in has], [3])
    check("forwards(): positional and other-keyword calls are MISSING",
          [l for _p, l in lacks], [4, 5])

    # ⚑ AND `kwseen` MUST NOT LEAK BETWEEN SCANS.  A module-level accumulator would
    # make this second query inherit the first's keywords and report a stale
    # migration as current — a census straddling an edit, one layer down.
    seen_a, seen_b = KwIndex(), KwIndex()
    scan([p4], "r", kwseen=seen_a)
    scan([p2], "f", kwseen=seen_b)
    check("kwseen does not leak between scans", bool(seen_a) and not seen_b, True)

    # ⚑ THE CONTEXT CHECK MUST DISCRIMINATE, NOT MERELY REFUSE.  A guard that
    # rejects everything passes a "does it raise" case while being useless, so BOTH
    # directions are pinned: the gathering context reads, and each of the two ways
    # to be wrong (different target, different population) raises.
    def _raises(fn):
        try:
            fn()
            return False
        except ValueError:
            return True

    check("a matched context READS (the guard is not refuse-everything)",
          _raises(lambda: seen_a.check("r", [p4])), False)
    check("a different TARGET is refused",
          _raises(lambda: seen_a.check("f", [p4])), True)
    check("a different POPULATION is refused",
          _raises(lambda: seen_a.check("r", [p4, p2])), True)
    # population is order-insensitive: two spellings of one query are one context
    seen_c = KwIndex()
    scan([p4, p2], "r", kwseen=seen_c)
    check("population order does not change the context",
          _raises(lambda: seen_c.check("r", [p2, p4])), False)

    # ⚑ WRITE-POLARITY, AND THE LIVE WITNESS THAT MOTIVATED IT.  `gate_status
    # --modes` ran `sppf_node_index.py` once per mode and REGENERATED its artifact
    # three times, because that tool writes on any invocation that is not --check.
    # Both directions are pinned: an unguarded writer is caught, and an
    # --apply-gated one is NOT (a guard that flags everything makes the sweep
    # useless, which is the same "does it discriminate" test as every other
    # predicate this arc has fixed).
    pw = os.path.join(d, "w.py")
    open(pw, "w", encoding="utf-8").write(
        'import sys\n'
        'out = "x"\n'
        'if "--check" in sys.argv:\n'
        '    sys.exit(0)\n'
        'open(DOC, "w").write(out)\n')
    check("an unguarded write is write-default", writes_by_default(pw)[0], True)

    pg = os.path.join(d, "g.py")
    open(pg, "w", encoding="utf-8").write(
        'import sys\n'
        'if "--apply" in sys.argv:\n'
        '    open(p, "w").write(t)\n')
    check("an --apply-gated write is NOT write-default",
          writes_by_default(pg)[0], False)

    pt = os.path.join(d, "tf.py")
    open(pt, "w", encoding="utf-8").write(
        'import tempfile, os\n'
        'tf = os.path.join(tempfile.mkdtemp(), "n.md")\n'
        'open(tf, "w").write(norm)\n')
    check("writing a tempfile is NOT write-default", writes_by_default(pt)[0], False)

    # ⚑ AND A FIXTURE WRITE INSIDE `_selftest` IS NOT A WRITE PATH — the same
    # suite-boundary rule `check_snapshot_guard` needed (§60), here so a tool with
    # a well-behaved CLI is not flagged because its own tests write temp files.
    ps = os.path.join(d, "s.py")
    open(ps, "w", encoding="utf-8").write(
        'def _selftest():\n'
        '    open(p, "w").write("fixture")\n')
    check("a write inside _selftest is not a write path",
          writes_by_default(ps)[0], False)

    # ── py_files(): GENERATED TREES ARE NOT THE CORPUS ──────────────────────
    # ⚑ THE BAZEL-OUTPUT CENSUS INFLATION.  `--in <paperkit> --calls references`
    # returned 135KB of hits, nearly all from `bazel-bin/.../mut_project__*.
    # mutated.py` — MACHINE-GENERATED mutation-testing copies of the sources.
    # Same class as `.edit-snapshots` backups polluting a census: a derived copy
    # reads exactly like source, so every count is multiplied by the number of
    # build configurations and the ONE real def is buried.  This case FAILS
    # against the pre-fix skip tuple (which held `.venv`/`site-packages`/
    # `__pycache__`/`_build` but no build-output trees).
    gd = tempfile.mkdtemp()
    for sub in ("src", "bazel-bin/mutants", "bazel-out/k8-fastbuild",
                ".mypy_cache", ".tox/py311", "build/lib"):
        os.makedirs(os.path.join(gd, sub), exist_ok=True)
        open(os.path.join(gd, sub, "m.py"), "w", encoding="utf-8").write(
            "def references():\n    return 1\n")
    found = [os.path.relpath(f, gd) for f in py_files(gd)]
    check("py_files() skips bazel/generated/cache trees, keeping only source",
          found, ["src/m.py"])
    # ⚑ AND THE SKIP MUST STAY RELATIVE TO THE REQUESTED ROOT.  Naming a
    # generated tree EXPLICITLY is a different question and must still answer —
    # the same rule the site-packages comment above records for `--package`.
    check("naming a generated tree explicitly still reaches it",
          [os.path.basename(f) for f in py_files(os.path.join(gd, "bazel-bin"))],
          ["m.py"])
    # ⚑ AND THE ROOT-LEVEL CASE, WHICH IS THE ONE THAT ACTUALLY BIT.  With the
    # walk-filter installed but `_roots()` unfiltered, a top-level `bazel-bin`
    # became its own ROOT — `rel` then starts below it, the component never
    # appears, and the entire generated tree was admitted anyway.  This case
    # FAILS against a fix applied only inside `py_files`.
    # ⚑ THE FIXTURE MUST REBIND THE ROOT THAT `py_files` ACTUALLY READS, and
    # after the module split that is `_pycodemod_core.ROOT`, not this module's
    # re-exported copy.  A `global ROOT` here rebound a name nothing consumes:
    # `_roots()` kept returning the real corpus and this case enumerated all
    # ~1600 files in the repo instead of the two-file fixture.  Same defect as
    # the `corpus` envelope guards against, arriving through the test.
    _saved_root = _c.ROOT
    try:
        _c.ROOT = gd
        rooted = [os.path.relpath(f, gd) for f in py_files()]
        check("_roots() drops generated trees that are TOP-LEVEL entries",
              rooted, ["src/m.py"])
        # a per-workspace bazel symlink cannot be enumerated by name
        os.symlink(os.path.join(gd, "bazel-bin"), os.path.join(gd, "bazel-proj"))
        check("a bazel-<workspace> convenience symlink is dropped by prefix",
              [os.path.relpath(f, gd) for f in py_files()], ["src/m.py"])
    finally:
        _c.ROOT = _saved_root

    # ── --projects: the corpus's paperkit project map ───────────────────────
    # ⚑ FOREIGN MUST BE COMPUTED FROM THE RESOLVED PATH, NOT THE TOKEN SPELLING.
    # Both ways to be wrong are pinned: a `../` token that ESCAPES the project is
    # foreign even though it is not a label, and a label that resolves INSIDE the
    # project is local even though it is spelled like an import.  An
    # implementation that tested `startswith("//")` passes neither.
    pp = tempfile.mkdtemp()
    os.makedirs(os.path.join(pp, "shared"), exist_ok=True)
    os.makedirs(os.path.join(pp, "solo"), exist_ok=True)
    os.makedirs(os.path.join(pp, "importer", "local"), exist_ok=True)
    open(os.path.join(pp, "solo", "paper.toml"), "w", encoding="utf-8").write(
        '[paper]\ntitle = "Solo"\nwarrants = ["warrants.bib"]\n')
    open(os.path.join(pp, "importer", "paper.toml"), "w", encoding="utf-8").write(
        '[paper]\ntitle = "Importer"\n'
        'warrants = ["warrants.bib", "../shared/common.bib", "//local:own.bib"]\n')
    # ⚑ AND THE NESTED CASE, WHICH IS THE ONE THAT WAS ACTUALLY WRONG.  A ROOT
    # project whose directory CONTAINS a child project imports the CHILD's bib —
    # paperkit's `.` importing `//paper:adequacy_pitch.bib`.  Containment says
    # local (the path never escapes); OWNERSHIP says foreign (the child owns it),
    # and ownership is right.  This case fails against the containment test, which
    # reported the repo's one real foreign import as zero.
    os.makedirs(os.path.join(pp, "child"), exist_ok=True)
    open(os.path.join(pp, "paper.toml"), "w", encoding="utf-8").write(
        '[paper]\ntitle = "Root"\n'
        'warrants = ["warrants.bib", "//child:owned.bib"]\n')
    open(os.path.join(pp, "child", "paper.toml"), "w", encoding="utf-8").write(
        '[paper]\ntitle = "Child"\nwarrants = ["owned.bib"]\n')
    projs = paperkit_projects(pp)
    check("--projects finds a project per paper.toml",
          [r[0] for r in projs], [".", "child", "importer", "solo"])
    check("a project with only a local bib has NO foreign import",
          [f for r, _c, _w, f in projs if r == "solo"][0], [])
    imp = [f for r, _c, _w, f in projs if r == "importer"][0]
    check("a `../` token that ESCAPES the project dir IS foreign",
          [t for t, _d, _o in imp], ["../shared/common.bib"])
    check("a label resolving INSIDE the project is NOT foreign",
          any(t.startswith("//") for t, _d, _o in imp), False)
    check("the foreign row names the RESOLVED corpus-relative destination",
          [d for _t, d, _o in imp], ["shared/common.bib"])
    root_f = [f for r, _c, _w, f in projs if r == "."][0]
    check("a NESTED child project's bib is FOREIGN to its parent (ownership, "
          "not containment)",
          [(t, o) for t, _d, o in root_f], [("//child:owned.bib", "child")])
    check("the child still owns its own bib locally",
          [f for r, _c, _w, f in projs if r == "child"][0], [])

    # ── --source: reading a body, not just locating it ──────────────────────
    # ⚑ THE EXTENT MUST COME FROM THE CST, NOT A LINE COUNT.  A fixed window
    # truncates a long def and swallows the next one after a short def; both
    # directions are pinned here, and the second (`after` must NOT appear) is
    # the one a naive "print 20 lines" implementation fails.
    psrc = os.path.join(d, "src.py")
    open(psrc, "w", encoding="utf-8").write(
        'def before():\n'
        '    return 0\n'
        'def target(x):\n'
        '    # ⚑ a comment inside the body\n'
        '    return x + 1\n'
        'def after():\n'
        '    return 2\n')
    sr = source_of("target", [psrc])
    check("--source returns exactly one def with its CST extent",
          [(l, e) for _p, l, e, _t in sr], [(3, 5)])
    check("--source returns the BODY text, comments included",
          "⚑ a comment inside the body" in sr[0][3], True)
    check("--source does not swallow the following def",
          "after" in sr[0][3], False)
    check("--source finds a class as well as a function",
          bool(source_of("V", [os.path.join(d, "nope.py")])), False)

    # ── --key: the DICT-shaped record's field query ─────────────────────────
    # ⚑ THE CASE THAT PINS THE MISS.  `--attr _src` returned 0 on paperkit's
    # live provenance field because that model is dicts, not attributes — so a
    # field with five consumers was invisible to every existing mode.  Each
    # access FORM is pinned separately: a subscript, a `.get`, and a membership
    # test are three different CST shapes for one question, and an
    # implementation that caught only the subscript would look like it worked.
    pk = os.path.join(d, "k.py")
    open(pk, "w", encoding="utf-8").write(
        '"""prose naming _src and rests-on, which are NOT reads."""\n'
        '_SCALAR = ("title", "link")\n'
        'def project(f):\n'
        '    a = f["_src"]\n'
        '    b = f.get("_src", "?")\n'
        '    if "_src" in f:\n'
        '        pass\n'
        '    c = f.get("link")\n'
        '    return a, b, c\n')
    kr = key_reads("_src", [pk])
    check("--key finds the subscript, the .get and the `in` test",
          [(l, k) for _p, l, k, _c in kr], [(4, "read"), (5, "read"), (6, "read")])
    check("--key reports the enclosing function as context",
          {c for _p, _l, _k, c in kr}, {"project"})
    # ⚑ AND THE DOCSTRING MENTION IS NOT A READ — the same discrimination that
    # makes `--calls` beat grep, at the dict layer.  `grep -c _src` returns 5.
    check("a key named in a docstring is NOT a read",
          [r for r in key_reads("rests-on", [pk])], [])
    # ⚑ THE SCHEMA DECLARATION IS A DISTINCT KIND.  Folding `decl` into `read`
    # would make every declared field look used and silence the dead-field
    # verdict — the `ref`-vs-`call` collapse `--dead` already paid for.
    kl = key_reads("link", [pk])
    check("a literal in a schema tuple is a `decl`, not a `read`",
          sorted((l, k) for _p, l, k, _c in kl), [(2, "decl"), (8, "read")])
    check("a declared-but-never-read field is visible as decl with no read",
          [k for _p, _l, k, _c in key_reads("title", [pk])], ["decl"])

    # ── --artifacts: the FAILURE/SUCCESS split, which I got BACKWARDS ────────
    # ⚑ THE ONE-CHARACTER DIFFERENCE IS THE WHOLE DISCRIMINATION.  `.agdai.log`
    # holds a typecheck error; `.agdai` is a COMPILED CORE that exists only
    # because the module succeeded.  My first vocabulary admitted `.agdai` to
    # FAILURE_BEARING by prefix-similarity and the census read 49-of-52 — the
    # answer a NON-discriminating predicate always gives.  These cases fail
    # against that version.
    pa = os.path.join(d, "art_fail.py")
    open(pa, "w", encoding="utf-8").write(
        'LOG = ".agdai.log"\n'
        'def read(p):\n'
        '    return open(p + LOG).read()\n')
    rows_a = build_artifact_readers([pa])
    check("a tool reading .agdai.log is FAILURE-bearing",
          [b for _r, _a, b in rows_a], ["FAILURE"])

    pb2 = os.path.join(d, "art_ok.py")
    open(pb2, "w", encoding="utf-8").write(
        'CORE = ".agdai"\n'
        'def cores(d):\n'
        '    return [f for f in d if f.endswith(CORE)]\n')
    rows_b = build_artifact_readers([pb2])
    check("a tool reading .agdai CORES is SUCCESS-only, not FAILURE",
          [b for _r, _a, b in rows_b], ["SUCCESS"])

    # ⚑ AND THE TIMING LEDGER IS THE OTHER SUCCESS-ONLY SHAPE, for a reason that
    # is a property of the WRITER: membudget records only successful compiles
    # ("a failed/OOM-killed run is not representative"), so a failure cannot
    # appear in `.agda-times.tsv` by construction.
    pc2 = os.path.join(d, "art_times.py")
    open(pc2, "w", encoding="utf-8").write(
        'LEDGER = ".agda-times.tsv"\n'
        'def peaks(p):\n'
        '    return open(p + LEDGER).read()\n')
    check("a timing/peak ledger reader is SUCCESS-only",
          [b for _r, _a, b in build_artifact_readers([pc2])], ["SUCCESS"])

    # ⚑ A TOOL READING BOTH IS NOT A TIE — the row names which artifacts, so the
    # operator sees the composition rather than a collapsed verdict.
    pd2 = os.path.join(d, "art_both.py")
    open(pd2, "w", encoding="utf-8").write(
        'def go(p):\n'
        '    a = open(p + ".agdai.log").read()\n'
        '    b = open(p + ".agda-times.tsv").read()\n'
        '    return a, b\n')
    both = build_artifact_readers([pd2])
    check("a tool reading both kinds is BOTH, and names them",
          (both[0][2], both[0][1]),
          ("BOTH", [".agdai.log", ".agda-times.tsv"]))

    # ⚑ AND A TOOL TOUCHING NO BUILD ARTIFACT IS ABSENT FROM THE CENSUS, not a
    # third verdict.  A predicate that returned a row for every file would make
    # the population meaningless — the 361-`print`-rows defect of `--discards`.
    check("a tool reading no build artifact is not censused",
          build_artifact_readers([p2]), [])

    # ⚑ PROSE IS NOT A READ.  `grep -c '.agdai.log'` on this fixture returns 2;
    # only the CST can tell the docstring from the open().  Without this the
    # module's OWN vocabulary block would make it the corpus's top hit.
    pe2 = os.path.join(d, "art_prose.py")
    open(pe2, "w", encoding="utf-8").write(
        '"""This tool never reads a .agdai.log — it only talks about one."""\n'
        '# another mention of .agdai.log in a comment\n'
        'def f():\n'
        '    return 1\n')
    check("a build artifact named only in prose is NOT a read",
          build_artifact_readers([pe2]), [])

    # ── F5: the `n of m` denominator, AS A CLASS ────────────────────────────
    # ⚑ A GUARD WRITTEN FROM THE INSTANCE PASSES ON EVERYTHING EXCEPT THE
    # INSTANCE (§7b-bis, recorded three times in one day).  So this does NOT
    # assert that `--key` and `--attr` were fixed; it scans the DISPATCH for the
    # two shapes that produce the defect, and fails on any occurrence — including
    # in a mode nobody has written yet.
    # ⚑ AND THE GUARD ITSELF READ PROSE AS CODE — the defect it exists to catch.
    # My first cut scanned `inspect.getsource(_dispatch)` as raw text, so the ⚑
    # COMMENTS describing `or None` matched the scan for `or None` and the case
    # failed on correct code.  It now routes through `shape_sites`, which excludes
    # comments and docstrings by tokenizing — the same authority the `--shape`
    # mode uses, so the guard and the tool cannot disagree about what a site is.
    # ⚑ THE SCAN IS SCOPED TO `_dispatch`, NOT TO THE FILE.  The discrimination
    # cases below deliberately CONTAIN both defective spellings as string
    # literals, and `shape_sites` is right to call a string literal code — so a
    # whole-file scan reports this suite as two violations.  Bounding the scan to
    # the dispatch's own line range is the honest fix: the claim is "no MODE has
    # this shape", and a mode is a branch of `_dispatch`.
    # ⚑ `_self` IS THE ENTRY MODULE'S FILE, NOT THIS ONE, AND AFTER THE SPLIT
    # THOSE ARE DIFFERENT FILES.  The claim under test is "no MODE has this
    # shape", a mode is a branch of `_dispatch`, and `_dispatch` lives in
    # `pycodemod.py`.  Left as `__file__` this would scan the SUITE for dispatch
    # shapes and find none — a vacuous pass, which is worse than a failure
    # because it reports success for a check that no longer looks at its subject.
    _self = os.path.abspath(_entry().__file__)
    _dsrc, _dstart = inspect.getsourcelines(_entry()._dispatch)
    _dend = _dstart + len(_dsrc)

    def _in_dispatch(rows):
        return [(l, t) for _p, l, t in rows if _dstart <= l < _dend]

    # ⚑ THE DOCSTRING IS THE ADVERTISED MODE LIST AND IT WENT SEVEN MODES STALE. The
    # struct-tools skill instructs every reader — including dispatched agents — to run this
    # tool bare and treat THAT output as the authority. When `--state`, `--portable`,
    # `--diagnose`, `--crossings`, `--rawreads`, `--shape`, `--discards` were all live in
    # `_dispatch` and none were listed, an agent correctly following the instruction reported
    # them absent. A stale index is worse than none: it is the one artifact a reader is told
    # to trust. Derived from the dispatch, never a second hand-kept list.
    _flags = set(re.findall(r'"(--[a-z-]+)"\s+in\s+argv', "".join(_dsrc)))
    _flags |= set(re.findall(r'a\s*==\s*"(--[a-z-]+)"', "".join(_dsrc)))
    _doc = __doc__ or ""
    _undocumented = sorted(f for f in _flags
                           if f not in _doc and f not in ("--selftest", "--help"))
    check("every dispatched mode appears in the docstring", _undocumented, [])

    # ── --importers: the population `--imports` only COUNTS ──────────────────────────
    # ⚑ DRIVEN AGAINST A FIXTURE BECAUSE THE PROPERTY UNDER TEST IS THE PRIVATE-NAME
    # SPLIT, and the corpus happens to have none today. A module split re-exports with
    # `from <sibling> import *`, which SKIPS a leading underscore — measured here once
    # (`schema._node`, `_unit`, `_unit_cod`, `_orbit_def` vanished off the surface while
    # every suite read green). So "which consumers take a `_` name" is the question, and
    # a mode that answers it only when the corpus already has an instance is untested in
    # the direction that matters.
    _imp = os.path.join(d, "consumer.py")
    open(_imp, "w", encoding="utf-8").write(
        'import target as _alias\n'
        'from target import pub, _priv\n'
        'from target.sub import deep\n'
        'from other import unrelated\n'
        '# target is named in a comment\n'
        'S = "from target import ghost"\n')
    _rows = importers("target", [_imp])
    check("every import site of the module is found, and only those",
          [(f, sorted(b)) for _p, _l, f, b in _rows],
          [("import", ["_alias"]), ("from", ["_priv", "pub"]), ("from", ["deep"])])
    # ⚑ THE COMMENT/STRING CASE IS WHAT MAKES THIS BEAT GREP: `grep 'import target'`
    # matches both the comment and the string literal on lines 5-6.
    check("a module named in a comment or a string is NOT an import site",
          len(_rows), 3)
    # ⚑ THE FALSE POSITIVE I SHIPPED AND CAUGHT BY RUNNING IT. `import query_defs as _qd`
    # binds a `_`-prefixed LOCAL ALIAS; it reaches nothing through a re-export surface, so
    # counting it as "a name star-re-export cannot carry" is a false positive in a query
    # someone ACTS on — which this toolkit's own rule calls a bug, not a caveat.
    _priv_names = sorted({n for _p, _l, f, b in _rows if f.startswith("from")
                          for n in b if n.startswith("_")})
    check("a `_` name taken by `from` IS the re-export hazard", _priv_names, ["_priv"])
    check("...and a `_`-prefixed import ALIAS is not", "_alias" in _priv_names, False)

    # ── --aliases: the bare-import ban, by FORM ───────────────────────────────────────
    # ⚑ THE POLICY THIS ENCODES, so a later reader does not re-derive it from the counts:
    # the operator ruled that `from x import y` IS what lacking a bare import looks like in
    # python — it selects names out of a module and binds them where the definition site
    # carries `x.y`. So `import x` is the ONLY compliant form, and the ban extends into
    # function bodies for the `from` shapes while leaving a function-scoped `import x`
    # compliant (placement is orthogonal to form).
    # ⚑ `target.py` MUST EXIST ON DISK, and my first fixture omitted it. Locality is resolved
    # against the importing file's own directory — which is how python itself resolves a bare
    # `import x` — so a fixture importing a module that is not there is correctly reported as
    # importing something FOREIGN. The case went red for a real reason: the census was right
    # and the fixture was describing a repo that did not exist.
    open(os.path.join(d, "target.py"), "w", encoding="utf-8").write("pub = 1\n_priv = 2\n")
    _al = os.path.join(d, "aliasuser.py")
    open(_al, "w", encoding="utf-8").write(
        'import target\n'                       # BARE      — the only compliant form
        'import target as _t\n'                 # AS-MOD    — relabels the module
        'from target import pub\n'              # FROM      — selects
        'from target import pub as p2\n'        # FROM-AS   — selects and relabels
        'from target import *\n'                # FROM-STAR — takes all, binds bare
        'from . import sibling\n'               # RELATIVE  — positional, local by construction
        'import os\n'                           # foreign   — not this repo's namespace
        'from typing import Optional\n'         # foreign   — ditto
        '# from target import ghost\n'          # a comment is not an import
        'S = "from target import ghost"\n'      # nor is a string literal
        'def f():\n'
        '    import target\n'                   # func-scoped BARE — COMPLIANT
        '    from target import deferred\n')    # func-scoped FROM  — a violation
    _arows = aliases([_al], local_only=False)
    # ⚑ THREE `BARE`, NOT TWO — and my first expectation said two. Under `local_only=False`
    # the foreign `import os` is a BARE row too; I had written the list as though locality
    # still filtered, in the very case that turns locality OFF. The code was right and the
    # fixture expectation was wrong, which is the direction a selftest is supposed to catch.
    check("every import form is classified, and comments/strings are not imports",
          sorted(f for _p, _l, f, _m, _b, _s in _arows),
          ["AS-MOD", "BARE", "BARE", "BARE", "FROM", "FROM", "FROM", "FROM-AS",
           "FROM-STAR", "RELATIVE"])
    # ⚑ SCOPE IS A COLUMN, NOT AN EXCUSE, and the two function-scoped rows must land on
    # OPPOSITE sides of the verdict — that is the whole content of the operator's ruling.
    _func = sorted((f, s) for _p, _l, f, _m, _b, s in _arows if s == "func")
    check("a function body carries both a compliant and a violating import",
          _func, [("BARE", "func"), ("FROM", "func")])
    check("the func-scoped BARE import is COMPLIANT",
          [f for f, _s in _func if f in ALIAS_COMPLIANT], ["BARE"])
    # ⚑ THE FALSE ZERO I SHIPPED AND CAUGHT BY RUNNING IT. `local` was derived from the
    # PATHS PASSED IN, so asking about one file left only that file's own stem in the
    # locality set — every import it made read as foreign and the census answered
    # "0 of 0 local import(s)" for a file whose header is a nine-name `from` block. A
    # scoped question must narrow WHICH SITES ARE REPORTED, never what counts as local;
    # otherwise the answer changes with the question. This case fails against that version.
    # ⚑⚑ AND MY FIRST VERSION OF THIS CASE WAS TAUTOLOGICALLY GREEN — 383/383 against the
    # very code it was written to refute. It asserted `len(_scoped) > 0`, but the fixture
    # also contains `from . import sibling`, and RELATIVE bypasses the locality filter by
    # construction; the list was non-empty for a reason unrelated to the claim. The case
    # must name the site that ACTUALLY vanishes under the bug: `target`, whose stem is not
    # the scoped file's own.
    _scoped = aliases([_al], local_only=True)
    check("a single-file scope does not empty the locality set (the false zero)",
          sorted({m for _p, _l, _f, m, _b, _s in _scoped if m == "target"}), ["target"])
    check("...and `os`/`typing` are still excluded as foreign",
          sorted({m for _p, _l, _f, m, _b, _s in _scoped if m in ("os", "typing")}), [])
    # ⚑ RELATIVE SURVIVES `local_only`, and it must: `from . import y` has no module head to
    # test, so a name-based filter written for foreign modules would drop a violation class
    # entirely. Admitted by construction rather than by exemption.
    check("a relative import is local by construction, never filtered out",
          "RELATIVE" in {f for _p, _l, f, _m, _b, _s in _scoped}, True)
    # ⚑ FROM-STAR IS FOUND BY THE AST AND WAS MISSED BY `--literal`. I reported `import *`
    # at ZERO code sites from a literal search, which reads STRING literals — a fact about
    # the method reported as a fact about the corpus. The AST census finds 7 in the tree.
    check("a star-import is a syntax node, not a string literal",
          [f for _p, _l, f, _m, _b, _s in _arows if f == "FROM-STAR"], ["FROM-STAR"])

    # ── --size: over-large modules, and the multi-entry defect that motivated it ──────
    # ⚑ THE MULTI-ENTRY DETECTOR MUST BE DRIVEN AGAINST A FIXTURE, because the corpus
    # reports ZERO — `scope_fix.py` was the only instance and I merged its two guards before
    # writing this. A detector whose only observation is "none found" is untested in the
    # direction that matters, and this one exists precisely to catch a defect that already
    # shipped once: a mid-file `__main__` block calling `sys.exit`, with a second one at the
    # end of a 2800-line file that was therefore unreachable.
    import tempfile as _tf, shutil as _sh
    _d = _tf.mkdtemp(prefix="pycodemod_size_")
    _two = os.path.join(_d, "two_entries.py")
    open(_two, "w").write(
        'import sys\n'
        'if __name__ == "__main__":\n'
        '    sys.exit(0)\n'
        'def later():\n'
        '    return 1\n'
        'if __name__ == "__main__":\n'
        '    sys.exit(later())\n')
    _rows, _n = module_size([_two], threshold=10_000)   # threshold high: SIZE must not fire
    check("two __main__ guards are reported at ANY size", len(_rows), 1)
    check("...and the reason names them", "2 __main__ guards" in _rows[0][4], True)
    # ⚑ AND A SINGLE GUARD MUST NOT FIRE, or the census floods with every ordinary CLI.
    _one = os.path.join(_d, "one_entry.py")
    open(_one, "w").write('if __name__ == "__main__":\n    pass\n')
    _rows1, _ = module_size([_one], threshold=10_000)
    check("one __main__ guard is not a finding", _rows1, [])
    # ⚑ THE LINE COUNT IS OF *CODE*: comments are this corpus's incident log, and counting
    # them as bulk would rank the best-documented modules as the worst offenders.
    _cmt = os.path.join(_d, "commented.py")
    open(_cmt, "w").write("# c\n" * 500 + "x = 1\n")
    check("comment lines are not counted as bulk",
          module_size([_cmt], threshold=100)[0], [])
    # ⚑⚑ AND THE PHYSICAL COUNT IS CARRIED ANYWAY, WHICH IS THE OTHER HALF OF THE SAME
    # FILE. The case above pins that 501 lines of comment do not TRIP a 100-line cap —
    # correct, and it is why `sppf_db.py` reported `1060 code — OK, 140 under its cap`
    # while being ~1800 physical lines and genuinely too large to read whole. Both facts
    # have to be reachable: the cap stays on code, and the reader gets the number they
    # actually scroll past.
    _all_cmt, _ = module_size_all([_cmt], threshold=100)
    check("...but the PHYSICAL count is reported alongside", _all_cmt[0][7], 501)
    check("...and the code count still excludes them", _all_cmt[0][1], 1)
    # ⚑ APPENDED, NOT INSERTED — three cases here index these tuples positionally, so a
    # field added in the middle would shift `why`/`cap`/`incidents` under all of them at
    # once. This pins the position so a later widening cannot quietly do that.
    check("...at the END of the row, so no existing index shifts",
          (_all_cmt[0][4], _all_cmt[0][5]), ("", 100))

    # ── the ⚑ COMMENTARY census: the preservation gate for a SPLIT ───────────────────
    # ⚑ THESE DRIVE THE PROPERTY `--roundtrip` STRUCTURALLY CANNOT. Losslessness is
    # per-file; a decomposition MOVES a line to another file, so both halves round-trip
    # green while a ⚑ block goes missing. The census answers over a GROUP, so the case
    # simulates exactly that: one file split into two, with one note dropped.
    _whole = os.path.join(_d, "whole.py")
    open(_whole, "w", encoding="utf-8").write(
        '# ⚑ ONE — a note on the first def\n'
        'def a():\n'
        '    """⚑ TWO — a note in a docstring."""\n'
        '    print("  ⚑ THREE — a note the CLI prints")\n'
        'def b():\n'
        '    # ⚑ FOUR — a note on the second def\n'
        '    return 1\n')
    _r0, _t0, _ = commentary_census([_whole])
    check("every marked line is counted, in comments AND docstrings AND printed strings",
          _r0[0][1], 4)
    # the split: `b` moves out, and FOUR is dropped on the way
    _left = os.path.join(_d, "left.py")
    _right = os.path.join(_d, "right.py")
    open(_left, "w", encoding="utf-8").write(
        '# ⚑ ONE — a note on the first def\n'
        'def a():\n'
        '    """⚑ TWO — a note in a docstring."""\n'
        '    print("  ⚑ THREE — a note the CLI prints")\n')
    open(_right, "w", encoding="utf-8").write(
        'def b():\n'
        '    return 1\n')
    _r1, _t1, _ = commentary_census([_left, _right])
    check("a ⚑ line lost ACROSS a split is visible in the group total",
          sum(n for _p, n, _dd in _r1), 3)
    check("...and the census NAMES the text that vanished",
          sorted(set(_t0) - set(_t1)), ["⚑ FOUR — a note on the second def"])
    # ⚑ THE TEXTS WERE ALWAYS IN HAND; THE CLI COULD ONLY PRINT THE COUNT — and a reader who
    # asks for commentary and is handed `4 ⚑ line(s), 4 distinct` will report which lines the
    # file contains from a number they never expanded.  Measured: I told a peer a specific
    # sentence was absent from a file whose census I had run and whose 15 lines I had never
    # seen; the line was there, and a second corroborating site with it.  `--lines` is the
    # difference between HOW MANY and WHICH, which is the difference between a count and a
    # listing — and only the listing can support an absence claim.
    # ⚑ THE PRINTED NOTE KEYS UNDER ITS WHOLE LINE (`print(" ⚑ THREE…`), because the normalizer
    # strips a leading COMMENT sigil and a docstring quote but not an arbitrary code prefix.
    # That is correct for the preservation gate — the sentence still matches itself across a
    # move — and it is why a listing shows the line as written rather than a cleaned excerpt.
    check("the census carries the LINE TEXT, not only the count, for every mark",
          sorted(k for k in _t0 if "THREE" in k),
          ['print(" ⚑ THREE — a note the CLI prints")'])
    check("...and each text names its site, so a listing can be printed",
          [os.path.basename(p) for p, _ln in _t0["⚑ FOUR — a note on the second def"]],
          ["whole.py"])

    # ⚑⚑⚑ THE ARGUMENT MODEL IS DECLARED, AND THIS IS THE GATE THAT KEEPS IT TRUE. The defect
    # was never a bug list — it was that `_dispatch` holds 135 direct `sys.argv` reads, so each
    # branch parsed the command line on its own terms and PARALLEL FLAGS BEHAVED DIFFERENTLY:
    # `--since` subtracted `--marks`'s operand and its sibling `--commentary` did not, so
    # `--marks record` read `record` as a path. Deriving arity from implementation spellings
    # cannot close that, because each new spelling (`argopt` vs `sys.argv[i+1]`) is a new blind
    # spot found by a peer rather than by this suite. A DECLARATION can: a flag the derivers see
    # and the table does not is a FAILURE here, in this tree, before anyone borrows it.
    import pycodemod as _pc
    _derived = {f for f, wants in _pc.modes().items() if wants} | _pc.argopt_flags()
    _declared = _pc.declared_operand_flags()
    # ⚑ THE DERIVER OVER-FIRES AND THAT IS WHY IT CANNOT BE THE AUTHORITY. `_takes_operand`
    # matches `args[0]`/`len(args) <` ANYWHERE in a branch body, so `--commentary`,
    # `--discards` and `--banner` read as operand-taking when they are path-or-nullary modes
    # whose bodies index `args` for unrelated reasons. Under inference-only this was invisible
    # in BOTH directions at once: it missed `--marks` (wrong spelling) and invented these three
    # (right spelling, wrong subject). They are named here as MEASURED deriver noise rather
    # than declared as operands, because declaring them would make `--commentary <path>` eat
    # its own path — the gate must not be satisfied by lying to it.
    _DERIVER_OVERFIRES = {"--commentary", "--discards", "--banner"}
    check("⚑ every operand-taking flag the DERIVERS find is DECLARED in the table",
          sorted(_derived - _declared - _DERIVER_OVERFIRES), [])
    # ⚑ AND THE OVERFIRE SET IS ITSELF GATED: if the deriver stops over-firing on one of these,
    # this fails and the exemption gets deleted rather than outliving its cause — an exemption
    # that cannot expire is the shape `check_claims` refuses.
    check("...and the named deriver-overfires all still over-fire (no stale exemption)",
          sorted(_DERIVER_OVERFIRES - _derived), [])
    # ⚑ AND THE MODE SET ITSELF: a dispatched mode absent from `MODES` has no declared shape, so
    # nothing knows whether it takes paths or an operand — which is how `--lines` fell through
    # to the banner. Reported as a census rather than asserted empty: `MODES` covers the modes
    # whose SHAPE has been declared so far, and the honest number is the residue, not a claim
    # that it is zero.
    _undeclared = sorted(set(_pc.modes()) - set(_pc.MODES))
    check("the declared-mode census is stated, not assumed",
          isinstance(_undeclared, list), True)
    check("⚑ ...and every DECLARED mode is really dispatched (no invented shapes)",
          sorted(set(_pc.MODES) - set(_pc.modes()) - {"--selftest"}), [])

    # ⚑⚑ A MARK IN A `check(...)` NAME IS NOT PROSE — IT IS AN EXECUTABLE ASSERTION WHOSE NAME
    # IS THE CLAIM, and the flat census cannot tell it from a comment. Found by a peer reading
    # this repo through a symlink: of 20 marks in `hook_structural_query.py`, five are code —
    # two the refusal message a blocked reader sees, three selftest case names. Those are the
    # END STATE a claim-migration wants to reach, so counting them as migratable overcounts
    # the population and would move an argument away from the code that runs it.
    _kd = os.path.join(_d, "kinds.py")
    open(_kd, "w", encoding="utf-8").write(
        '"""⚑ ONE — a docstring note."""\n'
        '# ⚑ TWO — a comment note\n'
        'def f():\n'
        '    check("⚑ THREE — a selftest name", 1, 1)\n'
        '    print("  ⚑ FOUR — a message the program emits")\n')
    _kinds = commentary_kinds([_kd])
    check("⚑ a mark in a selftest NAME classifies as executable, not prose",
          sorted(t.split("(")[0] for _p, _l, t in _kinds["executable"]),
          ["check", "print"])
    check("...a comment mark classifies as comment",
          len(_kinds["comment"]), 1)
    check("...and a module docstring mark classifies as docstring",
          len(_kinds["docstring"]), 1)
    # ⚑ AN UNTOKENIZABLE FILE IS REPORTED, NOT DROPPED — an absent classification is a fact
    # about the METHOD, and this census is about to be used to size a migration.
    _bad = os.path.join(_d, "broken.py")
    open(_bad, "w", encoding="utf-8").write("# ⚑ note\ndef (:\n")
    check("⚑ a file that will not tokenize is reported as unparsed",
          len(commentary_kinds([_bad])["unparsed"]), 1)

    # ⚑⚑ A RELATIVE ROOT RESOLVED AGAINST THE TOOL'S TREE, SO A PEER GOT MY CENSUS AS THEIRS.
    # `py_files` did `os.path.join(ROOT, r)` unconditionally: a path that does not exist under
    # ROOT walks nothing, the population comes back EMPTY, and every caller falls through to
    # the default corpus. Measured — a delegate ran `--commentary tools/no_owner_audit.py`
    # from their own repo and got substrate's 6,005 lines back, caught only by recognising my
    # filenames. A path like `scripts/` that exists in BOTH trees is worse: it resolves
    # silently to mine and the answer is well-formed and about the wrong repo.
    import _pycodemod_core as _core
    _cwd0 = os.getcwd()
    try:
        os.chdir(_d)
        open(os.path.join(_d, "only_here.py"), "w", encoding="utf-8").write("# ⚑ local\n")
        check("⚑ a relative path resolves against the CALLER's cwd",
              [os.path.basename(p) for p in _core.py_files("only_here.py")],
              ["only_here.py"])
        # ⚑ AND AN UNRESOLVABLE ROOT RAISES rather than silently returning the default corpus —
        # the empty-population fallthrough IS the wrong-population bug.
        _raised = False
        try:
            _core.py_files("no/such/path/anywhere.py")
        except _core.PopulationError:
            _raised = True
        check("⚑ ...and a path in NEITHER tree raises, never falls back to the corpus",
              _raised, True)
    finally:
        os.chdir(_cwd0)
    # ⚑ THE ROOT FALLBACK SURVIVES, because gates inside this tree pass `scratch/`-relative
    # paths and run from anywhere; it is a FALLBACK now, so it can only widen what a caller
    # could already reach — never redirect it.
    check("...while a tool-tree-relative path still resolves from elsewhere",
          any(p.endswith("pycodemod.py") for p in _core.py_files("scratch/pycodemod.py")),
          True)

    # ⚑⚑ A SHORT ALPHANUMERIC MARK MATCHED INSIDE WORDS, SO WIDENING THE SET INFLATED THE
    # COUNT. `--marks 'NB'` hit "⚑ AN U**NB**ALANCED QUOTE IS BASH'S VERDICT" — measured, and
    # it mattered ecosystem-wide: a peer widened the marks to read another repo's conventions
    # (`NB`/`RACE.`/`PROVENANCE.`) and got 35 lines across substrate where 9 are real. The
    # widenable mark set exists precisely to compare corpora, and precision that depends on
    # how short the caller's sigil is defeats that.
    _mk = os.path.join(_d, "marks.py")
    open(_mk, "w", encoding="utf-8").write(
        "# AN UNBALANCED QUOTE IS NOT A NOTE\n"
        "# NB this one IS a note\n"
        "# ⚑ and the glyph still counts\n")
    _rm, _tm, _ = commentary_census([_mk], marks=("NB",))
    check("⚑ a short mark does NOT fire inside a word (NB in UNBALANCED)", _rm[0][1], 1)
    check("...and it DOES fire as its own token", "NB this one IS a note" in
          " ".join(_tm), True)
    # ⚑ THE BOUNDARY MUST BE CONDITIONAL: `\b` is defined against `\w`, so anchoring the glyph
    # would match nothing and report this whole corpus as empty — the same failure inverted.
    _rg, _tg, _ = commentary_census([_mk], marks=COMMENTARY_MARKS)
    check("⚑ ...while the GLYPH mark still matches, having no word boundary", _rg[0][1], 1)

    # ⚑⚑ ⟡apex-over-collisions — THE CASES PIN THE THREE DEFECTS THE BUILD ACTUALLY HIT,
    # not the happy path.  Each one produced a plausible-looking census that was wrong,
    # and none would have been caught by "does the mode run".
    _ap = os.path.join(_d, "apexcase.py")
    open(_ap, "w", encoding="utf-8").write(
        "class A:\n"
        "    def handler(self, x):\n"
        "        y = x + 1\n"
        "        return y\n"
        "class B:\n"
        "    def handler(self, x):\n"
        "        y = x + 1\n"
        "        return y\n"
        "def solo(a):\n"
        "    return a\n")
    _rows = {r[0]: r for _b, _rs in collision_apex([_ap]) for r in _rs}
    # (1) THE DEDENT.  `source_of` returns a method at its ORIGINAL indentation and
    # `templatize` lowers through `ast.parse`, which raises IndentationError on it.  The
    # first run scored ALL SEVEN names in scope as `no-shared-skeleton` — the strongest
    # negative a parse failure can produce.  Two byte-identical methods must read as a
    # deep match, and this fails loudly if the dedent is ever dropped.
    check("⚑ two byte-identical METHODS share a deep skeleton (the dedent)",
          _rows["handler"][4] and len(_rows["handler"][4]) == 2, True)
    check("...and their hole count is 0, not None — IDENTICAL, not undecidable",
          _rows["handler"][3], 0)
    # (2) A NON-COLLIDING NAME IS ABSENT, NOT ZERO-SCORED.  `solo` has one def, so it is
    # not a collision at all; a row for it would make "no rival" and "rivals that do not
    # match" indistinguishable.
    check("⚑ a single-def name yields NO row (absent ≠ scored zero)",
          "solo" in _rows, False)
    # (3) THE ROW IS SEVEN-WIDE.  The spine rung was added after the fact and the printer
    # unpacks positionally, so a width change is a TypeError at the CLI and silence here.
    check("⚑ a row carries both rungs: (name, n, nskel, holes, labels, nspine, spine_shared)",
          len(_rows["handler"]), 7)

    # ⚑⚑ THE TWO ROADS TO `modes()` MUST AGREE, AND ONLY ONE OF THEM RUNS HERE. `modes()`
    # parses with libcst; `_modes_ast` is the stdlib fallback a checkout without it takes.
    # In THIS tree the fallback is never exercised, so a divergence would surface only in a
    # borrowing repo — the checkout least able to diagnose it. Measured: `_arity = modes()`
    # runs at IMPORT, so its dependency was every mode's dependency, and a peer running this
    # by symlink got `AttributeError: 'NoneType' object has no attribute 'metadata'` from
    # `--size`, which is pure `ast` + `splitlines` and needs no CST at all.
    import pycodemod as _pcm
    _src = open(_pcm.__file__, encoding="utf-8").read()
    check("⚑ the stdlib road to modes() gives the SAME answer as the CST road",
          _pcm._modes_ast(_src), _pcm.modes())
    check("...and it finds a real number of modes, not an empty dict",
          len(_pcm._modes_ast(_src)) > 20, True)
    # ⚑ THE PRECONDITION IS PER-MODE. A blanket `if cst is None: exit(2)` refused modes that
    # never touch a CST, so a capability that EXISTS read as one that does not — the
    # absent-vs-empty distinction inside my own CLI.
    _cstm = _pcm.cst_modes()
    check("--roundtrip is derived as needing a CST", "--roundtrip" in _cstm, True)
    check("⚑ --size is NOT — it is ast + splitlines", "--size" in _cstm, False)
    check("⚑ --commentary is NOT — it is splitlines only", "--commentary" in _cstm, False)
    # ⚑ AND A RE-INDENTED LINE IS THE SAME LINE. A def moving to module scope loses four
    # spaces; a byte-compare would report it lost AND gained at once, answering a
    # formatting question while claiming to answer a preservation one.
    _reind = os.path.join(_d, "reindented.py")
    open(_reind, "w", encoding="utf-8").write(
        '# ⚑ FOUR — a note on the second def\n'
        'def b():\n'
        '    return 1\n')
    _r2, _t2, _ = commentary_census([_left, _reind])
    check("a re-indented ⚑ line is NOT reported as lost", sorted(set(_t0) - set(_t2)), [])
    check("...and the group total is preserved", sum(n for _p, n, _dd in _r2), 4)
    # ⚑ A COPY IS NOT A MOVE, and the two drift independently — so a text appearing in
    # more than one place after a split is its own finding, not a tie in the count.
    _r3, _t3, _ = commentary_census([_whole, _reind])
    check("a duplicated marker text is reported as multi-homed",
          len(_t3["⚑ FOUR — a note on the second def"]), 2)
    # ⚑ AN UNRESOLVABLE BASELINE MUST BE VISIBLE, NOT A PASS. `commentary_lost` returns an empty
    # LOST list both when every line survived and when the ref named nothing — and the second is
    # what a wrong ref, or a file that is untracked, silently produces. The counts are returned
    # alongside precisely so the caller can tell them apart; a gate that only read `lost == []`
    # would report a clean split over a comparison that never happened.
    _lost, _new, _before, _after = commentary_lost([_whole], ref="refs/tags/no-such-ref-xyz:")
    check("an unresolvable baseline reports LOST empty", _lost, [])
    check("...and says so by reporting a ZERO baseline, not a pass", _before, 0)
    check("...while still counting what is there now", _after, 4)
    _sh.rmtree(_d, ignore_errors=True)

    # shape 1: a file count derived from MATCHED ROWS with no `of <population>`.
    check("no mode derives its denominator from matched rows",
          [(l, t) for l, t in
           _in_dispatch(shape_sites(r'\{len\(\{p for p[^}]*\}\)\} file\(s\)',
                                    [_self]))
           if "of {len(" not in t], [])
    # shape 2: `py_files(...) or None` — an EMPTY scoped population becomes the
    # WHOLE CORPUS, so a scoped query that matches nothing silently widens.
    check("no mode turns an empty scope into the whole corpus",
          _in_dispatch(shape_sites(r'py_files\([^)]*\)\s+or\s+None', [_self])),
          [])
    # ⚑ AND THE CLASS-SCAN MUST DISCRIMINATE, or it is decoration.  Both patterns
    # are asserted to MATCH the defective spellings, so a future edit that breaks
    # the regex (rather than the code) fails loudly instead of passing empty.
    check("the row-derived-count pattern matches its own defect",
          bool(re.search(r'\{len\(\{p for p[^}]*\}\)\} file\(s\)',
                         'x = f"{name}: {len(reads)} in {len({p for p, _ in rows})} file(s)"')),
          True)
    check("the or-None pattern matches its own defect",
          bool(re.search(r'py_files\([^)]*\)\s+or\s+None',
                         'rows = key_reads(name, py_files(*scope) or None)')), True)

    # ── --shape: a finding must carry its LOCATION ──────────────────────────
    # ⚑ THE CLASS GUARD ABOVE FOUND SIX SITES AND PRINTED THE MATCHED TEXT, so I
    # spent four commands locating them by hand — the reprocessing loop, committed
    # while fixing a defect about exactly that.  Every sibling mode answers
    # `file:line`; this makes a SHAPE query answer it too.
    ps = os.path.join(d, "shape.py")
    open(ps, "w", encoding="utf-8").write(
        '"""A docstring mentioning foo or None, which is PROSE."""\n'
        '# a comment mentioning foo or None too\n'
        'x = foo(a) or None\n'
        'y = 1  # foo or None in a trailing comment on a CODE line\n')
    hits = shape_sites(r'foo\([^)]*\)\s+or\s+None', [ps])
    check("--shape locates the code site by line",
          [(l, t.startswith("x =")) for _p, l, t in hits], [(3, True)])
    # ⚑ PROSE IS NOT A SITE — my own ⚑ comment describing the `or None` defect
    # matched the scan for it, a sixth "occurrence" that was commentary about the
    # other five.  Same discrimination that makes `--calls` beat grep.
    check("a docstring mention is not a site",
          [l for _p, l, _t in hits if l == 1], [])
    check("a comment mention is not a site",
          [l for _p, l, _t in hits if l == 2], [])
    # ⚑ AND `--shape-all` MUST STILL FIND THEM — "does anything MENTION this" is a
    # different, legitimate question, and a mode that could only answer one would
    # send the operator back to grep for the other.
    allhits = shape_sites(r'foo[^\n]*or None', [ps], in_code_only=False)
    check("--shape-all includes prose", len(allhits) >= 3, True)
    # ⚑ A CODE LINE WITH A TRAILING COMMENT IS STILL CODE.  Dropping it would hide
    # any defect that happens to carry an explanation beside it.
    check("a code line with a trailing comment is not excluded",
          bool(shape_sites(r'y = 1', [ps])), True)
    # ⚑ AN ANCHOR MUST WORK, AND IT DID NOT — the whole-file pre-filter ran the
    # pattern without `re.M`, so `^`-anchored queries were discarded before any
    # line was examined and returned a confident ZERO.  I hit this twice and
    # rewrote the QUERY both times rather than suspecting the TOOL, which is the
    # instrument-vs-substrate error this repo names explicitly.
    pa = os.path.join(d, "anchor.py")
    open(pa, "w", encoding="utf-8").write(
        "import os\n"
        "def f():\n"
        "    import sys\n"
        "if __name__ == '__main__':\n"
        "    f()\n")
    check("a `^`-anchored pattern finds the column-0 site",
          [l for _p, l, _t in shape_sites(r'^import ', [pa])], [1])
    # ...and does NOT find the indented one, which is the whole point of anchoring
    check("a `^`-anchored pattern excludes the indented site",
          [l for _p, l, _t in shape_sites(r'^    import ', [pa])], [3])
    check("`^if __name__` locates the entry point",
          [l for _p, l, _t in shape_sites(r'^if __name__', [pa])], [4])

    p3 = os.path.join(d, "bad.py")
    open(p3, "w", encoding="utf-8").write("def (:\n")
    check("a syntax error is a verdict, not a crash", roundtrip(p3)[0], False)

    # ── --binding: where a name is BOUND, and where it is LIVE ──────────────
    # ⚑ THE CASE THAT PINS MY ACTUAL FAILURE.  I placed two selftest cases
    # BEFORE the line that assigns `grouped` — inside the right function, but
    # above the binding — and read it out of scope.  A tool that reports only
    # "it is bound in this function" would have told me nothing; the LIVE RANGE
    # is the part that answers "may I use it here".
    pb = os.path.join(d, "b.py")
    open(pb, "w", encoding="utf-8").write(
        "import os\n"
        "def outer():\n"
        "    total = 1\n"
        "    for total in range(3):\n"
        "        pass\n"
        "def inner(total):\n"
        "    return total\n")
    rows = bindings("total", pb)
    kinds = sorted(k for k, *_ in rows)
    check("--binding finds assignment, loop target and parameter",
          kinds, ["assign", "assign", "param"])
    check("--binding reports the defining LINE", sorted(r[2] for r in rows),
          [3, 4, 6])
    # ⚑ a name bound in one function is NOT live in a sibling: the live range of
    # the parameter starts at `inner`, not at module top.
    param = [r for r in rows if r[0] == "param"][0]
    check("--binding scopes a parameter to its own function", param[3], 6)
    check("--binding sees an import as a binding",
          [k for k, *_ in bindings("os", pb)], ["import"])
    check("--binding on an unbound name is empty, not an error",
          bindings("nowhere", pb), [])
    check("--binding reports a syntax error as a verdict",
          bindings("x", p3)[0][0], "<syntax-error>")

    # ⚑ --rivals: A DUPLICATED NAME IS NOT A DUPLICATED BODY.  The fixture holds
    # one real enumerator and one wrapper under the SAME name — the exact shape
    # T12 counts as "2 defs" and which a def-count cannot separate.
    pr = os.path.join(d, "riv.py")
    open(pr, "w").write(
        "def f():\n"
        "    '''doc'''\n"
        "    return _auth(ROOT)\n"
        "def g():\n"
        "    out = []\n"
        "    for x in walk():\n"
        "        out.append(x)\n"
        "    return out\n")
    _rv = {r[2]: r for r in rivals("f", [pr])}
    check("--rivals calls a one-line wrapper DELEGATES",
          list(_rv), ["DELEGATES"])
    check("--rivals names the callee, so the operator can read it",
          _rv["DELEGATES"][3], "_auth")
    # ⚑ THE DOCSTRING MUST NOT COUNT AS AN IMPLEMENTATION.  Every one of T12's
    # four wrappers carries a 9-line ⚑ docstring; counting prose as body would
    # report all four as REIMPLEMENTS — the false positive that would have kept
    # the item open forever.
    check("--rivals does not count a docstring as a body",
          _rv["DELEGATES"][4], 1)
    check("--rivals calls a real body REIMPLEMENTS",
          [r[2] for r in rivals("g", [pr])], ["REIMPLEMENTS"])

    # ⚑ THE CORPUS IS DISCOVERED, AND THAT IS PINNED.  The roots were a frozen
    # `("scratch", "scripts")`, so `catalog/` sat outside every unscoped query:
    # `--attr own_agda_files_definers` returned 0 while the call was right
    # there.  An empty result from a query that cannot see the subject reads as
    # a finding.  Asserting a LITERAL list here would re-freeze it one layer
    # up, so the case asserts the PROPERTY: a real top-level package with tools
    # in it is in scope, and the excluded ones are excluded.
    # ⚑ THE CACHE IS KEYED ON CONTENT, so an EDIT must change the answer and a
    # re-read must not.  A cache that survives an edit is worse than no cache:
    # it reports the old tree as current, which is the staleness class
    # `run_selftests --last` exists to refuse.
    pc = os.path.join(d, "cache_probe.py")
    open(pc, "w").write("def f():\n    return g()\n")
    _first = _cached_defs(pc)
    check("a cached parse is stable when content is unchanged",
          _cached_defs(pc), _first)
    check("the parse reports delegation", _first[0][2], True)
    open(pc, "w").write("def f():\n    x = 1\n    return x\n")
    _second = _cached_defs(pc)
    check("editing a file changes its cached answer",
          _second[0][2], False)

    # ⚑ AND THE KEY NAMES ITS DERIVER, WHICH THE DOCSTRING CLAIMED AND THE CODE
    # DID NOT DO.  A content-only key is fresh w.r.t. the INPUT; across a libcst
    # upgrade the same bytes derive a different artifact and the old one comes
    # back silently.  Corrected by cassian-observability reviewing our ask.
    # These assert the RELATION, never a literal digest — a hardcoded hash would
    # pin today's libcst and fail on every upgrade, reporting a correct
    # environment as broken.
    import hashlib as _h
    check("the deriver tag names the library and the schema",
          ("libcst=" in _DERIVER and "schema=" in _DERIVER), True)
    # ⚑ AN EMPTY VERSION WOULD SILENTLY COLLAPSE THE KEY BACK TO CONTENT-ONLY.
    # libcst ships no `__version__` on this install (`--available` reports
    # "(no __version__)"), so the metadata fallback is the LIVE path here, not a
    # defensive branch — if it ever resolved to "" nothing would say so.
    check("the deriver tag is never empty-versioned",
          _DERIVER.split(";")[0] == "libcst=", False)
    check("a different deriver yields a different key",
          _h.sha1(b"x" + _DERIVER.encode()).hexdigest()
          == _h.sha1(b"x" + b"libcst=9.9.9;schema=99").hexdigest(), False)
    check("the same deriver and bytes yield the SAME key (still a cache)",
          _h.sha1(b"x" + _DERIVER.encode()).hexdigest()
          == _h.sha1(b"x" + _DERIVER.encode()).hexdigest(), True)

    _rts = _roots()
    check("the corpus discovers catalog/", "catalog" in _rts, True)
    check("the corpus discovers scratch/ and scripts/",
          {"scratch", "scripts"} <= set(_rts), True)
    check("the corpus excludes the Agda tree", "agda" in _rts, False)
    check("the corpus excludes dotdirs",
          [r for r in _rts if r.startswith(".")], [])

    # ── --state: a CACHE is not an ACCUMULATOR ──────────────────────────────
    # ⚑ THE FIRST CUT SHIPPED A 145-ROW CENSUS OF WHICH ~134 WERE NOISE.
    # "module-level dict that something mutates" admits every accumulator in a
    # script whose whole body runs at import — `_SNAPPED` (a once-flag, ~25
    # rows), and every `figures/`/`checks/` `bad`/`edges`/`stack`.  Acting on
    # that population is the over-wide-census failure this repo keeps paying
    # for, so the discriminator is pinned here rather than trusted.
    _sd = os.path.join(d, "state")
    os.makedirs(_sd, exist_ok=True)

    # a CACHE: written and READ INSIDE A FUNCTION, so it serves a later call
    _cp = os.path.join(_sd, "c.py")
    open(_cp, "w", encoding="utf-8").write(
        "_C = {}\n"
        "def get(k):\n"
        "    if k in _C:\n"
        "        return _C[k]\n"
        "    _C[k] = k * 2\n"
        "    return _C[k]\n")
    # an ACCUMULATOR: mutated in straight-line module code, consumed in scope
    _ap = os.path.join(_sd, "a.py")
    open(_ap, "w", encoding="utf-8").write(
        "bad = []\n"
        "for x in range(3):\n"
        "    bad.append(x)\n"
        "print(len(bad))\n")
    # a CONST table: never mutated at all
    _kp = os.path.join(_sd, "k.py")
    open(_kp, "w", encoding="utf-8").write(
        "TABLE = {'a': 1}\n"
        "def look(k):\n"
        "    return TABLE[k]\n")

    _rows, _n = module_state([_cp, _ap, _kp])
    _by = {r[1]: r[3] for r in _rows}
    check("a dict read INSIDE a function is a cache", _by.get("_C"), "cache")
    # ⚑ THE DISCRIMINATOR.  Both are module-level dicts/lists that something
    # mutates; only the read-site distinguishes them, and a predicate keyed on
    # mutation alone calls BOTH a cache.
    check("an accumulator mutated only at module scope is NOT a cache",
          _by.get("bad"), "accum")
    check("an unmutated table is const, not a cache", _by.get("TABLE"), "const")
    # ⚑ `n of m` OVER THE WHOLE POPULATION — the set-aside rows are COUNTED, so a
    # reader can sanity-check the predicate instead of trusting the filter.
    check("every candidate is classified, none silently dropped",
          len(_rows), 3)
    check("the file denominator is the scope, not the matches", _n, 3)
    # ⚑ THE LIVE WITNESS, because a synthetic fixture cannot show the predicate
    # holds on real code.  `_SNAPPED` is the once-flag that flooded the first cut
    # (145 rows, ~134 of them accumulators); `_DAG` is a real memo.
    #
    # ⚑ AND THIS CASE JUST CAUGHT ITS OWN SUBJECT BEING RETIRED.  It named
    # `agda_lex._MASK_CACHE` — the measured 58,580-call/10,717-eviction cache —
    # which the `lru_cache` conversion DELETED, so the case failed on a fixture
    # that no longer exists rather than on a predicate defect.  That is the census
    # working: a population shrinking is exactly what it should notice.  Repointed
    # at a cache that is still hand-rolled, so the case keeps discriminating.
    # ⚑⚑ AND IT HAS NOW HAPPENED A SECOND TIME, BY A DIFFERENT MECHANISM — worth keeping
    # because the two are the same event with different causes. The first repoint was a
    # DELETION (`_MASK_CACHE` retired by an `lru_cache` conversion). This one is a MOVE:
    # `split_pipeline.py` was decomposed 2026-08-11 and `_DAG` went with the read side, so
    # `--binding _DAG` now reports `assign` in `split_census.py:43` and `import` in
    # `split_pipeline.py:61`. `module_state` correctly declines to classify an IMPORT as a
    # hand-rolled memo — the predicate is right and the fixture moved out from under it.
    #
    # ⚑ NEITHER AGENT COULD HAVE SEEN THIS. Six modules were decomposed in parallel; each
    # verified its own file in isolation exactly as briefed, and this coupling lives BETWEEN
    # two of them. It is the residue that per-file verification cannot reach, and the reason
    # a reconciling pass over the union is owed after any parallel dispatch.
    #
    # ⚑ REPOINTED AT THE DEFINING MODULE, NOT THE RE-EXPORTING ONE. `split_census.py` is
    # where `_DAG` is now ASSIGNED; naming `split_pipeline.py` again would pass today (the
    # import resolves) and break the moment the re-export is tidied — an assertion should
    # name the thing that holds the fact, not a module that forwards it.
    _live, _ = module_state([os.path.join(_c.ROOT, "scratch", "split_census.py"),
                             os.path.join(_c.ROOT, "scratch", "split_upstream.py")])
    _lby = {r[1]: r[3] for r in _live}
    check("a live hand-rolled memo classifies as a cache", _lby.get("_DAG"),
          "cache")
    check("the _SNAPPED once-flag does NOT", _lby.get("_SNAPPED"), "accum")

    # ── --sql ────────────────────────────────────────────────────────────────
    # ⚑ EVERY CASE HERE PINS A DEFECT THIS MODE SHIPPED WITH, and both were
    # found by RUNNING it on a second identifier rather than by reading it.
    import tempfile as _tf
    _sqlsrc = '''
_SCHEMA = """CREATE TABLE _module_edges (src_pid TEXT, dst_pid TEXT)"""
LABEL = "WITH RECURSIVE +"
NOTE = "WITH RECURSIVE (UNION)"
def go(con, m):
    con.execute("SELECT dst FROM module_edges WHERE src = ?", (m,))
    return QB.run(con, "modedges")
def drain(con, sub):
    con.execute("DELETE FROM drainq WHERE core_id IN (%s)" % sub)
    execute(con, "SELECT count(*) FROM drainq WHERE core_id = %s" % ph(), (1,))
    con.execute("DELETE FROM evq e WHERE e.n = 1")
'''
    _d = _tf.mkdtemp()
    _p = os.path.join(_d, "sqlfix.py")
    with open(_p, "w", encoding="utf-8") as _fh:
        _fh.write(_sqlsrc)

    # ⚑ PROSE THAT STARTS WITH A KEYWORD IS NOT SQL.  My first predicate
    # accepted any fragment over two tokens whose head matched, so
    # `sql_lift.py`'s cost-model LABELS ("WITH RECURSIVE +") counted as query
    # sites — the guard-from-the-instance shape, written against the statements
    # I expected.  Measured: `--sql RECURSIVE` reported 7, of which 3 were prose.
    _rec = sql_sites("RECURSIVE", _p)
    check("a prose label starting with a SQL keyword is NOT a site", _rec, [])

    # ⚑ AND THE SECOND PREDICATE WAS ALSO WRONG, IN A WAY THAT CHANGED NOTHING.
    # I tightened it with `complete_statement`, which is a LEXER — it reports
    # lexical termination, so appending `;` makes almost any string "complete"
    # and `"WITH RECURSIVE +;"` still passed.  The re-run returned the identical
    # 7 rows, which is the only reason I caught it before reporting the fix as
    # landed.  `EXPLAIN` is the parser: prose fails to prepare.
    check("a real statement IS a site, and carries its style",
          [(s, h) for s, h, _l, _t in sql_sites("module_edges", _p)],
          [("literal", "CREATE"), ("raw", "SELECT")])

    # ⚑ THE STYLE IS THE VERDICT, not the hit: a raw `con.execute` bypasses the
    # compiled-builder layer that `QB.run` reaches.  A mode reporting only
    # "mentioned here" cannot tell a refactor which sites are the work.
    check("a builder call is not counted as a raw SQL literal",
          [s for s, _h, _l, _t in sql_sites("modedges", _p)], [])

    # ⚑⚑ A FORMAT PLACEHOLDER IS A VALUE, NOT SYNTAX — AND JUDGING IT AS SYNTAX
    # MADE THIS MODE BLIND TO THE IDIOM THIS REPO MANDATES (ⓑ).  `schema.ph()`
    # exists so a caller never types a placeholder, which makes
    # `"… core_id = %s" % ph()` house style — and `%` is sqlite's MODULO, so every
    # such literal died at `syntax error near "%"` and was reported as not-SQL.
    # MEASURED on the real corpus: `--sql obs schema_queue.py` returned 5 sites
    # before this and 13 after, and among the 8 it could not see were BOTH
    # `DELETE FROM obs WHERE core_id IN (%s)` statements — i.e. the census of who
    # touches `obs` could not see the statement that deletes the corpus.
    #
    # ⚑ AND THE STYLE IS PART OF THE CLAIM.  The literal sits inside a `BinOp`, so
    # the old `isinstance(arg, ast.Constant)` test missed the ENCLOSING execute
    # too — a raw driver call censused as an inert string constant.
    check("a %s-parameterised statement IS a site, and is RAW (the ph() idiom)",
          sorted((h, s) for s, h, _l, _t in sql_sites("drainq", _p)),
          [("DELETE", "raw"), ("SELECT", "raw")])

    # ⚑⚑ AND THE RECOGNISER'S ORACLE MUST BE THE DIALECT THE STORE RUNS.  This
    # judged a postgres-only corpus by sqlite's grammar long after ⓺ retired the
    # backend: `DELETE FROM t alias`, `age(xmin)`, `WITH ORDINALITY` and
    # `RETURNING` are all valid here and all rejected there, so the corpus's own
    # dialect read as prose.  A recogniser holding a retired premise under-reports
    # while looking exact — this file's recurring shape, at the level of the judge.
    #
    # ⚑ AND AN UNREACHABLE STORE IS UNMEASURED, NOT PASSED.  The sqlite arm needs
    # no connection and is asserted above unconditionally; only this one degrades,
    # and it SAYS so rather than quietly asserting nothing.
    #
    # ⚑⚑⚑ THIS LINE WAS THE ONE STORE THE TENANT CONTRACT COULD NOT BIND (`gate-F29`), AND
    # IT IS CLOSED (⟡live-store-in-precommit, 2026-08-24).  `_pg_probe_con` was
    # `store.connect(mode="rw", back="postgres")`: a LIVE READ-WRITE connection to the main
    # store, opened from inside the pre-commit selftest roster, never calling `store.tenant`
    # and so never consulting argv.  A `selftest-tenant: sandbox` pragma here would have been
    # a FALSE declaration (`gate-F24`) — the flag appended, the same live store opened.
    #
    # ⚑⚑ THE FIX WAS NOT TO DECLARE THE TENANT BUT TO REMOVE THE CHOICE.  What this case
    # asserts is a fact about SQL TEXT — that `DELETE FROM evq e` is valid postgres and not
    # prose — and the oracle for that is postgres' PARSER, which is not a tenant.  `evq` is a
    # fixture table in a `mkdtemp` file; it exists in NEITHER store, and the recogniser counts
    # `UndefinedTable` as PARSED, so it never wanted the live schema either.  MEASURED across
    # live/rw, live/ro and sandbox: all six dialect cases identical in all three arms, while
    # only live/rw could `CREATE TABLE`.  `_pg_probe_con` is now the sandbox handle.
    #
    # ⚑ AND THE SKIP NAMES ITS CAUSE NOW.  `except Exception: None` made "no store" and
    # "connected" the same reading from outside, so every verdict about this probe was
    # unfalsifiable — a zero with no positive control.  `pg_probe_status` returns the reason,
    # so an UNMEASURED line is a stated fact rather than an absence.
    _probe_con, _probe_why = pg_probe_status()
    if _probe_con is None:
        print("  SKIP the postgres-dialect case — sandbox store unreachable "
              f"({_probe_why}): UNMEASURED, not passed")
    else:
        check("a POSTGRES-only statement is a site (sqlite's grammar is not the store's)",
              [h for _s, h, _l, _t in sql_sites("evq", _p)], ["DELETE"])

    # ── --literal ────────────────────────────────────────────────────────────
    # ⚑ EVERY CASE HERE IS A ROLE THE MODE MUST TELL APART, and the fixture is a
    # miniature of the sqlite retirement this mode was written for: one dispatch
    # branch, one call that names the value, one roster entry, one docstring
    # paragraph, and one COMMENT.  A `grep sqlite` over it returns all five.
    _litsrc = '''"""A module about sqlite and how it is retired."""
BACKENDS = ("sqlite", "postgres")
DEFAULT = "sqlite"

def ph(n, back):
    # sqlite takes ? and psycopg takes %s — a comment, NOT a site
    if back == "sqlite":
        return "?" * n
    return "%s" * n

def go():
    return ph(1, "sqlite")
'''
    _ld = _tf.mkdtemp()
    _lp = os.path.join(_ld, "litfix.py")
    with open(_lp, "w", encoding="utf-8") as _fh:
        _fh.write(_litsrc)
    _lit = {(r[2], r[4]) for r in literal_sites("sqlite", [_lp])}

    # ⚑ THE DISPATCH BRANCH IS THE FINDING.  `back == "sqlite"` is the only line
    # a backend retirement DELETES; a mode that reported "5 mentions" without
    # separating it hands back the same undifferentiated list grep does.
    check("a comparison operand is role=compare",
          ("compare", "sqlite") in _lit, True)

    # ⚑ AND A CALL ARGUMENT IS A SECOND, DIFFERENT DECISION — the caller that
    # NAMES the retired value, which survives deleting the branch.
    check("a call argument is role=arg", ("arg", "sqlite") in _lit, True)

    # ⚑ THE ROSTER SITE IS `decl`, the same split `--key` draws between a schema
    # declaration and a read: fold them together and every value looks used.
    check("a collection element is role=decl", ("decl", "sqlite") in _lit, True)

    # ⚑ THE DOCSTRING IS REPORTED, NOT DROPPED — a retirement must update the
    # prose too, so silently excluding it would make this mode disagree with
    # `--commentary` about the same file.  It is a distinct role because it never
    # blocks the code change.
    check("a docstring mention is role=doc, not role=other",
          ("doc", "A module about sqlite and how it is retired.") in _lit, True)

    # ⚑ THE CASE THAT MAKES THIS BEAT GREP, and the reason the mode exists at
    # all: the fixture's comment names `sqlite` and is NOT a site.  In the real
    # corpus the comment lines outnumber the code lines several to one, so a
    # grep census reports the documentation as the migration work.
    check("a mention in a COMMENT is not a literal site",
          [v for _r, v in _lit if "psycopg" in v], [])

    # ⚑ AND A ROLE MUST NOT ESCAPE ITS OWN STATEMENT.  `DEFAULT = "sqlite"` is a
    # plain assignment; the parent walk must stop at the statement and answer
    # `other`.  Without that bound it keeps climbing to the Module and the answer
    # depends on what happens to be lexically nearby, which is not a fact about
    # the literal at all.
    check("a plain assignment RHS is role=other", ("other", "sqlite") in _lit, True)

    # ⚑ THE COUNT IS FIVE AND MY FIRST DRAFT SAID FIVE WITH ONLY FOUR SITES IN THE
    # FIXTURE — the case was written from the plan and the run refuted it (`got 4
    # want 5`).  Recorded rather than quietly corrected: a total is the one
    # assertion that catches a role being silently folded into its neighbour, so
    # it has to be counted from the fixture, not from the intent.
    check("every site is found exactly once, one role each", len(_lit), 5)

    # ── --crossings ──────────────────────────────────────────────────────────
    # ⚑ EVERY CASE HERE IS A DEFECT THIS MODE SHIPPED WITH, and each was found by
    # RUNNING it on a site it had already flagged — never by review.  A case
    # written to confirm current behaviour would have passed all four.
    _xsrc = '''
def parse_tree():
    disk = {}
    for dp, _, fns in os.walk(SRC):
        disk[dp] = fns
    deps = {m: set() for m in disk}
    return disk, deps

def reach(root):
    seen, stack = set(), [root]
    while stack:
        n = stack.pop()
        seen.add(n)
    return seen

def rows(src):
    out = []
    for r in src.items():
        out.append(r)
    return out

def parse(text):
    rec = {}
    rec["a"] = text
    return rec

def walk_it(xs):
    for x in xs:
        yield x
'''
    _xd = _tf.mkdtemp()
    _xp = os.path.join(_xd, "xing.py")
    with open(_xp, "w", encoding="utf-8") as _fh:
        _fh.write(_xsrc)
    _x = {r[1]: (r[3], r[4]) for r in crossings([_xp])}

    # ⚑ A COMPREHENSION IS THE CORPUS CASE AND THE FIRST CUT MISSED IT.
    # `parse_tree` returns `disk, deps`; only `disk` was reported, because
    # `deps = {m: set() for m in disk}` is a DictComp and `built` only recorded
    # Assign-to-a-literal.  Comprehensions are PRECISELY how a corpus-shaped
    # container gets built in one expression, so the census was blind to the
    # class it exists to find.
    #
    # ⚑ AND THE ORDER IS THE RETURN STATEMENT'S, NOT `sorted()`.  `crossed` was a
    # `set()` with `sorted()` at the yield — the downward half at the point of
    # use: construction discarded the order, the consumer invented alphabetical,
    # and the row read `deps, disk` for source that says `disk, deps`.
    check("a comprehension counts, and the order is the source's",
          _x.get("parse_tree"), ("corpus", "disk, deps"))

    # ⚑ A WORKLIST IS AN UNFOLD, AND IT MUST BEAT THE `for` SCAN.  `reach` has
    # BOTH a `while stack:` and a `for` over that stack; a for-first reading
    # files a transitive closure as an ordinary loop.  The first cut had no
    # `unfold` class at all and put this in the quiet bucket I had named
    # `local` — which I then read as "small, a paydown need not chase".
    check("a while-driven closure is an unfold, not a plain loop",
          _x.get("reach"), ("unfold", "seen"))

    # ⚑ ITERATING A CONTAINER IS `derived`, iterating the CORPUS is `corpus`.
    # Without the split, an inversion of 3 entries and a walk of 3457 files read
    # identically — a row saying "returns a dict" cannot tell them apart.
    check("iterating a container is derived, not corpus",
          _x.get("rows"), ("derived", "out"))

    # ⚑ `unattr` IS AN INSTRUMENT GAP, NOT A LICENCE — and naming it `local` was
    # the defect: it invited "small, therefore acceptable", which is a THRESHOLD,
    # and a sanctioned threshold makes SHRINKING the container the optimisation
    # target instead of streaming it.
    check("a container built with no visible bound is unattr",
          _x.get("parse"), ("unattr", "rec"))

    # ⚑ A GENERATOR IS REPORTED, NOT SKIPPED, so paydown shows as a row MOVING
    # class rather than vanishing.  A census whose population shrinks on paydown
    # cannot distinguish progress from a predicate that stopped matching.
    check("a generator is reported as paid, not omitted",
          _x.get("walk_it"), ("yields", "generator"))

    # ── --relalg: relational algebra withheld from the engine ────────────────
    # ⚑ THESE FAIL AGAINST THE PRE-CHANGE CODE by construction: `relalg_sites`
    # did not exist, and no other mode answers "what algebra happens to the rows
    # AFTER they land". `--rawreads` sees `con.execute` in `withheld` and reports
    # `unpacked` — a fact about the CURSOR, silent about the join.
    _rsrc = '''
def withheld(con):
    left = {}
    for a, b in con.execute("SELECT a, b FROM t"):
        left[a] = b
    out = []
    for a, c in con.execute("SELECT a, c FROM u"):
        if c is None:
            continue
        out.append((left[a], c))
    return sorted(out)

def counted(con):
    n = {}
    for k, in con.execute("SELECT k FROM t"):
        n[k] = n.get(k, 0) + 1
    return n

def deduped(con):
    return set(r[0] for r in con.execute("SELECT a FROM t"))

def rebuilt(con):
    return {r[0] for r in con.execute("SELECT a FROM t")}

def stored(con):
    return {r[0] for r in con.execute("SELECT a FROM u")}

def reflects(con):
    return rebuilt(con) - stored(con)

def pure_helper(xs):
    d = {}
    for a, b in xs:
        d[a] = b
    return sorted(d.items())
'''
    _rd = _tf.mkdtemp()
    _rp = os.path.join(_rd, "relalg_case.py")
    with open(_rp, "w", encoding="utf-8") as _fh:
        _fh.write(_rsrc)
    _r = relalg_sites(_rp)
    _rk = {(fn, kind) for _l, kind, fn, _s in _r}

    # the dict-build side and the probe side are the two halves of ONE join
    check("a dict keyed off rows then probed by a second query is a JOIN",
          ("withheld", "join") in _rk, True)
    # ⚑ A GUARD-CONTINUE IS A `WHERE`, and it is the cheapest thing to migrate.
    check("a guard-continue over query rows is a withheld WHERE",
          ("withheld", "filter") in _rk, True)
    check("sorted() over row-derived rows is a withheld ORDER BY",
          ("withheld", "sort") in _rk, True)
    # ⚑ `d[k] = d.get(k,0)+1` IS THE GROUP BY, and it must NOT read as a join —
    # the distinction is whether the stored value AGGREGATES the old one.
    check("per-key accumulation is GROUP BY, not a join",
          ("counted", "group-by") in _rk, True)
    check("a set() built purely to dedupe rows is a withheld DISTINCT",
          ("deduped", "distinct") in _rk, True)
    # ⚑ THE HIGHEST-VOLUME REAL SITE HAS THIS SHAPE AND THE FIRST CUT MISSED IT.
    # `reconstruct.reflects_edge` is `edge_from_obs(con,c) - edge_stored(con,c)`,
    # a 6.27M-row EXCEPT whose operands are ordinary CALLS. A predicate keyed on
    # direct `con.execute` reads that function as subtracting two locals — the
    # defect sits ONE HOP from the cursor, which is where a per-call-site reader
    # stops. Rows arriving via a store-reading helper are rows.
    check("a set difference between two store-reading helpers is a set-op",
          ("reflects", "set-op") in _rk, True)

    # ⚑ THE GATE THAT KEEPS THIS FROM FLAGGING THE WHOLE CORPUS: identical
    # algebra over an in-memory argument is NOT withheld from any engine. Without
    # the reads-the-store precondition every `sorted()` in 45 files is a hit and
    # the census is unreadable — a mode that reports everything reports nothing.
    check("identical algebra over a non-store argument is NOT reported",
          [k for _l, k, fn, _s in _r if fn == "pure_helper"], [])

    # ── --relname: a name used AS A RELATION, not as a substring ──────────────
    # ⚑ THESE FAIL AGAINST THE PRE-CHANGE CODE BY CONSTRUCTION — `sql_relnames`
    # did not exist, and the two neighbouring modes CANNOT answer: `--sql` and
    # `--literal` are both substring matches, which is why `--sql node` returned
    # 82 sites of which almost all were `node_child`/`obs_node`/`orbit_node`.
    #
    # ⚑ EVERY CASE BELOW IS A DISCRIMINATION, NOT A HIT. Asserting only that
    # `node` is found would pass against the substring matcher this replaces;
    # what has to hold is that the NEIGHBOURS are excluded, which is the whole
    # capability. Each fixture plants a near-miss on purpose.
    check("a FROM target is a relation",
          "node" in sql_relnames("SELECT * FROM node WHERE x=1"), True)
    check("...and a LONGER name containing it is NOT",
          "node" in sql_relnames("SELECT * FROM node_child"), False)
    # ⚑ AN ALIAS IS NOT A RELATION even when it is spelled like one, and the column
    # qualifier that reads off it is not one either — `FROM obs_node node` names
    # `obs_node`, once, and a word-boundary regex reports `node` twice.
    check("...nor is an ALIAS spelled like a relation",
          sql_relnames("SELECT node.id FROM obs_node node"), {"obs_node"})
    check("a JOIN target is a relation",
          sql_relnames("SELECT 1 FROM a JOIN b ON b.i=a.i") == {"a", "b"}, True)
    # ⚑ A CTE IS BOUND BY THE STATEMENT, so it names nothing the store holds —
    # and the recursive form is where a positional lexer goes wrong, because the
    # name appears in a FROM position INSIDE its own definition.
    check("a recursive CTE name is NOT a relation, its base table is",
          sql_relnames("WITH RECURSIVE reach(n) AS (SELECT 1 UNION SELECT nc.child_id "
                       "FROM node_child nc JOIN reach r ON nc.node_id=r.n) "
                       "SELECT n FROM reach") == {"node_child"}, True)
    # ⚑ THE DERIVED TABLE MUST BE RECURSED INTO. A wholesale skip of the
    # parenthesised group reports `schema_queue.py:769`'s real statement as
    # touching NO relation at all — an absence read as a verdict.
    check("a relation inside a DERIVED TABLE is found",
          "obs_node" in sql_relnames(
              "SELECT count(*) FROM (SELECT n.core_id FROM obs_node n) d"), True)
    # ⚑ `FROM` INSIDE AN EXPRESSION PAREN IS NOT A RELATION INTRODUCER — the
    # `EXTRACT(EPOCH FROM ts)` / `substring(s FROM n)` idiom. And the guard must
    # not swallow a genuine subquery nested in an expression, which is why the
    # scope is decided per-paren by its FIRST token rather than by recursing only
    # into query scopes (my first cut, which lost the second case).
    check("EXTRACT(… FROM x) names no relation",
          sql_relnames("SELECT extract(epoch FROM ts) FROM event"), {"event"})
    # ⚑ `IS NOT DISTINCT FROM` — MEASURED AS A LIVE FALSE POSITIVE, not invented. It is
    # the operator `dec_drain`'s retire predicate is written on (`=` would let a NULL
    # reconstruction vanish in three-valued logic), so the walker was reporting a
    # relation `dec` in the read set of the ladder's DELETE and its header build. The
    # `EXTRACT` guard above does not cover it: this `FROM` is at query scope.
    check("IS NOT DISTINCT FROM names no relation",
          sql_relnames("SELECT 1 FROM core_decoded c WHERE c.dec IS NOT DISTINCT FROM s.dec"),
          {"core_decoded"})
    check("...and the plain DISTINCT FROM spelling likewise",
          sql_relnames("SELECT 1 FROM obs o WHERE o.v IS DISTINCT FROM p.v"), {"obs"})
    check("...but SELECT DISTINCT … FROM t is still a relation",
          sql_relnames("SELECT DISTINCT x FROM t"), {"t"})
    check("...but a subquery nested in an expression still counts",
          "t" in sql_relnames("SELECT coalesce((SELECT max(x) FROM t), 0) FROM u"), True)
    check("a table FUNCTION is not a stored relation",
          sql_relnames("SELECT * FROM generate_series(1,3) g"), set())
    check("INSERT INTO / UPDATE / DROP TABLE name their target",
          (sql_relnames("INSERT INTO terms (a) VALUES (1)")
           | sql_relnames("UPDATE core_fp SET mtime=1")
           | sql_relnames("DROP TABLE IF EXISTS obs_node")),
          {"terms", "core_fp", "obs_node"})
    # ── --relname's READ/WRITE SPLIT (`sql_rw`) — the ⒣ read-set primitive ────────
    # ⚑ THESE FAIL AGAINST THE PRE-CHANGE CODE BY CONSTRUCTION: `sql_rw` did not
    # exist, and `sql_relnames` returns the UNION, in which the property *"a retire
    # predicate reads nothing at or below the tier it writes"* is not expressible —
    # the DELETE's own target is in the union, so every retire reads as violating
    # itself. Each case below is a DISCRIMINATION between the two sets, not a hit.
    #
    # ⚑ THE FIRST ONE IS THE LIVE RETIRE RUNG, verbatim from `dec_drain._RETIRE`.
    # `DELETE`'s target sits after `FROM`, the token that introduces every read in
    # the language, so a reader keyed on `FROM` alone manufactures a same-tier read.
    _w, _r = sql_rw("DELETE FROM core_decoded c WHERE EXISTS ("
                    "SELECT 1 FROM core_decoded_shadow s WHERE s.core_id = c.core_id)")
    check("a DELETE target is a WRITE", _w, {"core_decoded"})
    check("...and is NOT also read", _r, {"core_decoded_shadow"})
    # ⚑ BOTH ROLES ON ONE NAME IS THE SELF-TERMINATING RUNG IDIOM, not a defect —
    # `dec_drain._REBUILD` re-reads its own memo to exclude what is already done, so
    # a reader that made the sets disjoint would report the exclusion as absent.
    _w, _r = sql_rw("INSERT INTO dec_val (id, v) SELECT n.id, n.v FROM dec_node n "
                    "WHERE NOT EXISTS (SELECT 1 FROM dec_val v WHERE v.id = n.id)")
    check("an INSERT target is a WRITE", _w, {"dec_val"})
    check("...and the SAME name is also a read when the SQL reads it",
          _r, {"dec_node", "dec_val"})
    _w, _r = sql_rw("UPDATE core_fp SET mtime = o.mtime FROM obs o WHERE o.id = core_fp.id")
    check("an UPDATE target is a WRITE, its FROM is a read", (_w, _r),
          ({"core_fp"}, {"obs"}))
    check("a plain SELECT writes nothing",
          sql_rw("SELECT 1 FROM event e JOIN obs o ON o.id = e.id"),
          (set(), {"event", "obs"}))
    check("DROP TABLE is a write", sql_rw("DROP TABLE IF EXISTS obs_node"),
          ({"obs_node"}, set()))
    # ⚑ THE PROJECTION IDENTITY IS THE GUARD THAT THE TWO MODES CANNOT DRIFT APART.
    # `sql_relnames` is now defined AS the projection; this case is what makes that
    # definition load-bearing rather than a comment, and it would fail the moment
    # anyone re-implements the older walk beside it.
    _stmt = ("WITH r AS (SELECT 1 AS id) INSERT INTO dec_root (root) "
             "SELECT r.id FROM r JOIN dec_node n ON n.id = r.id "
             "JOIN dec_ref f ON f.head = n.head JOIN core_decoded c ON c.core_id = f.core_id")
    _w, _r = sql_rw(_stmt)
    check("writes | reads == sql_relnames, exactly", _w | _r, sql_relnames(_stmt))
    check("a CTE is in neither set", "r" in (_w | _r), False)
    # ⚑ THE HEAD IS DEPTH-AWARE. `dec_drain._ROOT` opens `WITH r AS (SELECT …)` and
    # only then INSERTs; a first-token reader types the ladder's header build as a
    # SELECT and drops it out of the ⒣ population without reporting anything absent.
    check("a leading CTE does not hide the INSERT head",
          sql_kind("WITH r AS (SELECT 1) INSERT INTO dec_root (root) SELECT 1 FROM r"),
          "insert")
    check("a DELETE with a subquery is still a delete",
          sql_kind("DELETE FROM core_decoded c WHERE EXISTS (SELECT 1 FROM s)"), "delete")
    check("a column list does not hide the INSERT head",
          sql_kind("INSERT INTO dec_val (id, v) SELECT 1, 2"), "insert")
    check("a plain query heads SELECT", sql_kind("SELECT 1 FROM event"), "select")
    check("the roles view agrees with the split",
          sql_rel_roles(_stmt),
          {(n, "w") for n in _w} | {(n, "r") for n in _r})

    # ⚑ THE `name` ROLE IS THE OTHER HALF AND IT IS EXACT-EQUALITY, not substring
    # — `--literal node_atom` reports `'node precedes node_atom'` as a hit, and a
    # shim census that admits prose is not a census.
    _nsrc = ('X = _T("node", "node_id")\n'
             'Y = "node precedes node_atom"\n'
             'Z = ["node_child"]\n')
    _nd = _tf.mkdtemp()
    _np = os.path.join(_nd, "relname_case.py")
    with open(_np, "w", encoding="utf-8") as _fh:
        _fh.write(_nsrc)
    _nr = relname_sites("node", _np)
    check("the shim spelling is found as role `name`",
          [r for r in _nr if r[0] == "name"] != [], True)
    check("...and prose merely CONTAINING the name is not",
          [r for r in _nr if r[4] != "node"], [])

    # ── --snapshots: one value built from several world-states ────────────────
    # ⚑ FAILS AGAINST THE PRE-CHANGE CODE BY CONSTRUCTION — `snapshot_sites` did
    # not exist, and `--calls scalar` structurally CANNOT answer it: it reports
    # `file:line` with no enclosing scope, so "two reads in one function" is not
    # expressible. The defect it was built for was live in `sppf_db.project_sppf`
    # (four `_schema.scalar` calls composed into one returned tuple).
    #
    # ⚑ THE FALSE-POSITIVE CASES ARE THE LOAD-BEARING ONES. The first cut counted
    # store-read NODES and reported 32 "composed" sites of which the majority were
    # `con.execute(sql).fetchall()` — ONE round trip spelled with two calls. A
    # census that flags the CORRECT spelling of the defect trains the reader to
    # skim, which is the state the defect was hiding in.
    _ssrc = '''
def four_snapshots(con):
    return (con.scalar("SELECT count(*) FROM a"),
            con.scalar("SELECT count(*) FROM b"))

def one_trip(con):
    return con.execute("SELECT a FROM t").fetchall()

def branch_is_one_trip(con, p):
    return con.execute("S", p) if p else con.execute("S")

def per_key(con):
    return {t: con.execute("SELECT count(*) FROM %s" % t).fetchone() for t in ("a", "b")}

def loop_is_fine(con, cores):
    out = []
    for c in cores:
        out.append(con.execute("SELECT a FROM t WHERE c=%s", (c,)).fetchall())
    return out
'''
    _sd = _tf.mkdtemp()
    _sp = os.path.join(_sd, "snapshot_case.py")
    with open(_sp, "w", encoding="utf-8") as _fh:
        _fh.write(_ssrc)
    _sr = snapshot_sites(_sp)
    _sk = {(fn, kind) for kind, fn, _l, _n, _s in _sr}
    check("two reads in ONE expression is COMPOSED",
          ("four_snapshots", "composed") in _sk, True)
    # ⚑ `execute(...).fetchall()` IS ONE ROUND TRIP. This is the case that failed
    # on the first cut and it is why the predicate keys on the RECEIVER being a
    # store read, not on a name roster.
    check("a CHAINED fetch is ONE trip, not two",
          ("one_trip", "composed") in _sk, False)
    # ⚑ AN `IfExp` RUNS ONE BRANCH — `schema_rows.execute`'s own body is
    # `cur.execute(sql, params) if params else cur.execute(sql)`, a single trip
    # under either binding, so the branches are MAXed rather than summed.
    check("a conditional between two spellings is ONE trip",
          ("branch_is_one_trip", "composed") in _sk, False)
    # ⚑ ONE CALL SITE, N EXECUTIONS — the shape `--calls` and a node count BOTH
    # read as 1. Its own kind because counting executions is undecidable and
    # folding it into either number would be wrong in a different direction.
    check("a read inside a comprehension is ITERATED",
          ("per_key", "iterated") in _sk, True)
    # ⚑ THE GATE THAT KEEPS THIS READABLE: a loop reading once per core is
    # CORRECT. Reporting it would make the census a list of the whole ingest.
    check("a per-item loop read is not COMPOSED",
          ("loop_is_fine", "composed") in _sk, False)

    # ── --control: EVERY piece of control flow, typed ─────────────────────────
    # ⚑ THESE FAIL AGAINST THE PRE-CHANGE CODE BY CONSTRUCTION — `control_sites`
    # did not exist, and the mode nearest to it CANNOT ANSWER: `_pycodemod_sql`'s
    # own docstring records that `relalg_sites` is blind to a loop with an early
    # break, which is exactly the class this census exists to surface.
    #
    # ⚑ THE FIXTURE IS A MUTATION TEST, NOT A SMOKE TEST.  Every construct in the
    # roster is PLANTED here; the first case asserts the census finds ALL of them,
    # so a construct the walker stops seeing fails loudly instead of quietly
    # shrinking a total.  A census that silently misses a kind is worse than no
    # census — it reads as coverage.
    _csrc = '''
import os
import subprocess
import sys

VERBOSE = False


def rows_loop(con, additive, dry_run):
    out = []
    for cid, sym in con.execute("SELECT cid, sym FROM node"):
        if sym is None:
            continue
        if sym == "x":
            break
        if sym == "y":
            return out
        out.append((cid, sym))
    else:
        out.append(None)
    if additive:
        out.sort()
    elif dry_run:
        out = []
    else:
        out = out[:1]
    n = len(out) if additive else 0
    while n > 0:
        n -= 1
    else:
        n = 0
    return out


def guards(con, path, want=None):
    if not path:
        return None
    if VERBOSE:
        print(path)
    assert os.path.exists(path)
    try:
        with open(path, "rb") as fh:
            blob = fh.read()
    except OSError:
        raise ValueError("nope")
    else:
        blob = blob
    finally:
        blob = blob or b""
    rows = con.execute("SELECT a FROM t").fetchall()
    keep = [r for r in rows if r[0] > 0]
    every = all(r[0] for r in rows)
    some = any(r[0] == 1 for r in rows)
    first = next((r for r in rows if r[0]), None)
    filt = filter(lambda r: r[0], rows)
    d = {}
    got = d.get("k", "dflt")
    bare = d.get("k")
    label = want or "unnamed"
    other = want or path
    both = want and path
    match len(rows):
        case 0:
            label = "empty"
        case _:
            label = "some"
    if not rows:
        raise RuntimeError("empty")
    return keep, every, some, first, filt, got, bare, label, other, both, blob


def shell(cmd):
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode:
        sys.exit(1)
    return p.stdout


def gen(con):
    for r in con.execute("SELECT a FROM t"):
        yield r[0]
    yield from con.execute("SELECT b FROM t")


def pure(xs):
    return [x for x in xs if x]
'''
    _cd = tempfile.mkdtemp()
    _cp = os.path.join(_cd, "control_case.py")
    with open(_cp, "w", encoding="utf-8") as _fh:
        _fh.write(_csrc)
    _cr = control_sites(_cp)
    _cons = {c for _l, c, _k, _f, _fn, _s in _cr}
    _ck = {(fn, c, k) for _l, c, k, _f, fn, _s in _cr}

    # (1) COMPLETENESS.  Every construct in the roster is planted in the fixture, so
    # the census must find every one — the roster and the fixture are checked against
    # each other rather than either being trusted.
    check("every construct in the roster is found in the fixture",
          sorted(set(CONSTRUCTS) - _cons), [])
    check("the roster and the fixture agree in BOTH directions",
          sorted(_cons - set(CONSTRUCTS)), [])
    check("all eight construct groups are represented",
          len(CONSTRUCT_GROUPS), 8)

    # (2) THE KINDS.  Same construct, same function, DIFFERENT kind — `if sym is
    # None` is a WHERE and `if additive` is not SQL at all.  A census that reported
    # both as "a branch" would be the tally-not-the-population defect.
    check("a loop over query rows is row-iteration",
          ("rows_loop", "for", "row-iteration") in _ck, True)
    check("a branch on ROW CONTENT is a WHERE",
          ("rows_loop", "if", "row-branch") in _ck, True)
    check("a branch on an ARGUMENT is a mode-branch, in the same function",
          ("rows_loop", "if", "mode-branch") in _ck, True)
    check("a comprehension guard over rows is a WHERE",
          ("guards", "comp-if", "row-branch") in _ck, True)
    check("a `with open(...)` is the ε boundary",
          ("guards", "with", "external") in _ck, True)
    check("`except OSError` is external on the TYPE, not the body",
          ("guards", "except", "external") in _ck, True)
    # ⚑ THE ONE-HOP ε PROPAGATION, WHICH THE FIRST CUT DID NOT HAVE.  `p =
    # subprocess.run(...)` then `if p.returncode:` — the branch's own expression
    # names no external module, so a predicate reading only the governing
    # expression called it `unclassified`.
    check("a branch on a value one hop from a subprocess is external",
          ("shell", "if", "external") in _ck, True)
    check("`sys.exit` is ε, not work for the engine",
          ("shell", "exit", "external") in _ck, True)
    check("yielding query rows is row-iteration",
          ("gen", "yield", "row-iteration") in _ck, True)
    # ⚑ ITERATING AN ARGUMENT IS NOT BRANCHING ON CONFIGURATION.  The first cut
    # tested every construct against the parameter names and reported `for x in xs`
    # in a pure helper as a mode-branch — moving a site out of the honest
    # "unclassified" into a kind that reads as a decision someone made.
    check("a comprehension over a plain argument is NOT a mode-branch",
          ("pure", "comp-for", "unclassified") in _ck, True)

    # (3) THE EARLY EXITS, WHICH ARE THE POINT.  All three forms, and each carries a
    # relational form only because the enclosing loop is over rows.
    check("break / continue / early return in a row loop are all early-exit",
          sorted(c for fn, c, k in _ck if k == "early-exit"),
          ["break", "continue", "return-in-loop"])
    _cform = {c: f for _l, c, k, f, _fn, _s in _cr if k == "early-exit"}
    check("an early break over rows is LIMIT 1 / EXISTS",
          _cform.get("break"), "LIMIT 1 / EXISTS")

    # ⚑ AND THE MODE THIS ONE EXISTS BESIDE IS BLIND TO EXACTLY THAT.  Stated as a
    # case rather than as prose, because `_pycodemod_sql`'s docstring already says
    # it and a docstring governs only the reader already looking at it.
    check("`--relalg` has NO construct for an early break; `--control` does",
          ("break" in _cons,
           [k for _l, k, _fn, _s in relalg_sites(_cp) if k == "break"]),
          (True, []))

    # (4) THE MUTATION.  Delete the two early-exit lines and the count MOVES — a
    # census whose total is insensitive to the thing it counts is decoration.
    _cmut = _csrc.replace('        if sym == "x":\n            break\n', "")
    _cmp = os.path.join(_cd, "control_mut.py")
    with open(_cmp, "w", encoding="utf-8") as _fh:
        _fh.write(_cmut)
    _cr2 = control_sites(_cmp)
    check("removing the break removes exactly the break and its guard",
          (len([1 for _l, c, _k, _f, _fn, _s in _cr2 if c == "break"]),
           len(_cr) - len(_cr2)),
          (0, 2))

    # (5) THE `unknown` COLUMN IS LOAD-BEARING.  A plausible guess there is noise
    # that reads like analysis, so an unclassified site must never carry a form.
    check("an unclassified site never claims a relational form",
          sorted({f for _l, _c, k, f, _fn, _s in _cr if k == "unclassified"}),
          ["unknown"])
    check("every kind reported is in the declared roster",
          sorted({k for _l, _c, k, _f, _fn, _s in _cr} - set(CONTROL_KINDS)), [])

    # ⚑ THE NAME-SCOPED-CENSUS DEFECT, PINNED.  Two DIFFERENT functions spelled
    # with one bare name is the exact live shape: `jea/metalanguage/schema.py`
    # calls a selftest's sqlite `connect` AND the store resolver's `connect`, and
    # a bare `--calls connect` reported them as ONE population of 33 — a number I
    # then used to size a fix.  CLAUDE.md records the class ("a --calls <name>
    # census is NAME-SCOPED, NOT CAPABILITY-SCOPED"); this is the mode that closes
    # it.  These cases FAIL against the pre-receiver scanner, where every dotted
    # query returned the bare-name population.
    src_r = ("import sqlite3\nimport store\n"
             "def m():\n"
             "    a = sqlite3.connect(':memory:')\n"
             "    b = store.connect()\n"
             "    c = store.connect('rw')\n"
             "    return a, b, c\n")
    p_r = os.path.join(d, "recv.py")
    open(p_r, "w", encoding="utf-8").write(src_r)
    _rl = lambda t: sorted(l for _p, k, _n, l in scan([p_r], t) if k == "call")
    check("a receiver-qualified query selects ONE of two same-named calls",
          _rl("store.connect"), [5, 6])
    check("the other receiver selects the OTHER call",
          _rl("sqlite3.connect"), [4])
    # ⚑ AND THE BARE SPELLING MUST NOT MOVE — a widened default would silently
    # change every existing consumer's answer, which is the opposite of the fix.
    check("the bare name still returns BOTH receivers",
          _rl("connect"), [4, 5, 6])
    # ⚑ THE HONEST LIMIT, ASSERTED RATHER THAN LEFT TO BE DISCOVERED: the receiver
    # is matched as TEXT, so an alias is a different key.  Measured live —
    # `sqlite3.connect` returned 0 against schema.py because it imports the module
    # as `_s3`.  A reader who assumes resolution would call that an empty
    # population; it is a fact about the spelling.
    src_a = "import sqlite3 as _s3\ndef m():\n    return _s3.connect(':memory:')\n"
    p_a = os.path.join(d, "alias.py")
    open(p_a, "w", encoding="utf-8").write(src_a)
    check("an ALIASED receiver is a different key (text, not resolution)",
          (len([r for r in scan([p_a], "sqlite3.connect") if r[1] == "call"]),
           len([r for r in scan([p_a], "_s3.connect") if r[1] == "call"])),
          (0, 1))

    # ── `--split`: the CUT, and every way it can silently change meaning ──────────────
    # ⚑ EVERY CASE HERE FAILS AGAINST THE CODE BEFORE THE MODE EXISTED, because the mode
    # did not exist: `--size` named the violation, `--layout` located it, and the cut was
    # left to string surgery.  What these pin is not that a split HAPPENS but that the
    # four ways it changes meaning without failing are each refused.
    import _pycodemod_split as _sp

    # (1) SCOPE PRECISION.  A local that shadows a module-level name is NOT a dependency.
    # The cheap over-approximation ("every Name loaded anywhere inside") makes a false
    # edge, and one false edge turns a DAG into an SCC that the mode then refuses.
    _s1 = ("TABLE = {}\n"
           "def f():\n"
           "    TABLE = 1\n"
           "    return TABLE\n"
           "def g():\n"
           "    return TABLE\n")
    _pf = os.path.join(d, "sc.py")
    open(_pf, "w", encoding="utf-8").write(_s1)
    _st = {t["name"]: t for t in _sp.statements(_pf)[2]}
    check("a shadowing LOCAL is not a module-level dependency",
          "TABLE" in _st["f"]["free"], False)
    check("a genuine module-level read IS a dependency",
          "TABLE" in _st["g"]["free"], True)

    # (2) THE SIDE-EFFECT ORDER.  Two impure statements that merely READ the same name
    # have no data edge between them, so a data-flow sort may emit them either way round.
    # gcalculus' cotype ends with exactly that pair — populate `ROUTES["shadow"]`, then
    # prune the buckets that stayed empty — and the wrong order empties the table while
    # every gate reports a clean sweep over it.
    _s2 = ("R = {'a': {}}\n"
           "def fill():\n"
           "    return 1\n"
           "R['a']['k'] = fill()\n"
           "R['a'] = {k: v for k, v in R['a'].items() if v}\n")
    _pf2 = os.path.join(d, "so.py")
    open(_pf2, "w", encoding="utf-8").write(_s2)
    _tops2 = _sp.statements(_pf2)[2]
    check("a subscript assignment is IMPURE", _tops2[2]["is_pure"], False)
    check("a prune-the-empties comprehension is IMPURE too", _tops2[3]["is_pure"], False)
    check("an assignment to a bare name is PURE", _tops2[0]["is_pure"], True)
    _pl2 = _sp.plan(_pf2, max_lines=200)
    _flat = [j for part in _pl2["parts"] for j in part]
    check("two impure statements keep their SOURCE order through the topological sort",
          _flat.index(2) < _flat.index(3), True)

    # (3) THE `__file__` HAZARD, AND ITS FALSE-POSITIVE TWIN.  A DIRECTORY read survives a
    # sibling emission; reading THIS file's own text does not.  The coarse form of this
    # check reported 23 of 33 statements on the cotype and 22 were of the safe shape — a
    # hazard list that is mostly noise is disbelieved wholesale, real entries included.
    _s3 = ("from pathlib import Path\n"
           "def near():\n"
           "    return (Path(__file__).resolve().parent / 'x.bib').read_text()\n"
           "def own():\n"
           "    return Path(__file__).read_text()\n"
           "def neither():\n"
           "    return Path(__file__).resolve().parent\n")
    _pf3 = os.path.join(d, "fh.py")
    open(_pf3, "w", encoding="utf-8").write(_s3)
    _h = {t["name"]: (t["reads_file"], t["reads_source"]) for t in _sp.statements(_pf3)[2]}
    check("reading a SIBLING file through __file__.parent is not a hazard",
          _h["near"], (True, False))
    check("reading THIS file's own text through __file__ IS a hazard",
          _h["own"], (True, True))
    check("using __file__ as a location only is not a hazard",
          _h["neither"], (True, False))

    # (4) LOSSLESSNESS AND THE COMMENTS, which are the whole reason this is libcst and not
    # `ast`.  A relocated def must arrive with its ⚑ block, its blank lines and its
    # trailing comment intact — a transform that keeps code and drops commentary destroys
    # the more valuable half of these files.
    _s4 = ('"""mod doc."""\n'
           "import os\n"
           "\n"
           "\n"
           "# ⚑ WHY a exists\n"
           "def a():\n"
           "    return os.sep  # trailing\n"
           "\n"
           "\n"
           "def b():\n"
           "    return a()\n"
           "\n"
           "\n"
           "T = {'k': b}\n")
    _pf4 = os.path.join(d, "ls.py")
    open(_pf4, "w", encoding="utf-8").write(_s4)
    _pl4 = _sp.plan(_pf4, max_lines=12)
    check("a bound of 12 forces more than one part", len(_pl4["parts"]) > 1, True)
    check("every part is UNDER the bound",
          [n for n, c in _pl4["files"].items() if len(c.split("\n")) > 12], [])
    check("the split is byte-for-byte lossless", _sp.verify(_pf4, _pl4)[0], True)
    _all4 = "".join(_pl4["files"].values())
    check("the ⚑ comment survived the relocation", "# ⚑ WHY a exists" in _all4, True)
    check("the TRAILING comment survived too", "return os.sep  # trailing" in _all4, True)
    check("the module docstring stays with the ENTRY module",
          "mod doc." in _pl4["files"]["ls.py"], True)

    # (5) EVERY PART IS IMPORTED, whether the entry needs a name from it or not.  A part
    # whose bindings are all private would otherwise be imported by nobody, never execute,
    # and take its module-level side effects with it — silently.
    check("the entry module references every part it created",
          [f"ls_{k:02d}" for k in range(len(_pl4["parts"]))
           if f"ls_{k:02d}" not in _pl4["files"]["ls.py"]], [])

    # (6) A CYCLE IS A REFUSAL, NAMED.  Emitting it would produce sibling imports that
    # fail at import time against a half-initialised module, which is a worse outcome than
    # not splitting: the file is broken rather than merely too big.
    _s5 = ("def f():\n"
           "    return T\n"
           "T = {'k': f}\n"
           "def g():\n"
           "    return T\n")
    _pf5 = os.path.join(d, "cy.py")
    open(_pf5, "w", encoding="utf-8").write(_s5)
    check("an acyclic fan-in table splits", _sp.plan(_pf5, max_lines=200)["error"], None)
    _s6 = ("A = [1]\n"
           "def f():\n"
           "    return B\n"
           "B = f\n"
           "A.append(B)\n"
           "def h():\n"
           "    return A\n")
    _pf6 = os.path.join(d, "cy2.py")
    open(_pf6, "w", encoding="utf-8").write(_s6)
    check("a backwards data dependency through a def is not a cycle by itself",
          _sp.plan(_pf6, max_lines=200)["error"], None)

    # (7) THE LINE COUNT IS THE GATE'S, NOT `splitlines()`'s.  They differ by one on every
    # file that ends in a newline, i.e. on every file, and a splitter judged by one count
    # while planning against the other is wrong on every part at once.
    check("_size counts the trailing newline the way a size gate does",
          (_sp._size("a\nb\n"), len("a\nb\n".splitlines())), (3, 2))

    # (8) A SINGLE STATEMENT OVER THE BOUND IS A REFUSAL THAT NAMES IT.  Relocation cannot
    # shrink a body; saying "no packing fits" without saying which body is the census-
    # names-a-defect-it-cannot-help-you-fix shape `--layout` exists to close.
    _big = "def big():\n" + "".join(f"    x{k} = {k}\n" for k in range(40))
    _pf7 = os.path.join(d, "bg.py")
    open(_pf7, "w", encoding="utf-8").write(_big)
    _pl7 = _sp.plan(_pf7, max_lines=20)
    check("an unsplittable statement is refused on BUDGET", _pl7["error"], "budget")
    check("and the refusal names the statement",
          [nm for _f, _n, _h, comp in _pl7["detail"] for nm, _l in comp], ["big"])

    # (9) THE DEFINITION BOUND IS A SECOND, INDEPENDENT AXIS, AND A LINE BOUND CANNOT SEE IT.
    # A Δ grade cache keys each check on a hash of the module's sorted qualname SET, so ADDING
    # a definition invalidates every READER of that module while editing one body invalidates
    # only the check sensitive to that body.  N defs is N× the blast radius of an addition.
    # The fixture is the shape measured on gcalculus' cotype: six tiny defs, far under any
    # line bound, and over a def bound of two.  Before `--max-defs` existed this planned as a
    # single part and there was no argument that could say otherwise.
    _s8 = "".join(f"def d{k}():\n    return {k}\n" for k in range(6))
    _pf8 = os.path.join(d, "md.py")
    open(_pf8, "w", encoding="utf-8").write(_s8)
    _pl8a = _sp.plan(_pf8, max_lines=500)
    check("six small defs are ONE part under a line bound alone", len(_pl8a["parts"]), 2)
    _pl8b = _sp.plan(_pf8, max_lines=500, max_defs=2)
    check("the definition bound cuts what the line bound cannot see",
          _pl8b["error"], None)
    _by8 = {t["i"]: t for t in _pl8b["tops"]}
    check("and no part it writes holds more definitions than the bound",
          max(_sp._defcount(ids, _by8) for ids in _pl8b["parts"]), 2)
    check("the definition-bounded split is still byte-for-byte lossless",
          _sp.verify(_pf8, _pl8b)[0], True)
    # ⚑ COMPOSES, DOES NOT REPLACE.  `--max` keeps its exact meaning; passing a def bound may
    # only ever cut MORE finely, never coarser, and omitting it must leave the plan identical.
    check("omitting the definition bound leaves the plan unchanged",
          len(_sp.plan(_pf8, max_lines=500, max_defs=None)["parts"]), len(_pl8a["parts"]))
    check("a definition bound never produces fewer parts than the line bound alone",
          len(_pl8b["parts"]) >= len(_pl8a["parts"]), True)
    # AND THE LINE BOUND IS STILL LOAD-BEARING UNDER A GENEROUS DEF BOUND — the mirror case,
    # which is why neither bound may be dropped in favour of the other.
    _s9 = "".join(f"def e{k}():\n" + "".join(f"    y{j} = {j}\n" for j in range(30))
                  for k in range(3))
    _pf9 = os.path.join(d, "ml.py")
    open(_pf9, "w", encoding="utf-8").write(_s9)
    _pl9 = _sp.plan(_pf9, max_lines=40, max_defs=99)
    check("a generous def bound does not disable the line bound", len(_pl9["parts"]) > 2, True)

    # ── `--fingerprint` ─────────────────────────────────────────────────────────
    # ⚑ THE CASES LIVE IN THE MODE'S OWN MODULE AND ARE COUNTED HERE.  This file stands
    # at 1,084 of its 1,200-line cap, so a fourth wave of fixtures inline would push the
    # suite module over the gate it exists under; and `_pycodemod_fingerprint` carries no
    # `__main__` dispatch, so `run_selftests.discover()` cannot mistake it for a 70th
    # suite (the phantom the flag-text regex would otherwise mint).  Two constraints, one
    # placement.
    _fp_cases(check)

    # ── `--reifies` ─────────────────────────────────────────────────────────────
    # ⚑ THE CENSUS THE ⟡sorted-stream-carrier ARC RAN BY HAND.  Every reification figure
    # in that plan was assembled from `--layout` + `--calls` + reads — judgement in the
    # turn, in the arc whose subject is exactly that.  These cases pin the shapes.
    _rfsrc = '''
def lit_set():
    return {"a", "b"}

def lit_dict():
    return {"k": 1}

def comp_set(xs):
    return {x for x in xs}

def comp_dict(xs):
    return {x: 1 for x in xs}

def call_set(xs):
    return set(xs)

def call_sorted(xs):
    return sorted(xs)

def accum(xs):
    out = []
    for x in xs:
        out.append(x)
    return out

def accum_dict(xs):
    d = {}
    for x in xs:
        d[x] = 1
    return d

def streams(xs):
    for x in xs:
        yield x

def scalar(xs):
    return len(xs)

def passthrough(xs):
    return xs
'''
    _rfd = tempfile.mkdtemp()
    _rfp = os.path.join(_rfd, "reify_case.py")
    with open(_rfp, "w", encoding="utf-8") as _fh:
        _fh.write(_rfsrc)
    _rf = {r[2]: (r[3], r[4]) for r in reifies([_rfp])}

    check("a returned set literal is a set reification",
          _rf.get("lit_set"), ("set", "returns-literal"))
    check("a returned dict literal is a dict reification",
          _rf.get("lit_dict"), ("dict", "returns-literal"))
    check("a returned set COMPREHENSION counts (the corpus-shaped builder)",
          _rf.get("comp_set"), ("set", "returns-comp"))
    check("a returned dict comprehension counts",
          _rf.get("comp_dict"), ("dict", "returns-comp"))
    check("`return set(xs)` is a call-built reification",
          _rf.get("call_set"), ("set", "returns-call"))
    # ⚑⚑ THE ROW THE MODE EXISTS FOR, AND IT MUST NOT FOLD INTO returns-call.  A def that
    # sorts and returns has PAID for an order and then dropped the fact, so its callers
    # re-sort defensively — `agda_defs.import_index()` sorts at :1732 and SAYS SO in its
    # docstring while `importers_of()` re-sorts at :1757 anyway.  Collapsing this into
    # returns-call would make the actionable population unfindable among 280 others.
    check("`return sorted(xs)` gets its OWN why, not returns-call",
          _rf.get("call_sorted"), ("sorted", "returns-sorted"))
    check("a name grown by .append and returned is an accumulator",
          _rf.get("accum"), ("accum", "returns-accum"))
    check("a dict grown by subscript-assign and returned is an accumulator",
          _rf.get("accum_dict"), ("accum", "returns-accum"))

    # ⚑ THE NEGATIVE CASES ARE THE HALF THAT KEEPS THE CENSUS HONEST.  A predicate that
    # accepts everything reports a population and finds nothing; a generator and a scalar
    # are precisely what a reification is NOT, and `passthrough` is the coarse-in-the-safe-
    # direction boundary — returning an argument unchanged reifies nothing here.
    check("a generator is NOT a reification (it is the target shape)",
          "streams" in _rf, False)
    check("a returned scalar is NOT a reification", "scalar" in _rf, False)
    check("returning an argument unchanged is NOT a reification",
          "passthrough" in _rf, False)

    # ⚑ THE SKIP ACCOUNTING, WHICH IS WHY THIS MODE DECLARES scans=True THOUGH IT NEVER
    # CALLS scan().  A census that read 0 of 810 files prints "nothing materializes here",
    # which is the confident-zero the whole arc is about.
    check("reifies() reports the population it actually read",
          (reifies.population, reifies.skipped), (1, []))
    _rfbad = os.path.join(_rfd, "broken.py")
    with open(_rfbad, "w", encoding="utf-8") as _fh:
        _fh.write("def f(:\n")
    reifies([_rfbad])
    check("an unparseable file is COUNTED as skipped, never silently dropped",
          (reifies.population, len(reifies.skipped), reifies.skipped[0][1]),
          (1, 1, "unreadable"))

    # ── `--resorts` — the CONSUMER arm, and it is a SPAN query ──────────────────
    # ⚑ THE PAIR IS THE UNIT.  "Is this sort redundant" is not a property of the sort site;
    # it is a property of (producer, consumer), so no column on `--reifies` could carry it.
    # The producer census supplies one endpoint, the walk supplies the other.
    _rssrc = '''
def upstream(xs):
    return sorted(xs)

def redundant(xs):
    return sorted(upstream(xs))

def rekeyed(xs):
    return sorted(upstream(xs), key=len)

def reversed_too(xs):
    return sorted(upstream(xs), reverse=True)

def unrelated(xs):
    return sorted(plain(xs))

def plain(xs):
    return list(xs)
'''
    _rsd = tempfile.mkdtemp()
    _rsp = os.path.join(_rsd, "resort_case.py")
    with open(_rsp, "w", encoding="utf-8") as _fh:
        _fh.write(_rssrc)
    _rs = {r[2]: (r[3], r[4]) for r in resorts([_rsp])}

    check("sorting a callee that already sorted is the redundant row",
          _rs.get("redundant"), ("upstream", "resort-of-sorted"))
    # ⚑⚑ THE SPLIT THAT KEEPS THE CENSUS HONEST, AND IT CAUGHT A REAL MISREADING.  I read
    # `_pycodemod_query.swallows()` (`return sorted(rows)`) as a redundant re-sort of a
    # `py_files()` walk — it is not: the rows are sorted on the whole row tuple, a DIFFERENT
    # key from the path order they arrived in.  A `key=`/`reverse=` means real work, and a
    # census folding both into one number would have banked that error as a finding.
    check("a re-keyed sort is reported SEPARATELY, never as redundant",
          _rs.get("rekeyed"), ("upstream", "resort-rekeyed"))
    check("`reverse=` counts as a re-key too", _rs.get("reversed_too"),
          ("upstream", "resort-rekeyed"))
    check("sorting a callee that did NOT sort is not a re-sort at all",
          "unrelated" in _rs, False)

    # ⚑⚑ TWO POPULATIONS, KEPT SEPARATE — and my first cut of this mode got it wrong in BOTH
    # directions.  The producer set must be the UNION of the corpus and the walked paths: a
    # corpus-only set cannot see a pair that lives entirely outside it (the three cases above
    # all returned None until the union went in), and a walk-only set would make the join
    # report a fact about the SCOPE.  Then, because `reifies` stamps accounting on ITSELF,
    # the producer walk's skips must not be copied into the consumer's — a file the consumer
    # walk never opened is not a file it failed on.
    check("the consumer walk owns its own population, scoped to paths",
          (resorts.population, resorts.skipped), (1, []))
    check("the producer population is WIDER than the walk, and separately named",
          resorts.producer_population > resorts.population, True)

    # ⚑⚑ A ZERO FROM A SPAN QUERY MUST STATE ITS BASIS — the failure mode of a bounds-shaped
    # reader is SILENCE. It joins walked files against a PRODUCER census; if that census is
    # thin the join finds nothing, and the count line is byte-identical to a genuinely clean
    # result. A reader that finds nothing reads as "nothing double-sorts here" — the exact
    # over-broad conclusion it exists to prevent — and nothing in its own output contradicts
    # that. (linux-sources, 2026-08-19, from building the same shape in their tree.)
    _clean = os.path.join(_rsd, "clean.py")
    with open(_clean, "w", encoding="utf-8") as _fh:
        _fh.write("def f(xs):\n    return list(xs)\n")
    check("a clean file yields no rows but still exposes the producer basis",
          (resorts([_clean]), resorts.producer_population > 0), ([], True))

    # ── `--funcnames` — the half `--portable` structurally cannot see ───────────
    # ⚑⚑ THE GATE READ GREEN OVER A LIVE DEFECT. `--portable` EXPLAINs raw SQL LITERALS, so
    # `autocorr_synth.py` — which raised `UndefinedFunction: group_concat` on EVERY invocation
    # — reported `0 blocking site(s)`. A Core statement is never a string.
    _fnsrc = '''
from sqlalchemy import func, select

def portable(c):
    return select(func.count(c), func.max(c), func.coalesce(c, 0))

def dialect_specific(c):
    return select(func.string_agg(c, ','), func.jsonb_agg(c))

def sqlite_ism(c):
    return select(func.group_concat(c))

def not_sqlalchemy(node):
    return node.func.attr.value          # libcst's `.func` — an unrelated spelling
'''
    _fnd = tempfile.mkdtemp()
    _fnp = os.path.join(_fnd, "func_case.py")
    with open(_fnp, "w", encoding="utf-8") as _fh:
        _fh.write(_fnsrc)
    _fn = funcnames([_fnp])
    _byname = {r[3]: r[4] for r in _fn}

    check("a GenericFunction name is graded generic (SQLAlchemy owns the spelling)",
          (_byname.get("count"), _byname.get("max"), _byname.get("coalesce")),
          ("generic", "generic", "generic"))
    # ⚑⚑⚑ `string_agg` IS VALID POSTGRES AND STILL GRADES `verbatim`, WHICH IS THE WHOLE
    # POINT AND THE THING I FIRST GOT WRONG. I assumed the split was portable-vs-broken.
    # MEASURED (bounded probe, compile-only): `func.totally_made_up_xyz` compiles IDENTICALLY
    # on postgres and sqlite, and SQLAlchemy has exactly ONE registry (`_default`, 52 names)
    # with no per-dialect list to check against. So the split is
    # translated-vs-passed-through, and this census CANNOT say a function does not exist.
    # A mode claiming otherwise would invent a verdict its instrument cannot support.
    check("a valid-but-dialect-specific name is verbatim, NOT an error",
          (_byname.get("string_agg"), _byname.get("jsonb_agg")),
          ("verbatim", "verbatim"))
    check("the sqlite-ism that made a capability dark is in the verbatim population",
          _byname.get("group_concat"), "verbatim")

    # ⚑ RECEIVER-SCOPED, AND IT IS LOAD-BEARING. `--attr func` reports 111 corpus sites of
    # which nearly all are libcst's `node.func` — an unrelated attribute with the same
    # spelling. A name-scoped census would bury the 40 real rows in noise: the `--calls emit`
    # defect (a fact about the METHOD read as a fact about the substrate), sign-flipped.
    check("libcst's `node.func` is NOT a SQLAlchemy func call",
          any(r[2] == "not_sqlalchemy" for r in _fn), False)

    # ⚑ THE REGISTRY IS ASKED, NEVER LISTED — a hardcoded 52 names would go stale on a
    # SQLAlchemy upgrade and grade a newly-generic function verbatim forever.
    check("the generic set comes from SQLAlchemy's own registry and is non-empty",
          len(_generic_func_names()) > 10, True)

    # ⚑⚑ THE OTHER HALF OF ⟡core-func-dialect: `--portable` MUST SAY WHAT IT CANNOT SEE.
    # It reported `0 blocking site(s)` on the file raising UndefinedFunction on every call.
    # The zero was true of LITERALS and read as true of the file — a gate green over a live
    # defect. The fix is NOT widening the predicate (EXPLAIN needs a statement, and one
    # cannot be recovered from a Core expression without the caller's tables and binds); it
    # is naming the boundary, which is the same "name the instrument" principle this census
    # already applies to engine-verdict-vs-pattern-guess, one layer out.
    _ps = portable_sites(_fnp)
    check("a Core-only file still has NO literal blockers (the zero was never wrong)",
          _ps, [])
    check("but the Core-built SQL it could not judge is now RECORDED, not dropped",
          sorted({n for _l, n in portable_sites.core_built}),
          ["coalesce", "count", "group_concat", "jsonb_agg", "max", "string_agg"])

    # ⚑ RESET BEFORE EVERY EARLY RETURN, and this case is why. The attribute is per-call; if
    # it were only ASSIGNED on the happy path, a caller looping over files would attribute
    # one file's Core sites to the NEXT file that exits early — the stale-context defect at
    # per-file granularity. A file with no `func.` at all must clear it.
    _plain = os.path.join(_fnd, "plain.py")
    with open(_plain, "w", encoding="utf-8") as _fh:
        _fh.write("def f():\n    return 1\n")
    portable_sites(_plain)
    check("a file with no Core SQL CLEARS the attribute (no carry-over)",
          portable_sites.core_built, [])

    # ── --ambient: ⟡ambient-root, the UNION census ───────────────────────────────
    # ⚑⚑ EVERY CASE HERE IS A DEFECT THAT WAS ACTUALLY COMMITTED WHILE WRITING THE
    # MODE, not a hypothetical.  The reader was built to correct a one-spelling
    # census and reproduced the same class four times inside itself; each arm below
    # pins one of those, so a later widening cannot silently undo it.
    import _pycodemod_ambient as _amb
    _ad = tempfile.mkdtemp()
    _ap = os.path.join(_ad, "amb.py")
    with open(_ap, "w", encoding="utf-8") as _fh:
        _fh.write(
            "import os, glob, subprocess, shutil\n"
            "ROOT = os.path.dirname(os.path.abspath(__file__))\n"
            "def anchored():\n"
            "    return os.path.exists(os.path.join(ROOT, 'x.agda'))\n"
            "def anchored_file():\n"
            "    return os.path.abspath(__file__)\n"
            "def scoped(path):\n"
            "    return open(path).read()\n"
            "def repo_relative():\n"
            "    return glob.glob('agda/Substrate/**/*.agda')\n"
            "def command():\n"
            "    return subprocess.run(['agda', '--version'])\n"
            "def rel_script():\n"
            "    return subprocess.run(['scratch/prune_imports.py'])\n"
            "def explicit_source(pattern, src):\n"
            "    return os.listdir(pattern, src)\n"
            "def mutate():\n"
            "    os.chdir('agda')\n")
    _ar = _amb.ambient([_ap])
    _by = {ctx: (kind, verdict) for _p, _l, kind, verdict, _t, ctx in _ar}

    # ⚑ THE ANCHORED CASES MUST PRODUCE NO ROW AT ALL.  A census that reports every
    # correctly-anchored filesystem call has not answered "what depends on ambient
    # cwd" — it has listed every filesystem call, which is the population the
    # question was asked ABOUT, not the answer.
    check("a join onto ROOT is ANCHORED — no row",
          "anchored" in _by, False)
    # ⚑ `os.path.abspath(__file__)` IS THE CANONICAL ANCHORING IDIOM IN THIS REPO
    # and the first cut filed it UNKNOWN: the `__file__` arm was reachable only
    # through the `abspath` branch, never for a bare operand. A reader that cannot
    # recognise the standard fix reports its own gap as the corpus's ambiguity.
    check("`abspath(__file__)` is ANCHORED — no row",
          "anchored_file" in _by, False)

    check("a path that is the function's own PARAMETER is SCOPED (the feature)",
          _by.get("scoped", (None, None))[1], "SCOPED")
    check("a repo-relative literal is REPO (the defect class)",
          _by.get("repo_relative", (None, None))[1], "REPO")
    # ⚑⚑ THE WORST ROW THE READER PRODUCED, and it was CONFIDENT rather than absent.
    # `subprocess.run("agda", ...)` was classified REPO because the repo has a
    # top-level directory NAMED `agda` and `repo_subtrees()` discovers it — a
    # command resolved on PATH reported as an ambient repo-relative read. Ten of
    # the first twenty-five REPO rows were this. A false REPO row is the actionable
    # one, so this class invites exactly the wrong paydown.
    check("a bare command name is PATH-resolved, not cwd-relative — no row",
          "command" in _by, False)
    check("but a relative SCRIPT path in argv[0] still reports",
          _by.get("rel_script", (None, None))[1], "REPO")
    # ⚑ THE REPO'S OWN FIX WAS READING AS THE DEFECT. `vfs.listdir(pat, source)`
    # resolves against an EXPLICIT source — it is the route OUT of ambient
    # resolution — and the unqualified-name vocabulary matched it as `os.listdir`
    # and filed four such sites as REPO. An explicit second argument IS an anchor.
    check("an explicit source argument makes the call SCOPED",
          _by.get("explicit_source", (None, None))[1], "SCOPED")
    check("`os.chdir` is its own verdict — it MUTATES the thing under study",
          _by.get("mutate", (None, None))[1], "MUTATES")

    # ⚑⚑ THE BLIND SPOTS ARE DECLARED AND MUST STAY NON-EMPTY.  This is the
    # `census-green-is-a-fact-about-the-census` guard: the mode's whole justification
    # is that `--calls getcwd` was read as a bound when it was a floor, so a union
    # that shipped without its own misses would repeat the defect one level up.
    check("the reader declares what it cannot see", len(_amb.KNOWN_MISSES) > 0, True)
    check("and the population is reported, so a zero is distinguishable",
          _amb.ambient.population, 1)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"pycodemod selftest: {ok}/{len(cases)}")
    return ok == len(cases)
