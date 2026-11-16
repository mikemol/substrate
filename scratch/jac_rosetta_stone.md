# ⟡REGROUNDING #50 (2026-07-22) — ◆jac-gamma CLOSED: the literal statement, by a free-algebra UP lift. COMPACTION-SAFE, stands alone.

## STATE (one line)
**The whole ⟡jac-encoding-bridge Rosetta Stone is CLOSED at the LITERAL ℚ-function level.** `literal₁/₂/₃ :
(x y z) → evalℚ x y z R.fᵢ ≈ℚ C.fᵢ x y z` — machine-checked, `--safe --without-K`, no postulates/holes,
COMMITTED **`1856518`** (full build **1992/1992 PASS**, amend-marked). Modules: `JacobianExpr.agda` (the
`data Expr` + `encode` + `eᵢ` DEFINITION module) + `JacobianEncodingLiteral.agda` (the ≈ℚ hom PROOF).
Stack (6 unpushed, USER pushes): … `efe11c1` codecs → `0334648` β → `1856518` ◆jac-gamma. Tree CLEAN.

## THE RECURSIVE EITHER/OR COLLAPSE (this arc's invariant)
Every fork collapsed to ONE move: **the wall is INFERENCE, so SUPPLY the endpoints STRUCTURALLY (by a
free-algebra fold), never hand-pin/codemod the deep composition.**
- "restore the wall module + fix gen-v  vs  build fresh" → NEITHER: the wall module is a WALL-WITNESS (its
  local `≈⟨_⟩_` reasoning-combinator walls UNIVERSALLY under eta-`ℚ`, even `assoc-lll`; the compaction
  summary's "everything compiled except gen-v" was inaccurate). The positive close is a different object.
- "hand-pin γ  vs  codemod-pin γ" → NEITHER (user, twice): use the LAWVERE/EXTRUDER machinery — prove only
  the SHALLOW generator/hom laws, lift the DEEP composition by a UNIQUENESS induction (compiles; no deep ≈ℚ
  inference). The extractor (`jea_agdai.decode_core`) then materializes the pinned deep terms from the `.agdai`.
- "β+γ (distribute Cᴹfᵢ)  vs  opaque *P-homomorphism" → the UP-lift SUBSUMES both: `homAgree` is the
  evaluator-hom lifted by the free-`Expr` UP, staying factored, matching C's grouping.
- "bespoke `Expr`  vs  SPPF `inside-unique`" → both are free-algebra UPs; `Expr` NATIVELY carries negation
  (`⊖E`), which the free-SEMIRING SPPF cannot — so `Expr` is the honest minimal free-comm-RING term here.
- Deepest bottom: `homAgree` IS the codec `φ = evalℚ` lifted by the free-`Expr` universal property — the
  same `cong φ bridge` operational law, at C's LITERAL syntactic form. [[project_center_free_universal_property]].

## RETROSPECTIVE (gated)
- **G0.** Close ◆jac-gamma (`evalℚ R.fᵢ ≈ℚ C.fᵢ`), using the extruder/UP machinery, not banked prose.
- **G2 delta.** POSITIVE (closed + gated), via TWO user redirects. I executed the LOSSY compaction summary
  first — restored an uncompilable wall-witness, then reached to hand-pin then CODEMOD the proof. User
  stopped both and pointed at the machinery + "re-read the rosetta stone." Re-reading recovered the method.
- **G3 cause.** ROOT = ran the compaction summary as ground truth instead of recovering the arc's durable
  cotype (the Rosetta Stone) FIRST — [[feedback_recover_cotype_after_compaction]], which FIRED AGAIN via the
  user (a memory is skippable — the honest ceiling). Contributing = the mediation-guard: reaching for the
  DIRECT move (hand-pin/codemod) instead of the shadow structure (the free-algebra UP lift).
- **G6 sustain (PROTECT).** INCREMENTAL isolate-check (stage 1 rearrange → stage 2 hom-laws → stage 3
  Expr/homAgree, each EXIT 0 before proceeding — de-risked ~30 pinned lemmas); the wall-is-inference finding
  held (every pinned lemma landed); reuse-search via a mapper agent (found ℚ-Semiring/inside-unique/that
  shallow-laws-must-be-built) BEFORE building; GATE PAYDOWN not bypass (carrier-locality + def/proof fired →
  `_≋_` relation + def/proof split, never `--no-verify`); ran the gate scripts DIRECTLY (fast) before the
  heavy full-build commit; immediate revision on each user redirect.
- **G8 handoff.** operator=other residue: (i) whether the SPPF-`inside-unique-over` route is preferred over
  the bespoke `Expr` (a reuse-purity judgment; `Expr` is machine-checked faithful via the refl-equalities);
  (ii) whether `det Jac F ≈ℚ −2` deserves a matching LITERAL-ℚ statement (the counterexample's OTHER half).
- **G9 escalate.** Both memories widened (2026-07-22 instances): `recover_cotype_after_compaction` (the
  recurrence) + `project_center_free_universal_property` (the UP-lift method + the extractor). This
  regrounding IS the coverability move (the arc cotype made prominent).

## SHADOW-ENGINEER (Fano)
- **L₆ guard-reconstitution — the arc's defining pattern.** Each DIRECT move (restore-wall+fix-gen-v;
  hand-pin γ; codemod-pin γ) was REJECTED by the user's guard and RECONSTITUTED through the shadow structure
  (the free-`Expr` UP + `homAgree` uniqueness + the extractor). The guard's prohibition PRODUCED the correct
  architecture: the deep degree-9 tree became the INDUCTION, not a hand-pinned chain.
- **L₁ positive-closure** — the literal close delivered + committed (`1856518`).
- **S₃-fixed core:** every landing is a CODEC φ LIFTED BY A UNIVERSAL PROPERTY; the literal level is that
  move at C's syntactic form. **⟡pyrig-object-carrier** remains the standing live edge — and `Expr` (the
  free comm-ring term on 3 gens) is a small step toward that object universe.

