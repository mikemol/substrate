#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Trim named top-level definitions out of a module — as a MODE, not a hand-retyped file.

⚑⚑⚑ THE TRIM IS A WRITE, AND EVERY HAND-DONE ONE HIT THE SAME WALL. Six modules were split today
(an inline `def selftest()` plus its private helpers moved to a sibling `<module>_selftest.py`) and
each trim ran into this: THE EXCISION AND THE NOW-UNUSED IMPORTS ARE NON-CONTIGUOUS. Under the
zero-tolerance per-file gate BOTH `Edit` orderings leave a finding —

    remove the import first  →  F821 Undefined name `Callable`
    remove the def first     →  F401 `Callable` imported but unused

— and ANY finding refuses the write AND REVERTS THE WHOLE FILE. So there is no clean intermediate
state to pass through, and a trim cannot be done as `Edit`s at all: it has to be ONE `Write`
reproducing the entire trimmed file. One case retyped 250 lines by hand. Three agents discovered
this wall independently, which is what makes it a MODE rather than a technique.

⚑⚑ THE DILEMMA DISSOLVES IN `record_migrate`'s PIPELINE, WHICH IS WHY THIS SPECIALISES IT RATHER
THAN OPENING A SECOND WRITE PATH. That tool stages a prospective output INSIDE the project, hands
it to `ruff --fix`, checks the RESULT with the house checker, and writes only on CLEAN. `_autofix`
removes the newly-unused import MECHANICALLY, so the intermediate never has to be clean — it is
fixed before it is ever checked or written. This module contributes the TRANSFORM (remove these
names) and the GUARD; the staging, fixing, checking and verdict lattice are `record_migrate`'s,
called and never reimplemented.

⚑⚑ AND THE GUARD IS `split_lemmas`' CONSERVATION GUARD ONE LANGUAGE OVER. That splitter refuses to
write unless every non-blank body line lands in exactly one unit, and THAT GUARD HAS CAUGHT SEVEN
DISTINCT SILENT-DELETION BUGS. A mechanical extractor's characteristic output is PLAUSIBLE AND
WRONG — a trimmed module reads perfectly whether it dropped the right `def` or the one below it. So
this does not REASON that the excision was safe; it VERIFIES it, twice over:

  - every requested name is matched by a top-level definition, or the trim is REFUSED;
  - every code line of the original lands in the trimmed text or the extracted text, and neither
    partition invents a line the original never held.

A name that was asked for and is not present in the source is a REFUSAL, not a no-op: silently
trimming four of five requested names is exactly the plausible-and-wrong output the guard is for.

⚑⚑⚑ THE `__main__` DISPATCH BLOCK IS PART OF THE TAIL, AND IT WAS THIS MODE'S MEASURED BOUND.
Trimming `selftest` from a module whose `if __name__ == "__main__":` body calls it came back
FINDINGS — `F821 Undefined name selftest` — because the block is not a NAMED DEFINITION the trim
could take, so removing the def stranded the reference. Nothing was written; the tool refused
rather than emitting the error, which was correct and still a real limit: the block had to be
removed by hand first, which is the retype this mode exists to abolish.

⚑⚑ IT IS CLOSED BY IDENTIFYING THE BLOCK STRUCTURALLY AND ASKING WHAT IT OUTLIVES. A guard whose
body references ONLY names being trimmed is tail and comes out with them. A guard that ALSO
references a definition that SURVIVES is a module whose command line outlives its cases — taking it
would silently delete the entry point — so that is REFUSED, naming the survivor. The block is
partitioned into the extracted text, never exempted from the conservation guard: an exemption would
re-open the hole the both-baselines rule was written to close.

    module_trim.py --dry-run substrate/x.py selftest _helper
    module_trim.py --apply   substrate/x.py selftest _helper
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import libcst as cst
from mikemol.corpus import tree_root

from substrate import corpus, record_migrate, suite_gap

# The verdict a trim carries when the guard refused it — distinct from a checker's FINDINGS.
UNSAFE = "UNSAFE"

#: What a module's suite is called. ⚑ READ FROM THE CENSUS THAT OWNS THE CONVENTION rather than
#: retyped: `suite_gap` decides what counts as coverage, and a second spelling here would let this
#: tool write a file the census does not recognise as the suite it just created.
SUITE_SUFFIX: str = suite_gap.SUITE_SUFFIX

# What a trim reports when nothing was asked of it.
NOTHING_ASKED = "name at least one definition to trim"

# How a top-level import statement begins.
IMPORT_PREFIXES = ("import ", "from ")

# The dunder a dispatch guard tests, and the value it tests it against.
_DUNDER_NAME = "__name__"
_MAIN = "__main__"


@dataclass(frozen=True, slots=True)
class Trim:
    """One module's prospective trim: what would remain, what came out, and whether it may land.

    ⚑ `removed` IS THE EXTRACTED TEXT, NOT A COUNT. The conservation guard compares LINES, so the
    text that came out has to survive to the point of the comparison — a count could not tell a
    correct excision from an excision of a different body of the same length.
    """

    relpath: str
    verdict: str
    names: tuple[str, ...]
    removed: str
    report: str
    source: str

    @property
    def writable(self) -> bool:
        """Report whether this trim may be committed to disk.

        ⚑ ONLY `CLEAN` IS WRITABLE, and this defers to `record_migrate` for what CLEAN means rather
        than restating the lattice. UNSAFE and UNKNOWN are refused on the same footing as FINDINGS:
        a guard that refused and a checker that could not run have both established nothing.
        """
        return self.verdict == record_migrate.CLEAN


def _defined_name(statement: cst.BaseStatement) -> str | None:
    """Return the name a top-level statement DEFINES, or None when it defines nothing.

    ⚑⚑ THE PARTITION IS OVER `Module.body`, WHICH IS WHAT MAKES "TOP LEVEL" A FACT RATHER THAN A
    DEPTH COUNTER. A method spelled `selftest` on some class is a DIFFERENT definition that happens
    to share a name; a visitor matching on the name alone would remove it, which is the
    silent-deletion shape. Reading the module's own body list cannot reach one.
    """
    if isinstance(statement, (cst.FunctionDef, cst.ClassDef)):
        return statement.name.value
    return None


