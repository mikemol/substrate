---
name: feedback-file-size-one-pass-rewrite
description: "Files should be small enough to fully rewrite in one Write call; if a file requires effort to figure out how to patch via Edit, it's already too large — decompose via submodule hierarchy + public re-export."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---
<!-- POLICY: load-bearing discipline; full text at docs/governance/file_size_one_pass_rewrite.md -->

**Policy migrated to repository: see [`docs/governance/file_size_one_pass_rewrite.md`](file:///home/mikemol/github/substrate/docs/governance/file_size_one_pass_rewrite.md).**

This memory file now exists only as a pointer. The full policy content lives in the repository at the path above. When future sessions load this memory, they should follow the link rather than acting on stale content here.

Why migrated: this discipline applies to ALL contributors (human and LLM), and the substrate has produced concrete thresholds + decomposition precedent that benefit from being in-repo. Single source of truth: the repository file.
