#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""THE BOTTOMING-OUT SET: the types this corpus takes as GIVEN rather than inferred.

⚑⚑⚑ THIS FILE IS THE TERMINATION ARGUMENT, MADE READABLE. A recursive dataflow reader is
only honest if you can name where it stops, and "where it stops" is not a property of the
walk — it is this enumeration. Everything here is a type nobody in this repo derived: a
literal carries its own, and typeshed states the rest. `iface_dataflow` recurses; this
module is the floor it lands on, and it deliberately CANNOT recurse — nothing in it calls
anything that resolves a slot.

⚑⚑ SIX KINDS, AND THEY DO NOT ALL POINT THE SAME WAY.

  B1 LITERALS       `"scratch"` is `str`, `[...]` is a list display. Given by the grammar.
  B2 ANNOTATED      A slot the source already states. Read by `iface_infer`, not here.
  B2d DEFAULT       A parameter's DEFAULT EXPRESSION — stated by the def, not inferred.
  B3 TYPED SURFACE  A call into builtins / stdlib / a `py.typed` package. Given by typeshed.
  B4 BODY REQUIRES  What the body DEMANDS of a value, whatever flows in.
  B5 ELEMENT        Subscripting a value whose ELEMENT type is given — `x.split()[0]`.

  B1, B2d, B3 and B5 are FORWARD facts: a value of this type arrives here. B4 is a
  BACKWARD constraint: whatever arrives must support this. They are separate evidence and
  they can DISAGREE — a call site passing a `Path` into a body that calls `.endswith` is a
  latent bug, and a reader that averaged them would erase exactly the finding worth having.

⚑⚑ B2d IS STATED, NOT INFERRED, AND IT IS ALSO USUALLY PARTIAL. `def scan(paths=None)`
reported *"no call site passes this parameter — the slot is DEAD"* while the authored stub
said `Iterable[str] | None`. Both readings were honest about what they looked at: `scan()`
IS called with no argument, so no call site passes it, and the DEFAULT was the only evidence
in the corpus. But a bare `= None` witnesses only the `None` ARM. Reporting `NoneType` as
the whole answer would be the `carrier_of` majority-vote inversion committed a second time —
so a `None` default is emitted as a PARTIAL witness, and the caller must not read a partial
set as a join. A NON-`None` default (`= 0`, `= "x"`) is the total answer for what the
default alone can say and is emitted as ordinary evidence.

⚑ A NAME ABSENT FROM THESE TABLES DOES NOT BECOME `Any`. It becomes an UNRESOLVED finding.
That inversion is the whole discipline: an incomplete bottom under-reports what was
computed, which is safe, whereas defaulting to `Any` over-reports and buries the site.

⚑ EVERY SOURCE HERE READS THE DEFINING MODULE'S OWN TEXT — a default expression, a body
subscript, an element expression. None of them reaches a CALL SITE, so none can widen the
population from which a fixture in `tests/` or a module's selftest region becomes a witness.
That is a property of where the evidence is read, not a filter applied afterwards.