def is_dispatch_guard(statement: cst.BaseStatement) -> bool:
    """Report whether a top-level statement is an `if __name__ == "__main__":` block.

    ⚑⚑ MATCHED ON THE COMPARISON'S STRUCTURE, NOT ON ITS SOURCE TEXT. A substring test for
    `__main__` would also match a docstring that mentions it, a comment, or an `if __name__ !=
    "__main__"` — the last of which is the OPPOSITE block and would be taken as tail. Reading the
    `Comparison` node's operator and both operands is what makes this a fact rather than a guess.
    """
    if not isinstance(statement, cst.If):
        return False
    test = statement.test
    if not isinstance(test, cst.Comparison) or len(test.comparisons) != 1:
        return False
    if not isinstance(test.left, cst.Name) or test.left.value != _DUNDER_NAME:
        return False
    target = test.comparisons[0]
    if not isinstance(target.operator, cst.Equal):
        return False
    return (
        isinstance(target.comparator, cst.SimpleString)
        and target.comparator.evaluated_value == _MAIN
    )


def names_used(node: cst.CSTNode) -> set[str]:
    """Return every bare `Name` this subtree READS.

    ⚑ AN ATTRIBUTE'S BASE COUNTS, ITS LEAF DOES NOT — `sys.exit(...)` reads `sys`, and no
    module-level definition named `exit` exists for a trim to strand. Collecting the leaf would make
    a guard appear to reference a survivor that is not a definition at all, refusing correct trims
    over a name nothing could have bound.

    ⚑ WALKED DIRECTLY RATHER THAN THROUGH A `CSTVisitor`, because libcst's visitor hooks are spelled
    `visit_Name` — a capitalised method the house lint refuses (N802) with no suppression path. The
    recursion over `children` is the same traversal without the naming contract.
    """
    if isinstance(node, cst.Attribute):
        return names_used(node.value)
    found = {node.value} if isinstance(node, cst.Name) else set()
    for child in node.children:
        found |= names_used(child)
    return found


def guard_survivors(
    statement: cst.BaseStatement, defined: set[str], names: tuple[str, ...]
) -> tuple[str, ...]:
    """Return the module-level definitions a guard references that this trim does NOT take.

    ⚑⚑⚑ THIS IS THE CONSERVATIVE HALF, AND IT IS WHAT SEPARATES A TAIL FROM A CLI. A guard reaching
    ONLY names being trimmed is part of the tail: removing the definitions and leaving the block
    strands the reference (the measured F821), and removing both is the whole excision. A guard that
    ALSO calls `main` — a module whose command line outlives its cases — is NOT tail, and taking it
    would silently delete the entry point. So the predicate is asked in the direction that can
    REFUSE: report what SURVIVES, and take the block only when nothing does.

    ⚑ SCOPED TO WHAT THE MODULE DEFINES. A guard reads `sys`, `__name__`, builtins — none of which a
    trim can strand. Only a name bound by a top-level `def`/`class` is at risk, so only those are
    weighed; counting the rest would refuse every guard and make the mode dead on arrival.
    """
    return tuple(sorted((names_used(statement) & defined) - set(names)))


def branch_is_tail(block: cst.If, defined: set[str], names: tuple[str, ...]) -> bool:
    """Report whether this branch's own test and body reference ONLY names being trimmed.

    ⚑ THE `orelse` IS EXCLUDED DELIBERATELY. A branch's `elif` chain holds OTHER branches with
    their own fates, so folding them in would ask about the whole remaining chain and reproduce the
    all-or-nothing reading this exists to replace.
    """
    reached: set[str] = names_used(block.test) | names_used(block.body)
    return bool(reached & set(names)) and not ((reached & defined) - set(names))


def without_trimmed_branches(
    block: cst.If, defined: set[str], names: tuple[str, ...]
) -> tuple[cst.If | None, list[cst.If]]:
    """Return the block with every tail branch removed, plus the branches that were taken.

    ⚑⚑⚑ THE BRANCH IS THE UNIT, NOT THE BLOCK, AND TREATING THE BLOCK AS ATOMIC REFUSED SIX SPLITS.
    A dispatch guard routinely holds two branches with opposite fates — `if "--selftest" in
    sys.argv: sys.exit(_selftest())` is TAIL and leaves with the cases, while the `sys.exit(main(
    sys.argv))` beneath it SURVIVES. Asked of the whole block, `guard_survivors` correctly reports
    that something outlives the trim and correctly refuses; asked per branch, the two separate.

    ⚑⚑ AND THE SAME FACT APPEARS IN `main`'s BODY, which is why this takes any `If`. `iface_readers`
    holds the `--selftest` branch in its `__main__` guard and `sandbox_connect` holds it inside
    `main`, so the tool reported UNSAFE for one and FINDINGS for the other — two verdicts for one
    shape. The location was never the fact; the branch's CONTENT is.

    ⚑ THE CONSERVATISM IS MOVED DOWN A LEVEL, NEVER LOOSENED. A branch calling both a trimmed name
    and a survivor is kept, and the caller refuses exactly as before.
    """
    if branch_is_tail(block, defined, names):
        return (None, [block])

    # ⚑⚑⚑ THE TAIL BRANCH IS A NESTED STATEMENT, NOT AN `elif`. Read from the tree rather than
    # assumed: `iface_readers`' guard holds `if "--selftest" in sys.argv: sys.exit(_selftest())`
    # as a statement INSIDE its body, with `sys.exit(main(sys.argv))` as a SIBLING after it — no
    # `orelse` anywhere. A first cut recursed on `orelse` alone and matched nothing, leaving the
    # refusal exactly as it was. The body's own statement list is where the branches live.
    body = block.body
    if not isinstance(body, cst.IndentedBlock):
        return (block, [])
    taken: list[cst.If] = []
    kept_body: list[cst.BaseStatement] = []
    for inner in body.body:
        if isinstance(inner, cst.If) and branch_is_tail(inner, defined, names):
            taken.append(inner)
        else:
            kept_body.append(inner)
    if not taken:
        return (block, [])
    return (block.with_changes(body=body.with_changes(body=kept_body)), taken)