## LABELED ⟡ NEXT STEPS (specify by symbol)
### STANDING / IMMEDIATE
- **⟡push** — 6 unpushed (`937800d`…`1856518`), all amend-marked, tree clean; the USER pushes (`git fetch` + ff).
### ROSETTA COMPLETION (the encoding-bridge arc; optional/polish)
- **⟡rosetta-capstone-wire** — wire `literal₁/₂/₃` back into the capstone as the TERM that closes its flagged
  "single-object-identification gap" (a re-export / apex citing the literal close + the codec routes). Small.
- **⟡jac-det-literal** — the OTHER half: a literal-ℚ `det Jac F ≈ℚ −2` mirroring the components (the capstone
  `be4324b` has detJac via the WEDGE at the residue level; a literal-ℚ det statement completes the ℚ picture).
- **⟡jac-literal-via-sppf** — OPTIONAL reuse-purer variant: route the literal through `inside-unique-over`
  (the ≈ℚ-parameterized mirror of SPPF `inside-unique`, ~10 lines — the mapper's one load-bearing build,
  reusable for ANY free-semiring hom into a setoid) instead of the bespoke `Expr`. Needs the negation bridge
  (`a −ℚ b ≈ℚ a +ℚ (−1)·b`) SPPF lacks. NOT needed (Expr already closes it); a consolidation, not a gap.
- **⟡pin-quot-relation** — the STANDING open (below §DEEPER UNIFICATION): the exact in-tree term algebraically
  relating log/quotient/antilog as `quot()`s (candidates `_≈D_` Grothendieck quotient / div-mod `recon` /
  `NilpotentLogExpBridge`). Searched, not singled out.
- **⟡loose-eq-synonym** — MINOR: the `_≋_` device (loose-fixity ≈ℚ synonym for the `*ℚ`/`≈ℚ` level-20 parse
  collision) is local to JacobianEncodingLiteral; home/generalize only if it recurs.
### STANDING MISSION EDGE
- **⟡pyrig-object-carrier** — the mission's live edge (what IS the pyast rig-cat's Set₀ object carrier);
  `Expr` is a concrete free-term-algebra instance in its vicinity.

## SATURATED SPECS (2026-07-22, 3 read-only agents; turn-key, file:line-grounded — survive compaction)

### ⟡jac-det-literal — SATURATED (agent a7c7b8cb). VERDICT: the honest form is MPoly-evaluated; 4-line reuse, ALL ingredients EXIST.
`R.detJac` (`JacobianResidue.agda:192-199`) = the 6-term Leibniz det (∂-products + `kP (-suc 0)` sign carriers,
`∂x/∂y/∂z:151`, `kP:175`). `normalize R.detJac ≡ kP (-suc 1)` (= −2) is ALREADY refl (`JacobianCounterexample.agda:
47-48` `norm-detJac-is-const`, also field `det-is-const-neg2`). THE STATEMENT + EXACT PROOF (append INSIDE
`module _ (x y z)` in `JacobianEncodingLiteral.agda` after `literal₃`; reuses private `E` + public `gen-kP:199`):

    detJac-literal : E R.detJac ≋ ℤ→ℚ (-suc 1)
    detJac-literal =
      ≈ℚ-trans {E R.detJac} {E (R.kP (-suc 1))} {ℤ→ℚ (-suc 1)}
        (β.normalize-eval x y z R.detJac)   -- keeps detJac STRUCTURAL (walks the pre-computed spine, no re-distribute)
        (gen-kP (-suc 1))                    -- evalℚ (kP (-suc 1)) ≈ℚ ℤ→ℚ (-suc 1)

`gen-kP` is PUBLIC (only `E`/`eT`/`mv` are private); NO new imports (R.detJac/R.kP via the `import … as R`;
`ℤ→ℚ`/`-suc_`/`β`/`≈ℚ-trans` already in scope); NO `data`/`record` (def/proof gate inert). `ℤ→ℚ (-suc 1) = mkℚ
(-suc 1) 0` is the HONEST form — NO canonical `-2ℚ` literal exists (only `2ℚ/3ℚ/4ℚ` at `JacobianCollision:54`).
⚑ HEAP: heaviest single obligation of the cluster (raw `detJac` = 6 products-of-triples) but LINEAR (normalize-eval
walks the pre-computed list, never re-distributes) — same KIND as β's evalBridge, just bigger; build as its own
checked unit, time it. CURRIED-ℚ 3×3 det of `C.fᵢ` is ABSENT (search-by-method: only MPoly `∂` exists, no ℚ→ℚ
derivative) and NOT needed — the honest analog mirrors `identify₁/₂/₃` (evaluate the MPoly, not a curried construct).
OPTIONAL capstone field (mirrors identify): `det-literal : (x y z) → β.evalℚ x y z R.detJac ≈ℚ ℤ→ℚ (-suc 1)` =
`L.detJac-literal`; needs `open import …Q.Embeddings using (ℤ→ℚ)` (the ONE new capstone import; `-suc_` already there).

