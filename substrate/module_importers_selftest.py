#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.module_importers` — both spellings, and the zero that was banked.

⚑⚑⚑ THE SUBMODULE CASE IS HERE BECAUSE ITS ABSENCE ALREADY COST A FALSE ZERO ON THE LIVE TREE.
The origin resolves `node.module.split(".")[0]`, so `from substrate import corpus` registers as an
import of `substrate` and never of `substrate.corpus`. MEASURED against the origin:
`--importers corpus` -> `0 import site(s) in 0 of 998 file(s)`, for a module twenty-odd files in
this package import by name. A reader without this case goes on reporting that zero forever.

⚑⚑ AND THE POSITIVE CONTROL IS WHAT MAKES THE ZERO CASES MEAN ANYTHING. A resolver that matched
NOTHING would pass every *this must not be reported* case here — the unrelated module, the
relative import, the near-miss prefix. Each is paired with a case proving the same resolver still
finds the real import, so the negatives discriminate rather than excusing the population.

⚑⚑⚑ AND THE SAME CLASS RETURNED ONE OPERAND-SHAPE OVER (Ⓝ74 ⟡importers-path-spelling), WHICH IS
WHY THE SPELLING ARMS ARE HERE. MEASURED on the live tree, minutes apart:
`substrate/reach_ratchet.py` -> 0 sites, `substrate.reach_ratchet` -> 1 site. Same module, same
question; the failing spelling is the one a reader HAS — arriving from a census row, a traceback
or `suite_gap_report`, you hold a path, and the dotted name is what you own only once you already
know the answer. The arms below pin the EQUIVALENCE of the spellings rather than either answer.

⚑⚑ THE BOUNDARY ARMS ARE NOT DECORATION. A promoted reader inherits the QUESTION and drops the
BOUNDARY — three false zeros in one toolkit in one day — so `unresolved` is tested for being
CONDITIONAL, not merely non-empty. An arm asserting only that it names something would pass a
function that named every shape always, which is the same collapse with better manners.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live corpus measures today's tree, so it
would report the corpus rather than the reader — and go green the moment an unrelated file moved.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import module_importers

# The spelling the origin cannot see: the module is named in the ALIAS LIST, not in `node.module`.
_SUBMODULE = "from substrate import corpus\n"

# The spelling the origin can see.
_DOTTED = "from substrate.corpus import py_files\n"

_PLAIN = "import substrate.corpus\n"

_ALIASED = "import substrate.corpus as C\n"

_STAR = "from substrate.corpus import *\n"

# Leading-underscore names — exactly what a star re-export drops.
_PRIVATE = "from substrate.corpus import _SKIP_PARTS, py_files\n"

# A relative import: unresolvable without the importer's package.
_RELATIVE = "from . import corpus\n"

# A different module of the same package — must NOT match a query for `substrate.corpus`.
_SIBLING = "from substrate import name_collision\n"

# A near miss: a longer name that merely STARTS with the query.
_PREFIX = "import substrate.corpus_helpers\n"

# A runtime import: the name need not even be a literal, so no static read resolves it.
_DYNAMIC = "import importlib\nm = importlib.import_module('substrate.corpus')\n"

_TWO = 2


def _write(where: str, files: dict[str, str]) -> list[tuple[Path, str]]:
    """Write fixture files under `where` and return the `(path, label)` pairs.

    ⚑ ONE WRITER FOR BOTH READERS. `sites` and `unresolved` must be asked about the SAME tree, or
    an arm could pass because the two saw different fixtures — a defect that would look exactly
    like the reader disagreeing with itself.
    """
    pairs = []
    for label, text in files.items():
        path = Path(where) / label
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        pairs.append((path, label))
    return pairs


def _sites(files: dict[str, str], module: str) -> tuple[module_importers.Site, ...]:
    """Write fixture files under a temp root and read the import sites back."""
    with tempfile.TemporaryDirectory() as where:
        return module_importers.sites(module, _write(where, files))


