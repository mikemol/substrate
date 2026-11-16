# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⟡ambient-root — the UNION census of ambient-cwd dependence, in one query.

⚑⚑ THIS EXISTS BECAUSE THE QUESTION HAD ONLY ONE-SPELLING READERS, AND EACH
REPORTED A FLOOR AS IF IT WERE A BOUND.  "What depends on ambient cwd?" was being
tracked by `--calls getcwd` (20 sites, 9 files).  But a RELATIVE-PATH READ is the
same dependence under a different name and calls no `getcwd` at all:

    os.path.exists(mod.replace(".", "/") + ".agda")

is fully ambient and invisible to that census.  `--calls exists` returns 153 sites
and is ALSO not a bound — `open`, `listdir`, `glob`, `Path(...)`, and `subprocess`
with a relative argv are further spellings again.  No name-keyed census bounds the
union, because the union is not keyed on a NAME: it is keyed on the PROPERTY
"this call resolves a path, and the path it is given is not anchored".

⚑ SO THE PREDICATE IS TWO-PART, NOT A NAME MATCH.  A row is ambient when

  (a) the CALLEE is a filesystem-resolving function — recognised by its
      unqualified name against a declared vocabulary that spans FIVE families
      (`os.path`, `os`, `builtins.open`, `pathlib.Path`, `subprocess`+`shutil`),
      and
  (b) the PATH ARGUMENT is not anchored — it is not an absolute literal, does not
      flow from a name this module recognises as a root (`ROOT`, `_root`, `root`,
      `base`, `HERE`, `__file__`-derived), and is not itself an `os.path.join(...)`
      onto such a name.

Neither half alone is the population.  (a) alone reports every filesystem call in
the corpus, most of which are correctly anchored; (b) alone is not decidable.

⚑⚑ AND THE UNION IS STILL A FLOOR — WHICH THIS MODULE SAYS RATHER THAN HIDES.
`--ambient --misses` prints the spellings this reader KNOWS it cannot see, because
`census-green-is-a-fact-about-the-census`: a number without its blind spots reads
as a bound and gets banked as one.  That is the exact defect this module was built
to correct, and reproducing it one level up would be worse than not building it.
The known misses are enumerated in `KNOWN_MISSES` and printed on demand — never
computed, because a reader cannot derive what it cannot see.

⚑ CLASSIFICATION IS THE DELIVERABLE, NOT THE COUNT.  Not every relative path is a
defect.  A tool that operates on `os.getcwd()` as THE USER'S CHOSEN SCOPE (a
linter given a directory, a `--in <dir>` envelope) is behaving correctly; a tool
that resolves a REPO-RELATIVE path ambiently — `Substrate/...`, `agda/...`,
`scratch/...` — is a latent defect that reads wrong from any other directory.  The
second is the bug class; the first is the feature.  Rows are therefore reported
under three verdicts:

    SCOPED    the path is the caller's argument or an explicit parameter — the
              directory IS the question being asked.  Feature.
    REPO      the path literal (or its first component) names a KNOWN REPO
              SUBTREE — it is repo-relative and resolved ambiently.  Defect class.
    UNKNOWN   a computed path whose anchoring this reader cannot decide.

⚑⚑ `UNKNOWN` IS REPORTED AND NEVER FOLDED INTO EITHER SIDE.  Folding it into REPO
inflates the defect; folding it into SCOPED reads a defect as a feature — and the
witness for why that matters is in this repo already: `scope_source._source()`
returns `vfs.WorkingTree(os.getcwd())`, and passing `vfs.WorkingTree()` instead
would have reported every module ABSENT.  A read that succeeds at being wrong.
UNKNOWN is the honest boundary of the classifier, so it is a column, not a bucket.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pycodemod_core


