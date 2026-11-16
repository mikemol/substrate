---
name: feedback_decouple_deserialize_from_processing
description: "Complete tokenizing→structuring (deserialization) as a DISTINCT phase producing a structured object, decoupled from the structural processing that consumes it. If you call split/rsplit/parse, do NOT act on the elements right there — that welds deserialization to use. It is the same 'parameterize / expose-don't-collapse' move applied to deserialization / functional programming: parse once into a rich structure, then all downstream works on the structure, never re-parsing a string."
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Stated 2026-07-11 (⟡catalog-unhold-fp / the lift arc). Reviewing `reuse_catalog.DbBuilder.add`, the
user: *"DbBuilder is conflating tokenizing with structural processing. We should complete
tokenizing→structuring decoupled from structural processing; if we're calling 'split', we shouldn't be
doing anything with the elements right there; that's a deserialization step that needs to be distinct
from what uses the deserialized object. This is the same 'parameterized' move, applied to
deserialization/functional programming."* `add` was rsplit-ing qnames, peeling field-heads, traversing
the ref-graph, AND building db rows in one interleaved pass. Fixed: `deserialize_core(core) →
ParsedCore` (ALL tokenizing — every rsplit/peel/traverse — produces a structured `ParsedStruct`), and
`DbBuilder.add` consumes the structure (fp is a JOIN of already-split names, not a split; no split next
to a use-site). Behaviour-preserving (reuse-index.md byte-identical).

**Why:** interleaving "split X" with "use the pieces of X" is the deserialization analogue of the
mission's collapse-to-a-proxy: the raw string is re-tokenized at each use-site instead of being parsed
ONCE into a structure the consumers share. It is "parse, don't validate" — deserialize into a rich
typed object at the boundary; every downstream step reads fields of that object and NEVER re-splits a
string. Same root as [[set1-carrier-always-parameterize]] and the un-hold moves: EXPOSE the structure
(the deserialized object) as a first-class thing, don't COLLAPSE it into inline tokenize-and-act. The
tokenize/act conflation is also invisible to the dedup for the same reason semantic dups are (different
inline shapes), so decoupling it makes the deserialization reusable AND dedup-legible.

**How to apply:** when a function both PARSES (split/rsplit/regex/json/peel a tree) and PROCESSES
(build rows/fp/edges/emit), split it into (a) a deserialize phase returning a structured object
(namedtuple/dataclass with all fields pre-tokenized) and (b) a processing phase consuming that object.
The tell: a `.split()`/`.rsplit()`/`raw[...]` immediately followed by using the result — hoist the
tokenize to the deserialize phase, let the processor read the structured field. This is a standing lint
across the pipeline (many modules re-tokenize qnames inline); apply it wherever tokenize sits adjacent
to use. Sibling of [[feedback_lift_and_import_dont_reroll]] (share the machinery) — this shares the
STRUCTURE the machinery produces. Verify behaviour-preserving (byte-identical output) since it is a
pure refactor.