def _unresolved(files: dict[str, str], module: str) -> tuple[str, ...]:
    """Write fixture files under a temp root and read the BLIND SHAPES back."""
    with tempfile.TemporaryDirectory() as where:
        return module_importers.unresolved(module, _write(where, files))


def a_package_submodule_import_is_found(out: list[str]) -> int:
    """Check `from substrate import corpus` resolves as an import of `substrate.corpus`.

    ⚑⚑⚑ THE CASE THAT CATCHES THE BANKED ZERO. The origin keys on `node.module`, which says only
    `substrate` here — so every submodule of every package reads as having no importers at all.
    Measured on the live tree: `--importers corpus` -> 0, against twenty real importers.
    """
    got = _sites({"a/one.py": _SUBMODULE}, "substrate.corpus")
    if len(got) != 1 or got[0].names != ("corpus",):
        out.append(f"selftest: a package-submodule import was not resolved: {got!r}")
        return 1
    return 0


def a_dotted_from_import_is_found(out: list[str]) -> int:
    """Check `from substrate.corpus import py_files` still resolves — the spelling that worked.

    ⚑ THE POSITIVE CONTROL FOR THE SUBMODULE REPAIR. Widening a resolver can break what it already
    matched; without this, the fix above could have traded one false zero for another.
    """
    got = _sites({"a/one.py": _DOTTED}, "substrate.corpus")
    if len(got) != 1 or got[0].names != ("py_files",):
        out.append(f"selftest: a dotted from-import was not resolved: {got!r}")
        return 1
    return 0


def a_plain_import_is_found(out: list[str]) -> int:
    """Check `import substrate.corpus` resolves and reports the dotted name it binds."""
    got = _sites({"a/one.py": _PLAIN}, "substrate.corpus")
    if len(got) != 1 or got[0].form != module_importers.PLAIN:
        out.append(f"selftest: a plain import was not resolved: {got!r}")
        return 1
    return 0


def an_alias_is_reported_as_the_bound_name(out: list[str]) -> int:
    """Check `import x as y` reports `y` — the name the file actually uses.

    ⚑ REPORTING `x` DESCRIBES THE STATEMENT, NOT THE FILE. A rename driven off that report would
    miss every use site, which is the half of a mechanized edit that gets forgotten.
    """
    got = _sites({"a/one.py": _ALIASED}, "substrate.corpus")
    if len(got) != 1 or got[0].names != ("C",):
        out.append(f"selftest: an alias was not reported as the bound name: {got!r}")
        return 1
    return 0


def a_star_import_is_marked_as_one(out: list[str]) -> int:
    """Check a star import gets its own form rather than an empty name list.

    ⚑ AN EMPTY LIST READS AS *binds nothing* and a star import binds the most of any form — the
    inversion is total, and a consumer acting on it would drop the widest dependency in the file.
    """
    got = _sites({"a/one.py": _STAR}, "substrate.corpus")
    if len(got) != 1 or got[0].form != module_importers.STAR:
        out.append(f"selftest: a star import was not marked: {got!r}")
        return 1
    return 0


def an_underscore_name_is_reported_as_unexportable(out: list[str]) -> int:
    """Check a `_`-prefixed bound name is flagged as one a star re-export cannot carry.

    ⚑⚑ THE MEASURED INCIDENT: `_node`, `_unit`, `_unit_cod`, `_orbit_def` vanished off a
    re-export surface while every suite stayed green, because `import *` skips a leading
    underscore. A split that reads only the file list re-exports with a star and ships the break.
    """
    got = _sites({"a/one.py": _PRIVATE}, "substrate.corpus")
    if module_importers.unexportable(got) != ("_SKIP_PARTS",):
        out.append(f"selftest: a private bound name was not flagged: {got!r}")
        return 1
    return 0