Usage: iface_bottom.py [--selftest]
"""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass

# ⚑ B3, ENUMERATED RATHER THAN GUESSED. Keyed by the callee's dotted TAIL, so both
# `os.path.join(...)` and a `from os.path import join` call resolve to the same entry.
TYPED_RETURNS: dict[str, str] = {
    "join": "str",
    "abspath": "str",
    "dirname": "str",
    "basename": "str",
    "relpath": "str",
    "normpath": "str",
    "expanduser": "str",
    "isdir": "bool",
    "isfile": "bool",
    "exists": "bool",
    "islink": "bool",
    "listdir": "list[str]",
    "getcwd": "str",
    "parse": "ast.Module",
    "unparse": "str",
    "read_text": "str",
    "readlines": "list[str]",
    "len": "int",
    "str": "str",
    "int": "int",
    "bool": "bool",
    "repr": "str",
    "set": "set[Any]",
    "list": "list[Any]",
    "dict": "dict[Any, Any]",
    "tuple": "tuple[Any, ...]",
    "open": "TextIOWrapper",
}

# ⚑ B4: a method whose presence PINS its receiver. The value is the narrowest type the
# corpus can honestly claim from the call ALONE — no wider guess, since a wide guess here
# manufactures the claim this whole arc exists to stop manufacturing.
PINNING_METHODS: dict[str, str] = {
    "endswith": "str",
    "startswith": "str",
    "strip": "str",
    "lstrip": "str",
    "rstrip": "str",
    "lower": "str",
    "upper": "str",
    "split": "str",
    "rsplit": "str",
    "splitlines": "str",
    "encode": "str",
    "format": "str",
    "replace": "str",
    "removeprefix": "str",
    "removesuffix": "str",
}

# ⚑ B5: what ONE ELEMENT of a value of this type is. Deliberately a SEPARATE table from
# `TYPED_RETURNS`, and the separation is the same one that keeps `STR_ARGUMENT_CALLS` apart
# from it: a return table answers "what does this call produce", an element table answers
# "what falls out of subscripting it". `set[Any]` has no element access at all and
# `dict[Any, Any]`'s subscript yields a VALUE rather than a member, so neither appears —
# an entry invented for table symmetry would manufacture a type nothing states.
ELEMENT_OF: dict[str, str] = {
    "list[str]": "str",
    "tuple[str, ...]": "str",
    "str": "str",
}

# ⚑ THE METHODS WHOSE RESULT IS `list[str]`, kept apart from `PINNING_METHODS` even though
# the same names appear in both. That table answers "what does calling this pin the
# RECEIVER to"; this one answers "what does the call PRODUCE". `carrier_of`'s
# `parts[0].split()[0]` needs the second, and reading the first in its place would report
# `str` where a `list[str]` stands — one table serving two questions is the merge
# `STR_ARGUMENT_CALLS` was split out to undo.
_SPLIT_RESULTS: frozenset[str] = frozenset({"split", "rsplit", "splitlines"})

# ⚑ THE NODE KINDS THAT OPEN A NEW SCOPE — what a per-function walk must NOT descend into.
# Named as a constant because `returns_none`'s two tests both depend on it and a walk that
# entered an inner def would attribute a nested `yield` or `return` to its enclosing
# function, which is a wrong answer carrying a `file:line` rather than a missing one.
_NESTED_SCOPES: tuple[type[ast.AST], ...] = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
)

# ⚑ B1, AS A TABLE RATHER THAN A RETURN LADDER. Several display forms each carrying their
# own type is a LOOKUP, not control flow; spelling it as branches is what made the first cut
# of `given_type` exceed the per-file complexity gate — the gate reading the shape correctly.
_DISPLAYS: tuple[tuple[type[ast.expr], str, str], ...] = (
    (ast.JoinedStr, "str", "f-string"),
    (ast.List, "list[Any]", "list display"),
    (ast.Dict, "dict[Any, Any]", "dict display"),
    (ast.Set, "set[Any]", "set display"),
    (ast.Tuple, "tuple[Any, ...]", "tuple display"),
)

# How wide a rendered expression may be in a witness's detail field.
_DETAIL_WIDTH = 40

# One selftest case: a name, what the reader returned, what it must return.
_Check = Callable[[str, object, object], None]


@dataclass(frozen=True, slots=True)
class Witness:
    """One piece of evidence about a slot: a type, where it was read, and which kind.

    ⚑ A TYPE WITHOUT A `where` IS THE AUTHORED CLAIM THIS ARC EXISTS TO STOP. The field is
    not optional and not derived; every type this toolkit reports can be checked at a
    `file:line` by a reader who does not trust the tool.

    ⚑⚑ `partial` MARKS EVIDENCE THAT IS TRUE BUT NOT THE WHOLE ANSWER. A `= None` default
    witnesses the `None` arm and says nothing about the other; a reader that joined it with
    nothing else and called the result a type would report `NoneType` for a slot whose
    authored stub reads `Iterable[str] | None`. The flag is what lets the caller refuse to
    treat a fragment as a join, and it defaults False so no existing witness changes meaning.
    """

    type_name: str
    where: str
    kind: str
    detail: str = ""
    partial: bool = False


def callee_name(node: ast.Call) -> str | None:
    """Return the dotted tail of a call's callee — `join` for `os.path.join`."""
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return None


def _receiver_type(node: ast.expr) -> str | None:
    """Return the type of a subscript's VALUE, by B3 or a split result, when stated.

    ⚑ A PINNING METHOD'S RESULT IS READ HERE, AND ONLY IN THE RECEIVER POSITION.
    `parts[0].split()[0]` needs `.split()`'s RESULT (`list[str]`), which `TYPED_RETURNS`
    does not hold because `split` is the pinning entry for its RECEIVER. The two tables
    answer different questions about the same name, and merging them is the error
    `STR_ARGUMENT_CALLS` was split out to avoid — so `_SPLIT_RESULTS` states the one case
    where a pinning method's own result is itself given.
    """
    if isinstance(node, ast.Call):
        tail = callee_name(node)
        if tail in _SPLIT_RESULTS:
            return "list[str]"
        if tail is not None and tail in TYPED_RETURNS:
            return TYPED_RETURNS[tail]
    return None


