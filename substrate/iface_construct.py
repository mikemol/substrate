#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""EVALUATE a module-level assignment's constructor — the slot kind the engine had no name for.

⚑⚑⚑ THE LINE BETWEEN READING AND RUNNING, AND IT IS THE SPINE OF THIS FILE. `DECL =
re.compile(r"...")` states its type as plainly as `"x"` does, and the engine could not say so
— not because the information was absent but because `iface_dataflow.module_interface`
enumerates `mod.functions`, and a module-level assignment is not a function. It is invisible
to every reader in this toolkit, which is why `DECL`, `SIG` and `IMPRE` never appear in an
under-annotation census. Three tiers, and the third is a REFUSAL rather than a gap:

  C1 EVALUATE A CONSTRUCTOR'S TYPE  `re.compile(...)`, `Path(...)`, `frozenset({...})`.
     No execution. The type is the callee's declared return, APPLIED to these arguments.
  C2 CONSTANT-FOLD A PURE EXPRESSION  a literal display. Deterministic, no I/O, no side
     effects — and already the floor `iface_bottom.given_type` provides.
  C3 DO NOT EXECUTE  an expression whose value depends on the machine this runs on.

⚑⚑⚑ C3 IS NOT A LIMIT TO APOLOGISE FOR — IT IS THE SLOT WHERE A RUNTIME ORACLE ALREADY CAUGHT
A GUESS. `stubtest` observed `gen_build_makefiles.AGDA_JOBS` as `Literal['20']` and refuted a
draft that had read `int` from what the NAME means. Source-reading stops at C3 and this module
says so, rather than reaching one step further and manufacturing the claim the arc exists to
stop. ⚑ THE LIVE INSTANCE IS NOT THE ONE THAT MOTIVATED THE RULE: `AGDA_JOBS = "20"` is a
STRING LITERAL, so C2 types it without an oracle and without running anything. The rule stands
because the SHAPE it refuses is real — `ROOT = os.path.dirname(...(__file__))` in that same
module is machine-dependent — not because that particular assignment needed it.

⚑⚑⚑ A CONSTRUCTOR'S RETURN IS A PI TYPE, AND A NAME-KEYED TABLE IS THE NON-DEPENDENT
APPROXIMATION. `re.compile : (s : str | bytes) -> Pattern[Elem s]` — the return VARIES with
the argument's TYPE, so `re.compile(str)` is `Pattern[str]` and `re.compile(bytes)` is
`Pattern[bytes]`. That is not a quirk of one callee. Measured on this machine, each of these
eliminates differently by argument: `open(p)` is `TextIOWrapper[_WrappedBuffer]` while
`open(p, "rb")` is `BufferedReader[_BufferedReaderStream]`; `d.get(k)` is `int | None`,
`d.get(k, 0)` is `int`, and `d.get(k, "s")` is `int | str`. A `{name: type}` table is WRONG
for that whole family, not merely imprecise.

⚑⚑⚑ SO TYPESHED IS THE ORACLE, NOT A TABLE HERE. Typeshed encodes the dependency already — in
overloads, generics and Literal-discriminated returns — and mypy already applies it. Asking
mypy to reveal the assignment's own expression gets the Pi type ELIMINATED at these arguments,
correctly and for free. Re-deriving that by hand would reimplement typeshed badly and would be
wrong for exactly the family that motivated the feature. `iface_bottom.TYPED_RETURNS` stays
what it is — a fast constant-return floor — and this module neither extends nor duplicates it.

⚑⚑⚑ AND THE ORACLE'S SPELLINGS ARE TYPESHED'S, NOT THE TIDY ONES. `open()` reveals as
`_io.TextIOWrapper[_io._WrappedBuffer]`, not `TextIOWrapper`. A consumer must treat a revealed
type as an OPAQUE STRING carrying a `file:line`, never string-match it against the name it
expected — matching is how a reader talks itself back into the hand-kept table this module
exists to avoid.

⚑⚑ ONE BATCHED PROBE, NOT ONE RUN PER EXPRESSION, AND THE COST WAS MEASURED RATHER THAN
ASSUMED. Every expression gets its own LINE in a single probe file and the answers come back
keyed by line number. Measured: eleven expressions cost 6.0s under `--no-incremental`, 5.1s
cold into a fresh cache, and 0.53s against a warm one — so a per-expression `--no-incremental`
call is the worst choice available on both axes. The cache directory is therefore persistent
and shared, and `--no-incremental` is not used.

