#!/usr/bin/env python3
"""jea_omml_domain.py — Σ-OMML-DOMAIN: the audience-domain carrier.

OMML's presentation UNDERDETERMINES semantics: `f(x)` is application OR multiplication; `'` is
derivative OR prime; `ab` is one symbol OR a·b. The pass-11 finding: this is NOT a lossy gap to
disambiguate — it is a PARTITION to EXPOSE, and exposing it is a CrossMix CONSUMER (no new mechanism).
The lowerer emits BOTH strands into one Intern; `CrossMix.cross_term(App, Mul)` surfaces the fork
(head_agree=False, the divergence graded, each strand's commitment its residue).

WHAT SELECTS A STRAND is the presentation AUDIENCE — a type-theory paper reads `f(x)` as application,
a physics paper as multiplication, a mixed-domain document keeps the fork open. So the AUDIENCE IS A
CARRIER, the OMML analogue of CUDA's memory-space carrier: the meaning of the marks is carrier-
relative, and the carrier is the domain made explicit.

THE OBJECT (the recursive law on "commit vs stay-confounded": NOT two behaviors — one PARTIAL MAP,
defined vs undefined):
  * a Partition = a tagged CrossMul: (pattern_tag, strand_a, strand_b, cross_term). The tag names
    WHICH ambiguity produced it (ADJACENCY, PRIME, ...), so a Domain keys on the partition's own
    identity, not raw OMML.
  * a Domain = a PARTIAL map { pattern_tag -> chooser }, where a chooser picks 'a' or 'b' (or is
    absent). The domain only ADDS commitments where it has authority.
  * resolve(partition, domain) = APPLICATION of that partial map: where defined -> commit to the
    chosen strand (a Resolved); where the domain is SILENT -> the Partition passes through UNCHANGED
    (silence = identity; the fork is NEVER collapsed by a domain that lacks authority over it). This
    is the keep-the-residue discipline: a domain cannot erase a partition, only commit one it owns.

Composition of domains is partial-map OVERRIDE (a more specific domain extends/overrides a base one),
associative, with the empty domain as identity (resolves nothing — every partition stays open). So
domains form a monoid under override, and `resolve` is a monoid action on partitions.

FRONT-END-AGNOSTIC: this composes onto ANY tagged CrossMul. The real OMML lowering (emit App/Mul
strands tagged ADJACENCY, etc.) is separate work [Σ-OMML]; this module is the carrier that consumes
its output. Exercised here on a hand-built f(x) partition against the same real CrossMix surface."""
from __future__ import annotations
from dataclasses import dataclass, field
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, CrossMix, CrossTerm


@dataclass(frozen=True)
class Partition:
    """A tagged CrossMul: a presentation pattern that admits two semantic strands, with the cross-term
    that surfaces the fork. `tag` names the ambiguity kind (the key a Domain resolves on)."""
    tag: str                       # e.g. "ADJACENCY", "PRIME", "IMPLICIT_MULT"
    strand_a: int                  # interned id of the A-reading (e.g. App(f,x))
    strand_b: int                  # interned id of the B-reading (e.g. Mul(f,x))
    label_a: str = "a"             # human label for the A-reading (e.g. "application")
    label_b: str = "b"             # human label for the B-reading (e.g. "multiplication")
    cross: CrossTerm | None = None # the surfaced fork (head_agree=False where the readings differ)

    @property
    def confounded(self) -> bool:
        # a real fork iff the strands are NOT the same canonical node (degree>0 / heads disagree)
        return self.strand_a != self.strand_b


@dataclass(frozen=True)
class Resolved:
    """A partition a domain committed: which strand, by which tag-authority, the chosen interned id."""
    tag: str
    chosen: int
    reading: str
    via: str                       # the domain name that had authority


class Domain:
    """The audience-domain carrier: a PARTIAL map pattern_tag -> chooser('a'|'b'). A chooser absent =
    the domain has no authority over that ambiguity -> the partition stays open."""
    def __init__(self, name: str, choices: dict[str, str] | None = None):
        self.name = name
        self.choices = dict(choices or {})     # tag -> 'a' | 'b'

    def override(self, other: "Domain") -> "Domain":
        """Monoid op: `other` extends/overrides self (more specific wins). Empty domain = identity."""
        merged = dict(self.choices); merged.update(other.choices)
        return Domain(f"{self.name}+{other.name}", merged)

    def __call__(self, tag: str) -> str | None:
        return self.choices.get(tag)