def _element_type(node: ast.Subscript) -> str | None:
    """Return the type of `x[i]` when `x`'s element type is stated and `i` is an INDEX.

    ⚑ A SLICE IS NOT AN ELEMENT, and the distinction is load-bearing rather than pedantic.
    `parts[0]` is a member; `parts[1:]` is another sequence of the same type. Reading the
    two alike would report `str` for a slot holding a `list[str]` — a wrong type carrying a
    `file:line`, which this module holds to be worse than no answer at all.
    """
    if isinstance(node.slice, ast.Slice):
        return None
    recv = _receiver_type(node.value)
    return None if recv is None else ELEMENT_OF.get(recv)


def _homogeneous(elts: list[ast.expr]) -> str | None:
    """Return the one type every element bottoms out to, or None if they disagree."""
    if not elts:
        return None
    got = [given_type(e, "") for e in elts]
    if any(w is None for w in got):
        return None
    names = {w.type_name for w in got if w is not None}
    return names.pop() if len(names) == 1 else None


def _display_type(node: ast.expr) -> tuple[str, str] | None:
    """Return the (type, detail) a display form carries, refined by its elements.

    ⚑⚑ THE ELEMENTS ARE READ ONE LEVEL DOWN, AND THE COARSE ANSWER IS KEPT WHEN THEY DO NOT
    ALL BOTTOM OUT. `tuple[Any, ...]` was honest but coarser than the authored stubs, and
    the element expressions are typeable by this same floor. But a tuple whose first element
    is a literal and whose second is a bare name has ONE element known, not a type — and
    refining on the arms that happened to bottom out is the `carrier_of` majority vote in a
    new position. So refinement requires EVERY element to bottom out; otherwise the display
    reports the type it always did, and the residue stays visible upstream.

    ⚑ A HETEROGENEOUS TUPLE IS SPELLED OUT POSITIONALLY, because `tuple[bool, list[Any]]`
    is what the source states and `tuple[Any, ...]` merely fails to contradict it.
    """
    for cls, name, detail in _DISPLAYS:
        if not isinstance(node, cls):
            continue
        if isinstance(node, ast.Tuple):
            got = [given_type(e, "") for e in node.elts]
            if node.elts and all(w is not None for w in got):
                inner = ", ".join(w.type_name for w in got if w is not None)
                return (f"tuple[{inner}]", detail)
        elif isinstance(node, ast.List):
            refined = _homogeneous(node.elts)
            if refined is not None:
                return (f"list[{refined}]", detail)
        return (name, detail)
    return None


def given_type(node: ast.expr, where: str) -> Witness | None:
    """Type ONE expression by B1, B3 and B5 alone. None when none applies.

    ⚑ THIS IS THE BOTTOM ITSELF, AND IT DELIBERATELY DOES NOT RECURSE INTO THE SLOT GRAPH.
    A name, a call to an unannotated def — anything whose type would have to be INFERRED
    from what flows through the corpus — returns None and becomes the caller's problem to
    resolve or to report unresolved. It DOES descend into an expression's own
    SUB-EXPRESSIONS (a tuple's elements, a subscript's receiver), which is not the same
    thing: that walk is bounded by the syntax tree of one expression and terminates on its
    leaves, whereas the slot graph is what this module's termination argument is about.
    """
    if isinstance(node, ast.Constant):
        return Witness(
            type(node.value).__name__, where, "literal", ast.unparse(node)[:_DETAIL_WIDTH]
        )
    disp = _display_type(node)
    if disp is not None:
        return Witness(disp[0], where, "literal", disp[1])
    if isinstance(node, ast.Subscript):
        elem = _element_type(node)
        if elem is not None:
            return Witness(elem, where, "element", ast.unparse(node)[:_DETAIL_WIDTH])
    if isinstance(node, ast.Call):
        tail = callee_name(node)
        if tail is not None and tail in TYPED_RETURNS:
            return Witness(TYPED_RETURNS[tail], where, "typed-surface", f"{tail}()")
    return None


