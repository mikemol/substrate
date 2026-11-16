---
name: s3-on-v4-file-per-lemma
description: agda/Substrate/Groups/Actions/S3-on-V4 decomposed to file-per-lemma (7 → 39 files) so similarity script can find cross-file twins
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

`Substrate.Groups.Actions.S3-on-V4` has been decomposed from 7 monolithic
section-headered files (Axioms, Composition, Dispatch, Generators,
HomRotations, HomSwaps, Twist; 53–127 lines each) into 39 file-per-lemma
modules under `S3-on-V4/{File}/{Lemma}.agda`. Each top-level file is now
a thin re-export shim.

Decomposition map:
- Axioms (4 files): ActCong, ActEpsilon, ActEpsilonN + re-export
- Twist (4): ActEqualsPow, SwapRotateTwist, RotPowSwapTwist + re-export
- Dispatch (3): ActOnCanonical, Act + re-export
- HomRotations (4): HomId, HomRot, HomRot2 + re-export
- HomSwaps (6): HomSwapAB, HomSwapAG, HomSwapBG, ActHomOnCanonical, ActHom + re-export
- Generators (11): Rotate, SwapAB, RotPow, SwapPow, RotPowAppend, SwapPowAppend, RotateCubeId, SwapSquareId, RotPowNormalizeEq, SwapPowNormalizeEq + re-export
- Composition (7): Block00, Block01, Block10, Block11, ActDotCanonical, ActDot + re-export

Pre-existing breakage fixed in the same pass: `canonical-is-fixed-Z3`
(stale name from pre-Cyclic refactor) renamed to `canonical-is-fixed`
in `Z2-on-Z3.agda` and `Composition.agda` (was previously preventing the
Actions/ tree from typechecking; Manifest didn't catch it because
Actions isn't in Manifest).

Why: the user's hypothesis was "if we can reach file-per-lemma in a
reasonably structured way, our similarity script will be extremely
effective at helping us decompose that which seems impossible to
decompose". Verified — after decomposition, `agda_similarity.py`
finds 10+ pairs at 0.66–0.79 similarity that the section-level layout
hid (e.g., HomSwapAG ↔ HomSwapBG @ 0.79, Block00 ↔ Block01/10/11
@ 0.68–0.70, HomRot2 ↔ HomSwapBG @ 0.66 cross-family).

How to apply: when a sub-tree's intra-file decomposition is unclear,
push to file-per-lemma first; then run similarity to find cross-file
twins; THEN extract universals or further sublime. The decomposition
itself doesn't shrink line count but it unblocks similarity-driven
universal recognition.

Sub-arc deferred: arithmetic generalization of inv-left/right/inv-canonical
(needs `∸-+-id` already staged in `Foundation.Nat.Properties.Sub` +
`inv-pos-add-mod` arithmetic proof in Cyclic). Would let per-Zₙ-Coxeter
drop canonical-cover + variadic pattern synonyms.
