#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The INVERSE import reader: which files import a module, and WHICH NAMES each one binds.

⚑⚑⚑ THE ORIGIN RETURNED ZERO FOR A MODULE WITH TWENTY-SIX IMPORTERS, AND THAT MEASUREMENT IS WHY
THIS EXISTS. `scratch/pycodemod.py --importers corpus` reports `0 import site(s) in 0 of 998
file(s)` for `substrate/corpus.py` — a module whose own docstring records 71 call sites and which
this reader finds imported at 26 sites. The origin compares only `node.module.split(".")[0]`, so
inside a PACKAGE every importer spells the dependency as the package and the submodule question
can only ever answer zero.

⚑⚑ A FALSE ZERO GETS BANKED WHERE A FALSE FINDING GETS ARGUED WITH, and this one is the shape
this repo has paid for repeatedly: a fact about the METHOD (the reader keys on one spelling)
reported as a fact about the SUBSTRATE (nothing imports it). The repair is to resolve BOTH
spellings — the top-level name AND the submodule reached through `from <pkg> import <mod>` — not
to add an exemption for package trees.

⚑⚑⚑ AND THE PROMOTED READER CARRIED THE SAME CLASS ONE OPERAND-SHAPE OVER (Ⓝ74
⟡importers-path-spelling). MEASURED on the live tree, both spellings of one module, minutes
apart:

    module_importers.py substrate/reach_ratchet.py  ->  0 import site(s) in 0 of 1155 file(s)
    module_importers.py substrate.reach_ratchet     ->  1 import site(s) in 1 of 1155 file(s)

Same module, same question, one answer true and one a bare zero — with no note and no *did you
mean*, so it is indistinguishable from a genuine absence. AND THE FAILING SPELLING IS THE ONE A
READER ACTUALLY TYPES: arriving from a census row, a traceback or `suite_gap_report`, you hold a
PATH. The dotted name is what you have only once you already know the answer's shape.

⚑⚑ THE GENERAL FORM, WITNESSED THREE TIMES IN ONE SESSION: **a promoted reader inherits the
QUESTION but not the BOUNDARY.** `--attr`'s dotted form, `--importers`' package keying, and this
were all false zeros in one toolkit in one day. Each promotion fixed the specific miss that
motivated it and reintroduced the class at a different OPERAND SHAPE, because the origin's
boundary was never written down — only its symptom. So this module now states its boundary
(`unresolved`) rather than leaving the next reader to rediscover it as a symptom.

⚑ THE BOUND NAMES ARE THE POINT, NOT THE FILE LIST. `from m import *` SKIPS a leading underscore,
so a consumer reading `schema._node` vanishes off a re-export surface while every suite stays
green — measured at the origin (`_node`, `_unit`, `_unit_cod`, `_orbit_def`). A `_`-prefixed name
here is one a star-re-export CANNOT carry and that a split must therefore re-import BY NAME. That
is the question a module split asks and neither a count nor an attribute census can answer.

⚑ PROMOTED AS THE READER, NOT THE TOOLKIT (⟡promote-pycodemod). The origin sits inside a
six-module cycle (`_pycodemod_census → shared_cache → pycodemod → _pycodemod_control →
_pycodemod_sql → _pycodemod_query → _pycodemod_census`) and reaches its corpus through a module
whose `ROOT` is REBOUND under `global`. Neither is needed to ask which files import a module: the
walk is `ast`, the population is `substrate.corpus`, and nothing here holds state.

⚑ RELATIVE IMPORTS ARE REPORTED AS UNRESOLVED, NOT SILENTLY DROPPED. `from . import x` names a
module this reader cannot resolve without knowing the importer's package, and the origin skips
`node.level` entirely. Silently dropping them would put the same false zero back one level in, so
they are excluded from a NAMED query and the exclusion is stated rather than left to be found.

⚑⚑⚑ Ⓝ122g — AND THE PROMOTED READER CARRIED THE CLASS A FOURTH TIME, AT THE SITE INSTEAD OF THE
OPERAND. Every note above is about the OPERAND: three spellings a caller might type, all now
normalised to one dotted name. Normalising the operand is right. Matching SITES against only that
normalised name is not, and it is what this module did. MEASURED on the live tree:

    module_importers.py _agdatext              ->  0 import site(s) in 0 of 1272 file(s)
    adopter_import.py --reach-back             ->  _agdatext: 21 consumer(s)

The operand `_agdatext` resolves to `scripts._agdatext` and the reader then asks for
`import scripts._agdatext` — which nothing writes. All 21 consumers spell it `import _agdatext`,
BARE, reachable only under a `sys.path` insert. The reader printed its resolution, honestly, and
then answered a question no file in the tree asks.

⚑⚑ A BARE SITE AND A DOTTED SITE ARE DIFFERENT FACTS, NOT TWO SPELLINGS OF ONE. `import
_agdatext` resolves only when something has already inserted `scripts/` on `sys.path`; it fails
for an adopter importing the installed wheel. `from scripts import _agdatext` is portable. So the
split is not presentation — it is the answer to *who is blocked from adopter import*, which is
`adopter_import --reach-back`'s question asked from the other side. Rendering them identically
makes this reader unable to answer it, and rendering only the dotted half makes it answer zero.

⚑⚑ REPORTED BY DEFAULT, NEVER BEHIND A FLAG. A reader whose correct answer needs an option
nobody knows to pass fails exactly the way the collapse does — the default answer is the one that
gets banked. `sites` returns both populations and `render` prints both counts whenever either is
non-empty; there is no `--bare` to forget.

⚑ THE TWO READERS AGREE ON THE MEASURED CASE, AND THAT AGREEMENT IS CHECKED RATHER THAN ASSERTED.
They remain DIFFERENT INSTRUMENTS — `--reach-back` walks the INSTALLED distribution's
module-scope imports and groups by callee; this walks the working tree at every scope and reports
per-site lines — so they can legitimately diverge (a function-scope import counts here and not
there). The case pins the SHAPE (a bare-only consumer is visible), never a frozen count, because
a count pinned here would go red when the paydown queue drains, which is when it is working.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Iterable

