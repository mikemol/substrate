#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A DRIFT GATE over module-level ASSIGNMENT types — the slot kind no census could see.

⚑⚑⚑ WHAT THIS GATES, AND WHY IT IS THE HALF THAT CAN SHIP. The interface arc wants a drift
gate over a module's whole derived interface, and it cannot have one yet: `iface_readers
--eligible` reports 0 of 5 repo-local stubs generatable, because `stubgen` writes `Incomplete`
(= `Any` under this repo's `disallow_any_expr`) wherever the source states nothing. Generating
those stubs today would DELETE type information the authored `.pyi` states. But the interface
has two halves and they cost differently, measured rather than assumed:

  * an ASSIGNMENT's type is a query over the DEFINING MODULE'S OWN TEXT. Measured:
    `iface_construct --module scratch/agda_lex.py` resolves 16 of 17 in 1.5s; all five
    stub-backed modules together resolve in 3.4s.
  * a PARAMETER's type is a query over the WHOLE CORPUS — every call site, transitively.
    Measured: `iface_dataflow --module scratch/agda_lex.py` does not finish in 600s (exit 124).

So the assignment half is gate-cheap and the function half is not, and this gate takes only the
half it can afford. ⚑ THE SPLIT IS THE DESIGN, NOT A COMPROMISE: merging them would put a 3.4s
answer behind a 600s+ one and the gate would be disabled the first time someone waited for it.

⚑⚑⚑ WHAT A GREEN VERDICT ACTUALLY ASSERTS — AND IT IS NARROWER THAN "THESE TYPES ARE CORRECT".
State it plainly, because this session recorded four greens that were facts about their
instrument rather than the tree. A green here asserts EXACTLY:

    For every module-level assignment in the census population, the type
    `iface_construct` derives TODAY is byte-identical to the type it derived when the block
    was last synced — and the SET of assignments is unchanged.

That is a DIFFERENTIAL claim about a DERIVATION, not a claim about truth. Specifically:

  * It does NOT assert the derived types are correct. A derivation that was wrong at sync time
    stays wrong and stays green. The gate catches CHANGE, not error.
  * It does NOT assert agreement with the authored `.pyi`. Three of these assignments are
    stubbed `object` while the derivation says `re.Pattern[str]`; the gate is green on that
    disagreement because agreement with a stub is a different question, asked by
    `--vs-stubs` and deliberately ADVISORY (see below).
  * An UNRESOLVED slot is carried in the block as UNRESOLVED. So a green also asserts that
    what the reader could NOT type it still cannot type — a slot becoming resolvable is drift
    and fires the gate, which is correct: that is a real change in what the tree states.
  * A slot whose expression is edited so it derives a DIFFERENT type fires. That is the
    defect class the gate is for.

⚑⚑ AND THE ONE THING IT ASSERTS THAT IS NOT MERELY DIFFERENTIAL: the population is derived
from `iface_readers.repo_local_stubs`, which DISCOVERS its members from `stubs/*.pyi`. So a
green also asserts no stub-backed module was added or removed unnoticed. That is a genuine
existence claim, and it is the only one here.

⚑⚑ THE ORACLE IS PART OF THE INSTRUMENT, WHICH BOUNDS THE GREEN FURTHER. `iface_construct`
answers UNRESOLVED when mypy is absent or times out, and it says so rather than guessing. But
this gate compares STATUSES, so a machine without the oracle derives UNRESOLVED where the
committed block says COMPUTED and the gate fires — reporting a fact about THAT MACHINE as
drift in the tree. That is the honest failure direction (a false STALE, never a false fresh),
and it is named here rather than papered over.

⚑⚑⚑ THE FIXTURE QUESTION, ANSWERED STRUCTURALLY RATHER THAN BY INSPECTION. Ⓝ104f records a
live defect where a slot witnessed only by `tests/` fixtures reads as a confident COMPUTED.
ASSIGNMENTS CANNOT DRAW A FIXTURE WITNESS, and the reason is structural rather than a filter
someone remembered to apply: `iface_construct.resolve_module` reads only the defining module's
own `ast.Module` — its assignment expressions and its import block — and asks the oracle about
THOSE. It never enumerates call sites, so `corpus.py_files` never enters the walk and a
`tests/` file has no position from which to become evidence. This is the same property
`iface_bottom` states for its own sources ("EVERY SOURCE HERE READS THE DEFINING MODULE'S OWN
TEXT... none of them reaches a CALL SITE"), and it holds here for the same reason. A fixture
could only affect this gate by being a stub-backed module itself.

⚑⚑ `--vs-stubs` IS ADVISORY AND MUST STAY SO, BECAUSE THE STUB IS SOMETIMES RIGHT. The
comparison is worth printing and must never gate, and `KNOWN_PRODUCERS` is why: the source
says `tuple[tuple[str, str], tuple[str, str], tuple[str, str]]` — the derivation reading a
three-element display — while `stubs/tsdbprobe.pyi` says `tuple[tuple[str, str], ...]`. The
STUB IS BETTER. Arity is not part of that contract, and a generator that emitted the derived
spelling would over-specify: appending a fourth producer would break every consumer typed
against it. A gate that demanded agreement would demand the WRONG answer here.

Usage: check_assign_types.py --check | --sync | --vs-stubs | --selftest
"""

from __future__ import annotations

import ast
import difflib
import sys
from pathlib import Path

from substrate import iface_construct, iface_readers

REPO = Path(__file__).resolve().parent.parent

CENSUS_MD = REPO / "scripts" / "assign_census.md"
BEGIN = "--- BEGIN assign-census ---"
END = "--- END assign-census ---"

# How the census file is named back to the reader in every message it appears in.
_REL = "scripts/assign_census.md"

# The header the file carries when `--sync` has to create it. Everything between the markers
# is derived; everything outside them is this preamble and is never regenerated.
_PREAMBLE = """# Module-level assignment types — a GENERATED census

⚑ DO NOT EDIT BETWEEN THE MARKERS. This block is derived by
`scripts/check_assign_types.py --sync` from `substrate/iface_construct.py`, which reads each
module's own assignment expressions and asks mypy to eliminate the constructor's Pi type at
those arguments. `--check` refuses a commit whose derived block differs from the committed one.

⚑ A GREEN `--check` ASSERTS A DIFFERENTIAL, NOT A TRUTH: the types derive the same way they
did at sync time, and the set of assignments is unchanged. It does NOT assert the types are
correct, and it does NOT assert they agree with `stubs/*.pyi` — see `--vs-stubs`, which is
advisory precisely because the stub is sometimes the better claim.

"""


class BlockError(Exception):
    """The host file or its marker pair is missing, duplicated or inverted.

    ⚑ A FACT ABOUT THE TREE, REPORTED AS ONE, rather than a traceback — the same choice
    `gate_census.BlockError` makes, and for the same reason: a malformed host is operator
    work with a named remedy, not a crash.
    """


def population() -> list[tuple[str, Path]]:
    """Return the census population — every stub-backed repo-local module, discovered.

    ⚑⚑ DISCOVERED, NEVER LISTED. `iface_readers.repo_local_stubs` derives the roster from
    `stubs/*.pyi` paired against `scratch/` and `scripts/`, so adding a stub extends the
    census with no edit here. A hand-written roster is the frozen-allowlist shape this repo's
    policy rule refuses, and it is also what would let a new stub-backed module enter the tree
    ungated while the gate stayed green.
    """
    return iface_readers.repo_local_stubs(REPO)


def rows_for(source: Path) -> list[tuple[str, str, str]]:
    """Return (name, status, type) for every module-level assignment in one module.

    ⚑ THE UNRESOLVED ONES ARE CARRIED, NOT DROPPED. A slot the reader cannot type is part of
    what the block asserts: if it becomes typeable the tree changed, and that is drift worth
    reporting. Dropping them would make the gate silent about exactly the transition the
    derivation exists to achieve.
    """
    try:
        tree = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return []
    return [
        (r.name, r.status, r.type_name) for r in iface_construct.resolve_module(tree, str(source))
    ]


def render_block() -> str:
    """Render the census body — one line per assignment, in source order, module by module."""
    out: list[str] = []
    for module, source in population():
        rows = rows_for(source)
        rel = source.relative_to(REPO)
        computed = sum(1 for _n, s, _t in rows if s == "COMPUTED")
        # ⚑ A BLANK LINE AFTER THE HEADING, because the block is markdown and the tree's
        # markdown linter (MD022) requires headings to be surrounded by them. A generated
        # artifact that a linter flags is one a reader is invited to hand-edit, which is the
        # one thing the markers exist to prevent.
        out.append(f"\n## {module}  ({rel})")
        out.append("")
        out.append(f"{computed} of {len(rows)} assignment(s) resolved from the module's text.")
        out.append("")
        for name, status, type_name in rows:
            shown = type_name or "-"
            out.append(f"    {status:10s} {name}: {shown}")
    return "\n".join(out)


def _span(src: str) -> tuple[int, int]:
    """Return the offsets between the marker pair, or name what is wrong with the host.

    ⚑ THREE DISTINCT MALFORMATIONS, THREE DISTINCT MESSAGES. A missing pair, a duplicated
    marker and an inverted pair are different operator errors with different remedies, and
    collapsing them into one "malformed" would leave the reader to find which by eye.
    """
    i, j = src.find(BEGIN), src.find(END)
    if i < 0 or j < 0:
        raise BlockError(
            "no marker pair in " + _REL + " — run "
            "`python3 scripts/check_assign_types.py --sync` to create it."
        )
    if src.count(BEGIN) != 1 or src.count(END) != 1:
        raise BlockError("duplicated markers in " + _REL + " — exactly one of each is required.")
    if j < i + len(BEGIN):
        raise BlockError("inverted markers in " + _REL + " — the end precedes the begin.")
    return (i + len(BEGIN), j)


def splice(src: str, body: str) -> str:
    """Replace whatever sits between the markers with `body`."""
    a, b = _span(src)
    return src[:a] + "\n" + body + "\n" + src[b:]


def current_body(src: str) -> str:
    """Return what currently sits between the markers."""
    a, b = _span(src)
    return src[a:b]


def _host() -> str:
    """Return the census file's text, or the empty scaffold when it does not exist yet."""
    try:
        return CENSUS_MD.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _PREAMBLE + BEGIN + "\n" + END + "\n"


def cmd_sync() -> int:
    """Rewrite the generated block — the paydown counterpart every drift gate here carries."""
    CENSUS_MD.write_text(splice(_host(), render_block()), encoding="utf-8")
    total = sum(len(rows_for(s)) for _m, s in population())
    sys.stdout.write(
        f"check_assign_types --sync: wrote {total} assignment(s) across "
        f"{len(population())} module(s) to {_REL}.\n"
    )
    return 0


def cmd_check() -> int:
    """DRIFT GATE — exit 1 unless the committed block is what `--sync` would write.

    ⚑ A MISSING HOST EXITS 1, NOT 2, and the distinction is the one `sql_lift` records: an
    absent census is a fact about the TREE that leaves the gate unable to verify anything, so
    it must not read as a gate invoked badly. The refusal names the command that populates it.
    """
    if not CENSUS_MD.exists():
        sys.stderr.write(
            "check_assign_types --check: " + _REL + " does not exist — run "
            "`python3 scripts/check_assign_types.py --sync` to create it.\n"
        )
        return 1
    src = CENSUS_MD.read_text(encoding="utf-8")
    fresh = render_block()
    if splice(src, fresh) == src:
        sys.stdout.write(
            "check_assign_types --check: the assignment census in " + _REL + " is fresh.\n"
            "  ⚑ THIS ASSERTS A DIFFERENTIAL: every module-level assignment derives the same\n"
            "  type it did at sync time, and the set is unchanged. It does NOT assert the\n"
            "  types are correct, nor that they agree with `stubs/*.pyi`.\n"
        )
        return 0
    for line in difflib.unified_diff(
        current_body(src).splitlines(),
        ("\n" + fresh + "\n").splitlines(),
        fromfile=_REL + " (committed)",
        tofile="derived just now",
        lineterm="",
    ):
        sys.stdout.write(line + "\n")
    sys.stderr.write(
        "\ncheck_assign_types --check: the assignment census in " + _REL + " is STALE — run "
        "`python3 scripts/check_assign_types.py --sync`\n"
    )
    return 1


def stub_declarations(stub: Path) -> dict[str, str]:
    """Return `NAME: type` for every module-level annotated declaration in a `.pyi`.

    ⚑ ONLY `AnnAssign` AT MODULE LEVEL, because that is what a stub uses to declare a
    constant. A class body's annotations are a different surface and folding them in would
    compare a module constant against a field that merely shares its name.
    """
    try:
        tree = ast.parse(stub.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return {}
    return {
        node.target.id: ast.unparse(node.annotation)
        for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }


def disagreements() -> list[tuple[str, str, str, str]]:
    """Return (module, name, stub-type, derived-type) wherever the two differ."""
    out: list[tuple[str, str, str, str]] = []
    for module, source in population():
        declared = stub_declarations(REPO / "stubs" / f"{module}.pyi")
        for name, status, type_name in rows_for(source):
            got = type_name if status == "COMPUTED" else "<" + status + ">"
            want = declared.get(name)
            if want is not None and want != got:
                out.append((module, name, want, got))
    return out


def cmd_vs_stubs() -> int:
    """ADVISORY — print where the derivation and the authored stub disagree.

    ⚑⚑⚑ ADVISORY BY CONSTRUCTION, AND THE REASON IS A LIVE CASE RATHER THAN CAUTION. Exit 0
    whatever it measured, because a disagreement here does not say which side is wrong.
    `KNOWN_PRODUCERS` derives as a three-element tuple and is stubbed `tuple[tuple[str, str],
    ...]`; the STUB is right, because arity is not part of that contract and a generator must
    WIDEN a homogeneous tuple or it over-specifies. Meanwhile `DECL`/`SIG`/`IMPRE` are stubbed
    `object` where the derivation says `re.Pattern[str]`, and there the DERIVATION is right —
    the stub's own text records that weakening as an inability to VERIFY, which is debt the
    derivation retires. And `HEADER: _HeaderLike` is a DECISION, stated in the stub's prose,
    which no derivation should overturn. Three disagreements, three different verdicts, none
    of them mechanical — so this mode reports and a human decides.
    """
    rows = disagreements()
    for module, name, want, got in rows:
        sys.stdout.write(
            "    " + module + "." + name + ": stub `" + want + "`  derived `" + got + "`\n"
        )
    sys.stdout.write(
        f"check_assign_types --vs-stubs: {len(rows)} disagreement(s) between the authored "
        "stubs and the derivation.\n"
        "  ⚑ ADVISORY, AND A DISAGREEMENT NAMES NO WINNER. The stub is better where it WIDENS\n"
        "  a homogeneous tuple (arity is not part of the contract); the derivation is better\n"
        "  where the stub wrote `object` because it could not VERIFY; and a stub stating a\n"
        "  protocol is a DECISION no derivation may overturn. Exit 0 either way.\n"
    )
    return 0


def _malformation(src: str) -> str:
    """Return the FIRST word of the refusal a malformed host earns — the case's comparand."""
    try:
        _span(src)
    except BlockError as e:
        return str(e).split(" ", 1)[0]
    return "none"


def _cases_block() -> list[tuple[str, object, object]]:
    """Pin the splice round-trip, the drift detector, and the malformed-host messages."""
    scaffold = _PREAMBLE + BEGIN + "\n" + END + "\n"
    body = "\n## m  (x.py)\n1 of 1"
    synced = splice(scaffold, body)
    return [
        # ⚑ THE SPLICE ROUND-TRIPS AND IS IDEMPOTENT — a second sync over a synced file must
        # be a no-op, or the gate would fire on its own output forever.
        ("splice is idempotent", splice(synced, body), synced),
        ("the block round-trips through its markers", current_body(synced).strip(), body.strip()),
        # ⚑⚑ THE DISCRIMINATOR THAT MAKES THIS A GATE RATHER THAN A PRINTER: a CHANGED body
        # must NOT compare equal. Without this arm every case above passes on a splice that
        # ignored its argument, and the gate would read green against any drift at all. Both
        # directions are asked at once so neither a splice that always changes nor one that
        # never does can be green here.
        (
            "a changed body is drift and an unchanged one is not",
            [
                splice(synced, body + "\n    COMPUTED X: str") == synced,
                splice(synced, body) == synced,
            ],
            [False, True],
        ),
        # ⚑ THE THREE MALFORMATIONS ARE NAMED APART, asked as one mapping so a `_span` that
        # collapsed them into a single message fails here rather than in one omitted case.
        (
            "a malformed host is named by KIND, not crashed",
            {
                "missing": _malformation("nothing here"),
                "duplicated": _malformation(BEGIN + END + BEGIN + END),
                "inverted": _malformation(END + BEGIN),
                "well-formed": _malformation(synced),
            },
            {
                "missing": "no",
                "duplicated": "duplicated",
                "inverted": "inverted",
                "well-formed": "none",
            },
        ),
    ]


def _cases_population() -> list[tuple[str, object, object]]:
    """Pin the stub reader and the POSITIVE CONTROL over the live population.

    ⚑⚑⚑ THE POSITIVE CONTROL IS THE POINT. A census whose population came back empty renders
    exactly as legitimately as a correct one and would report every module fresh forever —
    `census-green-is-a-fact-about-the-census`, the shape that printed `0 tier(s)` beside a
    correct relation count. So the roster is asserted to FIRE, not merely to avoid crashing.
    """
    fix = REPO / "scripts" / "_assign_census_fixture.pyi"
    fix.write_text("A: int\nB = 1\nclass C:\n    D: str\n", encoding="utf-8")
    try:
        got = stub_declarations(fix)
    finally:
        fix.unlink(missing_ok=True)
    return [
        # ⚑⚑ THE STUB READER AND ITS DISCRIMINATORS. It must read a module-level `AnnAssign`
        # and must NOT read a bare assignment (`B`, which states no type) or a CLASS field
        # (`D`, a different surface that merely shares a namespace). A reader taking either
        # would compare a module constant against something that is not one.
        ("the stub reader takes module-level annotations only", got, {"A": "int"}),
        ("the population is discovered and non-empty", len(population()) > 0, True),
        # ⚑ AND IT ACTUALLY YIELDS ASSIGNMENTS, which is a SEPARATE failure: a roster of five
        # modules that each derived zero rows would also be silently green.
        ("the derived block is non-empty over that population", len(render_block()) > 0, True),
    ]


def _selftest() -> int:
    """Cases pinning the block round-trip, the drift detector, and the stub comparison."""
    cases = _cases_block() + _cases_population()
    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"check_assign_types selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Dispatch one mode; 2 on an unusable command line, 1 when a block cannot be read."""
    try:
        if "--selftest" in argv:
            return _selftest()
        if "--sync" in argv:
            return cmd_sync()
        if "--check" in argv:
            return cmd_check()
        if "--vs-stubs" in argv:
            return cmd_vs_stubs()
    except BlockError as e:
        sys.stderr.write("check_assign_types: " + str(e) + "\n")
        return 1
    sys.stderr.write(__doc__ or "")
    sys.stderr.write(
        "\nmodes:\n"
        "  --check     DRIFT GATE: exit 1 unless the committed census is current\n"
        "  --sync      regenerate the census block\n"
        "  --vs-stubs  ADVISORY: where the derivation and the authored stub disagree\n"
        "  --selftest  the guarded cases\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