#: The callee vocabulary, BY FAMILY — the five spellings of "resolve a path".
#:
#: ⚑ KEYED ON THE UNQUALIFIED NAME, and that is a deliberate over-reach in the
#: SAFE direction.  `exists` resolves whether written `os.path.exists`,
#: `path.exists`, `osp.exists` or bare after a `from os.path import exists`; a
#: qualified-name matcher would have to know every alias, and the aliases are what
#: `census-keyed-on-one-spelling` is about.  A false positive here is a row a
#: reader opens; a false negative is a site nobody ever sees again.
PATH_CALLS = {
    "os.path": ("exists", "isfile", "isdir", "islink", "getmtime", "getsize",
                "abspath", "realpath", "relpath", "samefile", "lexists"),
    "os":      ("listdir", "walk", "scandir", "stat", "lstat", "open", "remove",
                "unlink", "rename", "mkdir", "makedirs", "rmdir", "chdir"),
    "builtin": ("open",),
    "pathlib": ("Path",),
    "proc":    ("run", "call", "check_call", "check_output", "Popen", "which",
                "copy", "copy2", "copytree", "move", "rmtree"),
    "glob":    ("glob", "iglob"),
}

#: name -> family, flattened once.
_CALLEE_FAMILY = {n: fam for fam, names in PATH_CALLS.items() for n in names}

#: Names that ANCHOR a path — a call whose path flows from one of these is not
#: ambient.  ⚑ A ROOT IS RECOGNISED BY NAME, WHICH IS AN APPROXIMATION AND IS
#: DECLARED AS ONE.  `_pycodemod_core.ROOT`, `vfs.WorkingTree(root)`, and the
#: `_resolve_root(r)` idiom all bind the anchor to one of these spellings; a repo
#: that anchored on `self._where` would read as UNKNOWN here, correctly, rather
#: than as ambient.
ANCHOR_NAMES = {"ROOT", "root", "_root", "base", "basedir", "base_dir", "HERE",
                "here", "REPO", "repo", "repo_root", "AGDA", "_agda", "prefix",
                "dirname", "d", "top", "topdir", "workdir", "cwd", "tmpdir",
                "tmp", "outdir", "out_dir", "srcdir", "dest", "destdir"}

#: The repo's own top-level subtrees.  A relative literal whose FIRST COMPONENT is
#: one of these is REPO-relative — resolved against ambient cwd but MEANING a
#: fixed place in the tree.  That mismatch is the defect class.
#:
#: ⚑ DISCOVERED, NOT FROZEN — the `_SKIP_DIRS`/`run_selftests.DIRS` lesson
#: (`_pycodemod_core` records it as the THIRD occurrence in this repo).  A frozen
#: roster is only as current as its last edit, so the subtrees are read off the
#: repo root at call time and the constant below is only the fallback.
_REPO_SUBTREE_FALLBACK = {"agda", "scratch", "scripts", "jea", "catalog",
                          "Substrate", "docs", "_build"}


def repo_subtrees(root=None):
    """The repo's top-level directory names — DISCOVERED from the tree."""
    root = root or _pycodemod_core.ROOT
    try:
        found = {e.name for e in os.scandir(root) if e.is_dir()
                 and not e.name.startswith(".")}
    except OSError:
        found = set()
    # `Substrate` is a subtree of `agda/`, not of the root, and it is the single
    # most-quoted relative prefix in the scope tools — union it in explicitly.
    return found | _REPO_SUBTREE_FALLBACK


def _first_component(text):
    return text.replace("\\", "/").split("/", 1)[0]


def _callee_name(node):
    """The unqualified callee name of a Call, plus the receiver text if any."""
    f = node.func
    if isinstance(f, ast.Name):
        return f.id, None
    if isinstance(f, ast.Attribute):
        recv = f.value
        parts = []
        while isinstance(recv, ast.Attribute):
            parts.append(recv.attr)
            recv = recv.value
        if isinstance(recv, ast.Name):
            parts.append(recv.id)
        return f.attr, ".".join(reversed(parts)) or None
    return None, None


