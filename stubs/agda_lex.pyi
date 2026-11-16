# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Signatures for `scratch/agda_lex.py` — THE Agda-text authority.

⚑⚑ WRITTEN TO UNBLOCK A DRAIN THAT COULD NOT OTHERWISE LAND. `tests/test_rederive_agreement.py`
holds four route-agreement classes that run BOTH routes over the live corpus and diff the sets —
the only instrument for the derived-view-divergence class, and the only site in the tree pinning
any of them. Draining it means re-homing those classes into modules written clean in one pass,
and every one of them must reach `agda_lex`. A bare `import agda_lex` from a clean module is
`import-not-found`, and the resulting `Any` propagates into every expression that touches it, so
the strict bar refuses the file. That is a fact about PACKAGING, not about the module: a `.pyi`
supplies signatures independently of packaging, which is the repair
`check_scratch_independence.pyi` and `tsdbprobe.pyi` already record.

⚑⚑ THE WHOLE PUBLIC SURFACE IS DECLARED, NOT THE SIX NAMES THE TESTS READ, and the reason is
measured and written down in `tsdbprobe.pyi`: `stubtest` requires every runtime name to be
present, so a narrow stub fails with one error per undeclared name. Narrowness buys silence only
with an allowlist that then has to be maintained against someone else's edits.

⚑⚑ A STUB IS A CLAIM, AND AN UNVERIFIED CLAIM ABOUT TYPES IS WORTH LESS THAN NO CLAIM — because
it TYPE-CHECKS. Both prior stubs in this tree record that their FIRST DRAFT invented declarations
from the shape the module *ought* to have (one invented five names and a `main` arity). This file
is therefore only as good as `scripts/check_stub_authority.py`, which runs `stubtest` over it.

⚑ ALMOST NOTHING HERE IS ANNOTATED AT SOURCE, so these parameter and return types are a READING
of the implementation, not a transcription. `stubtest` verifies NAMES and ARITY; it cannot verify
that `root: str` is what the body assumes. Where a body returns a structure the source never
names, `object` is the honest declaration — it forces a consumer to narrow rather than letting an
invented shape type-check.

⚑⚑⚑ BUT A READING THAT BOTTOMS OUT IS NOT A GUESS, AND `NEXT` / `MODULE_HEAD` / `SECTION` WERE
DEMOTED TO `object` BY THAT CONFLATION. Each is `re.compile(<str>)` at source;
`substrate.iface_construct --module scratch/agda_lex.py` computes all three with a `file:line`
witness (`:59`, `:887`, `:1106`). A type obtained by evaluating an assignment's own constructor is
correct by CONSTRUCTION — unfalsifiable, which is not the same as unwarranted, and the derivation
IS the verification. `object` is the honest declaration for a shape nothing determines; it is the
LAZY one for a shape the source states outright, and spending it there costs the distinction below.

⚑⚑⚑ `HEADER` IS THE SLOT THAT MAKES THAT DISTINCTION LEGIBLE, AND IT IS A DECISION, NOT DEBT. It
is an instance of a private class, deliberate at source: a drop-in for a compiled `^module … where`
pattern so six tools holding one as a pattern object did not need rewriting. Its `.search`/`.match`
return a duck-typed match, never a `re.Match`, so the protocol below declares only the two members
those call sites use — declaring `re.Match` would be exactly the fiction this file's second flag
warns about. ⚑⚑ AND THE DERIVATION AGREES INDEPENDENTLY: `HEADER` is the ONE assignment in this
module that does NOT bottom out, reported UNRESOLVED rather than filled with `Any`. So the author's
refusal of the top type and the reader's inability to resolve the slot pick out the same name.
**A DECISION AND AN INABILITY LOOK IDENTICAL WHEN BOTH ARE SPELLED `object`** — `HEADER` is
readable as a judgement only because the lazy spelling was declined here, which is precisely why
the derivable siblings above must not keep it.

