---
name: feedback_targeted_edit_means_too_large
description: "needing targeted edits to a file IS the signal it's too large to reason through in one pass; decompose (theorem/lemma-per-file). Never leave a malformed file mid-edit."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Standing policy (user, stated firmly after I left a `where`-with-no-body
mid-edit and did serial targeted edits on a ~140-line SingerOrder):

"Don't let files get larger than you can reason through in one pass; if you
have to do targeted edits, the file is already too large, and requires
decomposition. That's why I have the theorem/lemma-per-file rule."

**How to apply:**
- Write each file so it fits in ONE Write call you can reason through whole
  (this is [[feedback_file_size_one_pass_rewrite]] sharpened: the trigger
  is "am I reaching for Edit to fix what I just wrote?").
- Needing a sequence of targeted Edits to make a file compile = the file is
  doing too much → split it (one theorem/lemma per file + a re-export
  shim), don't patch.
- NEVER leave a malformed file (incomplete `where`, dangling clause)
  between tool calls — write complete compilable units.
- Example of the violation: SingerOrder's structural proof bundled 4
  lemmas (singer-commutes + basis lemmas, iterate-commutes, order-on-basis,
  HasOrder-singer) in one file; by the theorem-per-file rule each wants its
  own file under a SingerOrder/ dir with a re-export. It landed as one
  file under regression-fix pressure; flagged as wanting decomposition.

Related: [[feedback_file_size_one_pass_rewrite]] (files fit one Write),
[[feedback_def_proof_separation_lever]] (def/proof split is one axis of
this), the theorem-per-file project policy.