def _shed_branches(
    fn: cst.FunctionDef, defined: set[str], names: tuple[str, ...]
) -> tuple[cst.FunctionDef, list[cst.If]]:
    """Return the function with its tail branches removed, plus the branches that were taken.

    ⚑⚑⚑ A SURVIVING FUNCTION CAN HOLD A TAIL BRANCH, AND MISSING THAT REFUSED TWO SPLITS.
    `sandbox_connect` and `iface_cost` dispatch `--selftest` from inside `main` rather than from a
    `__main__` guard — the same branch content, one nesting level in. The partition keyed on the
    guard alone, so both reported `F821 Undefined name _selftest`: a message that reads as a defect
    in the module and is really the reach of this reader (gate-G324, the half left open).

    ⚑ THE FUNCTION IS NEVER TAKEN, ONLY THINNED. It survives by definition — it is not among the
    trimmed names — so the def is kept and only its `--selftest` branch travels with the cases.
    """
    body = fn.body
    if not isinstance(body, cst.IndentedBlock):
        return (fn, [])
    taken: list[cst.If] = []
    kept: list[cst.BaseStatement] = []
    for inner in body.body:
        if isinstance(inner, cst.If) and branch_is_tail(inner, defined, names):
            taken.append(inner)
        else:
            kept.append(inner)
    if not taken:
        return (fn, [])
    return (fn.with_changes(body=body.with_changes(body=kept)), taken)


def _excised(source: str, names: tuple[str, ...]) -> tuple[str, str, tuple[str, ...], str]:
    """Return `(trimmed, extracted, names_taken, guard_refusal)` for one module's text.

    ⚑⚑ THE GUARD BLOCK IS PARTITIONED, NEVER EXEMPTED. When it is taken it goes into `extracted`,
    so its lines are weighed by the conservation guard exactly like a trimmed `def`'s. An exemption
    would have been simpler and would have re-opened the hole the both-baselines rule was written to
    close: a block that vanished from BOTH sides and was accused by neither.

    ⚑ ONLY A GUARD THAT ACTUALLY REFERENCES A TRIMMED NAME IS CONSIDERED. A module whose tail is
    being trimmed but whose guard calls only `main` is left untouched — that block is no part of
    this excision, so it is neither taken nor refused.

    ⚑ THE REFUSAL IS RETURNED, NOT RAISED, so `consider` renders it as UNSAFE beside the other
    content refusals rather than as a traceback the caller has to interpret.
    """
    module = cst.parse_module(source)
    defined = {name for name in map(_defined_name, module.body) if name is not None}

    kept: list[cst.BaseStatement] = []
    gone: list[cst.BaseStatement] = []
    taken: list[str] = []
    refusal = ""
    for statement in module.body:
        name = _defined_name(statement)
        if name is not None and name in names:
            taken.append(name)
            gone.append(statement)
        elif isinstance(statement, cst.FunctionDef) and names_used(statement) & set(names):
            # ⚑⚑ A SURVIVING FUNCTION SHEDS ITS TAIL BRANCHES RATHER THAN STRANDING THEM. See
            # `_shed_branches`: the def is kept, only its `--selftest` branch travels.
            shed, branches = _shed_branches(statement, defined, names)
            kept.append(shed)
            gone.extend(branches)
        elif is_dispatch_guard(statement) and names_used(statement) & set(names):
            survivors = guard_survivors(statement, defined, names)
            if not survivors:
                gone.append(statement)
            elif (
                isinstance(statement, cst.If)
                and (pair := without_trimmed_branches(statement, defined, names))[1]
            ):
                # ⚑⚑⚑ THE BLOCK OUTLIVES THE TRIM AND SOME OF ITS BRANCHES DO NOT. Taking the tail
                # branches and keeping the rest is what lets a module whose command line survives
                # still shed its cases — six splits refused on the all-or-nothing reading.
                remainder, branches = pair
                if remainder is not None:
                    kept.append(remainder)
                gone.extend(branches)
            else:
                refusal = (
                    "the `__main__` dispatch block also references "
                    + ", ".join(survivors)
                    + " — this module's command line outlives the definitions being "
                    "trimmed, so the block is not tail; rewrite it by hand first"
                )
                kept.append(statement)
        else:
            kept.append(statement)
    trimmed = module.with_changes(body=kept).code
    extracted = module.with_changes(body=gone, header=()).code
    return (trimmed, extracted, tuple(taken), refusal)


def _is_import(line: str) -> bool:
    """Report whether a stripped source line is an import statement."""
    return line.startswith(IMPORT_PREFIXES)