# How a file spells its dependency. ⚑ NAMED ONCE: the reader, the render and the cases cite these
# rather than respelling the strings.
PLAIN, FROM, STAR = "import", "from", "from-*"

# How the OPERAND was spelled. ⚑ THE ANSWER MUST SAY WHICH ONE IT RESOLVED, because the whole
# defect was two spellings of one question giving two answers with nothing to distinguish them.
DOTTED, PATH = "dotted", "path"

# How the SITE spelled its dependency, which is a DIFFERENT AXIS from how the OPERAND was
# spelled. ⚑⚑ Ⓝ122g: `import _agdatext` (BARE) needs a `sys.path` insert and breaks for an
# adopter; `from scripts import _agdatext` (DOTTED_SITE) is portable. Naming them apart is what
# lets one census answer both "who imports this" and "who is blocked from adopter import".
BARE, DOTTED_SITE = "bare", "dotted"

# Shapes no static single-pass read can resolve; reported as themselves, never folded into a zero.
# ⚑ THE ROSTER IS `attr_reads`' — the same three shapes, because they are properties of static
# import reading and not of that module. Respelling them would make two vocabularies for one
# boundary, which is how the class propagated in the first place.
CHAIN, DYNAMIC, RELATIVE_PKG = "re-export-chain", "dynamic-import", "relative-package"

# The suffix a path operand carries and a module name never does.
_PY = ".py"

# A package directory's module file — `a/b/__init__.py` names the module `a.b`, not `a.b.__init__`.
_INIT = "__init__"

# The bound-name list a star import stands for — it binds whatever the target exports, which this
# reader cannot know without importing. Reported as itself rather than as an empty list, because
# an empty list reads as "binds nothing" and a star import binds the most of any form.
_STAR_NAMES = ("*",)

# One resolved import: the LINE it sits on, the form it took, the names it bound, and WHICH
# SPELLING the site used to name the module.
#
# ⚑ THE LINE TRAVELS WITH THE BINDING, and leaving it to the caller was a measured `Any`. Only the
# resolver holds the CONCRETE node type; a caller holding an `ast.AST` can reach `lineno` only
# through `getattr`, which returns `Any` and carries it into every row — the typed-accessor
# boundary `import_edges._eager_bodies` records under the same rule.
#
# ⚑⚑ THE SPELLING TRAVELS WITH IT FOR THE SAME REASON (Ⓝ122g). Only the resolver knows whether it
# matched the dotted name or the bare leaf; recovering that downstream would mean re-deriving it
# from the rendered text, which is the collapse this repair exists to end.
Binding = tuple[int, str, tuple[str, ...], str]


@dataclass(frozen=True, slots=True)
class Operand:
    """A caller's spelling of a module, and the dotted name it resolved to.

    ⚑⚑ THE SPELLING IS CARRIED, NOT DISCARDED AFTER NORMALISING. A reader who typed a PATH and
    gets an answer about a dotted name needs to see that translation happen — otherwise a
    resolution that went somewhere unexpected is indistinguishable from one that went nowhere,
    which is the defect this class exists to close rather than to move.
    """

    given: str
    module: str
    spelling: str

    @property
    def translated(self) -> bool:
        """Report whether normalising changed the operand."""
        return self.given != self.module


def normalise(operand: str) -> Operand:
    """Return the dotted module name `operand` denotes, in either spelling.

    ⚑⚑⚑ THIS IS THE Ⓝ74 REPAIR. `substrate/reach_ratchet.py` and `substrate.reach_ratchet` are
    the same question and answered 0 and 1 respectively. A reader arriving from a census row, a
    traceback or `suite_gap_report` holds the PATH; requiring the dotted name means the tool
    answers correctly only for a caller who already knows the answer's shape.

    ⚑ A PATH IS ANY OPERAND CARRYING A SEPARATOR OR THE `.py` SUFFIX, not merely one that exists
    on disk. Testing the filesystem would make the answer depend on the CWD — the wrong-root
    class `corpus.resolve_root` records — and would silently refuse a path for a deleted module,
    which is a question worth asking.

    ⚑ `a/b/__init__.py` IS THE MODULE `a.b`. Carrying `__init__` into the dotted name would query
    a module that no importer can ever name, which is a false zero built by the normaliser.
    """
    if "/" not in operand and not operand.endswith(_PY):
        return Operand(given=operand, module=operand, spelling=DOTTED)
    parts = Path(operand).with_suffix("").parts
    if parts and parts[-1] == _INIT:
        parts = parts[:-1]
    return Operand(given=operand, module=".".join(parts), spelling=PATH)