✅✅ **BUILT 2026-07-22 — ⟡jac-det-literal LANDS at ~85 MB (was >3 GB), gate-safe. The >3 GB was NOT the proof; it
was THREE STACKED def/proof-SEPARATION MEMORY ANTI-PATTERNS (`scripts/check_def_proof_separation.sh`: an import
deserializes the full closure incl. proof terms at ~40×). The user pointed at the gate; reading it dissolved the
"wall".** [[feedback_declaring_a_wall_is_the_rebuild_reflex]] fired: my first verdict "DO NOT BUILD / gate-infeasible"
was the wall-reflex — the bare `normalize-eval x y z R.detJac` elaboration is only **63 MB / 1.5 s** (measured, imports
β+R only). The blowups were all IMPORT/UNFOLD costs, each fixed by SPREADING OVER MODULES:
1. **importing the γᵢ giant.** The first "isolated" `JacobianDetLiteral` did `import JacobianEncodingLiteral` just for
   `gen-kP` → deserialized L's degree-9 γ₁/γ₂/γ₃ closure at ~40× → >3 GB. FIX: split `JacobianEncodingLiteral` into
   three: `JacobianEncodingGen` (E/eT/mv + monoval + gen-X/Y/Z/kP — the MINIMAL generators) · `JacobianEncodingHom`
   (§0/§1 point-free lemmas + `Point2`: `homAgree` + `*P`/`+P` laws) · `JacobianEncodingLiteral` (thin: γᵢ/literalᵢ,
   opens Point/Point2). L's `literal₁/₂/₃` interface is BYTE-IDENTICAL (E = β.evalℚ, ≋ = ≈ℚ) so the capstone wiring is
   untouched. Measured: Gen 70 MB · Hom 87 MB · L 892 MB · capstone 558 MB — all <1 GB.
2. **deserializing the whole engine.** detJac importing `JacobianEncodingHom` (for gen-kP) still deserialized §3/§4
   (`homAgree`/`*P` proofs) at 40× → 1.12 GB. FIX: detJac imports ONLY the minimal `JacobianEncodingGen`.
3. **unfolding `Point.E` across the raw det.** Pinning the outer `≈ℚ-trans` with `E` (= opened `Point.E x y z`) forced
   unfolding `Point.E` over the HUGE `R.detJac` inside the trans implicit → 1.12 GB. FIX: pin the det/normalize
   endpoints with `β.evalℚ x y z` DIRECTLY (matches `normalize-eval`'s result syntactically, no reduction); take only
   `gen-kP` from `Point` (it touches the tiny `R.kP`, unfold is free). ALSO isolate the `normalize R.detJac ⇒
   R.kP (-suc 1)` reduction in a local `nd = refl` + `cong (β.evalℚ x y z) nd` so the trans node never reduces the det.
THE FINAL TERM (`Substrate/Algebra/Q/JacobianDetLiteral.agda`, `module _ (x y z)`, `open Point x y z using (gen-kP)`):

    nd : normalize R.detJac ≡ R.kP (-suc 1)  ;  nd = refl
    detJac-literal : β.evalℚ x y z R.detJac ≈ℚ ℤ→ℚ (-suc 1)
    detJac-literal =
      ≈ℚ-trans {β.evalℚ x y z R.detJac} {β.evalℚ x y z (normalize R.detJac)} {ℤ→ℚ (-suc 1)}
        (β.normalize-eval x y z R.detJac)
        (≈ℚ-trans {β.evalℚ x y z (normalize R.detJac)} {β.evalℚ x y z (R.kP (-suc 1))} {ℤ→ℚ (-suc 1)}
          (β.≡→≈ℚ (cong (β.evalℚ x y z) nd)) (gen-kP (-suc 1)))

⚑ **NOT a capstone field.** `IsJacobianCounterexample` declares a `record` (a def-provider); a `det-eval` field would
import detJac-literal's heavy `normalize-eval` proof, deserialize it at 40×, and OOM the capstone (MEASURED 1.12 GB) —
the def/proof mechanism recurring. So the capstone HOLDS the cheap rigid `det-is-const-neg2` (refl) and REFERENCES the
ℚ-eval companion by comment; detJac-literal is a standalone corollary module. All gates clean (def/proof · carrier ·
sumtype · import-shape · makefiles regenerated). This CORRECTS the SATURATION ⚑ HEAP line: the "LINEAR / just bigger"
note was optimistic on the constant BUT the deliverable is feasible — the fix was the module split, not a smaller proof.

### ⟡jac-literal-via-sppf — SATURATED (agent a28ef306). VERDICT: genuine but MODEST consolidation (reuse-pure, ~lateral lines). Build `inside-unique-over` REGARDLESS (reusable); the jac-rewrite is optional.
THE ONE LOAD-BEARING BUILD = **`inside-unique-over`** (~14 lines, append to `Algebra/Semiring/SPPFUP.agda` inside
`module _ (S)(v)`; makes the existing `inside-unique` its `_≡_` instance — a strict generalization mirroring
`fold-unique`/`fold-unique-over`). `inside-unique` (`SPPFUP.agda:44-58`) hardcodes `_≡_` and the `Semiring` is LAW-FREE
(only names `_×_`=*-monoid, `_+_`=+-monoid, `1×`=ε; `SPPFUP.agda:39-41`). Template `fold-unique-over`
(`OrientationUniversal.agda:84-98`, header `:62-81`: consumes ONLY trans + the two congruences, NO refl/sym). The
mirror parameterizes `(_≈_)(≈-trans)(×-cong)(+-cong)`; discharge with `≈ℚ-trans` (`Q/Equiv.agda:50`), `*ℚ-cong`/
`+ℚ-cong` (`Q/Properties/Congruence.agda:33/43`). `≈ℚ-refl` NOT needed by the induction.
- `SPPF` (`SPPF.agda:34-41`, `gen/one/_⊗_/_⊕_`), `inside : Semiring A → (G→A) → SPPF G → A` (`:48-52`, ⊗↦*-monoid,
  ⊕↦+-monoid, one↦ε). `ℚ-Semiring` (`Q/AsModule.agda:215-223`; `_×_`=`*ℚ`, `_+_`=`+ℚ`, `1×`=`1ℚ`); `ℚ-Ring:225`.
- INSTANTIATION: `data Gen {gX gY gZ; gK : ℤ→Gen}` (constants are ℤ-labeled leaves, NOT built from `one`/`⊕`);
  `v-dir : Gen→ℚ` (gX↦x…, gK k↦ℤ→ℚ k) → `hᶜ = inside ℚ-Semiring v-dir`; `encodeSPPF : SPPF Gen → MPoly`
  (gen gX↦R.X…, gK k↦R.kP k, one↦R.𝟙P, ⊗↦*P, ⊕↦+P) → `hᴹ = β.evalℚ x y z ∘ encodeSPPF`. `tᵢ : SPPF Gen` mirrors
  `eᵢ` (JacobianExpr) 1-to-1 (⊕E→⊕, ⊗E→⊗); `encodeSPPF tᵢ ≡ Cᴹfᵢ` refl.
- The 4 UP obligations ARE the already-pinned lemmas in `JacobianEncodingLiteral`: `hg`=`gen-X/Y/Z/gen-kP`,
  `h⊗`=`evalℚ-*P:255`, `h⊕`=`evalℚ-++:233`; only `h1 : E R.𝟙P ≈ℚ 1ℚ` is a NEW ~2-liner (`evalℚ-single`+`monoval-000`).
- ⚑ NEGATION CRUX SURVIVES (does NOT dissolve). SPPF is a free SEMIRING — no `⊖`. f₁/f₂ (no subtraction) route
  CLEANLY (`inside … tᵢ ≡ C.fᵢ` refl). f₃'s `_-ℚ_` → transcribe each `a−b` as `a ⊕ (gen (gK (-suc 0)) ⊗ b)` (matching
  R.f₃/Cᴹf₃), so `inside … t₃` reduces to `a +ℚ (ℤ→ℚ(-suc 0) *ℚ b)` — NOT `C.f₃`'s `-ℚ` shape → needs a post-hoc
  bridge (`a -ℚ b = a +ℚ (-ℚ b)` is refl via `Q/Sub.agda:17`; `ℤ→ℚ(-suc 0)*ℚw ≈ℚ -ℚ w` = the EXISTING inline
  `neg1w`/`neg1`+`neg-*ℚ-l`+`neg-cong`, `JacobianEncodingLiteral.agda:315-322`) applied at the 2 sites via
  `+ℚ-cong (≈ℚ-refl _) neg1`. ~8-12 lines. So f₃ ALSO routes through the semiring UP, just with the negation tail.