def _body(text: str) -> list[str]:
    """Return the code lines of `text`, stripped — the unit the conservation guard compares.

    ⚑ BLANK AND COMMENT LINES ARE NOT CONSERVED, DELIBERATELY. Excising a definition necessarily
    disturbs the blank-line runs around it, and `ruff --fix` rewrites import blocks wholesale. A
    guard that demanded those match would fire on every correct trim and be switched off — which is
    how a guard stops catching anything. What must be conserved is CODE.
    """
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def conserved(source: str, trimmed: str, extracted: str) -> tuple[str, ...]:
    """Return the reasons this trim loses or invents content — empty when nothing moved wrongly.

    ⚑⚑⚑ THIS IS `split_lemmas`' GUARD, AND ITS DUTY IS THAT NOTHING VANISHES SILENTLY. Seven
    distinct silent-deletion bugs were caught by the Agda-side form of exactly this comparison. The
    check is a MULTISET one over code lines: every line of the original must appear in the trimmed
    text or the extracted text, and neither may invent a line the original did not hold.

    ⚑⚑ A MULTISET, NOT A SET, because a duplicated line is how an excision that ran twice looks. And
    both directions are load-bearing: ORIGINAL⊆PARTS catches deletion, PARTS⊆ORIGINAL catches a
    transformer that REWROTE a line while moving it — the failure a line-count assertion cannot see.

    ⚑ IMPORT LINES ARE EXEMPT IN THE LOSING DIRECTION ONLY. `ruff --fix` legitimately REMOVES a
    now-unused import — that is the whole reason this pipeline exists — and may re-sort the block.
    What it must never do is drop a line of BODY. So an import may vanish and may not appear.

    ⚑⚑ THE `__main__` BLOCK IS NOT A SECOND EXEMPTION. When the trim takes it, its lines land in
    `extracted` and are conserved exactly like a trimmed def's — which is what keeps this guard able
    to catch a block that was dropped rather than moved. The one thing an exemption here would have
    bought is the one thing the both-baselines incident proves must not be bought.

    ⚑⚑⚑ AND `source` MUST BE THE AUTOFIXED ORIGINAL, NOT THE RAW ONE — WHICH THIS GUARD GOT WRONG
    UNTIL 2026-09-01, IN A WAY THAT ONLY SHOWS ON A DIRTY FILE. `consider` compared the FIXED
    trimmed text against the RAW original, so every fix ruff applies for reasons unrelated to the
    trim read here as a line that vanished. On a clean target that difference is empty and the
    guard was right by accident. On `scripts/run_selftests.py` (1,832 findings) ruff reflows
    string literals and `re.compile` continuations, and the guard reported eleven "vanished"
    lines — none deleted, all REWRAPPED — **and it reported the SAME eleven whichever definition
    was named**, which is the tell: a guard whose complaint does not move with its input is not
    measuring its input. Three separate trims (`reach_ratchet` alone, four defs together,
    `_selftest` alone) produced byte-identical refusals.

    ⚑⚑ THE CONFOUND IS RUFF, SO THE FIX IS TO PUT RUFF ON BOTH SIDES. Comparing fixed-trimmed
    against fixed-original isolates the TRIM's effect, which is the only thing this guard has an
    opinion about. It does not weaken the check — a genuinely deleted body line is still absent
    from the fixed text — it stops the check attributing ruff's work to the trim.
    """
    original = _body(source)
    parts = _body(trimmed) + _body(extracted)
    reasons: list[str] = []
    for line in sorted(set(original)):
        lost = original.count(line) - parts.count(line)
        if lost > 0 and not _is_import(line):
            reasons.append(f"{lost} occurrence(s) of {line!r} vanished")
    for line in sorted(set(parts)):
        gained = parts.count(line) - original.count(line)
        # ⚑⚑⚑ AN IMPORT IS EXEMPT IN BOTH DIRECTIONS, AND THE ONE-WAY FORM REFUSED A CORRECT TRIM.
        # The rule above was written against ruff DELETING a now-unused import, so it allowed an
        # import to vanish and never to appear. Measured on `type_scope`: its only use of
        # `suite_emit` is the cases' own dispatch, so after the trim ruff NARROWS
        # `from substrate import corpus, mypy_census, suite_emit` to
        # `from substrate import corpus, mypy_census` — which vanishes AND appears, as one edit.
        #
        # ⚑⚑ THE GUARD'S DUTY IS BODY LINES, AND THAT IS UNCHANGED. A rewritten import is exactly
        # what `_autofix` exists to produce; treating its output as invented content makes the
        # pipeline accuse itself. A genuinely invented BODY line is still reported, which is the
        # property the seven silent-deletion bugs were caught by.
        if gained > 0 and not _is_import(line):
            reasons.append(f"{gained} occurrence(s) of {line!r} appeared from nowhere")
    return tuple(reasons)


def missing(names: tuple[str, ...], taken: tuple[str, ...]) -> tuple[str, ...]:
    """Return the requested names that no top-level definition carried.

    ⚑⚑ A NAME NOT FOUND IS A REFUSAL, NEVER A NO-OP. Trimming four of five requested names produces
    a module that reads perfectly and is wrong, and the caller — who is about to delete the sibling
    they moved these into — has no way to see the fifth stayed behind. Same shape as the `rglob` on
    a non-directory that reported a silent zero: an unsupported REQUEST rendered as an empty result.
    """
    return tuple(name for name in names if name not in taken)