def candidates(operand: str, files: Iterable[tuple[Path, str]]) -> tuple[str, ...]:
    """Return every dotted module in `files` a BARE operand could denote.

    ⚑⚑⚑ Ⓝ82. A bare name normalises to itself and is then queried as a TOP-LEVEL module,
    so `sites` derives `package = None` and the `from <pkg> import <mod>` branch — the one
    this module exists for — can never fire. MEASURED on the live tree:

        module_importers.py corpus            ->  0 import site(s) in 0 of 1181 file(s)
        module_importers.py substrate.corpus  ->  many

    Same module, same question, and the failing spelling is the SHORTEST one a reader
    types. This is the ⟡importers-path-spelling class a third time — a fact about the
    METHOD (the reader assumed a bare name is a top-level module) reported as a fact about
    the SUBSTRATE (nothing imports it) — arriving at the third operand shape, in the reader
    PROMOTED TO FIX IT.

    ⚑⚑ A BARE NAME IS GENUINELY AMBIGUOUS AND THAT IS NOT A DEFECT TO RESOLVE BY GUESSING.
    `corpus` denotes BOTH `substrate.corpus` and `tests.corpus` in this tree. Picking one —
    by depth, by alphabet, by a roots() preference order — would answer a question the
    caller did not ask, and answer it CONFIDENTLY: a well-formed census about the wrong
    module reads exactly like a right one, which is `resolve_root`'s recorded wrong-tree
    incident with the operand instead of the root. **THIS REPO DELETES ON ZEROS**, and a
    census attributed to the wrong module is worse than the zero it replaces, because the
    zero at least carries its boundary.

    ⚑ SO THIS ENUMERATES AND DOES NOT CHOOSE. The caller decides: one candidate resolves,
    several REFUSE and name them, none leaves the bare name alone as a genuine top-level
    module (which `import agda_lex` legitimately is).

    ⚑⚑ THE DOTTED AND PATH SPELLINGS FALL OUT WITH NO GUARD OF THEIR OWN, and the guard
    that was written for them has been DELETED rather than kept as reassurance. Both tests
    below compare against the RAW operand: a label's leaf is a bare word, so `corpus.py`,
    `substrate.corpus` and `substrate/corpus.py` each fail both — they already name their
    module, and this function is only ever consulted for the spelling that does not.

    ⚑⚑⚑ AN EXPLICIT `if "." in operand …: return ()` STOOD HERE AND WAS DEAD CODE. Three
    arms were written to pin it and the suite stayed 34/34 with it REMOVED — the arms were
    satisfied by the leaf test, so they measured a predicate that could not fail, which is
    a discriminator in name only. Kept as a note rather than as an unreachable branch: a
    guard nothing can trip is a claim about the code that the code does not make, and it
    would go on reading as the thing keeping the invariant while the leaf test did the work.
    """
    return tuple(
        sorted(
            {
                normalise(label).module
                for _p, label in files
                if Path(label).with_suffix("").name in (operand, _INIT)
                and normalise(label).module.rsplit(".", 1)[-1] == operand
            }
        )
    )


class Site(NamedTuple):
    """One file's import of the module in question, and HOW that file spelled it."""

    path: str
    line: int
    form: str
    names: tuple[str, ...]
    spelling: str = DOTTED_SITE

    @property
    def unexportable(self) -> tuple[str, ...]:
        """Return the bound names a `from m import *` re-export CANNOT carry.

        ⚑ THESE ARE THE WORK OF A SPLIT. A star re-export drops every leading-underscore name, so
        a consumer reaching one keeps working until the split lands and then fails at a site no
        suite covers. They must be re-imported by name, and nothing else in the row says so.
        """
        return tuple(n for n in self.names if n.startswith("_"))

    @property
    def portable(self) -> bool:
        """Report whether an adopter importing the installed wheel can execute this site.

        ⚑⚑ THIS IS THE QUESTION THE COLLAPSED READER COULD NOT ASK (Ⓝ122g). A BARE site names
        the module by its leaf alone, so it resolves only when something has already put the
        containing directory on `sys.path` — true in this checkout, false for an adopter. The
        dotted site carries its package and travels. Same module, same census row, opposite
        answers to *can this consumer be shipped*.
        """
        return self.spelling == DOTTED_SITE


def _bound(node: ast.ImportFrom, spelling: str, only: str | None = None) -> Binding:
    """Return the binding for a `from` node already known to name the module.

    ⚑ THE STAR TEST LIVES HERE SO IT IS ASKED ONCE. Each of `_from`'s three match branches
    needs it, and spelling it three times is how one branch ends up reporting `*` as an
    ordinary name list — a star binds whatever the target exports, which is the opposite of
    the handful of names an alias list carries.

    ⚑ `only` NARROWS TO ONE ALIAS for the `from <pkg> import <mod>` shape, where the module is
    named in the alias list rather than by `node.module` and the siblings are other modules.
    """
    if only is None and any(a.name == "*" for a in node.names):
        return node.lineno, STAR, _STAR_NAMES, spelling
    hit = [a for a in node.names if only is None or a.name == only]
    return (node.lineno, FROM, tuple(sorted(a.asname or a.name for a in hit)), spelling)


def _plain(node: ast.Import, module: str) -> Binding | None:
    """Resolve `import a.b` / `import a.b as c` against `module`, dotted OR bare.

    ⚑ AN ALIAS IS THE NAME THE FILE ACTUALLY USES, so `import x as y` reports `y`. A reader
    reporting `x` describes the import statement rather than the file, and a rename following that
    report would miss every use.

    ⚑⚑⚑ THE BARE ARM IS Ⓝ122g, AND WITHOUT IT THIS FUNCTION RETURNS THE MEASURED FALSE ZERO. The
    operand `_agdatext` normalises to `scripts._agdatext`, and its consumers all write
    `import _agdatext` — so a test of `a.name == module` alone matches NOTHING while
    `adopter_import --reach-back` names every one of them. The leaf is matched too, and the
    binding says WHICH matched, because the two are different facts about portability rather
    than two spellings of one.

    ⚑ THE DOTTED ARM IS TRIED FIRST AND WINS OUTRIGHT. A statement naming the module in full is
    a dotted site whatever else it also imports; falling through to the leaf test would let one
    `import a.b, b` report the portable spelling as bare.

    ⚑ THE LEAF IS MATCHED WHOLE, NEVER AS A SUFFIX. `import x` must not answer a query about
    `pkg.other_x`: a dotted candidate whose leaf merely ENDS with the operand is a different
    module, and matching it would trade a false zero for a false witness — strictly worse, since
    a wrong site carries a `file:line` that reads as proof.
    """
    leaf = module.rsplit(".", 1)[-1]
    for want, spelling in ((module, DOTTED_SITE), (leaf, BARE)):
        hit = [a for a in node.names if a.name == want or a.name.startswith(want + ".")]
        if hit:
            return (node.lineno, PLAIN, tuple(sorted(a.asname or a.name for a in hit)), spelling)
    return None