⚑⚑ THE PROBE CARRIES THE MODULE'S OWN IMPORTS, NEVER THE WHOLE MODULE. Without them `re` is
an undefined name and the oracle answers about a different program; with the whole module, its
existing type errors would arrive as findings about this slot.

⚑ AN UNAVAILABLE ORACLE IS UNRESOLVED, NEVER A GUESS, and its failure modes stay APART.
Absent, timed out, and answered-`Any` are three different facts, and collapsing them would
report a property of THIS MACHINE as a property of the expression — the census-green shape
this repo records. `Any` from the oracle is an ABSENCE of an answer and is treated as one.

⚑ THE PURITY TEST IS SYNTACTIC AND CONSERVATIVE. A call whose callee is not a dotted NAME, or
whose arguments are not themselves fully stated, is not evaluated. That refuses
`str(_compute())` structurally rather than by a name blocklist — the form that cannot rot,
since a blocklist must anticipate every impure helper and the first one it misses is a wrong
type carrying a `file:line`.

Usage: iface_construct.py --module <path> | --census [<path>...] | --selftest
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from substrate import corpus, iface_bottom
from substrate.iface_bottom import Witness

# How wide a rendered expression may be in a witness's detail field.
_DETAIL_WIDTH = 40

# ⚑ mypy SPELLS AN UNRESOLVED TYPE THIS WAY, and it is an ABSENCE of an answer, not an answer.
_NO_ANSWER = ("Any", "Never")

# ⚑ THE NOTE mypy PRINTS FOR A REVEALED TYPE, keyed by LINE so a batched probe's answers can
# be matched back to the expressions that asked for them.
_REVEAL = re.compile(r'^[^:]+:(\d+): note: Revealed type is "(.*)"$')

# ⚑ THE CACHE IS PERSISTENT AND SHARED, and that is the 10x. Measured: 5.1s cold into a fresh
# cache directory against 0.53s warm, for the same eleven expressions.
_CACHE = Path(tempfile.gettempdir()) / "substrate-iface-construct-mypy-cache"

# How long the oracle may take before the answer is reported as unavailable.
_TIMEOUT_S = 180.0

# ⚑ THE CALLEES WHOSE RETURN GENUINELY VARIES WITH AN ARGUMENT'S TYPE — the Pi family. ⚑ THIS
# TYPES NOTHING and is never read as evidence. It exists so `--census` can report which slots
# NEED the dependent form, which is the only honest way to judge whether a name-keyed table
# would be an acceptable shortcut for a given tree.
DEPENDENT_CALLEES: frozenset[str] = frozenset(
    {
        "compile",
        "open",
        "get",
        "max",
        "min",
        "load",
        "loads",
        "sorted",
        "next",
        "read_text",
        "read_bytes",
    }
)


@dataclass(frozen=True, slots=True)
class Assignment:
    """One module-level assignment: the name it binds and the expression it binds to."""

    name: str
    value: ast.expr
    lineno: int
    annotated: bool


def assignments(tree: ast.Module) -> list[Assignment]:
    """Return every module-level binding of a single NAME, in source order.

    ⚑ TOP LEVEL ONLY, AND A SINGLE TARGET ONLY. A name bound inside a function is not part of
    the module's interface, and `a, b = f()` binds two names to parts of one value this reader
    cannot split — reporting either would be a type the source does not state.

    ⚑ AN ANNOTATED ASSIGNMENT IS CARRIED WITH ITS FLAG RATHER THAN DROPPED, because "the
    source already states this" and "nothing states this" are different facts — the same
    separation `iface_dataflow` draws between STATED and COMPUTED.
    """
    out: list[Assignment] = []
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.value is not None:
                out.append(Assignment(node.target.id, node.value, node.lineno, annotated=True))
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt = node.targets[0]
            if isinstance(tgt, ast.Name):
                out.append(Assignment(tgt.id, node.value, node.lineno, annotated=False))
    return out