def _path_arg(node):
    """The AST node this call resolves as a path, or None if it takes none.

    ⚑⚑ A SUBPROCESS ARGV IS A LIST, AND ITS FIRST ELEMENT IS THE PATH.  My first
    cut handed the whole `List` node to the classifier, which could only report
    `<computed>` — so every `subprocess.run([...])` in the corpus banked as
    UNKNOWN and the largest single contributor to that bucket was a shape the
    reader could in fact decide.  Reading the LIST HEAD is the honest resolution:
    `run(["python3", "scratch/x.py"])` has a relative INTERPRETER (found on PATH,
    not cwd — not our question) but `run(["scripts/x.py"])` does not.
    ⚑ AND THE LATER ELEMENTS ARE NOT DROPPED SILENTLY — they are a DECLARED blind
    spot (`subprocess-argv` in `KNOWN_MISSES`), because a relative path in argv[2]
    is resolved by the CHILD against the cwd it inherits, and deciding that needs
    the child's own resolution rules.
    """
    if node.args:
        a = node.args[0]
        if isinstance(a, (ast.List, ast.Tuple)):
            return a.elts[0] if a.elts else None
        return a
    for kw in node.keywords:
        if kw.arg in ("path", "file", "filename", "dirname", "top", "cwd"):
            return kw.value
    return None


def _anchored(node):
    """Does this path expression flow from a recognised ROOT?

    ⚑ THE JOIN IS THE COMMON ANCHORING IDIOM AND IS CHECKED FIRST.
    `os.path.join(ROOT, "x")` is anchored by its FIRST argument; the later
    arguments are relative BY CONSTRUCTION and reading them would report every
    correctly-anchored site as ambient — an inversion, not an approximation.
    """
    if isinstance(node, ast.Call):
        name, _ = _callee_name(node)
        if name == "join" and node.args:
            return _anchored(node.args[0])
        # `os.path.abspath(__file__)` / `dirname(...)` anchor by construction.
        if name in ("abspath", "dirname", "realpath") and node.args:
            return _anchored(node.args[0]) or _mentions_file(node.args[0])
        return False
    # ⚑⚑ `__file__` IS THE STRONGEST ANCHOR IN THE CORPUS AND MY FIRST CUT MISSED IT.
    # `os.path.abspath(__file__)` is the standard module-anchoring idiom — it is
    # *the* way this repo binds `ROOT` — and it landed in UNKNOWN because the
    # `__file__` arm was reachable only through the `abspath` branch above, never
    # for a bare `__file__` operand.  A reader that files the canonical anchoring
    # idiom as "cannot decide" reports its own gap as the corpus's ambiguity, which
    # is the defect this module exists to correct, committed inside it.
    if _mentions_file(node):
        return True
    if isinstance(node, ast.Name):
        return node.id in ANCHOR_NAMES
    if isinstance(node, ast.Attribute):
        return node.attr in ANCHOR_NAMES
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return os.path.isabs(node.value)
    if isinstance(node, ast.JoinedStr):  # f-string: anchored if it starts anchored
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                return os.path.isabs(v.value)
            if isinstance(v, ast.FormattedValue):
                return _anchored(v.value)
            break
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _anchored(node.left)
    return False


def _mentions_file(node):
    return any(isinstance(n, ast.Name) and n.id == "__file__"
               for n in ast.walk(node))


def _classify(pathnode, params, subtrees):
    """SCOPED / REPO / UNKNOWN for an unanchored path expression."""
    # A bare string literal is the decidable case.
    if isinstance(pathnode, ast.Constant) and isinstance(pathnode.value, str):
        first = _first_component(pathnode.value)
        if first in subtrees:
            return "REPO", pathnode.value
        return "UNKNOWN", pathnode.value
    # A path built by joining onto a literal head — same question one level down.
    if isinstance(pathnode, ast.Call):
        name, _ = _callee_name(pathnode)
        if name == "join" and pathnode.args:
            return _classify(pathnode.args[0], params, subtrees)
        if name == "getcwd":
            return "SCOPED", "os.getcwd()"
    # ⚑ A PATH THAT IS THE ENCLOSING FUNCTION'S OWN PARAMETER IS THE CALLER'S
    # SCOPE, NOT AN AMBIENT ONE.  This is the SCOPED/REPO discriminator that makes
    # the classification mechanical rather than a judgement in the turn: the
    # directory is the question being asked, and the function is honest about
    # taking it.  Without this arm every path-taking utility reads as a defect.
    if isinstance(pathnode, ast.Name):
        if pathnode.id in params:
            return "SCOPED", pathnode.id
        return "UNKNOWN", pathnode.id
    if isinstance(pathnode, (ast.BinOp, ast.JoinedStr)):
        for n in ast.walk(pathnode):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                if _first_component(n.value) in subtrees:
                    return "REPO", n.value
        return "UNKNOWN", "<computed>"
    return "UNKNOWN", "<computed>"