def a_public_name_is_not_unexportable(out: list[str]) -> int:
    """Check a public bound name is NOT flagged — the control for the underscore case.

    ⚑ WITHOUT THIS, A READER FLAGGING EVERYTHING would pass the case above, and the census that
    tells a split what to re-import by name would name the whole surface.
    """
    got = _sites({"a/one.py": _DOTTED}, "substrate.corpus")
    if module_importers.unexportable(got) != ():
        out.append(f"selftest: a public name was flagged unexportable: {got!r}")
        return 1
    return 0


def a_relative_import_is_not_resolved(out: list[str]) -> int:
    """Check `from . import corpus` is not claimed as an import of `substrate.corpus`.

    ⚑ IT NAMES A MODULE THIS READER CANNOT RESOLVE without knowing the importer's package.
    Guessing would attribute an import to whichever package shares the leaf name — a false
    FINDING, which is the opposite error from the false zero above and just as wrong.
    """
    got = _sites({"a/one.py": _RELATIVE}, "substrate.corpus")
    if got != ():
        out.append(f"selftest: a relative import was resolved: {got!r}")
        return 1
    return 0


def a_sibling_submodule_is_not_matched(out: list[str]) -> int:
    """Check `from substrate import name_collision` does not match a query for another submodule.

    ⚑ THE SUBMODULE REPAIR MUST NOT WIDEN INTO THE PACKAGE. Matching on the package alone would
    report every file in it as importing every module in it — a census with no discrimination
    left, which is a different way of saying nothing.
    """
    got = _sites({"a/one.py": _SIBLING}, "substrate.corpus")
    if got != ():
        out.append(f"selftest: a sibling submodule matched: {got!r}")
        return 1
    return 0


def a_longer_name_is_not_a_match(out: list[str]) -> int:
    """Check `substrate.corpus_helpers` does not match a query for `substrate.corpus`.

    ⚑ MATCH A DOTTED COMPONENT, NOT A STRING PREFIX — the class this repo already paid for with a
    `"build" in rel` test that also ate `rebuild/` and `buildtools/`.
    """
    got = _sites({"a/one.py": _PREFIX}, "substrate.corpus")
    if got != ():
        out.append(f"selftest: a longer name matched as a prefix: {got!r}")
        return 1
    return 0


def a_bare_module_name_still_resolves(out: list[str]) -> int:
    """Check a caller may name the module without its package.

    ⚑ A CALLER ARRIVING FROM A FILENAME HAS THE BARE NAME and one arriving from a traceback has
    the dotted one. Requiring one spelling answers a question the caller did not ask — with a zero.
    """
    got = _sites({"a/one.py": "import agda_lex\n"}, "agda_lex")
    if len(got) != 1:
        out.append(f"selftest: a bare module name did not resolve: {got!r}")
        return 1
    return 0


def every_importing_file_is_reported(out: list[str]) -> int:
    """Check the census carries all sites, not just the first."""
    got = _sites({"a/one.py": _SUBMODULE, "b/two.py": _DOTTED}, "substrate.corpus")
    if len(got) != _TWO:
        out.append(f"selftest: not every importing file was reported: {got!r}")
        return 1
    return 0