def _from(node: ast.ImportFrom, module: str, package: str | None) -> Binding | None:
    """Resolve `from … import …` against `module`, in every spelling.

    ⚑⚑⚑ CHECKING ONLY THE FIRST SPELLING IS THE MEASURED DEFECT. `from a.b import x` names the
    module in `node.module`; `from a import b` names it in the ALIAS LIST. A reader testing only
    `node.module` reports zero importers for every submodule of every package it scans — which is
    exactly what the origin does, and `--importers corpus` returning 0 is the receipt.

    ⚑⚑ AND THE BARE `from` IS A THIRD SHAPE, NOT A RESPELLING OF EITHER (Ⓝ122g).
    `from agda_lex import agda_files` names the module by its LEAF with no package at all — the
    shape a `sys.path` insert enables and an adopter cannot execute. It is distinct from the
    dotted-submodule branch, which requires the PACKAGE to be named and finds the leaf in the
    alias list.

    ⚑ THE RELATIVE GUARD RUNS FIRST AND THAT ORDER IS LOAD-BEARING. `from . import _agdatext`
    carries the same LEAF the bare arm matches on, so without the guard the widening would
    convert a stated boundary — a module this reader cannot resolve — into a false witness.
    """
    if node.level or not node.module:
        # ⚑ A RELATIVE IMPORT IS UNRESOLVED HERE, NOT ABSENT — see the module docstring.
        return None
    short = module.rsplit(".", 1)[-1]
    if node.module == module or node.module.startswith(module + "."):
        return _bound(node, DOTTED_SITE)
    if package is not None and node.module == package:
        # ⚑ THE SUBMODULE SPELLING THE ORIGIN CANNOT SEE. `from substrate import corpus` imports
        # the module `substrate.corpus` while `node.module` says only `substrate`.
        if any(a.name == short for a in node.names):
            return _bound(node, DOTTED_SITE, only=short)
        return None
    if node.module == short:
        return _bound(node, BARE)
    return None


def _binds(node: ast.AST, module: str, package: str | None) -> Binding | None:
    """Return `(line, form, names, spelling)` if this node imports `module`, else None."""
    if isinstance(node, ast.Import):
        return _plain(node, module)
    if isinstance(node, ast.ImportFrom):
        return _from(node, module, package)
    return None


def _parsed(files: Iterable[tuple[Path, str]]) -> list[tuple[str, ast.AST]]:
    """Return `(label, tree)` for every file that parses.

    ⚑ ONE UNPARSEABLE FILE MUST NOT TAKE THE CENSUS DOWN — it would report nothing about the
    ~997 that parse, which is a far larger error than the one file it skips.
    """
    out: list[tuple[str, ast.AST]] = []
    for path, label in files:
        try:
            out.append(
                (
                    label,
                    ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=label),
                )
            )
        except (OSError, SyntaxError, ValueError):
            continue
    return out


def sites(module: str, files: Iterable[tuple[Path, str]]) -> tuple[Site, ...]:
    """Return every import of `module` across `files`, in BOTH site spellings.

    ⚑ `module` MAY BE DOTTED, BARE OR A PATH, and all three resolve. A caller arriving from a
    traceback has `substrate.corpus`; one arriving from a filename has `corpus`; one arriving
    from a census row or `suite_gap_report` has `substrate/corpus.py`. Requiring one spelling
    makes the tool answer a question the caller did not ask — with a zero.

    ⚑⚑ AND THE RETURN CARRIES BOTH SITE POPULATIONS, NEVER ONLY THE DOTTED ONE (Ⓝ122g). Each
    `Site` says how its file spelled the dependency; `split` partitions them for a caller that
    needs the two apart.
    """
    name = normalise(module).module
    package = name.rsplit(".", 1)[0] if "." in name else None
    out: list[Site] = []
    for label, tree in _parsed(files):
        for node in ast.walk(tree):
            got = _binds(node, name, package)
            if got is not None:
                out.append(
                    Site(path=label, line=got[0], form=got[1], names=got[2], spelling=got[3])
                )
    return tuple(sorted(out))


def all_sites(
    modules: Iterable[str], files: Iterable[tuple[Path, str]]
) -> dict[str, tuple[Site, ...]]:
    """Return `{module: sites}` for every name in `modules`, from ONE parse of `files`.

    ⚑⚑⚑ THE SAME QUESTION AS `sites`, WITH THE LOOPS INVERTED, AND THE INVERSION IS THE WHOLE
    POINT. `sites` parses the corpus once per module it is asked about, which is right for one
    question and quadratic for a census: `substrate/proof_only` asked it for ~700 candidates
    over 1593 files and did not finish in 120 seconds, twice. **A tool whose cost makes it
    unrunnable is orphaned by construction rather than by neglect** (gate-G301), and a census
    nobody can run reports nothing while looking like an instrument.

    ⚑⚑ IT SHARES `_parsed` AND `_binds` RATHER THAN REIMPLEMENTING THEM. A second resolution
    path beside this one would be two readers answering one question — the defect this module's
    own blind-spot reporting exists to keep honest — so the predicate is identical and only the
    iteration order differs. Anything `sites` cannot see, this cannot see either, by
    construction rather than by a matching comment.

    ⚑ A NAME WITH NO IMPORTS GETS AN EMPTY TUPLE, NOT A MISSING KEY, because a caller
    distinguishing *scanned and unimported* from *never asked* needs the key to exist. That is
    the same reason every census here carries its denominator.
    """
    wanted = {normalise(m).module: m for m in modules}
    out: dict[str, list[Site]] = {name: [] for name in wanted}
    packages = {name: (name.rsplit(".", 1)[0] if "." in name else None) for name in wanted}

    for label, tree in _parsed(files):
        for node in ast.walk(tree):
            for name in wanted:
                got = _binds(node, name, packages[name])
                if got is not None:
                    out[name].append(
                        Site(path=label, line=got[0], form=got[1], names=got[2], spelling=got[3])
                    )
    return {name: tuple(sorted(found)) for name, found in out.items()}