class _AmbientScan(ast.NodeVisitor):
    """Every unanchored filesystem-resolving call, with its enclosing def."""

    def __init__(self, subtrees):
        self.subtrees = subtrees
        self.rows = []
        self._ctx = []
        self._params = [set()]

    def visit_FunctionDef(self, node):
        self._ctx.append(node.name)
        a = node.args
        names = {p.arg for p in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)}
        if a.vararg:
            names.add(a.vararg.arg)
        # ⚑ THE PARAMETER SET IS INHERITED FROM THE ENCLOSING SCOPE, not reset.
        # A nested helper closing over its parent's `root` argument is anchored by
        # that argument; resetting would report the closure as ambient — a false
        # positive in the class this reader most needs to keep clean.
        self._params.append(self._params[-1] | names)
        self.generic_visit(node)
        self._params.pop()
        self._ctx.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self._ctx.append(node.name)
        self.generic_visit(node)
        self._ctx.pop()

    def visit_Call(self, node):
        name, recv = _callee_name(node)
        fam = _CALLEE_FAMILY.get(name)
        if fam is not None:
            self._record(node, name, recv, fam)
        self.generic_visit(node)

    def _record(self, node, name, recv, fam):
        # ⚑ `os.getcwd()` IS ITS OWN ROW KIND, kept because it is the SPELLING the
        # prior census used.  Dropping it here would make this reader a DIFFERENT
        # one-spelling census rather than the union, and a reader cannot claim to
        # subsume a census it does not reproduce.
        if name == "getcwd":
            self.rows.append((self._line(node), "getcwd", "SCOPED",
                              "os.getcwd()", ".".join(self._ctx) or "<module>"))
            return
        if name == "chdir":
            # A process-wide mutation of the very thing under study.  Always a row.
            self.rows.append((self._line(node), "chdir", "MUTATES",
                              _src(node), ".".join(self._ctx) or "<module>"))
            return
        # ⚑⚑⚑ AN EXECUTABLE NAME IS RESOLVED ON `PATH`, NOT AGAINST CWD, AND
        # CONFLATING THE TWO PRODUCED THE READER'S WORST ROW.  `subprocess.run("agda",
        # ...)` and `shutil.which("agda")` were classified REPO — because the repo has
        # a top-level directory *named* `agda`, and `repo_subtrees()` DISCOVERS it.
        # Ten of the first twenty-five REPO rows were this: a command name colliding
        # with a subtree name, reported as an ambient repo-relative read.
        #
        # ⚑ THIS IS THE `--calls emit` SHAPE ONE LEVEL IN.  The reader had one notion
        # of "first argument is a path" and the `proc` family does not share it, so a
        # correct predicate over the wrong family produced a CONFIDENT WRONG VERDICT
        # rather than a miss — which is worse, because a REPO row is the actionable
        # one and a defect list that is 40% false invites exactly the wrong paydown.
        #
        # ⚑ THE DISCRIMINATOR IS A SEPARATOR, not a name list.  A token with no `/`
        # is a command looked up on `PATH`; `scratch/prune_imports.py` and
        # `./x` are cwd-relative and stay.  No roster of known command names is
        # needed, and a roster would be the frozen-allow-list shape this repo keeps
        # paying for.
        if fam == "proc":
            head = _path_arg(node)
            if (isinstance(head, ast.Constant) and isinstance(head.value, str)
                    and "/" not in head.value and "\\" not in head.value):
                return
        p = _path_arg(node)
        if p is None:
            return
        # ⚑⚑ AN EXPLICIT SOURCE ARGUMENT IS AN ANCHOR, AND THIS REPO'S OWN FIX FOR
        # THE DEFECT WAS READING AS THE DEFECT.  `vfs.listdir("scratch/**", head)`
        # resolves against `head` — a `Rev` or a `WorkingTree`, passed explicitly —
        # so it is the ROUTE OUT of ambient resolution, and the unqualified-name
        # vocabulary matched it as `os.listdir` and filed four of them as REPO.
        # ⚑ THE COLLISION IS THE PRICE OF KEYING ON THE UNQUALIFIED NAME, which is
        # declared in `PATH_CALLS` as a deliberate over-reach in the safe direction.
        # The over-reach is safe only if the SECOND argument is read: `os.listdir`
        # takes one path, `vfs.listdir` takes a path AND a source.  So a second
        # positional argument that is not a flag/int is treated as an explicit
        # root, which is precisely what SCOPED means.
        if len(node.args) >= 2 and not isinstance(node.args[1], ast.Constant):
            self.rows.append((self._line(node), f"{fam}:{name}", "SCOPED",
                              _src(node.args[1]), ".".join(self._ctx) or "<module>"))
            return
        if _anchored(p):
            return
        verdict, shown = _classify(p, self._params[-1], self.subtrees)
        self.rows.append((self._line(node), f"{fam}:{name}", verdict, shown,
                          ".".join(self._ctx) or "<module>"))

    @staticmethod
    def _line(node):
        return node.lineno