def _pure_display(node: ast.expr) -> bool:
    """Report whether a display form's every element is itself fully stated.

    ⚑ THE THREE SEQUENCE DISPLAYS ARE MATCHED SEPARATELY RATHER THAN AS ONE UNION. They share
    an `elts` field, but reaching it through a tuple-typed `isinstance` costs the checker its
    narrowing and yields `Any` — which this repo's bar refuses, correctly: an `Any` there
    would silently admit whatever a future display class happens to carry.
    """
    if isinstance(node, ast.List):
        return all(_pure_arg(e) for e in node.elts)
    if isinstance(node, ast.Tuple):
        return all(_pure_arg(e) for e in node.elts)
    if isinstance(node, ast.Set):
        return all(_pure_arg(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        return all(k is not None and _pure_arg(k) for k in node.keys) and all(
            _pure_arg(v) for v in node.values
        )
    return False


def _pure_arg(node: ast.expr) -> bool:
    """Report whether one argument expression is fully stated by the source.

    ⚑ A LITERAL, A DISPLAY OF LITERALS, A UNARY SIGN, A CONSTANT-FOLDABLE BINARY OP, OR A
    DOTTED NAME FROM AN IMPORT. Bare names are admitted ONLY as attribute roots (`re.M`),
    never alone: a lone name could be bound to anything, while `re.M` is a constant of an
    imported module the probe also imports. Anything else — a call, a comprehension — could
    depend on the machine, so admitting it would cross the C3 line. `str(_compute())` is
    refused HERE, by the shape of its argument.
    """
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.Attribute):
        return _pure_arg(node.value) or isinstance(node.value, ast.Name)
    if isinstance(node, ast.UnaryOp):
        return isinstance(node.op, ast.USub | ast.UAdd) and _pure_arg(node.operand)
    if isinstance(node, ast.BinOp):
        return (
            isinstance(node.op, ast.BitOr | ast.Add)
            and _pure_arg(node.left)
            and _pure_arg(node.right)
        )
    return _pure_display(node)


def _dotted(func: ast.expr) -> str | None:
    """Return a callee's full dotted spelling — `re.compile`, or `Path` — else None."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        head = _dotted(func.value)
        return None if head is None else f"{head}.{func.attr}"
    return None


def is_constructor_call(node: ast.expr) -> bool:
    """Report whether an expression is a C1 constructor call this module may evaluate.

    ⚑⚑ THE TEST IS ON THE SHAPE, NOT ON A ROSTER OF APPROVED CALLEES. A dotted-name callee
    whose every argument is fully stated states its own value entirely; nothing about it can
    vary with the machine. A blocklist of impure helpers would have to anticipate each one,
    and the first one it missed would be a wrong type carrying a `file:line`.
    """
    if not isinstance(node, ast.Call):
        return False
    if _dotted(node.func) is None:
        return False
    return all(_pure_arg(a) for a in node.args) and all(_pure_arg(k.value) for k in node.keywords)


def exercises_dependency(node: ast.expr) -> str | None:
    """Return the dotted callee when a call's return VARIES with its argument types.

    ⚑ THIS TYPES NOTHING. It answers the census question — how much of a corpus a name-keyed
    table would get wrong — and a caller must not read it as evidence about a slot.
    """
    if not isinstance(node, ast.Call):
        return None
    dotted = _dotted(node.func)
    if dotted is None:
        return None
    return dotted if dotted.rsplit(".", 1)[-1] in DEPENDENT_CALLEES else None


def module_imports(tree: ast.Module) -> list[str]:
    """Return the module's own import statements, as source lines.

    ⚑ THE PROBE MUST RESOLVE NAMES THE WAY THE ASSIGNMENT'S HOME DOES. Without the imports
    `re.compile(...)` is an undefined name and the oracle answers about a different program.
    """
    return [ast.unparse(n) for n in tree.body if isinstance(n, ast.Import | ast.ImportFrom)]


def _normalise(spelled: str) -> str:
    """Render mypy's internal spelling the way a `.pyi` would state it.

    ⚑ ONLY THE `builtins.` PREFIX IS STRIPPED, because that is the one qualification a stub
    never writes. Stripping more would collapse `re.Pattern` with a same-named class from
    another module — and the revealed type stays an OPAQUE STRING either way: this is a
    rendering, never a parse, and no consumer may match it against a name it expected.
    """
    return spelled.replace("builtins.", "")


@dataclass(frozen=True, slots=True)
class Probe:
    """One batched oracle question: expressions by id, answered by line number."""

    imports: list[str] = field(default_factory=list)
    exprs: list[tuple[str, str]] = field(default_factory=list)

    def source(self) -> str:
        """Render the probe file — ONE `reveal_type` per line, in `exprs` order."""
        return "\n".join([*self.imports, *(f"reveal_type({src})" for _k, src in self.exprs), ""])

    def line_of(self, index: int) -> int:
        """Return the 1-based probe line the expression at `index` occupies."""
        return len(self.imports) + index + 1


def _run_mypy(body: str) -> tuple[str, str]:
    """Run the oracle over one probe file. Returns (stdout, reason-when-unusable)."""
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "probe.py"
        probe.write_text(body, encoding="utf-8")
        try:
            proc = subprocess.run(  # noqa: S603  - fixed argv, no shell
                [
                    sys.executable,
                    "-m",
                    "mypy",
                    "--no-error-summary",
                    "--ignore-missing-imports",
                    f"--cache-dir={_CACHE}",
                    str(probe),
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=_TIMEOUT_S,
            )
        except FileNotFoundError:
            return ("", "the mypy oracle is not installed on this machine")
        except subprocess.TimeoutExpired:
            return ("", f"the mypy oracle did not answer within {_TIMEOUT_S:g}s")
    return (proc.stdout, "")


def reveal_all(probe: Probe) -> tuple[dict[str, str], str]:
    """Ask the oracle EVERY expression at once. Returns (id -> type, reason-when-empty).

    ⚑⚑⚑ THIS IS THE PI-TYPE ELIMINATOR, AND IT IS BORROWED RATHER THAN BUILT. typeshed states
    `re.compile`'s return as a function of its argument, through overloads; mypy applies that
    to these arguments and prints the result. A table keyed on the callee name would answer
    `Pattern[str]` for `re.compile(rb"x")` — a wrong type with a `file:line`, which is the one
    outcome this toolkit holds to be worse than no answer at all.

    ⚑⚑ THE ANSWERS COME BACK BY LINE NUMBER, which is what makes ONE run serve N expressions.
    Each `reveal_type` occupies its own line and the note carries that line, so the mapping is
    positional and exact rather than a match on the rendered text.

    ⚑ AN EXPRESSION THE ORACLE DID NOT ANSWER IS SIMPLY ABSENT FROM THE RESULT, never present
    with a placeholder. A probe line that failed to typecheck yields an error rather than a
    note, and inventing an entry for it would convert a precise negative into a false positive.
    """
    if not probe.exprs:
        return ({}, "")
    out, why = _run_mypy(probe.source())
    if why:
        return ({}, why)
    by_line: dict[int, str] = {}
    for line in out.splitlines():
        m = _REVEAL.match(line)
        if m is not None:
            by_line[int(m.group(1))] = _normalise(m.group(2))
    got: dict[str, str] = {}
    for i, (key, _src) in enumerate(probe.exprs):
        spelled = by_line.get(probe.line_of(i))
        if spelled is not None and spelled not in _NO_ANSWER:
            got[key] = spelled
    return (got, "")


@dataclass(frozen=True, slots=True)
class Resolved:
    """What this reader determined about one module-level assignment."""

    name: str
    status: str
    type_name: str
    note: str
    order: int = 0
    witness: Witness | None = None


def _floor_rows(items: list[Assignment], path: str) -> tuple[list[Resolved], list[Assignment]]:
    """Split assignments into those the FLOOR types and those needing the oracle.

    ⚑⚑ C2 IS TRIED FIRST AND WITHOUT THE ORACLE. `iface_bottom.given_type` already types a
    literal display in-process, so reaching for a subprocess to learn that `"x"` is `str`
    would be slower for no additional truth AND would put the existing floor's answers behind
    an oracle that can be absent. `AGDA_JOBS = "20"` resolves here, which is why the C3 rule
    it motivated does not actually fire on it.
    """
    rows: list[Resolved] = []
    owed: list[Assignment] = []
    for i, a in enumerate(items):
        if a.annotated:
            rows.append(Resolved(a.name, "STATED", "", "annotated at source", i))
            continue
        where = f"{path}:{a.lineno}"
        floor = iface_bottom.given_type(a.value, where)
        if floor is None:
            owed.append(a)
        else:
            rows.append(
                Resolved(
                    a.name,
                    "COMPUTED",
                    floor.type_name,
                    "",
                    i,
                    Witness(floor.type_name, where, "constant-fold", floor.detail),
                )
            )
    return (rows, owed)


def _order_of(r: Resolved) -> int:
    """Return a row's source position — the sort key that restores declaration order."""
    return r.order


def resolve_module(tree: ast.Module, path: str) -> list[Resolved]:
    """Type every module-level assignment in one parsed module, in ONE oracle run."""
    items = assignments(tree)
    at = {a.name: i for i, a in enumerate(items)}
    rows, owed = _floor_rows(items, path)
    probe = Probe(
        module_imports(tree),
        [(a.name, ast.unparse(a.value)) for a in owed if is_constructor_call(a.value)],
    )
    got, why = reveal_all(probe)
    for a in owed:
        where = f"{path}:{a.lineno}"
        i = at[a.name]
        if not is_constructor_call(a.value):
            rows.append(
                Resolved(
                    a.name,
                    "UNRESOLVED",
                    "",
                    (
                        "not a constructor call over stated arguments — evaluating it would "
                        "require RUNNING the module (the C3 line)"
                    ),
                    i,
                )
            )
        elif a.name in got:
            rows.append(
                Resolved(
                    a.name,
                    "COMPUTED",
                    got[a.name],
                    "",
                    i,
                    Witness(
                        got[a.name], where, "constructor", ast.unparse(a.value)[:_DETAIL_WIDTH]
                    ),
                )
            )
        else:
            rows.append(
                Resolved(
                    a.name,
                    "UNRESOLVED",
                    "",
                    why
                    or (
                        "the oracle returned no type for this expression — a fact about the "
                        "probe or the checker, never proof the expression has no type"
                    ),
                    i,
                )
            )
    rows.sort(key=_order_of)
    return rows


def _render(rows: list[Resolved], path: str) -> int:
    """Print each assignment with its type and witness, then the residue."""
    done = [r for r in rows if r.status == "COMPUTED"]
    stated = [r for r in rows if r.status == "STATED"]
    stuck = [r for r in rows if r.status == "UNRESOLVED"]
    sys.stdout.write(
        f"iface-construct {path}: {len(done)} of {len(rows)} module-level assignment(s) "
        f"COMPUTED by evaluating their constructor; {len(stated)} already stated, "
        f"{len(stuck)} did NOT bottom out.\n"
    )
    for r in done:
        sys.stdout.write(f"    COMPUTED   {r.name}: {r.type_name}\n")
        if r.witness is not None:
            sys.stdout.write(
                f"          [{r.witness.kind}] {r.witness.where}  {r.witness.detail}\n"
            )
    for r in stated:
        sys.stdout.write(f"    STATED     {r.name}: {r.note}\n")
    if stuck:
        sys.stdout.write(
            "\n  DID NOT BOTTOM OUT — reported, never filled with `Any`. Reading STOPS at\n"
            "  an expression whose value depends on the machine; that is the C3 line, and\n"
            "  a RUNTIME oracle (`stubtest`) is what settles those.\n"
        )
        for r in stuck:
            sys.stdout.write(f"    UNRESOLVED {r.name}: {r.note}\n")
    return 0


def _census_rows(paths: list[str]) -> list[tuple[str, str, str]]:
    """Return (path, name, callee) for every assignment EXERCISING the Pi dependency."""
    out: list[tuple[str, str, str]] = []
    for p in paths:
        try:
            tree = ast.parse(Path(p).read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        out += [
            (p, a.name, dotted)
            for a in assignments(tree)
            if (dotted := exercises_dependency(a.value)) is not None
        ]
    return out


def _render_census(paths: list[str]) -> int:
    """Print which assignments need the DEPENDENT form — what a name-table gets wrong.

    ⚑ THIS IS THE ARTIFACT THE PI REFRAME ASKED FOR. It says how much of a corpus the
    non-dependent approximation would MISREPORT, which is the only honest way to judge
    whether a name-keyed table is an acceptable shortcut for a given tree.
    """
    rows = _census_rows(paths)
    sys.stdout.write(
        f"iface-construct census: {len(rows)} module-level assignment(s) across "
        f"{len(paths)} file(s) call a constructor whose return VARIES with its\n"
        "  argument type. For these a name-keyed return table is not imprecise but WRONG,\n"
        "  and the applied type must come from the oracle that holds the overloads.\n"
    )
    for p, name, dotted in rows:
        sys.stdout.write(f"    {p}: {name} = {dotted}(...)\n")
    return 0


def _dispatch_module(rest: list[str]) -> int:
    """Run `--module`, typing every module-level assignment of one file."""
    if not rest:
        sys.stdout.write("--module needs <path>\n")
        return 2
    try:
        src = Path(rest[0]).read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=rest[0])
    except (OSError, SyntaxError):
        sys.stdout.write(f"could not parse {rest[0]}\n")
        return 2
    return _render(resolve_module(tree, rest[0]), rest[0])


def main(argv: list[str]) -> int:
    """Dispatch one mode; 2 on an unusable command line."""
    rest = [a for a in argv[1:] if not a.startswith("-")]
    if "--census" in argv:
        return _render_census(rest or corpus.py_files())
    if "--module" in argv:
        return _dispatch_module(rest)
    sys.stdout.write(__doc__ or "")
    return 2


def _expr(src: str) -> ast.expr:
    """Parse one expression — the selftest's fixture builder."""
    stmt = ast.parse(src).body[0]
    if not isinstance(stmt, ast.Expr):
        raise TypeError(src)
    return stmt.value


def _cases_shape() -> list[tuple[str, object, object]]:
    """Pin the SYNTACTIC half — what counts as a constructor call, and what is refused."""
    return [
        # ⚑ THE LIVE SHAPE: `DECL = re.compile(r"...")` is a constructor over a stated arg.
        (
            "a dotted call over a literal is a constructor call",
            is_constructor_call(_expr('re.compile(r"^x")')),
            True,
        ),
        # ⚑⚑ THE DISCRIMINATOR THAT DRAWS THE C3 LINE, and it is the whole point of the file:
        # `str(_compute())` has a CALL as its argument, so its value depends on the machine
        # and it must be REFUSED. A predicate answering True here would cross into running.
        (
            "a call whose ARGUMENT is a call is NOT evaluable",
            is_constructor_call(_expr("str(_compute())")),
            False,
        ),
        # ⚑ THE LIVE C3 INSTANCE from `gen_build_makefiles`: a path derived from `__file__`.
        (
            "a call over __file__ is not evaluable",
            is_constructor_call(_expr("os.path.dirname(os.path.abspath(__file__))")),
            False,
        ),
        # ⚑ A DISPLAY OF LITERALS IS STATED, so `frozenset({"a"})` is admissible.
        (
            "a call over a display of literals is evaluable",
            is_constructor_call(_expr('frozenset({"a", "b"})')),
            True,
        ),
        # ⚑⚑ THE LIVE `IMPRE` SHAPE — a second argument that is a MODULE CONSTANT (`re.M`).
        # Refusing it would have left the motivating slot unresolved for a reason that has
        # nothing to do with the machine.
        (
            "a call taking a dotted module constant is evaluable",
            is_constructor_call(_expr('re.compile(r"^x", re.M)')),
            True,
        ),
        # ⚑ AND A NON-CALL IS NOT A CONSTRUCTOR CALL, so the predicate is not answering True
        # to every expression it is shown.
        ("a literal is not a constructor call", is_constructor_call(_expr('"x"')), False),
    ]


def _cases_assignments() -> list[tuple[str, object, object]]:
    """Pin the ASSIGNMENT walk — which bindings are module-interface slots."""
    tree = ast.parse("A = 1\nB: int = 2\nC, D = f()\ndef g():\n    E = 3\n    return E\n")
    return [
        # ⚑ ASKED AS ONE LIST so all three exclusions are pinned at once: a walk that
        # descended into functions, or split a tuple target, or dropped the annotated form,
        # fails here rather than in one omitted case.
        (
            "only single-target TOP-LEVEL bindings are slots, annotation flagged",
            [(a.name, a.annotated) for a in assignments(tree)],
            [("A", False), ("B", True)],
        ),
        # ⚑ THE IMPORTS ARE CARRIED, because without them the oracle sees an undefined name
        # and answers about a different program than the one the assignment lives in.
        (
            "the module's imports are collected for the probe",
            module_imports(ast.parse("import re\nfrom pathlib import Path\nX = 1\n")),
            ["import re", "from pathlib import Path"],
        ),
    ]


def _cases_probe() -> list[tuple[str, object, object]]:
    """Pin the BATCHING — one run, N expressions, matched back by line."""
    p = Probe(["import re"], [("a", '"x"'), ("b", '"y"')])
    return [
        (
            "the probe puts ONE reveal per line after the imports",
            p.source(),
            'import re\nreveal_type("x")\nreveal_type("y")\n',
        ),
        # ⚑⚑ THE LINE MAP IS WHAT MAKES ONE RUN SERVE N EXPRESSIONS. An off-by-one here would
        # attribute every answer to its neighbour — a wrong type with a file:line, silently.
        (
            "each expression's line accounts for the import block",
            [p.line_of(0), p.line_of(1)],
            [2, 3],
        ),
        # ⚑ THE NOTE IS PARSED BY LINE, not by matching the rendered text.
        (
            "a revealed-type note is read by its line number",
            _REVEAL.match('probe.py:6: note: Revealed type is "re.Pattern[builtins.str]"')
            is not None,
            True,
        ),
        # ⚑ ITS DISCRIMINATOR: an ERROR line is not a revealed type and must not parse.
        (
            "an error line is not a revealed type",
            _REVEAL.match("probe.py:1: error: boom") is None,
            True,
        ),
        # ⚑ ONLY THE `builtins.` QUALIFICATION IS STRIPPED — the type stays an opaque string.
        (
            "only the builtins qualification is stripped",
            _normalise("re.Pattern[builtins.str]"),
            "re.Pattern[str]",
        ),
    ]


def _cases_dependency() -> list[tuple[str, object, object]]:
    """Pin the Pi census — which calls EXERCISE the argument-dependent return."""
    return [
        (
            "re.compile is named as argument-dependent",
            exercises_dependency(_expr('re.compile(r"x")')),
            "re.compile",
        ),
        # ⚑⚑ ITS DISCRIMINATOR: a constant-return constructor must NOT be named, or the
        # census would report the whole corpus as needing the dependent form and say nothing.
        (
            "a constant-return constructor is NOT argument-dependent",
            exercises_dependency(_expr('frozenset({"a"})')),
            None,
        ),
        ("a literal exercises no dependency", exercises_dependency(_expr('"x"')), None),
    ]


def _cases_oracle() -> list[tuple[str, object, object]]:
    """Pin the ORACLE END-TO-END — the Pi elimination, on the live motivating pair.

    ⚑⚑⚑ THIS IS THE CASE A TABLE CANNOT FAKE. The SAME callee, two argument types, two
    different answers, both from ONE batched run. A name-keyed table passes every other case
    in this file and fails this one, which is exactly why it is here.
    """
    got, why = reveal_all(
        Probe(
            ["import re"],
            [
                ("s", 're.compile(r"^x")'),
                ("b", 're.compile(rb"^x")'),
                ("lit", '"x"'),
                ("dep", 'dict([("k", 1)]).get("k", "s")'),
            ],
        )
    )
    return [
        (
            "the SAME callee yields DIFFERENT types by argument type — the Pi eliminated",
            {"str-arg": got.get("s"), "bytes-arg": got.get("b")},
            {"str-arg": "re.Pattern[str]", "bytes-arg": "re.Pattern[bytes]"},
        ),
        # ⚑ THE BATCH KEEPS ITS ANSWERS APART: a third, unrelated expression in the same run
        # must come back under its OWN key, or the line map is decorative.
        #
        # ⚑⚑⚑ AND THE EXPECTED VALUE HERE IS THE ORACLE'S OWN SPELLING, NOT THE TIDY ONE —
        # this case FAILED asserting `str`, which is this file's own "opaque string" warning
        # violated inside the suite that documents it. mypy reveals a bare literal as
        # `Literal['x']?`: the LITERAL type, with `?` marking it inferred rather than final.
        # That is the SAME shape `stubtest` reported for `AGDA_JOBS` (`Literal['20']`), so
        # the spelling is not an artefact of this probe — it is what a literal's type IS
        # before a declared context widens it, and a consumer that string-matched `str` here
        # would have silently dropped a real answer.
        (
            "a batched run matches every answer to its own expression",
            got.get("lit"),
            "Literal['x']?",
        ),
        # ⚑⚑ A SECOND DEPENDENT FAMILY, so the mechanism is not tuned to `re.compile`:
        # `dict.get`'s return varies with the DEFAULT's type, and typeshed says so.
        (
            "a second dependent family eliminates through the same oracle",
            got.get("dep"),
            "int | str",
        ),
        # ⚑ AND THE ORACLE'S FAILURE IS A REASON, NOT A TYPE — an empty probe asks nothing
        # and must not manufacture an answer or a complaint.
        ("an empty probe asks nothing and reports nothing", reveal_all(Probe()), ({}, "")),
        ("a usable oracle reports no reason", why, ""),
    ]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