⚑ `mask_comments` IS WRAPPED BY THE `l2` DECORATOR at source, so the runtime object is the
wrapper. It is declared here with the signature the wrapper forwards, which is the one every
caller actually uses.
"""

import re
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Literal, NamedTuple, ParamSpec, Protocol, TypeVar

_P = ParamSpec("_P")
_R = TypeVar("_R")

# ⚑ DERIVED FROM THE ASSIGNMENT, NOT ASSERTED ABOUT IT — each is `re.compile(<str>)` at source.
NEXT: re.Pattern[str]
BODY_DELIMS: str
SUFFIX: str
SUFFIX_LEN: int
MODULE_HEAD: re.Pattern[str]
SECTION: re.Pattern[str]

class _Match(Protocol):
    """The duck-typed match `HEADER.search`/`HEADER.match` return — never a `re.Match`."""

    def group(self, n: int = ...) -> str: ...

class _HeaderLike(Protocol):
    """The compiled-pattern shape `HEADER` stands in for."""

    def search(self, text: str) -> _Match | None: ...
    def match(self, text: str) -> _Match | None: ...

HEADER: _HeaderLike

class Stmt(NamedTuple):
    """One lexical statement span: its kind, the module it names, and its line range."""

    kind: Literal["import", "open", "variable", "other"]
    module: str | None
    start: int
    end: int
    text: str

def observed(reset: bool = ...) -> list[str]: ...
# ⚑ GENERIC, because the decorator wraps ANY function: it was first declared over the
# `mask_comments` shape alone and the `figures` shim (W4 file 5 cut 6) wraps a walk returning a
# census. `key_fn` takes the wrapped function's first positional argument, whatever it is.
def l2(
    consumer: str, key_fn: Callable[[object], bytes], derives_from: object = ...
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...
def warm_masks(sources: Iterable[str]) -> int: ...
def mask_stats() -> tuple[int, int, int, int, int]: ...
def mask_l2_stats() -> dict[str, object]: ...
def mask_comments(src: str) -> str: ...
def statements(lines: Sequence[str]) -> Iterator[Stmt]: ...
def group_statements(
    lines: Iterable[str], opener: Callable[[str], object]
) -> list[list[str]]: ...
def module_name(head: str) -> str | None: ...
def using_names(stmt_text: str) -> set[str] | None: ...
def mixfix_delims(names: Iterable[str]) -> set[str]: ...
def body_tokens(body: str, mixfix: Iterable[str] = ...) -> set[str]: ...
def mixfix_forms(name: str) -> set[str]: ...
def module_path(path: str, root: str) -> str: ...
def module_file(mod: str, root: str) -> str: ...
def agda_files(root: str, include_build: bool = ...) -> list[str]: ...
def agda_root_from(start: str) -> str | None: ...
def span_end(lines: Sequence[str], i: int) -> int: ...
def head_span(lines: Sequence[str], i: int, limit: int | None = ...) -> int: ...
def word(n: str) -> object: ...
def module_name_of(src: str) -> str | None: ...
def is_public_open(stmt_text: str) -> bool: ...
def module_scopes(src: str) -> list[tuple[str, int, list[str], int, int]]: ...
def binds_at(src: str, tok: str, lineno: int) -> bool: ...
def telescope_span(src: str) -> tuple[int, int] | None: ...
def telescope_groups(
    src: str, span: tuple[int, int] | None = ...
) -> list[tuple[list[str], str]]: ...
def imports_before(src: str, lineno: int) -> set[str]: ...
def sections(src: str) -> list[tuple[int, str, str]]: ...
def resolves_here(
    src: str, lineno: int, op: str, homes: object
) -> bool: ...
def intended_operator(
    src: str, lineno: int, op: str, index: object
) -> str | None: ...
def unresolved_sections(
    paths: Iterable[str] | None = ...,
) -> list[tuple[str, int, str, str, object]]: ...