def split(found: tuple[Site, ...]) -> tuple[tuple[Site, ...], tuple[Site, ...]]:
    """Partition sites into (portable, bare) — the two populations, never one total.

    ⚑⚑ RETURNED AS SITES RATHER THAN COUNTS, because the reader needs the LINES. "7 bare sites"
    is a number to act on only once you know which files they are; the paydown is per-site, and
    the same partition is what `adopter_import --reach-back` presents grouped the other way.
    """
    return (tuple(s for s in found if s.portable), tuple(s for s in found if not s.portable))


def _blind_shapes(node: ast.AST, label: str, module: str) -> list[str]:
    """Return the unresolvable shapes this node exhibits, as reader-facing lines."""
    short = module.rsplit(".", 1)[-1]
    out: list[str] = []
    if isinstance(node, ast.ImportFrom):
        if node.level and any(a.name == short for a in node.names):
            out.append(
                f"{RELATIVE_PKG}: {label}:{node.lineno} imports `{short}` from an "
                f"unknown package — it may or may not be this module"
            )
        if (
            any(a.name == "*" for a in node.names)
            and (node.module or "").rsplit(".", 1)[-1] == short
        ):
            out.append(
                f"{CHAIN}: {label}:{node.lineno} re-exports `{short}` with a star; "
                f"consumers reach it under THIS module's name and name it nowhere"
            )
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "import_module"
    ):
        out.append(f"{DYNAMIC}: {label}:{node.lineno} imports a module at runtime")
    return out


def unresolved(module: str, files: Iterable[tuple[Path, str]]) -> tuple[str, ...]:
    """Return the shapes in `files` that could hide an import this reader cannot resolve.

    ⚑⚑ THIS IS THE HALF THAT MAKES A ZERO HONEST, and its absence here is Ⓝ74's second half. A
    count alone cannot separate *nothing imports this* from *this reader could not see*, and
    THIS REPO DELETES ON ZEROS (`--dead` is the census that authorises removal). Three false
    zeros were measured in one day in one toolkit; a zero must carry what it could not resolve.

    The shapes are `attr_reads`' three, because they are properties of reading imports
    statically rather than of that module:
      * `re-export-chain` — a star re-export puts this module's names under ANOTHER module's,
        and a consumer of those names names this module nowhere.
      * `dynamic-import` — `import_module(name)` binds at runtime and the name need not be a
        literal.
      * `relative-package` — `from . import mod` names a module whose package is unknown, so it
        can be neither claimed nor excluded.
    """
    name = normalise(module).module
    return tuple(
        sorted(
            {
                line
                for label, tree in _parsed(files)
                for node in ast.walk(tree)
                for line in _blind_shapes(node, label, name)
            }
        )
    )


def all_unresolved(
    modules: Iterable[str], files: Iterable[tuple[Path, str]]
) -> dict[str, tuple[str, ...]]:
    """Return `{module: shapes}` for every name in `modules`, from ONE parse of `files`.

    ⚑⚑⚑ THE TWIN OF `all_sites`, AND ITS ABSENCE IS WHY THE FIRST REPAIR DID NOT LAND. Adding
    a bulk site reader made `proof_only` parse once for the sites and then once more PER
    REPORTED MEMBER for the bounds — the same quadratic, one layer over, in a census that had
    just been repaired for exactly it. **Fixing one nested loop and leaving its twin is how a
    performance defect survives its own fix**, and the run was still killed at 120 seconds.

    ⚑⚑ THE PER-MODULE PRECISION IS KEPT, WHICH IS THE POINT OF DOING IT THIS WAY. These shapes
    answer *what could hide an importer OF THIS MODULE* — a relative import naming its leaf, a
    star re-export carrying its names, a runtime import. Reporting the corpus's shapes once for
    everyone would be a bound belonging to something else, wearing the shape of a fact about
    the subject.
    """
    wanted = {normalise(m).module: m for m in modules}
    out: dict[str, set[str]] = {name: set() for name in wanted}
    for label, tree in _parsed(files):
        for node in ast.walk(tree):
            for name in wanted:
                out[name].update(_blind_shapes(node, label, name))
    return {name: tuple(sorted(found)) for name, found in out.items()}


def population(root: Path | None = None) -> tuple[tuple[Path, str], ...]:
    """Return the corpus to scan, as `(path, repo-relative label)` pairs.

    ⚑ `corpus.py_files` RETURNS ABSOLUTE PATHS, and treating them as relative silently produced a
    census keyed on absolute names — legible to a human, and joinable by nothing. The label is what
    every consumer matches on, so it is DERIVED from the root rather than assumed to be the return.

    ⚑⚑⚑ AND A PATH OUTSIDE THE ROOT IS LABELLED, NOT RAISED ON (gate-G249, reported by summit-74).
    `corpus.resolve_root` resolves CWD FIRST by design, so from a BORROWING checkout the walk
    correctly returns that repo's files and `relative_to` against substrate's root then killed the
    run. This is the SECOND copy of that defect: the identical body in `attr_reads.population` was
    repaired one tick earlier, and I fixed that instance without asking how many existed.

    ⚑⚑ THE RULE ALREADY HAD TWO HOMES BEFORE THIS ONE. `name_collision._relative` and
    `case_count._label` both implement it, and the former's docstring states the remedy exactly —
    *"a reader handed an outside path wants a row, not a crash"* — written before either crash was
    reported and consulted by neither repair. Importing it here was refused correctly (`SLF001`):
    reaching a peer module's PRIVATE is coupling, not reuse. The honest repair is ONE OWNER for the
    rule, which is a wider edit than this fix and is recorded rather than approximated.
    """
    where = root if root is not None else corpus.ROOT
    return tuple((Path(p), _label(Path(p), where)) for p in corpus.py_files(root=where))


def _label(path: Path, root: Path) -> str:
    """Return `path` relative to `root`, or its absolute form when it lies outside.

    ⚑ A FOURTH SPELLING OF A RULE THAT SHOULD HAVE ONE OWNER, and saying so is the only thing that
    keeps the duplication legible until it is paid down. Dropping the outside path instead would
    silently shrink the population — the census-green shape — so an absolute label is longer and
    never wrong.
    """
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def unexportable(found: tuple[Site, ...]) -> tuple[str, ...]:
    """Return every bound name across `found` that a star re-export would drop."""
    return tuple(sorted({n for s in found for n in s.unexportable}))