- VERDICT: deletes ~87 bespoke lines (`Expr`+`encode`+`eᵢ`+`evalDirect`+`homAgree`), builds ~58 (14 reusable). Not a
  line win; STRICTLY better on the SHARED-UP axis (the deep uniqueness becomes the substrate's own free-semiring
  initiality — the SAME theorem grounding `PyAstRig.pyEval = inside`, `SPPFUP:13-21`), and the 6 shallow hom laws are
  reused UNCHANGED. Optional (bespoke already closes it); build `inside-unique-over` for the strengthened SPPFUP.

### ⟡pin-quot-relation — SATURATED (agent a7f576cf). VERDICT: the center is `split-Canonical`; the div-mod wedge IS an instance; but C1/R4 are NOT wired — a small 3-step BUILD makes it ONE term. (⚑ tree root is `agda/Substrate/`.)
**THE ONE REALIZED TERM = `split-Canonical`** (`Algebra/Quotient.agda:140-149`): `(F : A→B)(s : B→A)(retract :
F(s y)≡y) → Canonical (ker-Quotient F)` — "a quotient-to-canonical-form IS `s ∘ F`" (`canonical = s∘F`). Plus
`idem-Canonical` (`:155`), `Canonical` (`:71`), `ker-Quotient` (`:134`). Header (`:107-127`) NAMES the cluster
(wedge recon, ℚ reduce, eval/reify, CRT, Coxeter normalize, EEA CF).
- THE WEDGE `recon q b r` IS `split-Canonical`, TWICE (verbatim): `WedgeValue-Canonical = split-Canonical
  recon-pair divide-pair recon-divide` (`Algebra/Nat/GCD/WedgeCanonical.agda:53`, `recon-pair (q,r)=q*suc b+r`);
  `wedge-Canonical = split-Canonical U F forget∘free` (`Algebra/Wedge/Adjunction.agda:134`). The wedge core:
  `DivStr {z, recon:C→C→C→C}` (`Algebra/Wedge.agda:53-56`), `Wedge {quot, rem, wedge-eq : a ≡ recon q b r}` (`:65-69`).