def resolve(partition: Partition, domain: Domain):
    """Apply the partial map. Defined at this tag -> commit (Resolved); silent -> pass the Partition
    through UNCHANGED (the fork survives; a domain without authority never collapses it)."""
    if not partition.confounded:
        # not actually a fork (both strands the same node) -> already determinate; commit trivially
        return Resolved(partition.tag, partition.strand_a, partition.label_a, via="(determinate)")
    pick = domain(partition.tag)
    if pick is None:
        return partition                                   # silence = identity: stays confounded
    if pick == "a":
        return Resolved(partition.tag, partition.strand_a, partition.label_a, via=domain.name)
    if pick == "b":
        return Resolved(partition.tag, partition.strand_b, partition.label_b, via=domain.name)
    raise ValueError(f"chooser for {partition.tag!r} must be 'a'|'b', got {pick!r}")


def resolve_all(partitions: list[Partition], domain: Domain) -> list:
    return [resolve(p, domain) for p in partitions]


# ── named domains: the carrier made explicit per audience ────────────────────
EMPTY      = Domain("empty")                                          # resolves nothing (identity)
TYPE_THEORY = Domain("type-theory", {"ADJACENCY": "a", "PRIME": "a"})  # f(x)=application, '=derivative? no:
PHYSICS     = Domain("physics", {"ADJACENCY": "b", "IMPLICIT_MULT": "b", "PRIME": "b"})  # f(x)=mult, '=prime
#   (note: TYPE_THEORY leaves IMPLICIT_MULT open -- it has no standing convention there -> stays a fork)


if __name__ == "__main__":
    from jea_pyalg import IR
    print("=== Σ-OMML-DOMAIN: the audience-domain carrier resolves (or preserves) OMML partitions ===\n")
    I = Intern(); X = CrossMix(I)

    # build the f(x) ADJACENCY partition (App vs Mul) against the REAL CrossMix surface
    f = I.intern(IR(kind="Name", op="f", children=()))
    x = I.intern(IR(kind="Name", op="x", children=()))
    app = I.intern(IR(kind="App", children=(f, x)))
    mul = I.intern(IR(kind="BinOp", op="Mult", children=(f, x)))
    adj = Partition("ADJACENCY", app, mul, "application", "multiplication", X.cross_term(app, mul))

    # an IMPLICIT_MULT partition that physics resolves but type-theory leaves open
    a = I.intern(IR(kind="Name", op="a", children=()))
    b = I.intern(IR(kind="Name", op="b", children=()))
    juxta = I.intern(IR(kind="Name", op="ab", children=()))                 # one symbol "ab"
    prod  = I.intern(IR(kind="BinOp", op="Mult", children=(a, b)))          # a*b
    imp = Partition("IMPLICIT_MULT", juxta, prod, "single-symbol", "product", X.cross_term(juxta, prod))

    parts = [adj, imp]
    for dom in (EMPTY, TYPE_THEORY, PHYSICS):
        print(f"--- domain: {dom.name} ---")
        for r in resolve_all(parts, dom):
            if isinstance(r, Partition):
                print(f"  {r.tag:14} STILL CONFOUNDED (domain silent) — fork preserved: "
                      f"{r.label_a} | {r.label_b}  (cross degree {r.cross.degree})")
            else:
                print(f"  {r.tag:14} committed -> {r.reading!r} (via {r.via})")
        print()

    # composition: a base physics doc with a type-theory appendix (override)
    print("--- composition: PHYSICS.override(TYPE_THEORY) (appendix overrides base on ADJACENCY) ---")
    composed = PHYSICS.override(TYPE_THEORY)
    for r in resolve_all(parts, composed):
        if isinstance(r, Partition):
            print(f"  {r.tag:14} still open")
        else:
            print(f"  {r.tag:14} -> {r.reading!r} (via {r.via})")