def consider(path: Path, names: tuple[str, ...]) -> Trim:
    """Return what trimming `names` out of `path` would produce, without writing anything.

    ⚑ THE GUARD RUNS BEFORE THE CHECKER, and the order is the point. A checker answers *would this
    land*; the guard answers *is this the right file*. A trim that dropped the wrong definition is
    perfectly lintable, so a CLEAN report on an unguarded excision is precisely the plausible-and-
    wrong output this refuses to write.

    ⚑⚑ AND THE GUARD RUNS AGAINST THE FIXED TEXT, NOT THE RAW TRANSFORM OUTPUT. What lands is what
    `ruff --fix` leaves, so that is what must be shown to conserve the original — guarding the
    pre-fix text would verify a document that is not the one written. `_fixed` re-reads the staged
    file rather than reconstructing it, which is what keeps the checked bytes the written bytes.

    ⚑⚑⚑ AND THE LABEL RAISED FROM A BORROWING CHECKOUT (gate-G245 / gate-G257 / gate-G264). `main`
    resolves the operand against the CALLER's cwd — correctly, since a peer naming `substrate/x.py`
    means THEIR file — and this line then measured it against SUBSTRATE's root, so the tool died
    before it could refuse or report anything. It was invisible to a bare run for a whole arc,
    because without operands `main` prints usage and never reaches here: the UNMEASURABLE verdict
    was about the invocation, never about the site.

    ⚑ `tree_root.label` returns a path OUTSIDE the tree whole rather than raising, so a foreign
    operand now yields a row naming the file the caller actually meant.
    """
    relpath = tree_root.of(corpus.ROOT).label(path)
    source = path.read_text(encoding="utf-8")
    trimmed, extracted, taken, guard_refusal = _excised(source, names)
    absent = missing(names, taken)
    if absent:
        return Trim(
            relpath=relpath,
            verdict=UNSAFE,
            names=taken,
            removed=extracted,
            report="no top-level definition named: " + ", ".join(absent),
            source=source,
        )

    # ⚑⚑ A DISPATCH BLOCK THAT OUTLIVES THE TRIM IS REFUSED BEFORE THE CHECKER, on the same footing
    # as an absent name. Both are claims about CONTENT — the excision as asked is not the right one
    # — and neither is anything the checker has an opinion about. Letting it fall through would
    # report the stranded reference as a lint FINDINGS, naming the symptom and hiding the cause:
    # the reader would hunt a lint fix when what they need is to rewrite their entry point.
    if guard_refusal:
        return Trim(
            relpath=relpath,
            verdict=UNSAFE,
            names=taken,
            removed=extracted,
            report=guard_refusal,
            source=source,
        )

    fixed = record_migrate._fixed(trimmed)  # noqa: SLF001 — the pipeline this mode specialises
    # ⚑⚑⚑ THE TRIM IS GUILTY ONLY IF BOTH BASELINES ACCUSE IT. Ruff rewrites lines for reasons
    # that have nothing to do with the excision, and it rewrites them on ONE side of whichever
    # single comparison is chosen — so each baseline alone produces a class of false refusal, and
    # they are DIFFERENT classes. Against the RAW original, every fix ruff applied to the trimmed
    # text reads as a line that vanished (this is what refused `run_selftests.py` eleven times
    # over, identically, whichever definition was named). Against the FIXED original, a line ruff
    # rewrote in the baseline but NOT in the still-unfixed `extracted` text reads as vanished-and-
    # invented — which is what this module's own `Path(".")` case caught within minutes of the
    # one-sided fix landing. A real deletion is absent under both; a reflow is absent under at
    # most one. Intersecting the two accusations is what separates them.
    reasons = tuple(
        set(conserved(source, fixed, extracted))
        & set(
            conserved(
                record_migrate._fixed(source),  # noqa: SLF001 — same pipeline
                fixed,
                extracted,
            )
        )
    )
    if reasons:
        return Trim(
            relpath=relpath,
            verdict=UNSAFE,
            names=taken,
            removed=extracted,
            report="conservation guard REFUSED:\n" + "\n".join(reasons),
            source=fixed,
        )

    # ⚑⚑ THE ORIGIN'S PATH IS NAMED SO A PATH-KEYED IGNORE STILL APPLIES. Staged under a fixed
    # repo-root name, a trim of `substrate/type_scope.py` reported `S603` — which `pyproject`
    # exempts for exactly that path, and which the file on disk does not carry (gate-G334).
    report = record_migrate._check(trimmed, corpus.ROOT / relpath)  # noqa: SLF001 — house checker
    verdict = record_migrate._verdict(report)  # noqa: SLF001 — the shared three-state lattice
    return Trim(
        relpath=relpath,
        verdict=verdict,
        names=taken,
        removed=extracted,
        report=report,
        source=fixed,
    )


def render(trim: Trim) -> list[str]:
    """Render one trim's outcome, with its report bounded so it cannot bury the verdict."""
    header = (
        f"\n{trim.verdict:<9} {trim.relpath}  "
        f"({len(trim.names)} definition(s): {', '.join(trim.names)})"
    )
    out = [header]
    if trim.report.strip():
        out.extend(
            f"     {line}" for line in trim.report.splitlines()[: record_migrate.REPORT_LINES]
        )
    return out


def sibling_of(relpath: str) -> str:
    """Return the suite path a trimmed module's cases belong in."""
    return relpath.removesuffix(".py") + SUITE_SUFFIX


def top_level_bindings(source: str) -> set[str]:
    """Return every name the module's own body binds — defs, classes, and assignments.

    ⚑⚑ `_defined_name` COVERS DEFS AND CLASSES AND THAT IS NOT ENOUGH HERE. The cases also read
    module-level TABLES — `iface_bottom` has four — which are plain assignments, so a reader built
    only on the trim's partition would omit exactly the constants the suite needs imported back.
    Two questions, two readers: which statements can be TAKEN, and which names the module BINDS.
    """
    try:
        tree = cst.parse_module(source)
    except cst.ParserSyntaxError:
        return set()
    out: set[str] = set()
    for statement in tree.body:
        name = _defined_name(statement)
        if name is not None:
            out.add(name)
            continue
        if not isinstance(statement, cst.SimpleStatementLine):
            continue
        for small in statement.body:
            out.update(_small_bindings(small))
    return out


def _small_bindings(small: cst.BaseSmallStatement) -> set[str]:
    """Return the names one simple statement binds — assignment targets and import aliases.

    ⚑⚑⚑ AN IMPORT BINDS A NAME, AND OMITTING THAT BROKE A SPLIT. `iface_readers`' cases call
    `iface_infer.interface_of_src(...)`, and `iface_infer` is bound by `from substrate import
    iface_infer` — so a bindings reader covering only defs, classes and assignments left it out of
    the back-import and the suite died with `NameError: name 'iface_infer' is not defined`. The
    caller's docstring said *every name the module's own body binds* while the code enumerated
    three of the four ways to bind one.

    ⚑ SPLIT OUT BECAUSE THE GATE ASKED. Adding the fourth kind took `top_level_bindings` past its
    complexity limit — the per-file gate reading as a design signal rather than a ceiling: the
    statement-level question is its own, and the caller now only walks the module body.
    """
    if isinstance(small, cst.Assign):
        return {t.target.value for t in small.targets if isinstance(t.target, cst.Name)}
    if isinstance(small, cst.AnnAssign) and isinstance(small.target, cst.Name):
        return {small.target.value}
    if isinstance(small, (cst.Import, cst.ImportFrom)) and not isinstance(
        small.names, cst.ImportStar
    ):
        bound = (alias.asname.name if alias.asname else alias.name for alias in small.names)
        return {name.value for name in bound if isinstance(name, cst.Name)}
    return set()