def render(module: str, found: tuple[Site, ...], scanned: int, blind: tuple[str, ...] = ()) -> str:
    """Return the census — the sites, the resolution, the denominator, and what stayed invisible.

    ⚑⚑ THE DENOMINATOR IS PRINTED EVEN WHEN THE ANSWER IS ZERO, and printing it is the whole
    defence against the defect this module exists for. `0 sites` and `0 sites of 998 files
    scanned` are the same finding; only the second lets a reader see that the scan HAPPENED, so a
    reader keying on the wrong spelling learns the population was read rather than that the
    module is unused.

    ⚑⚑ AND THE RESOLUTION IS PRINTED WHENEVER IT TRANSLATED. `substrate/reach_ratchet.py` now
    answers as `substrate.reach_ratchet`, and saying so is what turns a silent normalisation into
    a checkable one — a reader who sees the wrong dotted name knows immediately that the operand
    was misread, rather than concluding the module has no importers.

    ⚑⚑⚑ THE BARE/DOTTED SPLIT PRINTS BY DEFAULT AND EVERY ROW CARRIES ITS SPELLING (Ⓝ122g). A
    flag would reproduce the defect it repairs: the default answer is the one that gets banked,
    and a correct answer nobody knows to ask for is not a correct reader. The summary line fires
    only when a BARE site exists, because an all-dotted module has no paydown to name — an
    unconditional line would train the reader to skip it.
    """
    op = normalise(module)
    lines = [
        f"  {s.form:<7} {s.spelling:<6} {s.path}:{s.line}  {', '.join(s.names)}" for s in found
    ]
    hit = len({s.path for s in found})
    resolved = f" (resolved from the {op.spelling} spelling `{op.given}`)" if op.translated else ""
    lines.append(
        f"{op.module}: {len(found)} import site(s) in {hit} of {scanned} file(s){resolved}"
    )
    portable, bare = split(found)
    if bare:
        lines.append(
            f"   ⚑ {len(bare)} BARE site(s) beside {len(portable)} dotted. A bare site "
            f"names this module by its leaf"
        )
        lines.append(
            "     alone, so it resolves only under a `sys.path` insert and FAILS for an adopter"
        )
        lines.append(
            "     importing the installed wheel — the paydown queue, not a second spelling."
        )
    dropped = unexportable(found)
    if dropped:
        lines.append(
            f"   ⚑ {len(dropped)} name(s) a star-re-export CANNOT carry: {', '.join(dropped)}"
        )
    if blind:
        lines.append(
            f"   ⚑ {len(blind)} shape(s) this reader CANNOT resolve — a zero above is "
            f"not yet an absence:"
        )
        lines.extend(f"     {b}" for b in blind)
    return "\n".join(lines) + "\n"


def refusal(operand: str, found: tuple[str, ...]) -> str:
    """Return the refusal for an ambiguous bare operand, naming every candidate.

    ⚑⚑ A REFUSAL, NOT A GUESS, AND NOT A ZERO. The three answers available for `corpus`
    are: a census of `substrate.corpus` (right by luck), a census of `tests.corpus`
    (wrong, and well-formed), or `0 sites` (the banked zero this module was promoted to
    kill). Only naming both candidates says what is actually true — the operand does not
    determine a module — and it hands the reader the exact strings that do.
    """
    return (
        f"{operand}: AMBIGUOUS — {len(found)} modules in the corpus carry this bare "
        f"name, so it\n  does not determine a question. Re-ask with one of:\n"
        + "\n".join(f"    {c}" for c in found)
        + "\n"
    )


def _probe(source: str, module: str) -> tuple[Site, ...]:
    """Resolve one source string against `module` — the fixture the spelling cases share.

    ⚑ FROM TEXT, NOT FROM DISK. A case that writes a temp file can fail for filesystem reasons
    and be read as a logic failure, which is the least useful kind of red suite.
    """
    name = normalise(module).module
    package = name.rsplit(".", 1)[0] if "." in name else None
    out: list[Site] = []
    for node in ast.walk(ast.parse(source, filename="probe.py")):
        got = _binds(node, name, package)
        if got is not None:
            out.append(
                Site(path="probe.py", line=got[0], form=got[1], names=got[2], spelling=got[3])
            )
    return tuple(sorted(out))