def _src(node):
    try:
        return ast.unparse(node)
    except Exception:
        return "<expr>"


#: ⚑⚑ WHAT THIS READER CANNOT SEE.  Declared, never computed — a census cannot
#: derive its own blind spots, and printing a number without them is exactly the
#: `census-green-is-a-fact-about-the-census` defect this module was built against.
KNOWN_MISSES = (
    ("indirection",
     "a path resolved through a helper (`_read(p)`, `vfs.WorkingTree(...).read`) "
     "— the resolving call is one frame away and this reader is intraprocedural"),
    ("dataflow",
     "a relative path stored in a variable/constant far from its use; only the "
     "same-function literal and parameter arms are decided"),
    ("alias",
     "a filesystem function reached under a rebound name (`ex = os.path.exists`) "
     "— the callee vocabulary is keyed on the unqualified NAME"),
    ("argv",
     "a relative path arriving from `sys.argv` or a config file at RUNTIME; no "
     "static reader sees it, and it is the largest class"),
    ("subprocess-argv",
     "a relative path inside a subprocess argv LIST after the first element, and "
     "any relative `cwd=` the child inherits"),
    ("import-time",
     "`sys.path` manipulation and relative-import resolution, which depend on cwd "
     "through a different mechanism entirely"),
    ("non-python",
     "shell recipes, Makefiles, hook scripts and agent dispatch text — the whole "
     "`env -C` surface lives here and NO python census reaches it"),
)


def ambient(paths=None):
    """[(path, line, kind, verdict, shown, ctx)] — the union census.

    ⚑ THE SAME ACCOUNTING `scan()` CARRIES, and for the same reason: a silently
    shrunken population turns "no ambient sites" into a fact about the reader.
    Reported on the function object, per call.
    """
    population = list(paths or _pycodemod_core.py_files())
    ambient.skipped = []
    ambient.population = len(population)
    subtrees = repo_subtrees()
    rows = []
    for p in population:
        try:
            src = open(p, encoding="utf-8").read()
        except OSError as e:
            ambient.skipped.append((p, "unreadable", type(e).__name__))
            continue
        try:
            tree = ast.parse(src)
        except Exception as e:
            ambient.skipped.append((p, "unparseable", type(e).__name__))
            continue
        v = _AmbientScan(subtrees)
        try:
            v.visit(tree)
        except Exception as e:
            ambient.skipped.append((p, "visit-failed", type(e).__name__))
            continue
        rows += [(p, ln, kind, verdict, shown, ctx)
                 for ln, kind, verdict, shown, ctx in v.rows]
    return sorted(rows)