- THE ADJUNCTION SPINE (`a=recon q b r` IS Free⊣Forgetful's triangle): `Algebra/Wedge/Adjunction.agda` `triangle=
  forget-correct` (`:96`), `comparison = rem(divide a)` ("the adjoint comparison IS the residue" `:137`). Residue =
  orientation = Lehmer digit = counit-defect: `WitnessTower/Wedge/Adjunction.agda:70-72` `counit-defect-is-
  orientation`, `Orientation n = Fin(suc n)` (`:41`).
- OTHER `split-Canonical` INSTANCES (grep, 7 total): `UPTerm-Canonical` (`Category/UniversalProperty/Eval.agda:161`),
  `TmDB-Canonical` (`…/TmDBGodel/Properties.agda:110`), `factor-Canonical` (`Algebra/Nat/Prime/Properties.agda:273`),
  `ir-Canonical` (`Algebra/Quotient/IRRetraction.agda:76`, jea extruder Skeleton×Residue = recon shape),
  `sign-Canonical` (`Algebra/Quotient/PermSign.agda:108`). Confirms [[object-universe-is-split-canonical]].
- THE TRANSPORT SHAPE = **`Bridge`** (`Algebra/Wedge/Bridge.agda:40-46`): a DivStr-hom `translate(recon₁ q b r) ≡
  recon₂ (translate q)(translate b)(translate r)` — carries one route's canonical form to another (the reification
  of the Rosetta operational law `φ-route = cong φ bridge`). `LaxBridge` (`:90-96`): the negative-capable form whose
  `gap` wedge IS the residue of a non-hom. BUT NOT instantiated for the actual Rosetta φ's (railify/codecify land by
  bare `cong φ`, not a `Bridge` record).
- ⚑ THE HONEST GAP (the two routes the user most wants unified are NOT wired): C1 `codec-inverse`
  (`Algebra/ExpLogCodec.agda:71`, additive-neg↔mult-reciprocal) is STANDALONE — not a `Bridge`/`split-Canonical`.
  R4 `_≈D_` (`Algebra/Z/JacobianNegSemiring.agda:84`, `(a,b)≈D(c,d)=a+d≡c+b`) is a BARE RELATION wired to nothing
  (`split`/`split-hom:106`). `NilpotentLogExpBridge` is morally a LaxBridge but not typed as one. `⟡jac-neg-cover`
  (`JacobianNegSemiring:161`, `CommRing:152`) is a PLANNED apex (prose flag "an ExpLogCodec ℤ with each route derived
  through it"), NOT an existing term (grep: no cover record). So C1/R4 share only the `recon q b r` SHAPE + doc prose.
- THE SMALL BUILD to make it ONE term (all off `split-Canonical`, ~5-15 lines each): (1) R4 → `groth-Canonical =
  split-Canonical (_⊖_) split split-⊖` (`split-⊖:101` is 90% of the retract); `_≈D_` = `KerRel _⊖_` up to rearrange.
  (2) C1 → retype `expL` as a `Bridge` (additive DivStr → multiplicative DivStr), `respects = exp-⊕`, `codec-inverse`
  = `transport` of the `x⊕neg x≡𝟘` wedge; `NilpotentLogExpBridge.bridge-below:58` is the same content as a partial
  LaxBridge. (3) C2 → `idem-Canonical normalize normalize-idem`. After (1)-(3) all four routes + the div-mod wedge
  are `Canonical (ker-Quotient F)` = `split-Canonical`/`idem-Canonical` instances, cross-linked by `Bridge`s off the
  `recon q b r` shape. ⟹ the term "exists" as `split-Canonical`; the C1/R4 instances closing the claim are a
  well-scoped BUILD, not yet in the tree.

---

# ⟡jac-encoding-bridge — THE ROSETTA STONE

**One identity, read across a product of orthogonal machineries — machine-checked where it can be, blocked-with-a-reason where it can't.** The deliverable is the lattice itself: it teaches *why* the obvious hand-proof is a wall and *how* the substrate's canonical-form machinery lands the same theorem.

---

## THE IDENTITY (the single theorem, the whole Stone)

    evalℚ x y z R.fᵢ  ≈ℚ  C.fᵢ x y z          (i ∈ {1,2,3})

HALF A's curried-ℚ `C.fᵢ` (`Algebra/Q/JacobianCollision.agda`) and HALF B's `MPoly`-over-ℤ `R.fᵢ`
(`Algebra/Z/JacobianResidue.agda`) are the SAME paper map F (the Jacobian-conjecture counterexample). Proving it
closes the capstone's flagged "single-object-identification gap."

---

## THE CENTRAL INSIGHT — enumeration = normalisation (LehmerPath is the theorem)

The three axes of the Stone (compose-by-hand · route-spine · synthesiser) look independent. They are not. **They
all collapse to one operation: `normalize`.**

- `LehmerPath n ≅ Perm n` (`WitnessTower/LehmerPath.agda`, both round-trips proven `decode-encode`/`encode-decode`):
  a Lehmer path is a *decorated witness walk* — each rung carries a factoradic choice `Fin (suc k)`. `decode` is the
  walk (`insert-at` per step), `encode` peels it back. **The factoradic code IS the canonical form** — every
  permutation equals the decode of its own *unique* path.
- `AgdaExtrude.enum≤` is smallest-first; `extrude = find-first spec (enum≤ bound)` returns the first hit =
  **minimal-by-construction**. Because the enumeration *order* is the factoradic/canonical order,
  minimal-by-construction ≡ **normal-by-construction**. So `encode` = normalize, `enum≤` = walk-the-canonical-order,
  first-hit = the normal form. **The extruder-in-canonical-order IS the normalise-and-compare tactic** — they were
  never two things, and LehmerPath is the proof that they're one.
- **Meta-reflection = the jea extractor on the `.agdai`.** The `.agdai` is the elaborated, interned core = the
  canonical normal form of the proof term; interning *is* canonicalisation (content-addressed, children-as-ids).
  Reading it (`jea_agdai.decode_core`) is normalisation one grade up — reflecting on the proof's canonical
  structure. (It is lossy for *re-emitting source*, and no core→source emitter exists — so extraction reads the
  normal form, it never round-trips text.)

⟹ The synthesiser is not a new machine and not the untyped SKI extruder. It is **`normalize`**, which the repo
already has (`MPolyNormalize.normalize` + `MPolySemiring.coeff-canonicity`), with the extruder as its
enumerate-shaped twin.

---

## THE WALL (why the hand proof cannot be written in this ℚ)

`_≈ℚ_` (`Q/Equiv.agda:37`) is a **transparent** cross-multiplication `≡` over an **eta-record** `ℚ`. So
`≈ℚ-trans`/`≈ℚ-sym`/`*ℚ-cong`/`+ℚ-cong` each must READ their endpoints from a sub-proof's `≈ℚ` type — and reading
any endpoint unfolds `≈ℚ` to non-injective `num`/`den-1` → unsolved metavariables. **This fails even when EVERY
implicit is pinned explicitly** (the inner `≈ℚ-sym`/`*ℚ-cong` must in turn read *their* endpoints; pinning is
infinitely recursive). `Field.agda` avoids the whole class by never composing `≈ℚ` — it matches `mkℚ` and reasons at
ℤ. Infeasible by hand for a degree-9 polynomial. **Verified empirically: EXIT 1.**

---

## THE LATTICE — one identity, N machineries

⚑ **The three "BLOCKED" verdicts below were WRONG — relayed absence-claims (the absence-word trap: I did not search
the substrate's named centers first). Structural search REFUTES all three; each dissolves into the same
quot()-to-canonical-form as C2, and the ⟡jac-neg arc already BUILT them for the determinant half.**

| Route | Machinery | Verdict | Evidence | Why / the center that dissolves it |
|---|---|---|---|---|
| **A** hand `≈ℚ-trans`, explicit endpoints | `Q/Equiv` + `Congruence` + `Field` | **WALL** | `JacobianEncodingBridge.agda` → **EXIT 1** (`UnsolvedConstraints`, `_a′.num`/`_b.den-1`) | fully-pinned still leaks `num` metas — reading any endpoint unfolds transparent `≈ℚ` |
| **B** local `IsRelatedTo` wrapper / opaque `_≋_` | data-wrapper rigidifying the relation | **WALL** | probed | fixes trans endpoint-recovery, NOT cong; opaque does not block unification-unfold |
| **C2** `normalize`, rigid ℤ `≡` | `MPolyNormalize.normalize` + `coeff-canonicity` | **LANDS-BY-REFL** ✅✅ | `JacobianEncodingNormalize.agda` → **EXIT 0** (`bridge₁/₂/₃ : normalize R.fᵢ ≡ normalize Cᴹfᵢ = refl`, the ENCODING BRIDGE itself); + `JacobianCounterexample.norm-detJac-is-const` (detJac) | `normalize` = quotient MPoly by the sorted-canonical relation; `Cᴹfᵢ` = C's own grouping (right-assoc, `-ℚ b` = `kP (-suc 0) *P b`) → non-trivial `refl` (reassoc + combine + sign-fold to one canonical list). Rigid ℤ, zero `≈ℚ` |
| **C1** log/antilog codec (ExpLogCodec) | `ZPow`/`expℤ` (`GValueLSpace.Primes`) + `codec-inverse` | **LANDS** ✅✅ | `JacobianEncodingCodec.agda` → **EXIT 0** (`codecBridge₁/₂/₃ = cong codecify bridgeᵢ`; `neg-transport`; `codec-discriminates`) | ~~SPPF has no negation~~ — **negation TRANSPORTED, not fielded**: `codecify` maps each coeff through `expℤ z = 2^z`, so f₃'s `−3`→`2⁻³` (reciprocal, NO additive inverse). Propositional `≡` on `List (Mono × ℚ)`, zero `≈ℚ` composition. (Full SPPF-`inside` wiring is a deeper layer; the load-bearing dissolution — the codec — is machine-checked here) |
| **R3** ring-solver / "Expr→Canonical+sound" | **ExpLogCodec + other codecs + GradedProductOver** | **NOT BLOCKED** ✅ | codecs above + `OrientationBimonoidal` GradedProductOver | ~~no solver~~ — **the codec IS the sound decider**: `exp-⊕`/`exp-𝟘` ARE the soundness (a monoid hom, `coeff` touches only `{0ℤ,+ℤ}`); GradedProductOver is the graded/rail carrier; the moves relate as **quot()s** (§ below). Not Agda-reflection; a codec/quotient decider |
| **R4** semiring / Grothendieck rails | **GradedProductOver ℕ×ℕ** (`JacobianNegSemiring.split`) | **LANDS** ✅✅ | `JacobianEncodingRails.agda` → **EXIT 0** (`railBridge₁/₂/₃ = cong railify bridgeᵢ`) | negation ELIMINATED by TRANSPOSITION into `GradedProductOver _+_ 0 (λ _ → ℕ)` = the ℕ×ℕ difference-pair; `railify` splits coeffs (f₃'s `−3`→`(0,3)`); **transported from C2's `bridgeᵢ` by `cong`** — no ℤ, no ℚ, no fresh proof |

## THE OPERATIONAL LAW (demonstrated: C2 lands ⟹ every route lands)

**C2's `.agdai` is the single materialised canonical core** (jea `decode_core` → 138 nodes / 8 units: `bridge₁/₂/₃`,
`Cᴹf₁/₂/₃`, `Cu/Cv`). Every landing route is a **codec `φ` applied to the one canonical identification**:

    φ-route  :  φ (normalize R.fᵢ)  ≡  φ (normalize Cᴹfᵢ)   =   cong φ bridgeᵢ

- **C2** — `φ = id` (the bridge itself, `refl`).
- **R4** — `φ = railify` (split coeffs → ℕ×ℕ rails, subtraction-free). `cong railify bridgeᵢ`, **EXIT 0**.
- **C1** — `φ = inside`-fold into a codec semiring (negation via `ExpLogCodec` log/antilog). Once `φ` is wired, `cong φ bridgeᵢ` lands it — the SPPF→codec `φ` is *instantiation to build*, not an obstruction.
- **any evaluator/normalizer/transport** — the same `cong φ bridge`.

⟹ A route is never "blocked" — it is at most "needs `φ` built." The wall (A/B) is the *only* genuine obstruction,
and it is exactly the case with NO such `φ` (hand-composing `≈ℚ` never reaches a canonical form). This is the
quot()-unification operationalised: C2 is the quotient-to-canonical-form; every other route is a further quotient-map
`φ` off the same canonical object — extracted once (the `.agdai`), re-codec'd many.

**The Stone in one line:** hand-composition is a *wall* (A/B, EXIT 1). Every OTHER route lands — through **one and
the same move: quotient to a canonical form** — the substrate simply names a different codec for each. C2 is
`normalize` (quotient MPoly); C1 is SPPF-intern + the log/antilog codec (negation as a quot()); R4 is the ℕ×ℕ
Grothendieck difference-pair (quotient by `a−b≡c−d`). The negative branches teach *why the transparent-ℚ
presentation defeats you* — and every positive branch is the same quotient-to-canonical-form.

## THE DEEPER UNIFICATION — every route is a `quot()` (the user's third pointer)

The routes are not alternatives; they are one operation read through different codecs. **Each is a quotient to a
canonical representative:**
- **`normalize`** (C2) — quotient `MPoly` by the sorted-monomial-combine relation; canonical rep = the sorted list.
- **SPPF intern** (C1) — quotient the term algebra by structural equality (content-address, children-as-ids); canonical rep = the interned node. (= the `.agdai` core the jea extractor reads.)
- **ExpLogCodec** — quotient-*transport*: negation = `antilog ∘ involute-about-𝟙 ∘ log` (`codec-inverse : expL x · expL (neg x) ≈ 𝟙`, DERIVED). The additive `neg` on the log side IS the multiplicative reciprocal on the exp side — a quot() carrying negation across the +↔× bridge, no inverse in the carrier.
- **GradedProductOver ℕ×ℕ** (R4) — quotient by the difference relation `a−b ≡ c−d ↦ a+d ≡ c+b` (`_≈D_`) = the Grothendieck group construction; `split : ℤ → ℕ×ℕ` + `split-hom` is the quotient map.
- **CF/EEA + Lawvere** — the terminal-coalgebra / factoradic canonical form + `prove-or-correct`'s no-dead-end = the totality that makes a quotient a *decision procedure*.
- **LehmerPath / extruder** — quotient `Perm` by the factoradic canonical form; `encode` = the quotient map to the Lehmer rep, `enum≤`-first-hit = that same rep by enumeration.

⟹ `normalize`, intern, `log/quot/antilog`, the difference-pair, CF/EEA, LehmerPath are ONE thing: **`recon q b r`
read as a quotient** (`a = q·b + r`, the div-mod wedge — `q` the quotient, `r` the residue/coset). Negation, the
apparent SPPF blocker, is itself a quot(). ⚑ TO PIN: the exact in-tree term "algebraically relating these moves as
quot()s" (candidates: the `_≈D_` Grothendieck quotient in `JacobianNegSemiring`, the div-mod `recon` in
`Algebra/Wedge`, `NilpotentLogExpBridge`'s log↔exp intertwine) — the user says it exists "somewhere"; searched but
not yet singled out.

---

## THE C2 SPINE (the landing route, restated so no `≈ℚ` is composed)

`evalℚ R.fᵢ ≈ℚ C.fᵢ` becomes `normalize R.fᵢ ≡ normalize Cᴹfᵢ`. R nests left-assoc, C right-assoc → not `≡` raw, but
`normalize` sends both to the identical canonical list → `refl` (or one-shot `coeff-canonicity`,
`MPolySemiring.agda:333`). **The entire degree-9 reassociation moves into the rigid `refl`, where there is no `≈ℚ`
to compose.** Anchors: `MPolyNormalize.normalize` `:142`, `isSortedB` `:160`, `*P-normalizeˡ/ʳ`
`MPolySemiring.agda:230/311`, `*P-assoc` `:129`.

The chain that reaches the literal ℚ statement, routing all hard reassociation through the rigid step:

    evalℚ R.fᵢ  ≈ℚ  evalℚ(normalize R.fᵢ)  ≡[cong evalℚ, refl]  evalℚ(normalize Cᴹfᵢ)  ≈ℚ  evalℚ Cᴹfᵢ  ≈ℚ  C.fᵢ
                └─────── β ───────┘          └────── step 3 (rigid ℤ) ──────┘        └─── β ───┘   └── γ ──┘

- **step 3** `normalize R.fᵢ ≡ normalize Cᴹfᵢ` — rigid ℤ `refl`; the reassociation lives here, no `≈ℚ`.
- **γ** `evalℚ Cᴹfᵢ ≈ℚ C.fᵢ` — Cᴹfᵢ transcribed with C's *same* association tree → structural / refl-per-node.
- **β** `evalℚ p ≈ℚ evalℚ (normalize p)` — the ONE new `≈ℚ` lemma, by induction on `normalize`'s `foldr insertT`,
  each step a *fixed* atomic fact (`+ℚ-comm` reorder, `k₁·m +ℚ k₂·m ≈ℚ (k₁+k₂)·m` combine). **A different shape
  from the wall** — structural fold-induction, not nested endpoint-inference over the degree — reused at both R and Cᴹ.

---

## ⚑ NEW DIMENSION — THE WALL IS *INFERENCE*, NOT COMPOSITION (β landed)

The wall was mis-diagnosed as "hand-composed `≈ℚ` is intractable." **Probed empirically:**
- Inferred endpoints wall UNIVERSALLY — even the fully-*abstract* `+ℚ` reassoc (`gtM-pattern A B P Q`)
  fails (EXIT 42). `ℚ` is an eta-record, so *every* `ℚ` eta-expands to `mkℚ (num …)(den-1 …)` and `+ℚ`
  reduces; reading an endpoint off any `≈ℚ` sub-proof unfolds to non-injective `num`/`den`. So concreteness
  was never the issue — it's Agda's implicit INFERENCE reading endpoints through the transparent relation.
- **Fully-PINNED endpoints LAND** — the same `gtM-pattern` with every `+ℚ-cong {a}{a′}{b}{b′}` /
  `≈ℚ-trans {a}{b}{c}` implicit supplied typechecks (EXIT 0). No inference is left to fail. **This is exactly
  the "extrude/extract the fully-elaborated proof, use it as the hand proof" pipeline** — the pinned term IS
  the synthesized canonical proof.

⚑⚑ **THE WALL IS *UNIFORMLY* INFERENCE — routes A, B, β, γ all.** Re-probed the *multiplicative* nested
cong-inside-cong (swap4 shape) fully-pinned → **EXIT 0**, correcting the earlier "swap4 resists even pinned"
claim. So the whole arc's "wall" is ONE thing: Agda's implicit INFERENCE reading `≈ℚ` endpoints through the
transparent eta-record relation. Fully-pinned terms land — additive AND multiplicative, at depth. The original
hand-composed bridge (`JacobianEncoding*`) walled at `gen-v` ONLY because it used the `≈⟨_⟩_` reasoning
combinator (inferred endpoints); fully-pinned it would land. So the literal ℚ statement `evalℚ R.fᵢ ≈ℚ C.fᵢ`
is NOT un-writable — it needs the endpoints SUPPLIED (= synthesized), never inferred. This is exactly the
"extrude/extract the elaborated proof, use it as the hand proof" pipeline: the synthesizer's job is to produce
the all-endpoints-pinned term. ⟹ γ is TRACTABLE (fully-pinned eval-`*P` homomorphism, or the cleaner
graded-hom/FreeUP lift where `GradedHomOver` parameterizes `≈ℚ` as the target so only the shallow generator
laws are proven and the deep composition is lifted by uniqueness).

⟹ **β (`◆jac-eval-respects-normalize`) IS BUILT — `JacobianEvalNormalize.agda` → EXIT 0.**
`normalize-eval : evalℚ p ≈ℚ evalℚ (normalize p)` by fully-pinned additive induction
(`consNZ-eval` → `insertT-eval` [ltM/eqM≡/gtM] → `normalize-eval`; atomic `evalT-zero`/`coeff-combine`/
`ℤ→ℚ-+ℚ-hom`). **PAYOFF: `evalBridge₁/₂/₃ : evalℚ fᵢ ≈ℚ evalℚ Cᴹfᵢ`** — β lifts C2's rigid `bridgeᵢ` across
the evaluator (`normalize-eval fᵢ` ⊕ `≡→≈ℚ (cong evalℚ bridgeᵢ)` ⊕ `≈ℚ-sym (normalize-eval Cᴹfᵢ)`). So the
two encodings of F agree WHEN EVALUATED at ANY point x y z — a genuine ℚ-level `≈ℚ` identification, not the
rigid-only variant.

## ⚑⚑ THE LITERAL STATEMENT IS CLOSED — `◆jac-gamma` DONE (EXIT 0, machine-checked)

`Substrate.Algebra.Q.JacobianEncodingLiteral` → EXIT 0, `--safe --without-K`, no postulates/holes:

    literal₁/₂/₃ : (x y z : ℚ) → evalℚ x y z R.fᵢ ≈ℚ C.fᵢ x y z          -- THE WHOLE STONE, closed.
    γ₁/₂/₃       : evalℚ Cᴹfᵢ ≈ℚ C.fᵢ x y z                              -- the last inch, closed.

**THE METHOD — a FREE-ALGEBRA UNIVERSAL-PROPERTY LIFT (the lawvere/extruder machinery), NOT hand-composed ≈ℚ.**
The wall is INFERENCE (transparent eta-`ℚ`), so a degree-9 hand-pinned chain is intractable. Instead the DEEP
composition is lifted by ONE uniqueness induction:
- `Expr` — the free commutative-ring term on `{x,y,z,+,·,−}` (point-independent syntax); `encode : Expr → MPoly`
  (`⊕E↦+P`, `⊗E↦*P`, `⊖E a b ↦ a +P kP(-1)*P b`, `eK↦kP`, `eX↦X`, …); `evalDirect : Expr → ℚ` (the direct ℚ fold).
- `homAgree : (e) → evalℚ (encode e) ≈ℚ evalDirect e` — the UNIQUENESS, by structural induction. Each constructor
  is a SHALLOW one-operation fully-PINNED ≈ℚ fact over ABSTRACT sub-results (which land — the finding). The deep
  tree never enters an ≈ℚ endpoint.
- `eᵢ` mirrors C's OWN grouping, so `encode eᵢ` reduces to `Cᴹfᵢ` and `evalDirect eᵢ` to `C.fᵢ x y z` — both by
  `refl`. Hence **`γᵢ = homAgree eᵢ`** directly, and **`literalᵢ = ≈ℚ-trans (evalBridgeᵢ) γᵢ`** (β ⊕ γ).
- SHALLOW HOM LAWS built (pinned, abstract, once): `evalℚ-++`, `evalℚ-*P` (via `evalℚ-scaleT`/`evalT-mulT`/
  `monoval-hom`/`powℚ-+`/`swap4`/`swap6`/`assoc-lll`/`distrib`), `gen-X/Y/Z/kP`, `neg-·-l`/`neg-cong` (the `⊖E`).
- **META-REFLECTION = the jea extractor on the `.agdai`** (as the Stone predicted): `jea_agdai.decode_core` reads
  the compiled core = 58 defmarks / 3626 interned nodes = the canonical normal-form proof DAG (the deep pinned
  terms `homAgree` GENERATED, content-addressed + shared). `literal₁/₂/₃`, `γ₁/₂/₃`, `homAgree`, `evalℚ-*P` all
  present at `sort UType level 0` (no Set₁ debt). The elaborator wrote the deep terms; the extractor read them out.

⟹ This is the operational law realized at the LITERAL level: `homAgree` is the codec `φ` (evalℚ) lifted by the
free-`Expr` UP, so the whole degree-9 reassociation is the induction, never a hand-pinned chain. The negative
A/B branches (`scratch/jac-wall-witness/`, EXIT-1) remain the machine-checked evidence of the inference wall
(their local `≈⟨_⟩_` reasoning combinator walls universally under eta — even `assoc-lll`); this module is the
positive close via the machinery.

---

## STANDING

- `◆jac-eval-respects-normalize` (β) — the one labelled-open lemma; the literal-ℚ last inch. Fold-induction shape.
- ⟡push — unpushed stack (17 unpushed; the USER pushes, never the assistant; wait for the post-commit amend marker).
- ⟡free-comm-monoid-3gen (§SAT-B) — NOT allocated.