def borrowed_imports(source: str, wanted: set[str]) -> tuple[str, ...]:
    """Return the origin's own import lines for the names in `wanted`, verbatim.

    ⚑⚑⚑ A NAME THE ORIGIN IMPORTED IS NOT PART OF ITS INTERFACE, AND THE CHECKER SAYS SO. Routing
    `iface_infer` through `from substrate.iface_readers import iface_infer` RUNS — the split suite
    scored 8/8 — and mypy refuses it: *module does not explicitly export attribute*. The code
    working is not the same as the import being legitimate (gate-G325).

    ⚑⚑ SO THE ORIGIN'S OWN STATEMENT IS RE-EMITTED RATHER THAN RECONSTRUCTED. `iface_infer` came
    from `from substrate import iface_infer`, and copying that line sends the sibling to the same
    source the origin used. Rebuilding the path from the bound name alone would be guesswork the
    origin's text already answers.

    ⚑ A STATEMENT IS TAKEN WHOLE WHEN IT BINDS ANY WANTED NAME, aliases included, so a multi-name
    import is not split into a form its author did not write. The sorter downstream normalises it.

    ⚑⚑⚑ AND THE WALK IS OVER THE WHOLE TREE, NOT `body`, BECAUSE AN IMPORT NESTS. `sandbox_connect`
    binds `DictRow` inside `if TYPE_CHECKING:`, so a reader iterating top-level statements alone
    never saw it — the split suite RAN at 7/7 and the gate refused the annotation with `F821
    Undefined name DictRow`. A conditional import is still the origin's own statement and still
    the honest source for the name.

    ⚑⚑⚑ AND A NESTED ONE KEEPS ITS GUARD, BECAUSE THE GUARD IS WHY IT WAS CORRECT. `DictRow` is
    used ONLY in an annotation and this generator emits `from __future__ import annotations`, so
    the name is never evaluated at runtime — which is exactly what `if TYPE_CHECKING:` encodes.
    Re-emitted flat it becomes a real import of a type-only name and ruff refuses it with `TC002
    Move third-party import into a type-checking block`. The line is returned WITH its guard so
    the context travels with the statement rather than being reconstructed downstream.
    """
    try:
        tree = cst.parse_module(source)
    except cst.ParserSyntaxError:
        return ()
    out: list[str] = []
    for statement in cst.matchers.findall(tree, cst.matchers.SimpleStatementLine()):
        if not isinstance(statement, cst.SimpleStatementLine):
            continue
        for small in statement.body:
            if not isinstance(small, (cst.Import, cst.ImportFrom)):
                continue
            if not _small_bindings(small) & wanted:
                continue
            line = tree.code_for_node(statement).strip()
            out.append(line if statement in tree.body else f"if TYPE_CHECKING:\n    {line}")
    return tuple(out)


def imported_bindings(source: str) -> set[str]:
    """Return only the names the module's body binds by IMPORTING them.

    ⚑ THE TWO HALVES OF `top_level_bindings` HAVE DIFFERENT HOMES, which is the whole of
    gate-G325. A def or assignment belongs to the origin and is imported FROM it; an imported name
    belongs to its own source and must be imported from THERE. One set could not express that.

    ⚑⚑ THE WALK DESCENDS, MATCHING `borrowed_imports`. A `TYPE_CHECKING` import binds a name one
    level below `body`, and the two readers must agree about which names are imported or a name
    lands in neither population — visible in neither import and undefined in the sibling.
    """
    try:
        tree = cst.parse_module(source)
    except cst.ParserSyntaxError:
        return set()
    out: set[str] = set()
    for statement in cst.matchers.findall(tree, cst.matchers.SimpleStatementLine()):
        if not isinstance(statement, cst.SimpleStatementLine):
            continue
        for small in statement.body:
            if isinstance(small, (cst.Import, cst.ImportFrom)):
                out.update(_small_bindings(small))
    return out


def reached_names(trim: Trim) -> tuple[str, ...]:
    """Return the origin's names the extracted cases read and no longer define themselves.

    ⚑⚑⚑ THIS IS WHAT THE BACK-IMPORT MUST NAME, AND GETTING IT WRONG IS SILENT. A sibling written
    with `import *` looks correct, imports cleanly, and dies at its first arm on every PRIVATE
    helper that stayed behind — the star applies an underscore filter (gate-G321, measured:
    `NameError: name '_named' is not defined`). An EXPLICIT `from m import _named` binds it.

    ⚑⚑⚑ AND THE FIRST CUT INTERSECTED WITH NOTHING, WHICH IS WHY IT EMITTED AN UNPARSEABLE FILE.
    Taking every bare `Name` the cases read put `False`, `None`, `bool`, `len`, `__doc__` and the
    cases' OWN LOCALS (`check`, `got`, `fn`) into the import list — a SyntaxError, caught before
    any checker could run, so the docstring's claim that *the checker filters these* was false.
    A reader answering *what names appear* was asked *what names must be imported*.

    ⚑⚑ SO THE POPULATION IS AN INTERSECTION WITH THE ORIGIN'S TOP-LEVEL BINDINGS, which admits no
    builtin, keyword or local BY CONSTRUCTION — rather than by a filter list that would need
    extending the first time a case used a builtin nobody anticipated.

    ⚑ A NAME THE CASES TAKE WITH THEM IS NOT REACHED. `trim.names` moves to the sibling and is
    defined there, so importing it back would shadow the local definition with an origin that no
    longer has one.
    """
    try:
        tree = cst.parse_module(trim.removed)
    except cst.ParserSyntaxError:
        return ()
    used = names_used(tree) - set(trim.names)
    origin = (corpus.ROOT / trim.relpath).read_text(encoding="utf-8")
    # ⚑⚑ THE IMPORTED HALF IS SUBTRACTED, NOT INCLUDED. Those names are bound in the origin at
    # runtime and are NOT part of its interface, so importing them through it is refused by the
    # checker even though it runs (gate-G325). `borrowed_imports` re-emits the origin's own line
    # for each, which sends the sibling to the same source the origin used.
    return tuple(sorted((used & top_level_bindings(origin)) - imported_bindings(origin)))