def _cases_spelling() -> list[tuple[str, object, object]]:
    """Pin Ⓝ122g: the SITE spelling is resolved and reported, not normalised away.

    ⚑⚑⚑ THE DISCRIMINATOR IS THE SHAPE OF `_agdatext` ITSELF, asked so every arm lands at once.
    A reader matching only the dotted name reports the bare arms as absent — the measured false
    zero; one matching only the leaf reports the dotted arms BARE and loses the portability
    answer; one normalising both to a single label passes a count case and still cannot say who
    is blocked. Only a reader carrying the axis passes all of these.
    """
    return [
        (
            "a bare-only consumer is VISIBLE and marked bare — the measured _agdatext shape",
            [
                (s.form, s.spelling, s.names)
                for s in _probe("import _agdatext\n", "scripts._agdatext")
            ],
            [(PLAIN, BARE, ("_agdatext",))],
        ),
        # ⚑ THE PORTABLE SPELLING OF THE SAME MODULE, so the axis cannot be a constant. A
        # reader answering BARE to everything passes the arm above and fails here.
        (
            "the dotted spelling of the same module reads dotted",
            [
                (s.form, s.spelling)
                for s in _probe("from scripts import _agdatext\n", "scripts._agdatext")
            ],
            [(FROM, DOTTED_SITE)],
        ),
        # ⚑⚑ THE BARE `from`, WHICH IS A THIRD SHAPE AND NOT A RESPELLING OF EITHER. This is
        # `check_carrier_locality`'s `from agda_lex import agda_files` after its path insert.
        (
            "a bare `from` names the leaf with no package and reads bare",
            [
                (s.form, s.spelling, s.names)
                for s in _probe("from agda_lex import agda_files\n", "scratch.agda_lex")
            ],
            [(FROM, BARE, ("agda_files",))],
        ),
        # ⚑⚑⚑ AND THE SPLIT IS THE DELIVERABLE, not the per-row label. Both populations from
        # ONE walk, which is the reader's whole claim: a caller asking "who imports this" and
        # one asking "who is blocked" get their answers from the same census.
        (
            "one walk yields both populations, partitioned",
            [
                len(p)
                for p in split(
                    _probe(
                        "import _agdatext\nfrom scripts import _agdatext\nimport _agdatext as t\n",
                        "scripts._agdatext",
                    )
                )
            ],
            [1, 2],
        ),
        # ⚑⚑ THE LEAF IS MATCHED WHOLE. A suffix test would claim `import other_agdatext` for
        # a query about `_agdatext`, trading the false zero for a false witness carrying a
        # `file:line` — strictly the worse error, since a wrong site reads as proof.
        (
            "a leaf that merely ENDS with the name is NOT this module",
            _probe("import other_agdatext\n", "scripts._agdatext"),
            (),
        ),
        # ⚑ THE DOTTED ARM WINS OUTRIGHT when one statement names both, so a portable site is
        # never downgraded by a bare sibling in the same `import`.
        (
            "a statement naming the module in full is dotted, whatever else it imports",
            [
                s.spelling
                for s in _probe("import scripts._agdatext, _agdatext\n", "scripts._agdatext")
            ],
            [DOTTED_SITE],
        ),
        # ⚑⚑ AND A RELATIVE IMPORT IS STILL UNRESOLVED RATHER THAN CLAIMED AS BARE. The bare
        # arm matches on the LEAF, and `from . import _agdatext` carries that same leaf — so
        # without the `node.level` guard first, the widening would silently convert a stated
        # boundary into a false witness. This arm is what makes that ordering checkable.
        (
            "a relative import is still unresolved, not swept up by the bare arm",
            _probe("from . import _agdatext\n", "scripts._agdatext"),
            (),
        ),
    ]


def _cases_bulk() -> list[tuple[str, object, object]]:
    """Pin that `all_sites` agrees with `sites` — the ONLY claim the bulk form owes.

    ⚑⚑⚑ A FASTER READER THAT ANSWERS DIFFERENTLY IS A REWRITE WEARING AN OPTIMISATION'S
    CLOTHES. `all_sites` exists to make a census runnable, and the entire argument for it is
    that it asks the SAME question — so the case is a differential, not a restatement of what
    I believe both should return.

    ⚑⚑ AND IT RUNS AGAINST THE LIVE CORPUS RATHER THAN A FIXTURE, because a fixture would only
    prove the two agree with my model of imports. The disagreement worth catching is one in a
    shape neither of us anticipated, and only real files carry those.

    ⚑ THE SUBJECTS ARE CHOSEN TO DIFFER: one module with many importers, one with few, and one
    with none. A differential over a single busy module passes against a bulk reader that
    silently drops empty results — which is exactly the key-versus-no-key distinction
    `all_sites` promises.
    """
    files = list(population())
    names = ("substrate.corpus", "substrate.module_importers", "substrate.md_hkey")
    bulk = all_sites(names, files)
    return [
        (
            "the bulk reader agrees with the per-module reader, module for module",
            [bulk[n] == sites(n, files) for n in names],
            [True, True, True],
        ),
        # ⚑ A NAME WITH NO IMPORTERS KEEPS ITS KEY. A reader that omitted it would make
        # *scanned and unimported* indistinguishable from *never asked*, which is the
        # denominator defect this repo pays for repeatedly.
        ("every requested name has a key, importers or not", sorted(bulk), sorted(names)),
        # ⚑⚑ AND THE TWIN, because adding `all_sites` alone left `unresolved` quadratic and the
        # census still did not finish. A differential on one of a pair proves nothing about the
        # other, and the pair is what a caller actually uses.
        (
            "the bulk blind-shape reader agrees with the per-module one",
            [all_unresolved(names, files)[n] == unresolved(n, files) for n in names],
            [True, True, True],
        ),
    ]


def _cases_unimported() -> list[tuple[str, object, object]]:
    """Pin that the census reports the unimported names and ONLY those.

    ⚑⚑ ON A FIXTURE, NEVER THE CORPUS. `--unimported` over the live tree is a ~13-minute fold —
    `all_sites` is one parse, but its inner loop runs per module per node, so at corpus scale the
    cost returns. A suite that spent it would be the class `all_sites` exists to avoid,
    reintroduced by its own case.

    ⚑ BOTH DIRECTIONS, because a reader returning EVERY name passes an arm that only checks the
    unimported one, and a reader returning NOTHING passes an arm that only checks the imported
    one. The fixture carries one of each so neither degenerate answer survives.

    ⚑ THE IMPORT IS LOCAL because the per-file gate enforces import-with-use in ONE write, and
    `tempfile` is used only here.
    """
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as where:
        root = Path(where)
        (root / "seen.py").write_text("x = 1\n", encoding="utf-8")
        (root / "lonely.py").write_text("y = 2\n", encoding="utf-8")
        (root / "reader.py").write_text("from seen import x\n", encoding="utf-8")
        files = tuple((p, p.name) for p in sorted(root.glob("*.py")))
        got = unimported(files)
    return [
        ("an imported module is not reported unimported", "seen" in got, False),
        ("and an unimported one is", "lonely" in got, True),
    ]


