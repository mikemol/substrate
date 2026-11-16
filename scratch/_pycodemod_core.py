# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Corpus enumeration and the shared CST visitor for `pycodemod`.

⚑ THIS IS THE SEAM EVERY OTHER MODULE SITS ON, AND `--calls py_files` MEASURED IT:
71 call sites, of which 3 are in OTHER TOOLS (`shared_cache.py`,
`check_mypy_ratchet.py`, `check_scratch_independence.py`).  So the corpus walk is
already the tool's public foundation; making it a module names what was true.

⚑ `ROOT`, `py_files` AND `corpus` ARE ONE UNIT AND CANNOT BE SEPARATED.
`py_files` reads the module-global `ROOT`; `corpus.__enter__` REBINDS it with
`global ROOT` so that `--archive` / `--in` swap the corpus under every mode at
once (its own docstring records the measurement: "25 of 25 query call sites route
through it").  Put the walker and the global in different modules and `global
ROOT` rebinds a name nothing reads — the envelope would go inert while still
reporting success.  They move together or not at all.

⚑ `_Scan` LIVES HERE BECAUSE FOUR MODES SHARE IT — `--calls`, `--dead`,
`--forwards`, `--binding`.  It carries a receiver field so `--calls store.connect`
can distinguish an aliased receiver from a resolved one; the ⚑ blocks inside it
record why a def's own name, and a call's own `func` name, must not count as
references (both would make `--dead` report nothing as dead, silencing the query
rather than failing it).

⚑ THE `if cst is not None:` GUARD IS PRESERVED VERBATIM.  This tool is importable
with libcst absent — `--available` and the usage banner still answer — and a
class defined unconditionally against a `None` module would turn that into an
ImportError at module load, breaking every consumer including `run_selftests`.
"""
import ast
import functools
import inspect
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import libcst as cst
    import libcst.metadata  # noqa: F401
except ImportError:  # pragma: no cover - environment probe
    cst = None



ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The `--discards` sweep's own census (see the `--discards` dispatch): a multi-minute
# corpus walk must not leave its result only in a terminal, or the next reader re-runs
# it — or redirects it to a scratch file the tool cannot read back.  Same shape as
# `split_pipeline`'s `.leaf-verify.tsv`.
DISCARD_LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              ".discards-census.tsv")


# ⚑ DISCOVERED, NOT FROZEN — and the frozen form was silently under-reporting.
# This was `("scratch", "scripts")`, so `catalog/` (the worklist's item and
# figure witnesses) was OUTSIDE the corpus: `--attr own_agda_files_definers`
# returned `0 read(s)` while `items.py:375` plainly calls it.  An empty result
# from a query whose scope excludes the subject is not a finding, it is a gap
# wearing a finding's clothes — and every unscoped question this tool answers
# was under-reporting by exactly that directory.
#
# THIRD OCCURRENCE OF THIS EXACT DEFECT IN THE REPO: `run_selftests.DIRS` was a
# frozen tuple twice (missing `jea/`, then missing `catalog/` — which did not
# exist when the tuple was written), and its own docstring argued against
# hardcoding while hardcoding one level up.  A roster can only ever be as
# current as its last edit; the fix is to discover, not to add a fourth entry.
_SKIP_DIRS = {"agda", "node_modules", "__pycache__", "docs", ".venv",
              ".git", ".edit-snapshots"}


# ⚑⚑ `--` ENDS THE FLAGS, AND WITHOUT IT A FLAG-SHAPED OPERAND IS UNASKABLE.  The
# dispatch strips every `-`-leading token from its operand list, which is right for
# flags and wrong for a mode whose SUBJECT can look like one: `--literal --holding` and
# `--literal=--holding` both fell through to the usage block, so *"which tools carry the
# literal `--holding`?"* — the question that LOCALIZES a mis-attributed mode in the
# `toolmodes` census — could not be put to this tool at all.  MEASURED 2026-08-18 while
# auditing exactly that; the answer (`edit_snapshot.py`, and NONE of the three tools the
# census named) was unreachable until this existed.
#
# ⚑ THE POSIX CONVENTION, NOT A NEW ONE, and it is the STANDING form of a repair the
# dispatch has taken five times per its own ⚑ blocks (`--corpus` ate `--bib`'s operand;
# `--key` ate `--archive`'s; `--marks record` read as a path; `--since` grew a private
# subtraction that fixed one branch and left its sibling).  Those all partition WHICH
# flag owns a token; this answers the PRIOR question — whether a token is a flag at all
# — which no amount of ownership bookkeeping can decide.
#
# ⚑⚑ AND IT MUST GOVERN FLAG *RECOGNITION*, NOT ONLY OPERAND COLLECTION.  The first cut
# split argv inside `_dispatch` alone, and `--literal -- --selftest` then RAN THE SUITE:
# the `__main__` guard tests `"--selftest" in sys.argv`, which reads straight past the
# marker.  Every site asking "is this flag present" must ask it of the SAME slice, or the
# marker is honoured in half the parse and ignored in the other — worse than not having
# it, because the operand silently becomes a mode.
#
# ⚑ HERE AND NOT IN `pycodemod.py` because the selftest module must reach them, and
# `pycodemod` imports THAT — the cycle is what places these in the core.
def flagged_argv(argv=None):
    """The argv slice in which a `-`-leading token is a FLAG — everything before `--`."""
    argv = sys.argv if argv is None else argv
    return argv[1:argv.index("--", 1)] if "--" in argv[1:] else argv[1:]


def operand_tail(argv=None):
    """The tokens after `--` — operands, UNFILTERED, however flag-shaped they look."""
    argv = sys.argv if argv is None else argv
    return argv[argv.index("--", 1) + 1:] if "--" in argv[1:] else []


def _roots():
    # ⚑ THE SKIP VOCABULARY MUST APPLY AT THE ROOT LEVEL TOO, AND ONCE DID NOT.
    # `py_files` filtered generated trees by walking `rel`, but a generated tree
    # that is a TOP-LEVEL entry becomes its own root — and then `rel` starts
    # BELOW it, so the component check never sees the name and the whole tree is
    # admitted.  Measured on paperkit: `bazel-bin/` is a top-level symlink into
    # bazel's output base, so `--in <paperkit> --imports` attributed `pathlib` to
    # 1425 files (mutation-testing copies) and `--calls references` returned
    # 135KB of generated hits, with the filter installed and doing nothing.
    # One vocabulary (`_GENERATED_DIRS`), enforced at BOTH levels.
    # ⚑ AND `os.path.isdir` FOLLOWS SYMLINKS.  bazel's convenience links
    # (`bazel-bin`, `bazel-<workspace>`) are symlinks, so an `isdir` test admits
    # them as ordinary directories; the name test is what excludes them, which
    # is exactly why the name test has to be here.
    return tuple(sorted(
        d for d in os.listdir(ROOT)
        if os.path.isdir(os.path.join(ROOT, d))
        and not d.startswith(".")
        and d not in _SKIP_DIRS
        and d not in _GENERATED_DIRS
        and not d.startswith("bazel-")))


def escapes(paths=None):
    """[(path, line, text, seq)] — string literals whose escape does not exist.

    ⚑ AN INVALID ESCAPE IS AN INTENT FAILURE, WHICH IS WORSE THAN A PARSE FAILURE
    (user, 2026-08-02).  I dismissed a `SyntaxWarning` as "not a parse failure" and
    that is the wrong reading: a parse failure is loud and self-correcting, while
    `"\\ "` PARSES FINE and silently means backslash-space -- so every regex
    containing one is matching a pattern its author did not write.  Python warns
    only because it intends to make this an error later; today it is a predicate
    quietly measuring something else.

    ⚑ THIS IS THE `\\b`-ON-AGDA-NAMES CLASS IN THE PYTHON LAYER.  That defect was a
    regex that ran, produced plausible output, and answered a different question
    (measured: 1269 of 10831 names invisible to it).  Same shape here, and it sat
    inside tools whose numbers I was quoting.

    ⚑ AND THE WARNING WAS THE SIGNAL I ARGUED PAST.  It fired on every run of the
    item sweep; I noted it as noise and reported the finding anyway.  The rule this
    repo already records -- when a measurement emits a complaint about its own
    instrument, fix the instrument before quoting the number -- applies, and a
    warning is exactly such a complaint.
    """
    import warnings as _w
    out = []
    for p in (paths or py_files()):
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        with _w.catch_warnings(record=True) as caught:
            _w.simplefilter("always", SyntaxWarning)
            try:
                compile(src, p, "exec")
            except SyntaxError:
                continue             # a real parse error is a different finding
        lines = src.splitlines()
        for w in caught:
            if not issubclass(w.category, SyntaxWarning):
                continue
            msg = str(w.message)
            if "escape sequence" not in msg:
                continue
            ln = w.lineno or 0
            seq = re.search(r'"(\\.)"', msg)
            out.append((p, ln,
                        (lines[ln - 1].strip() if 0 < ln <= len(lines) else ""),
                        seq.group(1) if seq else "?"))
    return out


def package_root(modname):
    """(path, detail) — where an INSTALLED module's source lives, or (None, why).

    ⚑ THE REUSE-SEARCH COULD NOT REACH A DEPENDENCY, WHICH IS WHERE IT MATTERS
    MOST.  `py_files` excludes `site-packages` BY CONSTRUCTION and correctly so:
    vendored code is not our corpus, and once it leaked in, a PY2 file made mypy
    refuse the entire run.  But the standing rule is to search for the structure a
    plan would reinvent — and the strongest candidate is usually a library that is
    already installed.  With no route to it, "does the OTLP exporter already
    retry/buffer?" had no answer here, and I reached for a `python3 -c` to read
    `__file__` — the shape this module exists to remove.

    ⚑ SCOPE STAYS EXPLICIT.  This never widens the DEFAULT corpus; it is reachable
    only by naming the package, so `--dead` over our tools cannot start counting
    third-party defs. Two populations, two questions, one tool.

    ⚑ AND IMPORTING IS THE ONLY HONEST RESOLVER.  A path guess (`site-packages/<name>`)
    is wrong for namespace packages, editable installs and vendored trees alike --
    `opentelemetry.exporter.otlp.proto.http` is a NAMESPACE package whose parts live
    in several distributions.  We ask the import system where it actually is.
    """
    import importlib.util
    try:
        spec = importlib.util.find_spec(modname)
    except (ImportError, ValueError, ModuleNotFoundError) as e:
        return None, f"not importable here: {e}"
    if spec is None:
        return None, "not importable here: no such module"
    # ⚑ A PACKAGE IS ITS DIRECTORY, NOT ITS `__init__.py`, AND CHECKING `origin`
    # FIRST GETS THAT BACKWARDS.  `sqlite3.__spec__.origin` is the `__init__.py`,
    # so an origin-first branch reported ONE file for a package with a dozen --
    # a population silently narrowed to its entry point.  Ask "does it claim
    # search locations" (i.e. is it a package) BEFORE falling back to origin.
    locs = [p for p in (getattr(spec, "submodule_search_locations", None) or [])
            if os.path.isdir(p)]
    if locs:
        return locs[0], "; ".join(locs)
    if spec.origin and spec.origin != "namespace" and os.path.isfile(spec.origin):
        # a plain module: its own file is the population
        return spec.origin, spec.origin
    return None, "importable but has no source on disk (built-in or frozen)"


# ⚑ GENERATED OUTPUT TREES ARE NOT THE CORPUS.  Same class as `.edit-snapshots`
# backups polluting a census: a MACHINE-DERIVED copy of a source file reads
# exactly like the source, so it enters every count silently.  Measured: `--in
# <paperkit> --calls references` returned 135KB of hits, nearly all from
# `bazel-bin/.../mut_project__*.mutated.py` — mutation-testing artifacts, one
# copy per mutant per build configuration, burying the single real definition.
# These are matched as whole PATH COMPONENTS (see below), so `rebuild/` and
# `buildtools/` are unaffected.  Naming one of these trees explicitly as a root
# still reaches it — that is a different question, and gets a different answer.
_GENERATED_DIRS = frozenset((
    "bazel-bin", "bazel-out", "bazel-testlogs", "bazel-genfiles",
    "build", "dist", "_build",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".nox", ".eggs",
))


class PopulationError(Exception):
    """A requested root resolved to nothing — raised rather than silently emptied."""


def _resolve_root(r):
    """One caller-supplied root → the absolute path it names. CWD FIRST, then the tool's tree.

    ⚑⚑ IT WAS `os.path.join(ROOT, r)` UNCONDITIONALLY, SO A RELATIVE PATH NAMED A FILE IN THE
    TOOL'S TREE RATHER THAN THE CALLER'S. This tooling is symlinked into other checkouts, and
    a peer running `--commentary tools/no_owner_audit.py` from their own repo got SUBSTRATE'S
    ENTIRE 6,005-line census back: the path does not exist under ROOT, `os.walk` on a missing
    directory yields nothing, the population came back empty, and every caller falls through
    to the default corpus. **They nearly recorded my flag count as their repo's**, and what
    stopped them was recognising my filenames — not anything this tool said.
    ⚑ A path like `scripts/` exists in BOTH trees, and that case is worse: it resolves
    silently to mine and the answer is well-formed, plausible and about the wrong repo.

    ⚑ CWD WINS, BECAUSE THE CALLER'S SHELL IS WHAT THEY MEANT. The ROOT fallback stays for
    the modes and gates inside this tree that pass `scratch/`-relative paths and are invoked
    from anywhere; it is a FALLBACK now, not the first reading, so it can only widen what a
    caller could already reach — never redirect it.
    """
    if os.path.isabs(r):
        return r
    here = os.path.abspath(os.path.join(os.getcwd(), r))
    if os.path.exists(here):
        return here
    there = os.path.join(ROOT, r)
    if os.path.exists(there):
        return there
    # ⚑ NEITHER TREE HAS IT — AND SILENTLY RETURNING THE DEFAULT CORPUS IS THE WHOLE BUG.
    # `print(" ⚑ NO FILES SEARCHED — a fact about the QUERY, not the code.")` is already in
    # this toolkit, three times, for exactly this class; the ENUMERATOR never consulted it.
    # An unresolvable root is a fact about the QUERY and must be raised, not absorbed.
    raise PopulationError(
        "no such path in the current directory or in %s: %s" % (ROOT, r))


def py_files(*roots):
    """Every tool source under the given roots (default: DISCOVERED from ROOT).

    ⚑ ONE ENUMERATION, NOT ONE PER CODEMOD — the rule `agda_lex.agda_files`
    enforces for the Agda corpus, applied to the Python corpus.  (For a TRANSFORM
    the CLI does its own walking; this is for the QUESTIONS below.)
    """
    out = []
    for r in (roots or _roots()):
        base = _resolve_root(r)
        if os.path.isfile(base):
            out.append(base)
            continue
        for d, _sub, fs in os.walk(base):
            # ⚑ VENDORED CODE IS NOT OUR CORPUS, AND ITS ABSENCE WAS UNTESTED.
            # The exclusion list held `__pycache__` and `.edit-snapshots` but not
            # virtualenvs, so `scratch/.venv/…/setuptools/…/bdist_msi.py` (PY2
            # syntax) entered the population and made mypy refuse the ENTIRE run.
            # `--roundtrip` and `--dead` were reading it too — silently, because a
            # third-party file that round-trips looks exactly like one of ours.
            # **The corpus this module claims to measure is `scratch/` + `scripts/`
            # AS WRITTEN HERE, not everything under those paths.**
            # ⚑ THE SKIP IS RELATIVE TO THE REQUESTED ROOT, NOT ABSOLUTE.  When a
            # caller NAMES a package under `site-packages` (`--package`, the
            # reuse-search's route to a dependency), skipping it would return an
            # empty population for the one question the mode exists to answer --
            # an absence wearing a finding's clothes, the defect this file's own
            # `_roots` comment records. Vendored code stays out of the DEFAULT
            # corpus because the default roots never reach it; asking for it
            # explicitly is a different question, and gets a different answer.
            # ⚑ GENERATED OUTPUT TREES ARE NOT THE CORPUS EITHER.  Same class as
            # `.edit-snapshots` above: `bazel-bin/` / `bazel-out/` (and the
            # `bazel-<workspace>` convenience SYMLINKS that point into them) hold
            # MACHINE-DERIVED copies of the sources — paperkit's mutation testing
            # emits `mut_project__*.mutated.py` there, so `--calls references`
            # returned 135KB of hits from generated mutants and none of it was
            # source.  Reading a generated copy as if it were the corpus inflates
            # every census by the number of build configurations.  `dist`/`build`
            # (setuptools) and `.tox`/`.mypy_cache`/`.pytest_cache` are the same
            # kind of tree.  As above, the skip is RELATIVE to the requested root:
            # naming `bazel-bin` explicitly still reaches it.
            rel = os.path.relpath(d, base)
            if any(x in rel for x in (".edit-snapshots", "__pycache__",
                                      ".venv", "site-packages", "node_modules",
                                      "/_build/", "/.git/")):
                continue
            # ⚑ MATCH A PATH COMPONENT, NOT A SUBSTRING.  `"build" in rel` would
            # also eat `rebuild/`, `buildtools/` and any real package whose name
            # merely CONTAINS the word — the class of bug this repo already paid
            # for with a hand-written regex whose `.` matched any character.
            # Split on the separator and compare whole components.
            parts = set(rel.split(os.sep))
            if parts & _GENERATED_DIRS:
                continue
            # bazel's convenience symlinks are named `bazel-<workspace>`, so the
            # set cannot enumerate them — the workspace name is per-repo.
            if any(x.startswith("bazel-") for x in parts):
                continue
            out.extend(os.path.join(d, f) for f in fs if f.endswith(".py"))
    return sorted(out)


def roundtrip(path):
    """(ok, detail) — does parse→emit reproduce the file BYTE-FOR-BYTE?"""
    if cst is None:
        return False, "libcst not importable"
    try:
        src = open(path, encoding="utf-8").read()
    except OSError as e:
        return False, f"unreadable: {e}"
    try:
        out = cst.parse_module(src).code
    except Exception as e:  # a syntax error is a real answer, not a crash
        return False, f"parse failed: {type(e).__name__}"
    return (out == src), ("identical" if out == src else "DIFFERS after re-emit")


class _Unknown:
    """The NOT-A-LITERAL marker for `_value_of`.

    ⚑ A SENTINEL AND NOT `None`, BECAUSE `None` IS A LITERAL VALUE.  `f(reset=None)`
    is a caller asserting a constant; `f(reset=flag)` is a value this reader cannot
    see.  Spelling both `None` would collapse exactly the distinction `_value_of`
    exists to draw — the same one-level-down collapse `--asserted` suffers when it
    reports `reset=True` and `reset=False` as one undifferentiated LITERAL bucket.

    ⚑ AND IT MUST NOT BE FALSY-BY-ACCIDENT EITHER.  `if value:` over a report that
    can legitimately carry `0`, `""` or `False` is the same defect wearing a
    different hat, so this compares only by IDENTITY (`is UNKNOWN`) and renders as
    a word a reader cannot mistake for data."""

    __slots__ = ()

    def __repr__(self):
        return "UNKNOWN"


UNKNOWN = _Unknown()


def _value_of(node):
    """The VALUE of a constant argument expression, or `UNKNOWN`.

    ⚑ THE STEP `--forwards` AND `--asserted` BOTH STOP SHORT OF, and it is the one
    that decides whether a call is DANGEROUS.  `--forwards` says the keyword was
    PASSED; `--asserted` says the value was WRITTEN rather than COUNTED; neither can
    say WHICH constant.  Measured live: `sandbox_connect(reset=…)` has 23 call sites
    and `--asserted` reports "23 of 23 pass a LITERAL", while `reset=True` calls
    `store.sandbox_reset()`, which DROPS EVERY RELATION in the tenant.  A 23-site
    destructive surface was therefore unauditable with this repo's own tools, and
    `grep` is hook-refused at `.py` by construction — a toolkit gap read as a
    category, which is the failure this repo's standing rule names.

    ⚑ NEVER GUESSES.  An f-string with interpolation, a bare name, an attribute, a
    conditional, a call, a container — every one of them returns `UNKNOWN`.  A
    reader that silently rendered `reset=flag` as a value would answer "is this call
    destructive" with a fabrication, which is strictly worse than the gap it fills:
    the gap is visible, the fabrication is not.

    ⚑ `_shape_of` IS DEFINED FROM THIS, NOT BESIDE IT.  Two predicates over the same
    call node, maintained separately, is the shape where `--asserted` and this mode
    could disagree about what a single site IS while agreeing they are looking at
    it.  Same reasoning `--fingerprint` records for subclassing `--control`'s census
    rather than re-deriving the verdict.  So the parity is structural, not a case.
    """
    if cst is None:                                  # pragma: no cover
        return UNKNOWN
    if isinstance(node, cst.UnaryOperation):
        inner = _value_of(node.expression)
        if inner is UNKNOWN:
            return UNKNOWN
        op = node.operator
        try:
            if isinstance(op, cst.Minus):
                return -inner
            if isinstance(op, cst.Plus):
                return +inner
            if isinstance(op, cst.BitInvert):
                return ~inner
            if isinstance(op, cst.Not):
                return not inner
        except TypeError:
            # ⚑ `-"abc"` PARSES AND DOES NOT EVALUATE.  The predecessor called this
            # a literal by recursing on shape alone; it is a TypeError at runtime,
            # so UNKNOWN is the honest reading and the two now agree here too.
            return UNKNOWN
        return UNKNOWN
    if isinstance(node, (cst.Integer, cst.Float, cst.Imaginary)):
        try:
            return ast.literal_eval(node.value)
        except (ValueError, SyntaxError):            # pragma: no cover
            return UNKNOWN
    if isinstance(node, cst.Name):
        if node.value == "True":
            return True
        if node.value == "False":
            return False
        if node.value == "None":
            return None
        return UNKNOWN
    if isinstance(node, cst.SimpleString):
        try:
            return ast.literal_eval(node.value)
        except (ValueError, SyntaxError):            # pragma: no cover
            return UNKNOWN
    if isinstance(node, cst.ConcatenatedString):
        left, right = _value_of(node.left), _value_of(node.right)
        if left is UNKNOWN or right is UNKNOWN:
            return UNKNOWN
        try:
            return left + right
        except TypeError:                            # pragma: no cover
            return UNKNOWN
    if isinstance(node, cst.FormattedString):
        # an f-string is a literal only if nothing is interpolated
        if any(isinstance(p, cst.FormattedStringExpression) for p in node.parts):
            return UNKNOWN
        return "".join(p.value for p in node.parts
                       if isinstance(p, cst.FormattedStringText))
    return UNKNOWN


def _shape_of(node):
    """"literal" if the argument is a constant expression, else "computed".

    ⚑ THE DISTINCTION `--forwards` CANNOT DRAW, and it is the one that separates a
    witness that MEASURES its population from one that ASSERTS a number.  A
    keyword's PRESENCE says the caller supplied it; only the value's SHAPE says
    whether the caller counted anything.  Measured live: `items.T25_LIBRARY`
    returns `size=1` from a short-circuit branch, and `T28_CLOSURE` computes
    `len(gaps)` over a two-branch decision tree — both booleans typed as integers,
    both feeding a SORT KEY, so they were guaranteed to tie forever.

    ⚑ A UNARY MINUS ON A LITERAL IS STILL A LITERAL (`size=-1`), and an f-string
    with no interpolation is too.  Getting either wrong would misreport the very
    sites this exists to find, so both are handled rather than left to the
    default — the guard-from-the-instance defect this repo has recorded five
    times is exactly "handle the shape in front of you and no other".

    ⚑ NOW DERIVED FROM `_value_of`, NOT A SECOND WALK OVER THE SAME NODE.  The two
    were written apart and would have had to be kept in agreement by hand; a
    predicate and the reader it gates, maintained separately, is precisely how
    `--asserted` and `--values` could come to disagree about what a single call site
    IS.  Deriving makes the parity structural — there is one classifier, and
    "literal" MEANS "a value came back".  (One behaviour moved as a consequence and
    is recorded rather than hidden: `-"abc"` used to read `literal` on shape alone;
    it is a TypeError at runtime, so it now reads `computed`.)
    """
    return "computed" if _value_of(node) is UNKNOWN else "literal"


def _src_of(node, limit=60):
    """The node's SOURCE TEXT, whitespace-collapsed and bounded.

    ⚑ THE THIRD MEMBER OF THE `_value_of` / `_shape_of` FAMILY, and it answers the
    question neither can: not what a node EVALUATES to (usually UNKNOWN for a test
    like `apply` — a bare name) and not whether it is constant, but WHAT THE AUTHOR
    WROTE.  For an enclosing `if` test that is the whole content: `if apply:` and
    `if args.apply:` are different keys, and collapsing them to UNKNOWN would make
    the condition census answer nothing.

    ⚑ BOUNDED BY CONSTRUCTION, because this text becomes a GROUPING KEY.  An
    unbounded condition (a long boolean chain) would mint a singleton bucket per
    site and turn a census into a listing — the same cardinality failure that put
    `bibstruct --add <KEY>` into three VictoriaLogs streams.  Truncation is marked
    with `…` so a reader can never mistake a clipped key for a complete one.

    Returns UNKNOWN if the node cannot be rendered, never a guess — the stance
    `_value_of` already takes.
    """
    if cst is None or node is None:
        return UNKNOWN
    try:
        text = cst.Module(body=[]).code_for_node(node)
    except Exception:
        return UNKNOWN
    text = " ".join(text.split())
    if not text:
        return UNKNOWN
    return text if len(text) <= limit else text[:limit] + "…"


class corpus:
    """`with corpus(path): ...` — run ANY query against another source tree.

    ⚑ AN ARCHIVE IS A SCOPE, NOT A MODE (user, 2026-08-02: *"what you want for
    --archive is to have it open up the archive and THEN do whatever else as it
    would normally do.  This isn't something to do in parallel, this is an
    envelope"* / *"where I said 'envelope' I should have said `with X:`"*).  I had
    built `--archive` as a leaf that walked members itself, then bolted `--show`
    onto it when I wanted a body -- so every question about a reference needed its
    own re-implementation, and `--archive` could only ever answer the sub-questions
    someone remembered to add.  That is the frozen-roster shape one level up.

    ⚑ THE PIVOT IS `py_files`, MEASURED: 25 of 25 query call sites route through
    it, and `ROOT` is ONE module-level assign live across the file.  So rebinding
    the root is sufficient for every query to follow -- no query changes, and the
    two bespoke archive readers (`archive_defs`, `archive_source`) become
    `--dead`, `--calls`, `--imports`, `--rivals` over a different root.

    ⚑ AND `with` IS LOAD-BEARING OVER A PARAMETER: the temp tree is removed by the
    protocol rather than by remembering, on the error path too.  A `root=` argument
    threaded through 25 sites is the same coupling this repo keeps retiring.

    ⚑ THE NO-EXTRACT RULE IS RE-EXAMINED, NOT INHERITED.  `archive_defs` recorded
    "a reference is READ, not installed" -- correct, because writing one into
    `scratch/` invites edits to a copy no gate covers.  A temp directory discarded
    on exit does not have that property, and carrying the old constraint into a
    different design would be exactly the stale-judgement-as-code this file's own
    `_roots` comment is about.  Accepts an archive OR a plain directory."""

    def __init__(self, path):
        self.path = path
        self._tmp = None
        self._saved = None

    def __enter__(self):
        global ROOT
        import tarfile
        import tempfile
        self._saved = ROOT
        if os.path.isdir(self.path):
            ROOT = os.path.abspath(self.path)
            return ROOT
        self._tmp = tempfile.mkdtemp(prefix="pycodemod-corpus-")
        with tarfile.open(self.path) as tf:
            # ⚑ MEMBERS ARE FILTERED, not trusted: a path-traversing member
            # ("../") would write OUTSIDE the temp tree, which is the one way a
            # read-only query could damage the repo it is run from.
            safe = [m for m in tf.getmembers()
                    if not os.path.isabs(m.name)
                    and ".." not in m.name.split("/")]
            try:
                tf.extractall(self._tmp, members=safe, filter="data")
            except TypeError:            # `filter=` is newer than some runtimes
                tf.extractall(self._tmp, members=safe)
        ROOT = self._tmp
        return ROOT

    def __exit__(self, *exc):
        global ROOT
        ROOT = self._saved
        if self._tmp:
            import shutil
            shutil.rmtree(self._tmp, ignore_errors=True)
        return False                     # never swallow the query's exception




def _per_file(fn, paths, workers=None):
    """Map `fn` over files — in PROCESSES when it pays, serially when it does not.

    ⚑ THE VEHICLE IS MEASURED, NOT CHOSEN.  `scratch/cache_probe.py` on this
    corpus: the per-file derivation is `MetadataWrapper.resolve`, which is 93% of
    the cost and pure-Python tree walking — so **8 threads run it at 0.73x
    (SLOWER than serial, contention plus overhead) and 8 processes at 3.32x**.
    A thread pool here would look like parallelism and be a regression.

    ⚑ AND THE RAM OBJECTION IS RETIRED BY MEASUREMENT, not by argument.  I would
    have refused a process pool yesterday on "8 interpreters plus 8 position maps"
    — but `cassian_psi_avg10{res="memory"}` reads 0.0 on both `some` and `full`,
    and the operator's point stands: zswap/zpool exchanges RAM for CPU long before
    swap, so memory pressure surfaces on the axis already being watched.  A worker
    also RELEASES its map on return, so peak is `workers x one map` — a tunable,
    not a fixed cost.

    ⚑ SERIAL BELOW A THRESHOLD, because spawn is not free.  For a handful of files
    the pool costs more than it saves; the crossover is where the fixed cost of
    starting interpreters is paid back, and under it this is a plain loop.

    ⚑ AND THE READING THAT JUSTIFIES ALL OF THIS HAS A TIMESTAMP.  CPU was the
    binding resource when measured (2026-08-04, `psi{cpu,some}` 0.48, everything
    else 0.0).  The bottleneck moves; if that stops being true this choice is
    worth re-measuring rather than inheriting.

    `fn` must be a MODULE-LEVEL callable taking one path and returning a list —
    a closure cannot cross a process boundary."""
    files = list(paths)
    if len(files) < 12:
        out = []
        for p in files:
            out.extend(fn(p))
        return out
    import concurrent.futures as cf
    try:
        with cf.ProcessPoolExecutor(max_workers=workers) as pool:
            return [r for rows in pool.map(fn, files, chunksize=4) for r in rows]
    except Exception:
        # ⚑ A POOL FAILURE MUST NOT FAIL THE QUERY.  Spawn can be refused (a
        # sandbox, a fork restriction, a resource limit); the serial path is
        # slower and correct, and silently returning fewer rows would be the
        # guard-degrades-to-measuring-nothing shape.
        out = []
        for p in files:
            out.extend(fn(p))
        return out