def reached_borrowed(trim: Trim) -> tuple[str, ...]:
    """Return the origin's import lines the extracted cases still need."""
    try:
        tree = cst.parse_module(trim.removed)
    except cst.ParserSyntaxError:
        return ()
    origin = (corpus.ROOT / trim.relpath).read_text(encoding="utf-8")
    wanted = (names_used(tree) - set(trim.names)) & imported_bindings(origin)
    return borrowed_imports(origin, wanted)


def sibling_text(trim: Trim, reached: tuple[str, ...], borrowed: tuple[str, ...] = ()) -> str:
    """Return the sibling suite's full source — header, imports, and the extracted cases.

    ⚑⚑⚑ THE EXTRACTED TEXT IS A BARE BODY AND A MODULE IS NOT. `Trim.removed` is the definitions
    that came out, with no licence header, no imports and no dispatch — writing it verbatim
    produces a file that does not run and does not pass the gate. The prologue is what makes the
    half a MODULE rather than a fragment.

    ⚑⚑ THE BACK-IMPORT IS EXPLICIT AND NEVER A STAR. That is gate-G321's repair: a wildcard drops
    the private helpers the cases depend on, and an explicit list carries them.

    ⚑⚑⚑ AND IT CARRIES TWO IMPORT POPULATIONS WITH DIFFERENT HOMES. `reached` names what the ORIGIN
    DEFINES and comes from the origin; `borrowed` is the origin's OWN import lines, re-emitted
    verbatim for names it merely imported — those are not part of its interface, so routing them
    through it is refused by the checker even though it runs (gate-G325).

    ⚑ `import sys` IS EMITTED ONLY IF THE BORROWED LINES DO NOT ALREADY CARRY IT. The dispatch tail
    needs it and most origins import it too, so a hardcoded line produced `F811 Redefinition of
    unused sys` the first time both appeared.

    ⚑ THE CASES ARE NOT REWRITTEN, ONLY RE-HOMED. The extracted text lands verbatim, so the
    conservation guard's line comparison stays meaningful across the move.
    """
    module = Path(trim.relpath).stem
    back = (
        (
            f"from substrate.{module} import (\n"
            + "".join(f"    {name},\n" for name in reached)
            + ")\n"
        )
        if reached
        else ""
    )
    lines = list(borrowed)
    if not any(line == "import sys" or line.startswith("import sys ") for line in lines):
        lines.insert(0, "import sys")
    # ⚑⚑ A GUARDED LINE NEEDS THE NAME ITS GUARD TESTS. `TYPE_CHECKING` is never in `wanted` —
    # the cases do not reference it, only the origin's guard does — so re-emitting a conditional
    # import without it would produce a file whose guard is itself undefined.
    if any(line.startswith("if TYPE_CHECKING:") for line in lines):
        lines.insert(0, "from typing import TYPE_CHECKING")
    return (
        f"#!/usr/bin/env python3\n"
        f"# SPDX-License-Identifier: Apache-2.0\n"
        f"# Copyright (c) 2026 Mike Mol\n"
        f'"""The cases for `substrate.{module}`, split out of its tail.\n'
        f"\n"
        f"⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,\n"
        f"moved verbatim — the conservation guard checked that every line landed in exactly\n"
        f"one of the two halves, which is the property a retype cannot offer.\n"
        f"\n"
        f"⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the\n"
        f"origin's private helpers, which the cases reach (gate-G321). A name the origin only\n"
        f"IMPORTED is taken from its own source instead (gate-G325).\n"
        f'"""\n'
        f"\n"
        f"from __future__ import annotations\n"
        f"\n" + "".join(f"{line}\n" for line in lines) + f"\n"
        f"{back}"
        f"\n"
        f"\n"
        f"{trim.removed.strip()}\n"
        f"\n"
        f"\n" + _dispatch_tail(trim)
    )


def _dispatch_tail(trim: Trim) -> str:
    """Return the sibling's `__main__` dispatch, or nothing when the cases brought their own.

    ⚑⚑⚑ THE ORIGIN'S GUARD IS OFTEN PART OF THE TAIL, AND APPENDING A SECOND ONE DUPLICATED IT IN
    FOUR SIBLINGS. When nothing survives a module's `__main__` block it travels WITH the cases, so
    the extracted text already ends in a dispatch — and the template then added its own. Measured:
    `wg_row_selftest` ends with two byte-identical guards, as do `iface_bottom`, `iface_infer` and
    `stub_declines`. Unreachable and harmless at runtime, which is why the gate passed it and
    nothing noticed for four splits.

    ⚑⚑ `sys.exit` HERE IS SAFE AND ONLY HERE. Inside `if __name__ == "__main__":` the block never
    runs on import, which is the house pattern (`suite_run` does the same). The operator's rule is
    about a REACHABLE `sys.exit`: raising `SystemExit` on an importable path takes the exit
    decision away from whoever imported the module. That is why the branch inside `main` is NOT
    rewritten to `sys.exit` — it would be reachable — and why the refusal for `iface_cost` and
    `sandbox_connect` stands.

    ⚑ THE ENTRY NAME COMES FROM `trim.names`, never a constant: `wg_row` spells it `selftest`
    where the rest use `_selftest` (gate-G328).
    """
    if _MAIN in trim.removed:
        return ""
    entry = next((name for name in trim.names if name.endswith("selftest")), "")
    if not entry:
        return ""
    return (
        f'if __name__ == "__main__":\n'
        f'    sys.exit({entry}() if "--selftest" in sys.argv '
        f"or len(sys.argv) == 1 else 0)\n"
    )