def _selftest() -> int:
    """Cases pinning the operand normalisation, the site spelling and the split."""
    cases: list[tuple[str, object, object]] = [
        # ⚑ THE OPERAND AXIS, which is DIFFERENT from the site axis and must stay so. All
        # three spellings name one module; a reader collapsing the two axes passes one of
        # these and fails the spelling cases.
        (
            "all three operand spellings normalise to one module",
            [
                normalise(o).module
                for o in ("substrate.corpus", "substrate/corpus.py", "substrate/corpus/__init__.py")
            ],
            ["substrate.corpus", "substrate.corpus", "substrate.corpus"],
        ),
        (
            "the operand spelling is carried, not discarded",
            [
                (normalise(o).spelling, normalise(o).translated)
                for o in ("substrate.corpus", "substrate/corpus.py")
            ],
            [(DOTTED, False), (PATH, True)],
        ),
        # ⚑ THE STAR FORM STILL REPORTS ITS OWN NAME LIST rather than an empty one, since an
        # empty list reads as "binds nothing" and a star binds the most of any form.
        (
            "a star import reports itself, never an empty binding",
            [
                (s.form, s.names)
                for s in _probe("from substrate.corpus import *\n", "substrate.corpus")
            ],
            [(STAR, ("*",))],
        ),
        # ⚑ THE UNEXPORTABLE NAMES, the question a module split actually asks.
        (
            "a leading-underscore bound name is named as star-unexportable",
            unexportable(_probe("from substrate.corpus import _node, ok\n", "substrate.corpus")),
            ("_node",),
        ),
        *_cases_spelling(),
        *_cases_bulk(),
        *_cases_unimported(),
    ]
    bad = [(n, g, w) for n, g, w in cases if g != w]
    for n, g, w in bad:
        sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"module_importers selftest: {len(cases) - len(bad)}/{len(cases)}\n")
    return 1 if bad else 0


def unimported(files: Iterable[tuple[Path, str]]) -> tuple[str, ...]:
    """Return every module in `files` that no file in `files` imports.

    ⚑⚑⚑ A ZERO HERE IS A FLOOR, NEVER AN ABSENCE, AND THE RENDERER MUST SAY SO. This reader
    names twelve shapes it cannot resolve — a dynamic import binds a module at runtime and no
    static walk sees it — so *"nothing imports this"* means *"nothing this reader can see imports
    this"*. A census that dropped the caveat would license a deletion, which is how
    `census-keyed-on-one-spelling` killed two links.

    ⚑⚑ AND UNIMPORTED IS NOT UNREACHED. A module with no importer may be a live ENTRY POINT:
    `payable_census` has zero importers and answers on a bare run. Asking that second question is
    `mode_dispatch`'s and `tool_population`'s, so this returns the import fact alone rather than
    guessing a verdict it cannot support — the two together are what an orphan claim needs.

    ⚑ ONE PARSE, NOT ONE PER MODULE. `all_sites` exists because `sites` is quadratic for a census
    and did not finish in 120 seconds over ~700 candidates (gate-G301). Folding it here is why
    this is a mode rather than a caller looping — a tool whose cost makes it unrunnable is
    orphaned by construction, which would be this census reporting on itself.
    """
    named = {normalise(label).module for _path, label in files}
    found = all_sites(sorted(named), files)
    return tuple(sorted(name for name, got in found.items() if not got))


def render_unimported(names: tuple[str, ...], scanned: int) -> str:
    """Return the unimported census, carrying its own denominator and its own blind spots."""
    out = [f"  {name}" for name in names]
    out.append(f"{len(names)} of {scanned} module(s) are imported by nothing this reader can see")
    out.append("   ⚑ A FLOOR, NOT AN ABSENCE. A dynamic import binds a module at runtime and no")
    out.append("     static walk sees it — ask `module_importers <name>` for the shapes it missed.")
    out.append("   ⚑ AND UNIMPORTED IS NOT UNUSED: a module with no importer may be a live entry")
    out.append("     point. `payable_census` has none and answers on a bare run.")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """Print the importers of the module named on the command line.

    ⚑ THE BARE NAME IS RESOLVED AGAINST THE CORPUS BEFORE IT IS QUERIED (Ⓝ82). A bare
    operand that names exactly one module is answered AS that module and says so; one that
    names several is refused with the candidates; one that names none is queried as the
    top-level module it appears to be, which is what `import agda_lex` legitimately is.

    ⚑⚑ AND THE RESOLUTION NO LONGER NARROWS THE ANSWER (Ⓝ122g). Resolving `_agdatext` to
    `scripts._agdatext` once meant asking for a spelling nothing writes; the census now covers
    both site spellings, so the note reports a translation rather than performing a filter.

    ⚑ `--unimported` INVERTS THE QUESTION OVER THE WHOLE CORPUS — which modules does nothing
    import. It is a MODE here rather than a caller's loop because `sites` is quadratic for a
    census and `all_sites` exists for exactly this fold (gate-G301). ⚑ ITS ZERO IS A FLOOR: the
    blind shapes this reader names apply to every row, so the render carries them in-band.
    """
    if argv == ["--unimported"]:
        files = population()
        sys.stdout.write(render_unimported(unimported(files), len(files)))
        return 0
    if not argv or any(arg.startswith("-") for arg in argv):
        sys.stderr.write(
            "usage: module_importers.py <module>|<path/to/module.py> [<module> ...]\n"
            "       module_importers.py --unimported\n"
        )
        return 2
    # ⚑ SEVERAL OPERANDS, ONE POPULATION READ. Retiring a module FAMILY asks this of each member;
    # twelve invocations joined by hand is the judgement-in-the-turn shape, and each would re-walk
    # the whole corpus. Each operand is still resolved, refused or answered on its own.
    files = population()
    worst = 0
    for operand in argv:
        found = candidates(operand, files)
        if len(found) > 1:
            sys.stderr.write(refusal(operand, found))
            worst = 2
            continue
        asked = found[0] if found else operand
        text = render(asked, sites(asked, files), len(files), unresolved(asked, files))
        if found:
            text = f"  ⚑ the bare name `{operand}` resolved to `{asked}`\n{text}"
        sys.stdout.write(text)
    return worst


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(_selftest())
    sys.exit(main(sys.argv[1:]))