def an_unparseable_file_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising.

    ⚑ ONE BAD FILE MUST NOT TAKE THE CENSUS DOWN — it would report nothing about the ~997 that
    parse, a far larger error than the one file it skips.
    """
    got = _sites({"a/one.py": "def broken(:\n"}, "substrate.corpus")
    if got != ():
        out.append(f"selftest: an unparseable file yielded {got!r}")
        return 1
    return 0


def the_render_prints_its_denominator_on_zero(out: list[str]) -> int:
    """Check an empty census still names how many files were scanned.

    ⚑⚑ `0 sites` AND `0 sites OF 998 FILES` ARE THE SAME FINDING and only the second lets a reader
    see the scan happened. This is the exact line that would have made the origin's `--importers
    corpus` zero legible as a question about the reader rather than about the tree.
    """
    text = module_importers.render("substrate.corpus", (), 998)
    if "of 998 file(s)" not in text:
        out.append(f"selftest: an empty census omits its denominator:\n{text}")
        return 1
    return 0


def the_render_names_the_unexportable_names(out: list[str]) -> int:
    """Check the star-unsafe names reach the report, not just the accessor."""
    rows = _sites({"a/one.py": _PRIVATE}, "substrate.corpus")
    text = module_importers.render("substrate.corpus", rows, 1)
    if "_SKIP_PARTS" not in text or "star-re-export" not in text:
        out.append(f"selftest: the render omits the unexportable names:\n{text}")
        return 1
    return 0


def a_path_spelling_resolves_to_the_dotted_name(out: list[str]) -> int:
    """Check `substrate/corpus.py` normalises to `substrate.corpus`.

    ⚑⚑⚑ THE Ⓝ74 CASE. The two spellings answered 0 and 1 on the live tree, with the failing one
    being the spelling a reader actually holds. This arm pins the translation itself, so a
    regression shows up here rather than as a bare zero somebody banks.
    """
    got = module_importers.normalise("substrate/corpus.py")
    if got.module != "substrate.corpus" or got.spelling != module_importers.PATH:
        out.append(f"selftest: a path spelling did not normalise: {got!r}")
        return 1
    return 0


def a_dotted_spelling_is_left_alone(out: list[str]) -> int:
    """Check `substrate.corpus` is not mangled by the path repair.

    ⚑ THE DISCRIMINATOR FOR THE ARM ABOVE. A normaliser that rewrote everything would pass it and
    silently break the spelling that already worked — trading one false zero for another, which
    is precisely how this class has propagated.
    """
    got = module_importers.normalise("substrate.corpus")
    if got.module != "substrate.corpus" or got.spelling != module_importers.DOTTED:
        out.append(f"selftest: a dotted spelling was rewritten: {got!r}")
        return 1
    return 0


def both_spellings_find_the_same_sites(out: list[str]) -> int:
    """Check a path and a dotted operand return identical censuses.

    ⚑⚑ THIS IS THE PROPERTY, NOT THE TRANSLATION. Normalising correctly and then querying with
    the wrong name would pass the two arms above; only comparing the ANSWERS pins what the
    measurement actually showed — two spellings of one question giving two different results.
    """
    files = {"a/one.py": _SUBMODULE}
    dotted = _sites(files, "substrate.corpus")
    path = _sites(files, "substrate/corpus.py")
    if dotted != path or len(path) != 1:
        out.append(f"selftest: the spellings disagree — dotted {dotted!r} vs path {path!r}")
        return 1
    return 0


def a_bare_filename_resolves(out: list[str]) -> int:
    """Check `corpus.py` — a path with no directory — resolves to the bare module name."""
    got = module_importers.normalise("corpus.py")
    if got.module != "corpus" or got.spelling != module_importers.PATH:
        out.append(f"selftest: a bare filename did not normalise: {got!r}")
        return 1
    return 0


def a_package_init_names_the_package(out: list[str]) -> int:
    """Check `substrate/__init__.py` normalises to `substrate`, not `substrate.__init__`.

    ⚑ CARRYING `__init__` INTO THE DOTTED NAME BUILDS A FALSE ZERO IN THE NORMALISER — it would
    query a module no importer can ever name, so the answer would be 0 for every package in the
    tree and the reason would live one layer below where anyone would look.
    """
    got = module_importers.normalise("substrate/__init__.py")
    if got.module != "substrate":
        out.append(f"selftest: a package __init__ did not name its package: {got!r}")
        return 1
    return 0


def the_render_names_the_spelling_it_resolved(out: list[str]) -> int:
    """Check a translated operand says so in the report.

    ⚑⚑ A SILENT NORMALISATION IS AN UNCHECKABLE ONE. A reader who sees the wrong dotted name
    knows the operand was misread; one who sees only a count concludes the module is unused —
    which is the same banked zero, one layer in.
    """
    text = module_importers.render("substrate/corpus.py", (), 998)
    if "substrate.corpus" not in text or "path spelling" not in text:
        out.append(f"selftest: the render hides its resolution:\n{text}")
        return 1
    return 0


def the_render_stays_quiet_on_an_untranslated_operand(out: list[str]) -> int:
    """Check a dotted operand gets no resolution note.

    ⚑ THE DISCRIMINATOR FOR THE ARM ABOVE. A render that always printed a resolution line would
    pass it, and the line would stop meaning *this was translated*.
    """
    text = module_importers.render("substrate.corpus", (), 998)
    if "spelling" in text:
        out.append(f"selftest: the render annotates an untranslated operand:\n{text}")
        return 1
    return 0


def a_zero_carries_its_unresolved_shapes(out: list[str]) -> int:
    """Check a star re-export of the queried module is named as a blind shape.

    ⚑⚑⚑ THIS REPO DELETES ON ZEROS. A count alone cannot separate *nothing imports this* from
    *this reader could not see*, and a star re-export puts the module's names under ANOTHER
    module's, where no consumer names this one at all.
    """
    got = _unresolved({"a/one.py": _STAR}, "substrate.corpus")
    if not any(b.startswith(module_importers.CHAIN) for b in got):
        out.append(f"selftest: a star re-export was not reported as a blind shape: {got!r}")
        return 1
    return 0


def a_relative_import_is_reported_as_unresolved(out: list[str]) -> int:
    """Check `from . import corpus` is NAMED rather than silently dropped.

    ⚑⚑ EXCLUDING IT FROM THE CENSUS IS CORRECT AND NOT ENOUGH. Dropping it silently puts the
    same false zero back one level in: the site exists, it may be this module, and a reader
    acting on the count would delete a module something imports.
    """
    got = _unresolved({"a/one.py": _RELATIVE}, "substrate.corpus")
    if not any(b.startswith(module_importers.RELATIVE_PKG) for b in got):
        out.append(f"selftest: a relative import was dropped without a note: {got!r}")
        return 1
    return 0


def a_dynamic_import_is_reported_as_unresolved(out: list[str]) -> int:
    """Check `importlib.import_module(...)` is named as a shape no static read resolves."""
    got = _unresolved({"a/one.py": _DYNAMIC}, "substrate.corpus")
    if not any(b.startswith(module_importers.DYNAMIC) for b in got):
        out.append(f"selftest: a dynamic import was not reported: {got!r}")
        return 1
    return 0


def the_unresolved_shapes_are_conditional(out: list[str]) -> int:
    """Check a file with none of the blind shapes yields an EMPTY unresolved list.

    ⚑⚑⚑ THE DISCRIMINATOR FOR THE WHOLE BOUNDARY HALF, and without it every arm above is
    satisfied by a function that names every shape on every call. A boundary reported
    unconditionally is one a reader learns to skip, which returns it to the caveat it replaced.
    """
    got = _unresolved({"a/one.py": _DOTTED}, "substrate.corpus")
    if got != ():
        out.append(f"selftest: unresolved fired on a file with no blind shapes: {got!r}")
        return 1
    return 0


def the_render_carries_the_boundary_into_the_report(out: list[str]) -> int:
    """Check the unresolved shapes reach the printed census, not just the accessor.

    ⚑ A BOUNDARY THE CLI DOES NOT PRINT IS ONE NOBODY READS. What a promoted reader drops is
    rarely the function — it is the function's route to the reader.
    """
    text = module_importers.render("substrate.corpus", (), 998, ("dynamic-import: a.py:1 x",))
    if "CANNOT resolve" not in text or "dynamic-import" not in text:
        out.append(f"selftest: the render drops the boundary:\n{text}")
        return 1
    return 0


def _candidates(labels: tuple[str, ...], operand: str) -> tuple[str, ...]:
    """Read the candidate modules for `operand` out of a fixture file list.

    ⚑ `candidates` READS ONLY THE LABELS, so the fixtures need no bodies — and giving them
    bodies would invite an arm to pass because of a body while the label logic was wrong.
    """
    return module_importers.candidates(operand, [(Path(x), x) for x in labels])


def an_ambiguous_bare_name_names_every_candidate(out: list[str]) -> int:
    """Check a bare name carried by two packages returns BOTH, rather than picking one.

    ⚑⚑⚑ Ⓝ82. `corpus` denotes `substrate.corpus` AND `tests.corpus` on the live tree, and
    the reader answered 0 for it — the banked zero, at the third operand shape, in the
    module promoted to kill it. Choosing a winner would answer a question the caller did
    not ask and answer it CONFIDENTLY, which is worse than the zero: a well-formed census
    about the wrong module is indistinguishable from a right one.
    """
    got = _candidates(("substrate/corpus.py", "tests/corpus.py"), "corpus")
    if got != ("substrate.corpus", "tests.corpus"):
        out.append(f"selftest: an ambiguous bare name did not name its candidates: {got!r}")
        return 1
    return 0


def an_unambiguous_bare_name_resolves_to_one_module(out: list[str]) -> int:
    """Check a bare name carried by exactly one package resolves to it.

    ⚑⚑ THE DISCRIMINATOR FOR THE ARM ABOVE. A resolver that refused every bare name would
    pass the ambiguity case while making the tool useless for the spelling a reader most
    often types — trading a false zero for a false refusal, which is the same class with
    better manners.
    """
    got = _candidates(("substrate/suite_emit.py", "substrate/corpus.py"), "suite_emit")
    if got != ("substrate.suite_emit",):
        out.append(f"selftest: an unambiguous bare name did not resolve: {got!r}")
        return 1
    return 0


def a_bare_name_no_module_carries_stays_bare(out: list[str]) -> int:
    """Check a bare name matching nothing in the corpus yields NO candidates.

    ⚑⚑ THIS IS WHAT KEEPS `import agda_lex` ANSWERABLE. A genuine top-level module is not
    in any package, so it has no candidates and must be queried as itself. A resolver that
    invented one would break the legitimate case the bare spelling already served — and
    `a_bare_module_name_still_resolves` is the arm that pins that behaviour end-to-end.
    """
    got = _candidates(("substrate/corpus.py",), "agda_lex")
    if got != ():
        out.append(f"selftest: a bare name with no carrier invented a candidate: {got!r}")
        return 1
    return 0


def a_dotted_operand_is_never_resolved_against_the_corpus(out: list[str]) -> int:
    """Check a dotted operand whose LEAF matches a corpus module yields no candidates.

    ⚑⚑⚑ THIS ARM PINS A PROPERTY, NOT A LINE, AND THE DIFFERENCE WAS MEASURED. `candidates`
    once opened with an explicit `if "." in operand …: return ()`; deleting it left the
    suite at 34/34, so the branch was DEAD — the leaf-name test already rejects every
    dotted operand, because a label's leaf is a bare word and the comparison is against the
    whole dotted string. The guard has been removed; the property it claimed is real and
    still needs asserting, which is what this arm does.

    ⚑⚑ SO A FAILURE HERE MEANS THE RESOLVER STARTED COMPARING LEAF-TO-LEAF instead of
    leaf-to-operand — at which point `substrate.corpus` matches `substrate/corpus.py` and a
    spelling that already names its module is routed into the ambiguity path. Pinning the
    property survives the guard's deletion; pinning the guard did not survive its own.
    """
    got = module_importers.candidates(
        "substrate.corpus", [(Path("substrate/corpus.py"), "substrate/corpus.py")]
    )
    if got != ():
        out.append(f"selftest: a dotted operand was resolved against the corpus: {got!r}")
        return 1
    return 0


def a_path_operand_is_never_resolved_against_the_corpus(out: list[str]) -> int:
    """Check a BARE FILENAME is read as a path, not as an ambiguous bare name.

    ⚑⚑ `corpus.py` IS THE NEAREST OPERAND TO THE AMBIGUOUS ONE. It is a PATH — the module
    it names is the top-level `corpus` — and `normalise` already resolves it; strip the
    suffix and it is spelled exactly like the bare name. A resolver that normalised the
    operand BEFORE testing it would put a spelling that determined its module into the
    ambiguity path, and the reader would get a REFUSAL for a question they had already
    asked precisely — the false zero's mirror, and just as wrong.
    """
    got = _candidates(("corpus.py", "tests/corpus.py"), "corpus.py")
    if got != ():
        out.append(f"selftest: a path operand was resolved against the corpus: {got!r}")
        return 1
    return 0


def a_package_init_does_not_carry_its_leaf_name(out: list[str]) -> int:
    """Check `substrate/corpus/__init__.py` is a candidate for `corpus`, not for `__init__`.

    ⚑ A PACKAGE IS A MODULE A BARE NAME CAN DENOTE. Keying on the FILE stem alone would
    make every `__init__.py` in the tree a candidate for the operand `__init__` and none
    for the package it actually names — a false zero built inside the resolver, one layer
    below where anyone would look for it.
    """
    got = _candidates(("substrate/corpus/__init__.py",), "corpus")
    if got != ("substrate.corpus",):
        out.append(f"selftest: a package __init__ did not carry its leaf name: {got!r}")
        return 1
    return 0


def the_refusal_names_every_candidate(out: list[str]) -> int:
    """Check the refusal text carries the candidates, not just the fact of ambiguity.

    ⚑⚑ A REFUSAL THAT DOES NOT HAND BACK THE NEXT COMMAND IS A DEAD END. The reader typed
    the shortest spelling because it is the one they had; telling them it is ambiguous
    without naming what it is ambiguous BETWEEN leaves them with less than the zero did.
    """
    text = module_importers.refusal("corpus", ("substrate.corpus", "tests.corpus"))
    if "substrate.corpus" not in text or "tests.corpus" not in text:
        out.append(f"selftest: the refusal omits its candidates:\n{text}")
        return 1
    return 0


_ARMS = (
    an_ambiguous_bare_name_names_every_candidate,
    an_unambiguous_bare_name_resolves_to_one_module,
    a_bare_name_no_module_carries_stays_bare,
    a_dotted_operand_is_never_resolved_against_the_corpus,
    a_path_operand_is_never_resolved_against_the_corpus,
    a_package_init_does_not_carry_its_leaf_name,
    the_refusal_names_every_candidate,
    a_package_submodule_import_is_found,
    a_path_spelling_resolves_to_the_dotted_name,
    a_dotted_spelling_is_left_alone,
    both_spellings_find_the_same_sites,
    a_bare_filename_resolves,
    a_package_init_names_the_package,
    the_render_names_the_spelling_it_resolved,
    the_render_stays_quiet_on_an_untranslated_operand,
    a_zero_carries_its_unresolved_shapes,
    a_relative_import_is_reported_as_unresolved,
    a_dynamic_import_is_reported_as_unresolved,
    the_unresolved_shapes_are_conditional,
    the_render_carries_the_boundary_into_the_report,
    a_dotted_from_import_is_found,
    a_plain_import_is_found,
    an_alias_is_reported_as_the_bound_name,
    a_star_import_is_marked_as_one,
    an_underscore_name_is_reported_as_unexportable,
    a_public_name_is_not_unexportable,
    a_relative_import_is_not_resolved,
    a_sibling_submodule_is_not_matched,
    a_longer_name_is_not_a_match,
    a_bare_module_name_still_resolves,
    every_importing_file_is_reported,
    an_unparseable_file_yields_nothing,
    the_render_prints_its_denominator_on_zero,
    the_render_names_the_unexportable_names,
)

# ⚑⚑ DERIVED, NEVER TYPED. This was `28` beside 27 arms — a hand-maintained count that had
# already drifted, so the suite reported a case it did not run. That is the reported number
# describing the DOCUMENT rather than the run, which is the shape this toolkit files most
# often; here it would also mask a deleted arm, since dropping one leaves the banner
# unchanged. `len` cannot disagree with the tuple it measures.
_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"module-importers selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"module-importers selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