def summary(trim: Trim, *, applied: bool, sibling: str = "") -> list[str]:
    """Render what happened, keeping UNSAFE and UNKNOWN distinct from FINDINGS.

    ⚑ THE THREE REFUSALS ARE PAID DOWN BY DIFFERENT WORK, so they are never collapsed. FINDINGS is
    a lint result; UNSAFE is a claim about CONTENT; UNKNOWN is a fact about the environment. Only
    the first is fixed by editing the module.

    ⚑⚑ AND BOTH HALVES ARE NAMED WHEN BOTH ARE WRITTEN. A trim that reported only the module it
    emptied read as a completed split while the cases were gone — `iface_bottom` went from 38/38
    to a silent exit, and the one-sided line still said `✓ WROTE` (gate-G320).
    """
    out: list[str] = []
    if trim.verdict == UNSAFE:
        out.append(
            "   ⚑ UNSAFE means the CONSERVATION GUARD refused — content would have been "
            "lost or invented. Nothing about the checker is claimed."
        )
    if trim.verdict == record_migrate.UNKNOWN:
        out.append(
            "   ⚑ UNKNOWN means the CHECKER could not run — a fact about this "
            "environment, never a clean bill."
        )
    if not applied:
        out.append("   (nothing written)")
        return out
    out.append(f"   ✓ WROTE {trim.relpath}")
    out.append(
        f"   ✓ WROTE {sibling}"
        if sibling
        else "   ⚑ THE CASES WERE NOT RE-HOMED — this is a TRIM, not a split."
    )
    return out


def main(argv: list[str]) -> int:
    """Trim the named definitions out of one module, writing only if it passes clean."""
    apply = "--apply" in argv
    if not apply and "--dry-run" not in argv:
        # ⚑ INTENT IS STATED, NEVER DEFAULTED — the house contract for a mutating tool. A
        # default-dry silently does nothing when you meant to write; a default-apply writes when
        # you meant to look.
        sys.stderr.write(__doc__ or "")
        return 2

    positional = [a for a in argv if not a.startswith("-")]
    if not positional:
        sys.stderr.write("module_trim: name a module and the definitions to trim\n")
        return 2
    names = tuple(positional[1:])
    if not names:
        sys.stderr.write(f"module_trim: {NOTHING_ASKED}\n")
        return 2

    trim = consider(Path(positional[0]).resolve(), names)
    for line in render(trim):
        sys.stdout.write(line + "\n")

    # ⚑⚑⚑ AN EXISTING SIBLING IS A REFUSAL, NOT AN OVERWRITE. Both halves are written together, so
    # a sibling already holding cases would be REPLACED by this one — the loss this whole path
    # exists to prevent, arriving through the repair for it.
    sibling = sibling_of(trim.relpath)
    if apply and trim.writable and (corpus.ROOT / sibling).exists():
        sys.stdout.write(f"   ⚑ REFUSED: {sibling} already exists — it would be overwritten\n")
        return 1

    # ⚑⚑⚑ THE SIBLING IS CHECKED BEFORE EITHER HALF LANDS, AND ITS ABSENCE SHIPPED TWO BROKEN
    # SUITES. `record_migrate` stages, checks and writes the TRIMMED ORIGIN; nothing did that for
    # the generated sibling, so a `--selftest` branch lifted out of `main` — carrying `return
    # _selftest()` — was written to module level, where `return` is a SyntaxError. Both halves were
    # on disk before anything noticed, and the conservation guard was satisfied because the lines
    # WERE conserved: they landed in the extracted text. Conserved is not the same as valid.
    #
    # ⚑⚑ A GUARD BRANCH AND A `main` BRANCH ARE NOT INTERCHANGEABLE, which is what this catches. A
    # `__main__` guard calls `sys.exit(_selftest())`; a function body says `return _selftest()`.
    # The branch CONTENT decided which were tail (gate-G324) and the branch's STATEMENTS decide
    # whether it can be re-homed at all — two questions the earlier reading collapsed.
    #
    # ⚑⚑⚑ AND THE PARSER MUST BE CPYTHON'S, NOT libcst's. A first cut checked with
    # `cst.parse_module` and it ACCEPTED the broken sibling — libcst is more permissive about a
    # module-level `return` than the interpreter that has to run the file. A validity check
    # answered by a tool laxer than the runtime certifies exactly the files that will fail, so the
    # builtin `compile` is used: the same front end that raised the error in the first place.
    #
    # ⚑⚑ THE CHECK RUNS IN BOTH MODES, NOT ONLY UNDER `--apply`. A dry run that reported CLEAN for
    # a split the apply then refuses is a preview of a different operation — the one shape a
    # preview must never have.
    if trim.writable:
        try:
            compile(
                sibling_text(trim, reached_names(trim), reached_borrowed(trim)), sibling, "exec"
            )
        except SyntaxError as exc:
            sys.stdout.write(
                f"   ⚑ REFUSED: the generated {sibling} does not parse — {exc}\n"
                f"     The extracted cases are not re-homable as written.\n"
            )
            return 1

    written = apply and trim.writable
    if written:
        # ⚑⚑ THE SIBLING IS WRITTEN FIRST, so a failure between the two leaves the cases present in
        # BOTH halves rather than in neither. Duplicated cases are visible and recoverable; a
        # module emptied into nothing is the state gate-G320 records.
        #
        # ⚑⚑⚑ AND THE SORTER DECIDES THE IMPORT ORDER, NOT THIS TEMPLATE. A first cut emitted the
        # back-import in plain `sorted()` order and ruff refused it with `I001`: its collation puts
        # `_BLANK_STOP` before `PARSED` where lexicographic order does the reverse. Two earlier
        # splits passed only because their name sets never exposed the difference — right by
        # accident. `record_migrate._autofix`'s own docstring names this bug class exactly: *an
        # isort reimplementation growing inside a codemod, while the real sorter ran in the very
        # next step*. So the written file is handed to the real sorter instead of ordered here.
        target = corpus.ROOT / sibling
        target.write_text(
            sibling_text(trim, reached_names(trim), reached_borrowed(trim)), encoding="utf-8"
        )
        record_migrate._autofix(target)  # noqa: SLF001 — the shared pipeline, called not rebuilt
        (corpus.ROOT / trim.relpath).write_text(trim.source, encoding="utf-8")
    for line in summary(trim, applied=written, sibling=sibling if written else ""):
        sys.stdout.write(line + "\n")
    return 0 if trim.writable or not apply else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