def default_type(default: ast.expr, path: str) -> Witness | None:
    """Read B2d: the type of a parameter's DEFAULT EXPRESSION, as a witness.

    ⚑⚑ A DEFAULT IS EVIDENCE THE SOURCE STATES OUTRIGHT, and the reader did not read it.
    `check_carrier_locality.scan(paths=None)` came back *"no call site passes this parameter
    — the slot is DEAD"*, which was true of call sites and false as a verdict: the def
    itself says what a caller omitting the argument gets. That is B1/B2 territory, not an
    inference, and it lives in the DEFINING module rather than at any call site.

    ⚑⚑ A `None` DEFAULT IS PARTIAL AND SAYS SO. `= None` witnesses only the `None` arm of
    what is nearly always a `T | None`; the other arm needs the body or a call site. Marking
    it partial is what stops a slot whose ONLY evidence is `= None` from reporting a
    confident `NoneType` — the same inversion `carrier_of`'s majority vote produced, where
    the fallback arm was mistaken for the answer.

    ⚑⚑⚑ IT TAKES THE EXPRESSION, NOT A (fn, param) PAIR, AND THAT IS A REUSE DECISION RATHER
    THAN A CONVENIENCE. `iface_dataflow.default_of` ALREADY owns the parameter→default
    lookup, including the right-alignment of `args.defaults` and the parallel `kw_defaults`
    holes that make that lookup easy to get wrong. A second copy here would be two
    authorities on one question — the same-name-different-body hazard this repo has retired
    repeatedly — and they would drift on exactly the alignment edge cases neither suite
    shares. So the lookup stays there and the TYPING lives here, which is the split the two
    modules already draw everywhere else.
    """
    got = given_type(default, f"{path}:{default.lineno}")
    if got is None:
        return None
    return Witness(
        got.type_name,
        got.where,
        "default",
        f"={ast.unparse(default)[:_DETAIL_WIDTH]}",
        got.type_name == "NoneType",
    )


def _own_nodes(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.AST]:
    """Collect every node in `fn`'s OWN scope, excluding nested function and class bodies."""
    out: list[ast.AST] = []
    stack: list[ast.AST] = list(fn.body)
    while stack:
        node = stack.pop()
        if isinstance(node, _NESTED_SCOPES):
            continue
        out.append(node)
        stack += list(ast.iter_child_nodes(node))
    return out


def _falls_through(body: list[ast.stmt]) -> bool:
    """Report whether a statement list can reach its end — the `None` return's premise.

    ⚑ CONSERVATIVE IN THE SAFE DIRECTION. A body this cannot prove terminating reads as
    falling through, which yields `None` — and `None` IS the answer for a function that
    reaches its end, so the residual risk sits entirely on the raise-only and loop-forever
    shapes, which are tested explicitly.
    """
    if not body:
        return True
    last = body[-1]
    if isinstance(last, ast.Raise):
        return False
    if isinstance(last, ast.While):
        forever = isinstance(last.test, ast.Constant) and bool(last.test.value)
        if forever and not any(isinstance(n, ast.Break) for n in ast.walk(last)):
            return False
    if isinstance(last, ast.If) and last.orelse:
        return _falls_through(last.body) or _falls_through(last.orelse)
    return True


def returns_none(fn: ast.FunctionDef | ast.AsyncFunctionDef, path: str) -> Witness | None:
    """Type the return slot of a function that reaches its end with no value — `None`.

    ⚑⚑⚑ A FUNCTION WITH NO VALUED RETURN IS `None`, WHICH IS DETERMINED, AND IT WAS FILED AS
    A FAILURE. `gen_build_makefiles.kahn_check` and `main` both reported *"no return
    statement with a value"* as UNRESOLVED — the strongest bottoming-out case in the set,
    printed in the residue. `kahn_check`'s authored stub says `-> None`, and the source
    states it as plainly as a literal does: the body ends, so the value is `None`.

    ⚑⚑ THREE SHAPES ARE NOT `None` RETURNS AND EACH IS EXCLUDED BY A DIFFERENT FACT.
      * a GENERATOR (`yield` in its own scope) returns an iterator, not `None`;
      * a function whose every exit RAISES never returns at all, so `None` would be a claim
        about a value no caller receives — `gen_build_makefiles.jobs` raises `SystemExit` on
        two arms and is a live instance of the near-miss;
      * a `while True:` with no `break` does not fall off its end either.
    The exclusions are not defensive padding: `jobs` sits in the same module as the two
    functions this rule was written for, and a rule reading "no valued return" alone would
    have typed it `None` while its stub says `int`.

    ⚑ A NESTED def's `yield` IS NOT THIS FUNCTION'S. `ast.walk` descends into inner
    functions, so both tests walk only the nodes belonging to this scope.
    """
    own = _own_nodes(fn)
    if any(isinstance(n, ast.Return) and n.value is not None for n in own):
        return None
    if any(isinstance(n, ast.Yield | ast.YieldFrom) for n in own):
        return None
    if not _falls_through(fn.body):
        return None
    return Witness("None", f"{path}:{fn.lineno}", "no-valued-return", "body has no valued return")


