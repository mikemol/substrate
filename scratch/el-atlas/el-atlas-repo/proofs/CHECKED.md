# Proof-tier check provenance

VerdictCrossbar.agda — CHECKED CLEAN
  checker : Agda version 2.6.3 (ubuntu 2.6.3-1build1)
  flags   : --safe --without-K  (in-file OPTIONS pragma)
  imports : NONE (self-contained; stdlib not required)
  command : agda --safe VerdictCrossbar.agda
  date    : 2026-06-11 (W13)
  theorems:
    swapE-involutive          — the rail swap is an involution (S5)
    swapV-involutive          — the verdict dual is an involution
    intertwine                — verdict ∘ swapE ≡ swapV ∘ verdict (S4 crossbar)
    no-single-rail-quotient   — the verdict map factors through no
                                single-Boolean quotient (S3 in miniature)
  note: the container is ephemeral; agda must be reinstalled to
  re-check (apt-get update; apt-get install -y --no-install-recommends
  agda). The .agda source is the durable artifact; .agdai excluded.