# ⚑ B4b: a TYPED SURFACE whose parameters are all `str`. Passing our parameter into one of
# these constrains it just as surely as calling a method on it — typeshed says so.
# Deliberately NOT every entry of `TYPED_RETURNS`: `len(x)` accepts anything with `__len__`
# and `str(x)` accepts everything, so reading a *return* table as an *argument* table would
# manufacture `str` for parameters nothing constrains. The two tables answer different
# questions and were briefly one; separating them is what keeps this honest.
STR_ARGUMENT_CALLS: frozenset[str] = frozenset(
    {
        "join",
        "abspath",
        "dirname",
        "basename",
        "relpath",
        "normpath",
        "expanduser",
        "isdir",
        "isfile",
        "islink",
        "listdir",
    }
)


def _pins(node: ast.AST, param: str) -> bool:
    """Report whether one node is a pinning method access on exactly `param`."""
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == param
        and node.attr in PINNING_METHODS
    )


def _method_pins(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, param: str, path: str
) -> list[Witness]:
    """Return every `param.<method>()` in the body that pins the receiver's type."""
    return [
        Witness(
            PINNING_METHODS[node.attr],
            f"{path}:{node.lineno}",
            "body-requires",
            f".{node.attr}(...)",
        )
        for node in ast.walk(fn)
        if _pins(node, param) and isinstance(node, ast.Attribute)
    ]


def _argument_pins(
    fn: ast.FunctionDef | ast.AsyncFunctionDef, param: str, path: str
) -> list[Witness]:
    """Return every site where the body hands `param` to a surface taking `str`.

    ⚑⚑ THIS ARM WAS MISSING AND THE WORKED CASE EXPOSED IT. `promotion_report(candidate)`
    reported UNRESOLVED while the AUTHORED stub said `str` — and the authored stub was
    RIGHT, because line 76 does `os.path.join(root, candidate)`. The evidence was in the
    body all along; the reader only knew how to see a METHOD CALL on a parameter, not a
    parameter passed as an ARGUMENT. A disagreement with a hand-written stub turned out to
    be a gap in the bottoming-out set rather than a defect in the stub, which is exactly
    why the comparison was worth running.
    """
    out: list[Witness] = []
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        tail = callee_name(node)
        if tail not in STR_ARGUMENT_CALLS:
            continue
        out += [
            Witness("str", f"{path}:{node.lineno}", "body-requires", f"passed to {tail}()")
            for a in node.args
            if isinstance(a, ast.Name) and a.id == param
        ]
    return out


def required_of(fn: ast.FunctionDef | ast.AsyncFunctionDef, param: str, path: str) -> list[Witness]:
    """Report B4: what the BODY requires of `param`, whatever any caller passes.

    ⚑ INDEPENDENT EVIDENCE, NOT A FALLBACK FOR MISSING CALL SITES. A call site says what a
    caller HAPPENS to pass today; the body says what any caller MUST pass. When they agree
    the slot is strongly determined; when they disagree, one of them is a latent bug, and
    surfacing that disagreement is worth more than either reading alone.

    ⚑ TWO ARMS, BECAUSE A PARAMETER IS CONSTRAINED IN TWO GRAMMATICAL POSITIONS — as a
    RECEIVER (`p.endswith(...)`) and as an ARGUMENT (`os.path.join(root, p)`). Reading only
    the first is what made the worked case disagree with its authored stub.

    ⚑⚑ THE DEFAULT IS NOT JOINED IN HERE, AND THAT PLACEMENT IS DELIBERATE. B4 is what the
    body DEMANDS; a default is what the def SUPPLIES. Folding a `= None` default into the
    backward requirement would put `NoneType` beside `str` and manufacture a CONFLICT out of
    a `str | None` parameter that nothing is wrong with. `default_type` is exported
    separately so the caller can weigh the two kinds rather than having them pre-mixed.
    """
    return _method_pins(fn, param, path) + _argument_pins(fn, param, path)


def _expr(src: str) -> ast.expr:
    """Parse one expression statement — the selftest's fixture builder."""
    stmt = ast.parse(src).body[0]
    if not isinstance(stmt, ast.Expr):
        raise TypeError(src)
    return stmt.value


def _fn(src: str) -> ast.FunctionDef:
    """Parse one function definition — the selftest's fixture builder."""
    node = ast.parse(src).body[0]
    if not isinstance(node, ast.FunctionDef):
        raise TypeError(src)
    return node


def _named(w: Witness | None) -> str | None:
    """Return a witness's type, or None — so a case can compare without unwrapping."""
    return None if w is None else w.type_name
